"""
Big Store - Helper Utilities
General helper functions
"""

import os
import re
import subprocess
from typing import Optional, List, Tuple
import shutil


def get_icon_path(icon_name: str, size: int = 64) -> Optional[str]:
    """
    Get the path to an icon.
    
    Args:
        icon_name: Icon name (with or without extension)
        size: Desired icon size
        
    Returns:
        Path to icon or None if not found
    """
    # Common icon directories
    icon_dirs = [
        '/usr/share/icons',
        '/usr/share/pixmaps',
        os.path.expanduser('~/.local/share/icons'),
        os.path.expanduser('~/.icons'),
    ]
    
    # Remove extension if present
    name = os.path.splitext(icon_name)[0]
    
    # Extensions to search
    extensions = ['.svg', '.png', '.xpm', '.jpg', '.jpeg']
    
    for icon_dir in icon_dirs:
        if not os.path.exists(icon_dir):
            continue
            
        # Search recursively
        for root, dirs, files in os.walk(icon_dir):
            for ext in extensions:
                # Try exact name
                icon_path = os.path.join(root, name + ext)
                if os.path.exists(icon_path):
                    return icon_path
                    
                # Try with app- prefix
                icon_path = os.path.join(root, 'app-' + name + ext)
                if os.path.exists(icon_path):
                    return icon_path
                    
    # Check pixmaps
    pixmaps_dir = '/usr/share/pixmaps'
    if os.path.exists(pixmaps_dir):
        for ext in extensions:
            icon_path = os.path.join(pixmaps_dir, name + ext)
            if os.path.exists(icon_path):
                return icon_path
                
    return None


def format_size(size_bytes: int) -> str:
    """
    Format bytes to human readable size.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes is None or size_bytes == 0:
        return '0 B'
        
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    
    for unit in units:
        if size < 1024:
            if unit == 'B':
                return f'{int(size)} {unit}'
            return f'{size:.1f} {unit}'
        size /= 1024
        
    return f'{size:.1f} PB'


def format_downloads(count: int) -> str:
    """
    Format download count to human readable format.
    
    Args:
        count: Number of downloads
        
    Returns:
        Formatted count string
    """
    if count is None or count == 0:
        return '0'
        
    if count >= 1000000:
        return f'{count / 1000000:.1f}M'
    elif count >= 1000:
        return f'{count / 1000:.1f}K'
    else:
        return str(count)


def format_duration(seconds: float) -> str:
    """
    Format duration to human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f'{int(seconds)}s'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f'{minutes}m {secs}s'
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f'{hours}h {minutes}m'


def sanitize_package_name(name: str) -> str:
    """
    Sanitize a package name for safe use.
    
    Args:
        name: Package name
        
    Returns:
        Sanitized name
    """
    # Remove unsafe characters
    safe = re.sub(r'[^a-zA-Z0-9._-]', '-', name)
    return safe.strip('-._')


def parse_depends(depends_str: str) -> List[str]:
    """
    Parse package dependencies string.
    
    Args:
        depends_str: Dependency string from package manager
        
    Returns:
        List of package names
    """
    if not depends_str:
        return []
        
    # Remove version constraints
    deps = []
    
    for dep in depends_str.split():
        # Handle >=, <=, >, <, = constraints
        name = re.split(r'[><=]', dep)[0]
        if name:
            deps.append(name)
            
    return deps


def is_process_running(process_name: str) -> bool:
    """
    Check if a process is running.
    
    Args:
        process_name: Name of the process
        
    Returns:
        True if running, False otherwise
    """
    try:
        result = subprocess.run(
            ['pgrep', '-x', process_name],
            capture_output=True
        )
        return result.returncode == 0
    except Exception:
        return False


