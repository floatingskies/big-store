"""
Big Store - Cache Utilities
Caching system for application data
"""

import json
import os
import time
import hashlib
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import pickle


@dataclass
class CacheEntry:
    """A cache entry with expiration"""
    key: str
    data: Any
    created: float
    expires: float
    
    def is_expired(self) -> bool:
        return time.time() > self.expires


class AppCache:
    """In-memory and persistent cache for app data"""
    
    def __init__(self, cache_dir: str = None, default_ttl: int = 3600):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory for persistent cache storage
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        
        # Setup cache directory
        if cache_dir:
            self._cache_dir = cache_dir
        else:
            home = os.path.expanduser('~')
            self._cache_dir = os.path.join(home, '.cache', 'big-store')
            
        os.makedirs(self._cache_dir, exist_ok=True)
        
        # Load persistent cache
        self._load_persistent_cache()
        
    def _get_cache_path(self) -> str:
        """Get the persistent cache file path"""
        return os.path.join(self._cache_dir, 'app_cache.json')
        
    def _load_persistent_cache(self):
        """Load cache from disk"""
        cache_path = self._get_cache_path()
        
        if not os.path.exists(cache_path):
            return
            
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                
            current_time = time.time()
            
            for key, entry in data.items():
                # Skip expired entries
                if entry.get('expires', 0) > current_time:
                    self._cache[key] = CacheEntry(
                        key=key,
                        data=entry.get('data'),
                        created=entry.get('created', current_time),
                        expires=entry.get('expires', current_time + self._default_ttl)
                    )
        except Exception:
            # If cache is corrupted, start fresh
            self._cache = {}
            
    def _save_persistent_cache(self):
        """Save cache to disk"""
        cache_path = self._get_cache_path()
        
        try:
            data = {}
            
            for key, entry in self._cache.items():
                # Only save serializable data
                if isinstance(entry.data, (str, int, float, list, dict, bool, type(None))):
                    data[key] = {
                        'key': entry.key,
                        'data': entry.data,
                        'created': entry.created,
                        'expires': entry.expires
                    }
                    
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
            
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                return None
                
            if entry.is_expired():
                del self._cache[key]
                return None
                
            return entry.data
            
    def set(self, key: str, data: Any, ttl: int = None):
        """Set a value in cache"""
        ttl = ttl or self._default_ttl
        
        with self._lock:
            self._cache[key] = CacheEntry(
                key=key,
                data=data,
                created=time.time(),
                expires=time.time() + ttl
            )
            
        # Save to disk asynchronously
        threading.Thread(target=self._save_persistent_cache, daemon=True).start()
        
    def delete(self, key: str):
        """Delete a value from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            
        # Remove cache file
        cache_path = self._get_cache_path()
        if os.path.exists(cache_path):
            os.remove(cache_path)
            
    def cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            expired = [k for k, v in self._cache.items() if v.is_expired()]
            for key in expired:
                del self._cache[key]
                
    def get_or_set(self, key: str, factory: callable, ttl: int = None) -> Any:
        """Get from cache or compute and store"""
        value = self.get(key)
        
        if value is None:
            value = factory()
            self.set(key, value, ttl)
            
        return value
        
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for v in self._cache.values() if v.is_expired())
            
            return {
                'total_entries': total,
                'valid_entries': total - expired,
                'expired_entries': expired,
                'cache_dir': self._cache_dir
            }


class IconCache:
    """Specialized cache for application icons"""
    
    def __init__(self, cache_dir: str = None):
        if cache_dir:
            self._cache_dir = cache_dir
        else:
            home = os.path.expanduser('~')
            self._cache_dir = os.path.join(home, '.cache', 'big-store', 'icons')
            
        os.makedirs(self._cache_dir, exist_ok=True)
        
    def get_icon_path(self, icon_name: str, size: int = 64) -> Optional[str]:
        """Get cached icon path or return None"""
        # Look up icon in system theme first
        try:
            import gi
            gi.require_version('Gtk', '4.0')
            from gi.repository import Gtk
            
            theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
            icon = theme.lookup_icon(icon_name, None, size, 1, 
                                     Gtk.TextDirection.NONE, 0)
            if icon:
                return icon.get_file().get_path()
        except Exception:
            pass
            
        # Check cache
        cached = os.path.join(self._cache_dir, f'{icon_name}_{size}.png')
        if os.path.exists(cached):
            return cached
            
        return None
        
    def cache_icon(self, icon_name: str, icon_data: bytes, size: int = 64) -> str:
        """Cache an icon"""
        path = os.path.join(self._cache_dir, f'{icon_name}_{size}.png')
        
        with open(path, 'wb') as f:
            f.write(icon_data)
            
        return path
        
    def clear(self):
        """Clear the icon cache"""
        import shutil
        if os.path.exists(self._cache_dir):
            shutil.rmtree(self._cache_dir)
            os.makedirs(self._cache_dir, exist_ok=True)


# Need to import Gdk for IconCache
try:
    import gi
    gi.require_version('Gdk', '4.0')
    from gi.repository import Gdk
except Exception:
    pass
