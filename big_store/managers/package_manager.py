"""
Big Store - Package Manager
Main package manager that coordinates all package sources
"""

import subprocess
import os
import threading
from typing import List, Dict, Optional, Callable, Tuple

from big_store.models import AppInfo, DistroInfo, DistroType
from big_store.data.app_fetcher import UnifiedAppFetcher
from big_store.utils.icon_manager import icon_manager


class PackageManager:
    """
    Main package manager that coordinates all package sources.
    """
    
    def __init__(self):
        self._fetcher = UnifiedAppFetcher()
        self._cache: List[AppInfo] = []
        self._cache_valid = False
        
    def get_available_sources(self) -> List[str]:
        """Get list of available package sources"""
        return self._fetcher.get_available_sources()
        
    def get_all_apps(self) -> List[AppInfo]:
        """Get all available apps"""
        if not self._cache_valid:
            self._cache = self._fetcher.get_all_apps()
            self._cache_valid = True
        return self._cache
        
    def search_apps(self, query: str) -> List[AppInfo]:
        """Search for apps"""
        return self._fetcher.search(query)
        
    def refresh_cache(self, callback: Callable = None):
        """Refresh app cache"""
        def _refresh():
            self._cache = self._fetcher.get_all_apps()
            self._cache_valid = True
            if callback:
                callback()
                
        thread = threading.Thread(target=_refresh, daemon=True)
        thread.start()
        
    def install_app(self, app: AppInfo, callback: Callable[[bool, str], None] = None):
        """Install an app"""
        def _install():
            success, message = self._install_package(app.id, app.source)
            if success:
                app.installed = True
            if callback:
                callback(success, message)
                
        thread = threading.Thread(target=_install, daemon=True)
        thread.start()
        
    def _install_package(self, pkg_id: str, source: str) -> Tuple[bool, str]:
        """Install a package based on source"""
        try:
            if source == 'flatpak':
                result = subprocess.run(
                    ['flatpak', 'install', '-y', 'flathub', pkg_id],
                    capture_output=True, text=True, timeout=300
                )
                return result.returncode == 0, result.stdout + result.stderr
                
            elif source == 'snap':
                result = subprocess.run(
                    ['sudo', 'snap', 'install', pkg_id],
                    capture_output=True, text=True, timeout=300
                )
                return result.returncode == 0, result.stdout + result.stderr
                
            elif source == 'aur':
                # Try with available AUR helper
                for helper in ['paru', 'yay', 'pamac']:
                    try:
                        subprocess.run(['which', helper], capture_output=True, timeout=5)
                        if helper == 'pamac':
                            result = subprocess.run(
                                ['pamac', 'build', '--no-confirm', pkg_id],
                                capture_output=True, text=True, timeout=600
                            )
                        else:
                            result = subprocess.run(
                                [helper, '-S', '--noconfirm', pkg_id],
                                capture_output=True, text=True, timeout=600
                            )
                        return result.returncode == 0, result.stdout + result.stderr
                    except Exception:
                        continue
                return False, "No AUR helper available"
                
            elif source == 'native':
                # Try with available package manager
                for pm in ['pamac', 'pacman', 'apt', 'dnf']:
                    try:
                        subprocess.run(['which', pm], capture_output=True, timeout=5)
                        if pm == 'pamac':
                            result = subprocess.run(
                                ['pamac', 'install', '--no-confirm', pkg_id],
                                capture_output=True, text=True, timeout=300
                            )
                        elif pm == 'pacman':
                            result = subprocess.run(
                                ['sudo', 'pacman', '-S', '--noconfirm', pkg_id],
                                capture_output=True, text=True, timeout=300
                            )
                        elif pm == 'apt':
                            result = subprocess.run(
                                ['sudo', 'apt', 'install', '-y', pkg_id],
                                capture_output=True, text=True, timeout=300
                            )
                        elif pm == 'dnf':
                            result = subprocess.run(
                                ['sudo', 'dnf', 'install', '-y', pkg_id],
                                capture_output=True, text=True, timeout=300
                            )
                        return result.returncode == 0, result.stdout + result.stderr
                    except Exception:
                        continue
                return False, "No package manager available"
                
            return False, f"Unknown source: {source}"
            
        except Exception as e:
            return False, str(e)
            
    def uninstall_app(self, app: AppInfo, callback: Callable[[bool, str], None] = None):
        """Uninstall an app"""
        def _uninstall():
            success, message = self._uninstall_package(app.id, app.source)
            if success:
                app.installed = False
            if callback:
                callback(success, message)
                
        thread = threading.Thread(target=_uninstall, daemon=True)
        thread.start()
        
    def _uninstall_package(self, pkg_id: str, source: str) -> Tuple[bool, str]:
        """Uninstall a package"""
        try:
            if source == 'flatpak':
                result = subprocess.run(
                    ['flatpak', 'uninstall', '-y', pkg_id],
                    capture_output=True, text=True, timeout=120
                )
                return result.returncode == 0, result.stdout + result.stderr
                
            elif source == 'snap':
                result = subprocess.run(
                    ['sudo', 'snap', 'remove', pkg_id],
                    capture_output=True, text=True, timeout=120
                )
                return result.returncode == 0, result.stdout + result.stderr
                
            elif source in ('aur', 'native'):
                for pm in ['pamac', 'pacman', 'apt', 'dnf']:
                    try:
                        subprocess.run(['which', pm], capture_output=True, timeout=5)
                        if pm == 'pamac':
                            result = subprocess.run(
                                ['pamac', 'remove', '--no-confirm', pkg_id],
                                capture_output=True, text=True, timeout=120
                            )
                        elif pm == 'pacman':
                            result = subprocess.run(
                                ['sudo', 'pacman', '-Rns', '--noconfirm', pkg_id],
                                capture_output=True, text=True, timeout=120
                            )
                        elif pm == 'apt':
                            result = subprocess.run(
                                ['sudo', 'apt', 'remove', '-y', pkg_id],
                                capture_output=True, text=True, timeout=120
                            )
                        elif pm == 'dnf':
                            result = subprocess.run(
                                ['sudo', 'dnf', 'remove', '-y', pkg_id],
                                capture_output=True, text=True, timeout=120
                            )
                        return result.returncode == 0, result.stdout + result.stderr
                    except Exception:
                        continue
                return False, "No package manager available"
                
            return False, f"Unknown source: {source}"
            
        except Exception as e:
            return False, str(e)
            
    def run_app(self, app: AppInfo) -> Tuple[bool, str]:
        """Run an installed application"""
        try:
            if app.source == 'flatpak':
                subprocess.Popen(['flatpak', 'run', app.id])
            elif app.source == 'snap':
                subprocess.Popen([app.id])
            else:
                # Try to find the executable
                exec_name = app.id.split('.')[-1] if '.' in app.id else app.id
                subprocess.Popen([exec_name])
            return True, "Application started"
        except Exception as e:
            return False, str(e)
