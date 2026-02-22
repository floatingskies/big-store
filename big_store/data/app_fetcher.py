"""
Big Store - Unified App Fetcher
Fetches apps from all sources with proper metadata
"""

import subprocess
import threading
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

from big_store.models import AppInfo
from big_store.data.popular_apps import (
    POPULAR_APPS, PACKAGE_IDS, 
    get_popular_app_keys, get_app_metadata, get_package_id, search_popular_apps
)
from big_store.utils.icon_manager import icon_manager


class UnifiedAppFetcher:
    """Unified app fetcher that combines all sources"""
    
    def __init__(self):
        self._available_sources = self._detect_sources()
        self._apps_cache: List[AppInfo] = []
        self._installed_cache: Dict[str, List[str]] = {}
        
    def _detect_sources(self) -> Dict[str, bool]:
        """Detect available package sources"""
        sources = {
            'flatpak': False,
            'snap': False,
            'aur': False,
            'native': False,
            'distrobox': False
        }
        
        # Check flatpak
        try:
            result = subprocess.run(['flatpak', '--version'], capture_output=True, timeout=5)
            sources['flatpak'] = result.returncode == 0
        except Exception:
            pass
            
        # Check snap
        try:
            result = subprocess.run(['snap', '--version'], capture_output=True, timeout=5)
            sources['snap'] = result.returncode == 0
        except Exception:
            pass
            
        # Check AUR helper
        for helper in ['paru', 'yay', 'pamac']:
            try:
                result = subprocess.run(['which', helper], capture_output=True, timeout=5)
                if result.returncode == 0:
                    sources['aur'] = True
                    break
            except Exception:
                pass
                
        # Check native package manager
        for pm in ['pamac', 'pacman', 'apt', 'dnf']:
            try:
                result = subprocess.run(['which', pm], capture_output=True, timeout=5)
                if result.returncode == 0:
                    sources['native'] = True
                    break
            except Exception:
                pass
                
        # Check distrobox
        try:
            result = subprocess.run(['distrobox', 'version'], capture_output=True, timeout=5)
            sources['distrobox'] = result.returncode == 0
        except Exception:
            pass
            
        return sources
        
    def get_available_sources(self) -> List[str]:
        """Get list of available sources"""
        return [s for s, available in self._available_sources.items() if available]
        
    def _get_installed_flatpaks(self) -> List[str]:
        """Get list of installed Flatpak IDs"""
        installed = []
        if not self._available_sources['flatpak']:
            return installed
            
        try:
            result = subprocess.run(
                ['flatpak', 'list', '--app', '--columns=application'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                installed = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        except Exception:
            pass
        return installed
        
    def _get_installed_snaps(self) -> List[str]:
        """Get list of installed Snap names"""
        installed = []
        if not self._available_sources['snap']:
            return installed
            
        try:
            result = subprocess.run(
                ['snap', 'list'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                installed = [line.split()[0] for line in lines if line.strip()]
        except Exception:
            pass
        return installed
        
    def _get_installed_aur(self) -> List[str]:
        """Get list of installed AUR packages"""
        installed = []
        try:
            result = subprocess.run(
                ['pacman', '-Qm'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                installed = [line.split()[0] for line in result.stdout.strip().split('\n') if line.strip()]
        except Exception:
            pass
        return installed
        
    def _get_installed_native(self) -> List[str]:
        """Get list of installed native packages"""
        installed = []
        
        # Try pamac first
        try:
            result = subprocess.run(
                ['pamac', 'list', '--installed'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                installed = [line.split()[0] for line in result.stdout.strip().split('\n') if line.strip()]
                return installed
        except Exception:
            pass
            
        # Try pacman
        try:
            result = subprocess.run(
                ['pacman', '-Q'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                installed = [line.split()[0] for line in result.stdout.strip().split('\n') if line.strip()]
                return installed
        except Exception:
            pass
            
        # Try apt
        try:
            result = subprocess.run(
                ['apt', 'list', '--installed'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '/' in line:
                        installed.append(line.split('/')[0])
        except Exception:
            pass
            
        return installed
        
    def _load_installed_cache(self):
        """Load installed packages from all sources"""
        self._installed_cache = {
            'flatpak': self._get_installed_flatpaks(),
            'snap': self._get_installed_snaps(),
            'aur': self._get_installed_aur(),
            'native': self._get_installed_native(),
        }
        
    def _is_installed(self, pkg_id: str, source: str) -> bool:
        """Check if a package is installed"""
        if source in self._installed_cache:
            return pkg_id in self._installed_cache[source]
        return False
        
    def get_all_apps(self, progress_callback: Callable = None) -> List[AppInfo]:
        """Get all available apps from popular apps database"""
        self._load_installed_cache()
        apps = []
        seen_ids = set()
        
        total = len(get_popular_app_keys())
        current = 0
        
        for app_key in get_popular_app_keys():
            current += 1
            if progress_callback:
                progress_callback(current / total)
                
            metadata = get_app_metadata(app_key)
            if not metadata:
                continue
                
            # Create app for each available source
            for source in self.get_available_sources():
                pkg_id = get_package_id(app_key, source)
                
                if pkg_id is None:
                    continue
                    
                # Skip if already added
                cache_key = f"{pkg_id}:{source}"
                if cache_key in seen_ids:
                    continue
                seen_ids.add(cache_key)
                
                # Check if installed
                installed = self._is_installed(pkg_id, source)
                
                # Get icon
                icon_name = icon_manager.get_icon_name(pkg_id, metadata['name'], source)
                
                app = AppInfo(
                    id=pkg_id,
                    name=metadata['name'],
                    summary=metadata['summary'],
                    icon_name=icon_name,
                    developer=metadata.get('developer', ''),
                    categories=metadata.get('categories', []),
                    source=source,
                    installed=installed,
                    downloads=metadata.get('downloads', 0),
                    rating=metadata.get('rating', 0),
                )
                apps.append(app)
                
        self._apps_cache = apps
        return apps
        
    def search(self, query: str) -> List[AppInfo]:
        """Search for apps"""
        results = []
        seen_ids = set()
        
        # Search in popular apps
        for app_key, metadata in search_popular_apps(query):
            for source in self.get_available_sources():
                pkg_id = get_package_id(app_key, source)
                
                if pkg_id is None:
                    continue
                    
                cache_key = f"{pkg_id}:{source}"
                if cache_key in seen_ids:
                    continue
                seen_ids.add(cache_key)
                
                installed = self._is_installed(pkg_id, source)
                icon_name = icon_manager.get_icon_name(pkg_id, metadata['name'], source)
                
                app = AppInfo(
                    id=pkg_id,
                    name=metadata['name'],
                    summary=metadata['summary'],
                    icon_name=icon_name,
                    developer=metadata.get('developer', ''),
                    categories=metadata.get('categories', []),
                    source=source,
                    installed=installed,
                )
                results.append(app)
                
        # Also search live in package managers
        results.extend(self._search_live(query, seen_ids))
        
        return results
        
    def _search_live(self, query: str, seen_ids: set) -> List[AppInfo]:
        """Search live in package managers"""
        results = []
        
        # Search Flatpak
        if self._available_sources['flatpak']:
            try:
                result = subprocess.run(
                    ['flatpak', 'search', query, '--columns=id,name,description'],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line and '\t' in line:
                            parts = line.split('\t')
                            app_id = parts[0]
                            cache_key = f"{app_id}:flatpak"
                            
                            if cache_key not in seen_ids:
                                seen_ids.add(cache_key)
                                name = parts[1] if len(parts) > 1 else app_id.split('.')[-1]
                                summary = parts[2] if len(parts) > 2 else ''
                                
                                results.append(AppInfo(
                                    id=app_id,
                                    name=name,
                                    summary=summary[:100],
                                    icon_name=icon_manager.get_icon_name(app_id, name, 'flatpak'),
                                    source='flatpak',
                                    installed=self._is_installed(app_id, 'flatpak'),
                                ))
            except Exception:
                pass
                
        # Search Snap
        if self._available_sources['snap']:
            try:
                result = subprocess.run(
                    ['snap', 'find', query],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]
                    for line in lines:
                        if line.strip():
                            parts = line.split(None, 4)
                            if parts:
                                name = parts[0]
                                cache_key = f"{name}:snap"
                                
                                if cache_key not in seen_ids:
                                    seen_ids.add(cache_key)
                                    summary = parts[4] if len(parts) > 4 else 'Snap package'
                                    
                                    results.append(AppInfo(
                                        id=name,
                                        name=name.replace('-', ' ').title(),
                                        summary=summary[:100],
                                        icon_name=icon_manager.get_icon_name(name, name, 'snap'),
                                        source='snap',
                                        installed=self._is_installed(name, 'snap'),
                                    ))
            except Exception:
                pass
                
        return results
        
    def get_apps_by_source(self, source: str) -> List[AppInfo]:
        """Get apps filtered by source"""
        return [app for app in self._apps_cache if app.source == source]
        
    def get_installed_apps(self) -> List[AppInfo]:
        """Get all installed apps"""
        return [app for app in self._apps_cache if app.installed]