def get_command_output(cmd: List[str], timeout: int = 10) -> Tuple[bool, str]:
    """
    Get output from a command.
    
    Args:
        cmd: Command and arguments
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def get_desktop_file_path(app_id: str) -> Optional[str]:
    """
    Find the .desktop file for an application.
    
    Args:
        app_id: Application ID
        
    Returns:
        Path to .desktop file or None
    """
    # Common desktop file directories
    desktop_dirs = [
        '/usr/share/applications',
        '/usr/local/share/applications',
        os.path.expanduser('~/.local/share/applications'),
        '/var/lib/flatpak/exports/share/applications',
        os.path.expanduser('~/.local/share/flatpak/exports/share/applications'),
    ]
    
    # Try different naming conventions
    names = [
        f'{app_id}.desktop',
        f'{app_id.lower()}.desktop',
        f'{app_id.replace(".", "-")}.desktop',
        f'{app_id.split(".")[-1]}.desktop',
    ]
    
    for desktop_dir in desktop_dirs:
        if not os.path.exists(desktop_dir):
            continue
            
        for name in names:
            path = os.path.join(desktop_dir, name)
            if os.path.exists(path):
                return path
                
        # Search for partial matches
        for filename in os.listdir(desktop_dir):
            if app_id.lower() in filename.lower() and filename.endswith('.desktop'):
                return os.path.join(desktop_dir, filename)
                
    return None


def parse_desktop_file(path: str) -> dict:
    """
    Parse a .desktop file.
    
    Args:
        path: Path to .desktop file
        
    Returns:
        Dictionary of key-value pairs
    """
    data = {}
    
    if not os.path.exists(path):
        return data
        
    in_desktop_entry = False
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            
            if line == '[Desktop Entry]':
                in_desktop_entry = True
                continue
            elif line.startswith('[') and in_desktop_entry:
                break
                
            if in_desktop_entry and '=' in line:
                key, value = line.split('=', 1)
                data[key.strip()] = value.strip()
                
    return data


def get_app_icon_from_desktop(app_id: str) -> Optional[str]:
    """
    Get the icon name for an application from its .desktop file.
    
    Args:
        app_id: Application ID
        
    Returns:
        Icon name or path
    """
    desktop_path = get_desktop_file_path(app_id)
    
    if not desktop_path:
        return None
        
    desktop_data = parse_desktop_file(desktop_path)
    
    return desktop_data.get('Icon')


def get_system_memory() -> int:
    """
    Get total system memory in bytes.
    
    Returns:
        Total memory in bytes
    """
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    # Value is in kB
                    return int(line.split()[1]) * 1024
    except Exception:
        pass
        
    return 0


def get_cpu_count() -> int:
    """
    Get the number of CPU cores.
    
    Returns:
        Number of CPU cores
    """
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1


def check_disk_space(path: str = '/') -> Tuple[int, int]:
    """
    Check available disk space.
    
    Args:
        path: Path to check
        
    Returns:
        Tuple of (total, available) in bytes
    """
    try:
        stat = shutil.disk_usage(path)
        return stat.total, stat.free
    except Exception:
        return 0, 0


def get_package_size(pkg_name: str) -> Optional[int]:
    """
    Get the installed size of a package.
    
    Args:
        pkg_name: Package name
        
    Returns:
        Size in bytes or None
    """
    # Try pacman first
    success, output = get_command_output(['pacman', '-Qi', pkg_name])
    
    if success:
        for line in output.split('\n'):
            if line.startswith('Installed Size'):
                size_str = line.split(':')[1].strip()
                return parse_size_string(size_str)
                
    # Try dpkg
    success, output = get_command_output(['dpkg', '-s', pkg_name])
    
    if success:
        for line in output.split('\n'):
            if line.startswith('Installed-Size:'):
                size_kb = int(line.split(':')[1].strip())
                return size_kb * 1024
                
    return None


def parse_size_string(size_str: str) -> int:
    """
    Parse a size string to bytes.
    
    Args:
        size_str: Size string like "10.5 MB"
        
    Returns:
        Size in bytes
    """
    match = re.match(r'([\d.]+)\s*([KMGT]?B)?', size_str, re.IGNORECASE)
    
    if not match:
        return 0
        
    size = float(match.group(1))
    unit = (match.group(2) or 'B').upper()
    
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }
    
    return int(size * multipliers.get(unit, 1))
