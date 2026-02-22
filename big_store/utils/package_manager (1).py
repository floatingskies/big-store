"""
Big Store - Package Manager
Main package manager that coordinates all package sources
"""

import subprocess
import os
from typing import List, Dict, Optional, Callable, Tuple
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from big_store.models import AppInfo, DistroInfo, DistroType
from big_store.managers.flatpak_manager import FlatpakManager
from big_store.managers.snap_manager import SnapManager
from big_store.managers.aur_manager import AURManager
from big_store.managers.native_manager import NativeManager
from big_store.managers.distrobox_manager import DistroboxManager


class PackageManager:
    """
    Main package manager that coordinates all package sources.
    Detects the distribution and uses the appropriate native package manager.
    """
    
    def __init__(self):
        self._distro_info: Optional[DistroInfo] = None
        self._managers: Dict[str, any] = {}
        self._cache: List[AppInfo] = []
        self._cache_valid = False
        
        # Detect distribution
        self._detect_distribution()
        
        # Initialize managers
        self._init_managers()
        
    def _detect_distribution(self) -> DistroInfo:
        """Detect the current Linux distribution"""
        distro_info = None
        
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                distro_info = self._parse_os_release(content)
                
        if not distro_info or distro_info.distro_type == DistroType.UNKNOWN:
            distro_info = self._detect_via_package_manager()
            
        self._distro_info = distro_info or DistroInfo(
            name='Unknown',
            distro_type=DistroType.UNKNOWN,
            version='',
            package_manager='auto'
        )
        
        return self._distro_info
        
    def _parse_os_release(self, content: str) -> Optional[DistroInfo]:
        """Parse /etc/os-release content"""
        data = {}
        
        for line in content.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                data[key] = value.strip('"\'')
                
        name = data.get('NAME', 'Unknown').lower()
        version = data.get('VERSION_ID', '')
        codename = data.get('VERSION_CODENAME', '')
        
        distro_type = DistroType.UNKNOWN
        base = ''
        package_manager = ''
        supports_aur = False
        
        if 'biglinux' in name:
            distro_type = DistroType.BIGLINUX
            base = 'arch'
            package_manager = 'pacman'
            supports_aur = True
        elif 'manjaro' in name:
            distro_type = DistroType.MANJARO
            base = 'arch'
            package_manager = 'pacman'
            supports_aur = True
        elif 'endeavouros' in name:
            distro_type = DistroType.ENDEAVOUROS
            base = 'arch'
            package_manager = 'pacman'
            supports_aur = True
        elif 'garuda' in name:
            distro_type = DistroType.GARUDA
            base = 'arch'
            package_manager = 'pacman'
            supports_aur = True
        elif 'arch' in name:
            distro_type = DistroType.ARCH
            base = 'arch'
            package_manager = 'pacman'
            supports_aur = True
        elif 'fedora' in name:
            distro_type = DistroType.FEDORA
            base = 'rhel'
            package_manager = 'dnf'
        elif 'ubuntu' in name:
            distro_type = DistroType.UBUNTU
            base = 'debian'
            package_manager = 'apt'
        elif 'debian' in name:
            distro_type = DistroType.DEBIAN
            base = 'debian'
            package_manager = 'apt'
        elif 'opensuse' in name or 'suse' in name:
            distro_type = DistroType.OPENSUSE
            base = 'suse'
            package_manager = 'zypper'
        elif 'gentoo' in name:
            distro_type = DistroType.GENTOO
            base = 'gentoo'
            package_manager = 'emerge'
        elif 'void' in name:
            distro_type = DistroType.VOID
            base = 'void'
            package_manager = 'xbps'
        elif 'alpine' in name:
            distro_type = DistroType.ALPINE
            base = 'alpine'
            package_manager = 'apk'
            
        return DistroInfo(
            name=data.get('PRETTY_NAME', data.get('NAME', 'Unknown')),
            distro_type=distro_type,
            version=version,
            codename=codename,
            base=base,
            package_manager=package_manager,
            supports_aur=supports_aur
        )
        
    def _detect_via_package_manager(self) -> Optional[DistroInfo]:
        """Detect distribution via available package manager"""
        package_managers = [
            ('pacman', 'arch', 'pacman', True),
            ('apt', 'debian', 'apt', False),
            ('dnf', 'rhel', 'dnf', False),
            ('zypper', 'suse', 'zypper', False),
        ]
        
        for cmd, base, pm, supports_aur in package_managers:
            if self._command_exists(cmd):
                return DistroInfo(
                    name='Auto-detected',
                    distro_type=DistroType.UNKNOWN,
                    version='',
                    base=base,
                    package_manager=pm,
                    supports_aur=supports_aur
                )
        return None
        
    def _command_exists(self, command: str) -> bool:
        try:
            subprocess.run(['which', command], capture_output=True, timeout=5)
            return True
        except Exception:
            return False
            
    def _init_managers(self):
        """Initialize package managers"""
        # Always initialize Flatpak (cross-distro)
        if self._command_exists('flatpak'):
            self._managers['flatpak'] = FlatpakManager()
            
        # Initialize Snap (cross-distro)
        if self._command_exists('snap'):
            self._managers['snap'] = SnapManager()
            
        # Initialize AUR for Arch-based distros
        if self._distro_info and self._distro_info.supports_aur:
            if self._command_exists('paru') or self._command_exists('yay') or self._command_exists('pamac'):
                self._managers['aur'] = AURManager()
                
        # Initialize native package manager
        self._managers['native'] = NativeManager(self._distro_info)
        
        # Initialize Distrobox
        if self._command_exists('distrobox'):
            self._managers['distrobox'] = DistroboxManager()
            
    def get_distro_info(self) -> DistroInfo:
        return self._distro_info
        
    def get_available_sources(self) -> List[str]:
        return list(self._managers.keys())
        
    def refresh_cache(self, callback: Callable = None):
        def _refresh():
            self._cache = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {}
                for source, manager in self._managers.items():
                    future = executor.submit(manager.get_apps)
                    futures[future] = source
                    
                for future in concurrent.futures.as_completed(futures):
                    source = futures[future]
                    try:
                        apps = future.result()
                        self._cache.extend(apps)
                    except Exception as e:
                        print(f"Error refreshing {source}: {e}")
                        
            self._cache_valid = True
            if callback:
                callback()
                
        import threading
        thread = threading.Thread(target=_refresh, daemon=True)
        thread.start()
        
    def get_all_apps(self) -> List[AppInfo]:
        if not self._cache_valid:
            self._cache = []
            for source, manager in self._managers.items():
                try:
                    apps = manager.get_apps()
                    self._cache.extend(apps)
                except Exception as e:
                    print(f"Error getting apps from {source}: {e}")
            self._cache_valid = True
        return self._cache
        
    def search_apps(self, query: str, sources: List[str] = None) -> List[AppInfo]:
        results = []
        query_lower = query.lower()
        
        for app in self.get_all_apps():
            if sources and app.source not in sources:
                continue
            if (query_lower in app.name.lower() or
                query_lower in app.summary.lower() or
                query_lower in app.description.lower()):
                results.append(app)
        return results
        
    def get_app(self, app_id: str, source: str = None) -> Optional[AppInfo]:
        for app in self.get_all_apps():
            if app.id == app_id:
                if source is None or app.source == source:
                    return app
        return None
        
    def install_app(self, app: AppInfo, callback: Callable[[bool, str], None] = None):
        manager = self._managers.get(app.source)
        if not manager:
            if callback:
                callback(False, f"Source {app.source} not available")
            return
            
        def _install():
            try:
                success, message = manager.install(app.id)
                if success:
                    app.installed = True
                    self._cache_valid = False
                if callback:
                    callback(success, message)
            except Exception as e:
                if callback:
                    callback(False, str(e))
                    
        import threading
        thread = threading.Thread(target=_install, daemon=True)
        thread.start()
        
    def uninstall_app(self, app: AppInfo, callback: Callable[[bool, str], None] = None):
        manager = self._managers.get(app.source)
        if not manager:
            if callback:
                callback(False, f"Source {app.source} not available")
            return
            
        def _uninstall():
            try:
                success, message = manager.uninstall(app.id)
                if success:
                    app.installed = False
                    self._cache_valid = False
                if callback:
                    callback(success, message)
            except Exception as e:
                if callback:
                    callback(False, str(e))
                    
        import threading
        thread = threading.Thread(target=_uninstall, daemon=True)
        thread.start()
        
    def update_app(self, app: AppInfo, callback: Callable[[bool, str], None] = None):
        manager = self._managers.get(app.source)
        if not manager:
            if callback:
                callback(False, f"Source {app.source} not available")
            return
            
        def _update():
            try:
                success, message = manager.update(app.id)
                if success:
                    app.update_available = False
                if callback:
                    callback(success, message)
            except Exception as e:
                if callback:
                    callback(False, str(e))
                    
        import threading
        thread = threading.Thread(target=_update, daemon=True)
        thread.start()
        
    def enable_flatpak(self, callback: Callable[[bool, str], None] = None):
        def _enable():
            try:
                if not self._command_exists('flatpak'):
                    native = self._managers.get('native')
                    if native:
                        success, msg = native.install('flatpak')
                        if not success:
                            if callback:
                                callback(False, f"Failed to install flatpak: {msg}")
                            return
                            
                subprocess.run(
                    ['flatpak', 'remote-add', '--if-not-exists', 'flathub',
                     'https://flathub.org/repo/flathub.flatpakrepo'],
                    capture_output=True, check=True
                )
                self._managers['flatpak'] = FlatpakManager()
                if callback:
                    callback(True, "Flatpak enabled successfully")
            except Exception as e:
                if callback:
                    callback(False, str(e))
                    
        import threading
        thread = threading.Thread(target=_enable, daemon=True)
        thread.start()
        
    def enable_snap(self, callback: Callable[[bool, str], None] = None):
        def _enable():
            try:
                if not self._command_exists('snap'):
                    native = self._managers.get('native')
                    if native:
                        success, msg = native.install('snapd')
                        if not success:
                            if callback:
                                callback(False, f"Failed to install snapd: {msg}")
                            return
                            
                subprocess.run(
                    ['systemctl', 'enable', '--now', 'snapd.socket'],
                    capture_output=True, check=True
                )
                self._managers['snap'] = SnapManager()
                if callback:
                    callback(True, "Snap enabled successfully")
            except Exception as e:
                if callback:
                    callback(False, str(e))
                    
        import threading
        thread = threading.Thread(target=_enable, daemon=True)
        thread.start()
        
    def install_deb_with_debtap(self, deb_path: str, callback: Callable[[bool, str], None] = None):
        if not self._distro_info or self._distro_info.base != 'arch':
            if callback:
                callback(False, "debtap is only available on Arch-based systems")
            return
            
        def _install():
            try:
                if not self._command_exists('debtap'):
                    aur = self._managers.get('aur')
                    if aur:
                        success, msg = aur.install('debtap')
                        if not success:
                            if callback:
                                callback(False, f"Failed to install debtap: {msg}")
                            return
                            
                subprocess.run(['sudo', 'debtap', '-u'], capture_output=True, check=True)
                output_pkg = deb_path.replace('.deb', '')
                subprocess.run(['debtap', '-Q', deb_path], capture_output=True, check=True)
                
                pkg_file = output_pkg + '.pkg.tar.zst'
                subprocess.run(['sudo', 'pacman', '-U', pkg_file, '--noconfirm'], capture_output=True, check=True)
                
                if callback:
                    callback(True, "Package installed successfully")
            except Exception as e:
                if callback:
                    callback(False, str(e))
                    
        import threading
        thread = threading.Thread(target=_install, daemon=True)
        thread.start()
