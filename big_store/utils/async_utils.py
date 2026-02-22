"""
Big Store - Async Utilities
Utilities for running asynchronous tasks
"""

import threading
import queue
from typing import Callable, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, Future
import time


class AsyncTask:
    """Represents an asynchronous task"""
    
    def __init__(self, func: Callable, callback: Callable = None, *args, **kwargs):
        self.func = func
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.error = None
        self.completed = False
        self._future: Optional[Future] = None
        
    def run(self):
        """Execute the task"""
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.completed = True
            return self.result
        except Exception as e:
            self.error = e
            self.completed = True
            raise
            
    def on_complete(self):
        """Called when task completes"""
        if self.callback:
            try:
                if self.error:
                    self.callback(False, str(self.error))
                else:
                    self.callback(True, self.result)
            except Exception:
                pass


class AsyncRunner:
    """Manages asynchronous task execution"""
    
    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: List[AsyncTask] = []
        self._lock = threading.Lock()
        
    def submit(self, func: Callable, callback: Callable = None, *args, **kwargs) -> AsyncTask:
        """Submit a task for execution"""
        task = AsyncTask(func, callback, *args, **kwargs)
        
        with self._lock:
            self._tasks.append(task)
            
        def run_task():
            try:
                task.run()
            finally:
                task.on_complete()
                with self._lock:
                    if task in self._tasks:
                        self._tasks.remove(task)
                        
        task._future = self._executor.submit(run_task)
        return task
        
    def wait_all(self, timeout: float = None):
        """Wait for all tasks to complete"""
        with self._lock:
            tasks = list(self._tasks)
            
        for task in tasks:
            if task._future:
                task._future.result(timeout=timeout)
                
    def cancel_all(self):
        """Cancel all pending tasks"""
        with self._lock:
            for task in self._tasks:
                if task._future:
                    task._future.cancel()
            self._tasks.clear()
            
    def shutdown(self, wait: bool = True):
        """Shutdown the executor"""
        self._executor.shutdown(wait=wait)


class TaskQueue:
    """A queue for sequential task execution"""
    
    def __init__(self):
        self._queue = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_task: Optional[AsyncTask] = None
        
    def add(self, func: Callable, callback: Callable = None, *args, **kwargs) -> AsyncTask:
        """Add a task to the queue"""
        task = AsyncTask(func, callback, *args, **kwargs)
        self._queue.put(task)
        
        if not self._running:
            self._start()
            
        return task
        
    def _start(self):
        """Start processing the queue"""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._process_queue, daemon=True)
        self._thread.start()
        
    def _process_queue(self):
        """Process tasks in the queue"""
        while self._running:
            try:
                task = self._queue.get(timeout=1.0)
                self._current_task = task
                
                try:
                    task.run()
                    task.on_complete()
                except Exception as e:
                    task.error = e
                    task.on_complete()
                finally:
                    self._current_task = None
                    self._queue.task_done()
                    
            except queue.Empty:
                if self._queue.empty():
                    self._running = False
                    break
                    
    def pause(self):
        """Pause task processing"""
        self._running = False
        
    def resume(self):
        """Resume task processing"""
        if not self._running:
            self._start()
            
    def clear(self):
        """Clear all pending tasks"""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
                
    def size(self) -> int:
        """Get the number of pending tasks"""
        return self._queue.qsize()
        
    def is_running(self) -> bool:
        """Check if the queue is processing"""
        return self._running


class ProgressTracker:
    """Track progress of long-running operations"""
    
    def __init__(self, total: int = 100, on_update: Callable = None):
        self.total = total
        self.current = 0
        self.on_update = on_update
        self._start_time = time.time()
        
    def update(self, amount: int = 1, message: str = None):
        """Update progress"""
        self.current = min(self.current + amount, self.total)
        
        if self.on_update:
            progress = self.current / self.total if self.total > 0 else 0
            self.on_update(progress, message)
            
    def set_progress(self, current: int, message: str = None):
        """Set specific progress"""
        self.current = min(current, self.total)
        
        if self.on_update:
            progress = self.current / self.total if self.total > 0 else 0
            self.on_update(progress, message)
            
    @property
    def percentage(self) -> float:
        """Get progress as percentage"""
        return (self.current / self.total * 100) if self.total > 0 else 0
        
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self._start_time
        
    @property
    def estimated_remaining(self) -> float:
        """Estimate remaining time"""
        if self.current == 0:
            return 0
            
        elapsed = self.elapsed_time
        rate = self.current / elapsed
        remaining = self.total - self.current
        
        return remaining / rate if rate > 0 else 0
