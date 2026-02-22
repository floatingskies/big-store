"""
Big Store - Native Package Manager
Multi-distro native package management
Supports: pacman, apt, dnf, zypper
"""

import subprocess
import os
from typing import List, Dict, Optional, Tuple

from big_store.models import AppInfo, DistroInfo
from big_store.utils.icon_manager import icon_manager


class NativeManager:
    """Manager for native packages across distributions"""
    
    def __init__(self, distro_info: Optional[DistroInfo] = None):
        self._distro = distro_info
        self._package_manager = self._detect_package_manager()
        
    def _detect_package_manager(self) -> str:
        """Detect which package manager is available"""
        managers = ['pamac', 'pacman', 'apt', 'dnf', 'zypper', 'apk', 'xbps-install']
        
        for pm in managers:
            try:
                result = subprocess.run(['which', pm], capture_output=True, timeout=5)
                if result.returncode == 0:
                    return pm
            except Exception:
                continue
        return 'unknown'
        
    def _get_icon(self, pkg_name: str, app_name: str) -> str:
        """Get icon for native package"""
        return icon_manager.get_icon_name(pkg_name, app_name, 'native')
        
    def _command_exists(self, cmd: str) -> bool:
        """Check if command exists"""
        try:
            subprocess.run(['which', cmd], capture_output=True, timeout=5)
            return True
        except Exception:
            return False
            
    def get_installed(self) -> List[AppInfo]:
        """Get list of installed native packages"""
        apps = []
        
        if self._package_manager == 'pamac':
            apps = self._get_installed_pamac()
        elif self._package_manager == 'pacman':
            apps = self._get_installed_pacman()
        elif self._package_manager == 'apt':
            apps = self._get_installed_apt()
        elif self._package_manager == 'dnf':
            apps = self._get_installed_dnf()
            
        return apps
        
    def _get_installed_pamac(self) -> List[AppInfo]:
        """Get installed packages using pamac"""
        apps = []
        try:
            result = subprocess.run(
                ['pamac', 'list', '--installed'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if parts:
                            pkg_name = parts[0]
                            version = parts[1] if len(parts) > 1 else ''
                            
                            # Get icon
                            icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                            
                            apps.append(AppInfo(
                                id=pkg_name,
                                name=pkg_name.replace('-', ' ').title(),
                                summary='Native package',
                                version=version,
                                source='native',
                                installed=True,
                                icon_name=icon_name,
                                categories=['installed']
                            ))
        except Exception as e:
            print(f"Pamac get_installed error: {e}")
        return apps
        
    def _get_installed_pacman(self) -> List[AppInfo]:
        """Get installed packages using pacman"""
        apps = []
        try:
            result = subprocess.run(
                ['pacman', '-Q'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            pkg_name = parts[0]
                            version = parts[1]
                            
                            # Get icon
                            icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                            
                            apps.append(AppInfo(
                                id=pkg_name,
                                name=pkg_name.replace('-', ' ').title(),
                                summary='Native package',
                                version=version,
                                source='native',
                                installed=True,
                                icon_name=icon_name,
                                categories=['installed']
                            ))
        except Exception as e:
            print(f"Pacman get_installed error: {e}")
        return apps
        
    def _get_installed_apt(self) -> List[AppInfo]:
        """Get installed packages using apt"""
        apps = []
        try:
            result = subprocess.run(
                ['apt', 'list', '--installed'],
                capture_output=True, text=True, timeout=60,
                env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and '/' in line:
                        parts = line.split('/')
                        pkg_name = parts[0]
                        
                        # Get icon
                        icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                        
                        apps.append(AppInfo(
                            id=pkg_name,
                            name=pkg_name.replace('-', ' ').title(),
                            summary='Native package',
                            source='native',
                            installed=True,
                            icon_name=icon_name,
                            categories=['installed']
                        ))
        except Exception as e:
            print(f"Apt get_installed error: {e}")
        return apps
        
    def _get_installed_dnf(self) -> List[AppInfo]:
        """Get installed packages using dnf"""
        apps = []
        try:
            result = subprocess.run(
                ['dnf', 'list', 'installed'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and '.' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            pkg_name = parts[0].split('.')[0]
                            version = parts[1]
                            
                            # Get icon
                            icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                            
                            apps.append(AppInfo(
                                id=pkg_name,
                                name=pkg_name.replace('-', ' ').title(),
                                summary='Native package',
                                version=version,
                                source='native',
                                installed=True,
                                icon_name=icon_name,
                                categories=['installed']
                            ))
        except Exception as e:
            print(f"Dnf get_installed error: {e}")
        return apps
        
    def get_available(self) -> List[AppInfo]:
        """Get list of available packages"""
        apps = []
        
        if self._package_manager == 'pamac':
            apps = self._get_available_pamac()
        elif self._package_manager == 'pacman':
            apps = self._get_available_pacman()
        elif self._package_manager == 'apt':
            apps = self._get_available_apt()
        elif self._package_manager == 'dnf':
            apps = self._get_available_dnf()
            
        return apps
        
    def _get_available_pamac(self) -> List[AppInfo]:
        """Get available packages using pamac"""
        apps = []
        try:
            result = subprocess.run(
                ['pamac', 'search', '--repo', '-q'],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n')[:200]:  # Limit
                    if line:
                        icon_name = self._get_icon(line, line.replace('-', ' ').title())
                        
                        apps.append(AppInfo(
                            id=line,
                            name=line.replace('-', ' ').title(),
                            summary='Native package',
                            source='native',
                            installed=False,
                            icon_name=icon_name,
                            categories=['available']
                        ))
        except Exception as e:
            print(f"Pamac get_available error: {e}")
        return apps
        
    def _get_available_pacman(self) -> List[AppInfo]:
        """Get available packages using pacman"""
        apps = []
        try:
            result = subprocess.run(
                ['pacman', '-Sl'],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                seen = set()
                for line in result.stdout.strip().split('\n')[:500]:  # Limit
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] not in seen:
                        seen.add(parts[1])
                        pkg_name = parts[1]
                        version = parts[2]
                        installed = '[installed]' in line
                        
                        icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                        
                        apps.append(AppInfo(
                            id=pkg_name,
                            name=pkg_name.replace('-', ' ').title(),
                            summary='Native package',
                            version=version,
                            source='native',
                            installed=installed,
                            icon_name=icon_name,
                            categories=['available']
                        ))
        except Exception as e:
            print(f"Pacman get_available error: {e}")
        return apps
        
    def _get_available_apt(self) -> List[AppInfo]:
        """Get available packages using apt"""
        apps = []
        try:
            result = subprocess.run(
                ['apt', 'cache', 'search', '.'],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n')[:300]:  # Limit
                    if line:
                        parts = line.split(' - ', 1)
                        if parts:
                            pkg_name = parts[0].strip()
                            summary = parts[1] if len(parts) > 1 else 'Native package'
                            
                            icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                            
                            apps.append(AppInfo(
                                id=pkg_name,
                                name=pkg_name.replace('-', ' ').title(),
                                summary=summary[:100],
                                source='native',
                                installed=False,
                                icon_name=icon_name,
                                categories=['available']
                            ))
        except Exception as e:
            print(f"Apt get_available error: {e}")
        return apps
        
    def _get_available_dnf(self) -> List[AppInfo]:
        """Get available packages using dnf"""
        apps = []
        try:
            result = subprocess.run(
                ['dnf', 'list', 'available'],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n')[:300]:  # Limit
                    if line and '.' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            pkg_name = parts[0].split('.')[0]
                            version = parts[1]
                            
                            icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                            
                            apps.append(AppInfo(
                                id=pkg_name,
                                name=pkg_name.replace('-', ' ').title(),
                                summary='Native package',
                                version=version,
                                source='native',
                                installed=False,
                                icon_name=icon_name,
                                categories=['available']
                            ))
        except Exception as e:
            print(f"Dnf get_available error: {e}")
        return apps
        
    def get_apps(self) -> List[AppInfo]:
        """Get all apps (installed + available)"""
        all_apps = self.get_installed()
        installed_ids = {app.id for app in all_apps}
        
        for app in self.get_available():
            if app.id not in installed_ids:
                all_apps.append(app)
                
        return all_apps
        
    def search(self, query: str) -> List[AppInfo]:
        """Search for packages"""
        apps = []
        
        if self._package_manager == 'pamac':
            try:
                result = subprocess.run(
                    ['pamac', 'search', '--repo', query],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = line.split(maxsplit=1)
                            if parts:
                                pkg_name = parts[0]
                                summary = parts[1] if len(parts) > 1 else ''
                                
                                icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                                
                                apps.append(AppInfo(
                                    id=pkg_name,
                                    name=pkg_name.replace('-', ' ').title(),
                                    summary=summary[:100],
                                    source='native',
                                    icon_name=icon_name
                                ))
            except Exception as e:
                print(f"Pamac search error: {e}")
                
        elif self._package_manager == 'pacman':
            try:
                result = subprocess.run(
                    ['pacman', '-Ss', query],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    current_pkg = None
                    for line in result.stdout.split('\n'):
                        if line and not line.startswith(' '):
                            parts = line.split()
                            if parts:
                                pkg_name = parts[0].split('/')[-1]
                                version = parts[1] if len(parts) > 1 else ''
                                
                                icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                                
                                current_pkg = AppInfo(
                                    id=pkg_name,
                                    name=pkg_name.replace('-', ' ').title(),
                                    summary='',
                                    version=version,
                                    source='native',
                                    icon_name=icon_name
                                )
                                apps.append(current_pkg)
                        elif line.startswith('    ') and current_pkg:
                            current_pkg.description = line.strip()
            except Exception as e:
                print(f"Pacman search error: {e}")
                
        elif self._package_manager == 'apt':
            try:
                result = subprocess.run(
                    ['apt', 'cache', 'search', query],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = line.split(' - ', 1)
                            if parts:
                                pkg_name = parts[0].strip()
                                summary = parts[1] if len(parts) > 1 else ''
                                
                                icon_name = self._get_icon(pkg_name, pkg_name.replace('-', ' ').title())
                                
                                apps.append(AppInfo(
                                    id=pkg_name,
                                    name=pkg_name.replace('-', ' ').title(),
                                    summary=summary[:100],
                                    source='native',
                                    icon_name=icon_name
                                ))
            except Exception as e:
                print(f"Apt search error: {e}")
                
        return apps
        
    def install(self, pkg_name: str) -> Tuple[bool, str]:
        """Install a package"""
        if self._package_manager == 'pamac':
            try:
                result = subprocess.run(
                    ['pamac', 'install', '--no-confirm', pkg_name],
                    capture_output=True, text=True, timeout=300
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        elif self._package_manager == 'pacman':
            try:
                result = subprocess.run(
                    ['sudo', 'pacman', '-S', '--noconfirm', pkg_name],
                    capture_output=True, text=True, timeout=300
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        elif self._package_manager == 'apt':
            try:
                result = subprocess.run(
                    ['sudo', 'apt', 'install', '-y', pkg_name],
                    capture_output=True, text=True, timeout=300
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        elif self._package_manager == 'dnf':
            try:
                result = subprocess.run(
                    ['sudo', 'dnf', 'install', '-y', pkg_name],
                    capture_output=True, text=True, timeout=300
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        return False, "No package manager available"
        
    def uninstall(self, pkg_name: str) -> Tuple[bool, str]:
        """Uninstall a package"""
        if self._package_manager == 'pamac':
            try:
                result = subprocess.run(
                    ['pamac', 'remove', '--no-confirm', pkg_name],
                    capture_output=True, text=True, timeout=120
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        elif self._package_manager == 'pacman':
            try:
                result = subprocess.run(
                    ['sudo', 'pacman', '-Rns', '--noconfirm', pkg_name],
                    capture_output=True, text=True, timeout=120
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        elif self._package_manager == 'apt':
            try:
                result = subprocess.run(
                    ['sudo', 'apt', 'remove', '-y', pkg_name],
                    capture_output=True, text=True, timeout=120
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        elif self._package_manager == 'dnf':
            try:
                result = subprocess.run(
                    ['sudo', 'dnf', 'remove', '-y', pkg_name],
                    capture_output=True, text=True, timeout=120
                )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        return False, "No package manager available"
        
    def update(self, pkg_name: str = None) -> Tuple[bool, str]:
        """Update packages"""
        if self._package_manager == 'pamac':
            try:
                if pkg_name:
                    result = subprocess.run(
                        ['pamac', 'update', pkg_name],
                        capture_output=True, text=True, timeout=300
                    )
                else:
                    result = subprocess.run(
                        ['pamac', 'update', '--no-confirm'],
                        capture_output=True, text=True, timeout=600
                    )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        elif self._package_manager == 'pacman':
            try:
                if pkg_name:
                    result = subprocess.run(
                        ['sudo', 'pacman', '-S', '--noconfirm', pkg_name],
                        capture_output=True, text=True, timeout=300
                    )
                else:
                    result = subprocess.run(
                        ['sudo', 'pacman', '-Syu', '--noconfirm'],
                        capture_output=True, text=True, timeout=600
                    )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        elif self._package_manager == 'apt':
            try:
                subprocess.run(['sudo', 'apt', 'update'], capture_output=True, timeout=60)
                if pkg_name:
                    result = subprocess.run(
                        ['sudo', 'apt', 'install', '--only-upgrade', '-y', pkg_name],
                        capture_output=True, text=True, timeout=300
                    )
                else:
                    result = subprocess.run(
                        ['sudo', 'apt', 'upgrade', '-y'],
                        capture_output=True, text=True, timeout=600
                    )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        elif self._package_manager == 'dnf':
            try:
                if pkg_name:
                    result = subprocess.run(
                        ['sudo', 'dnf', 'upgrade', '-y', pkg_name],
                        capture_output=True, text=True, timeout=300
                    )
                else:
                    result = subprocess.run(
                        ['sudo', 'dnf', 'upgrade', '-y'],
                        capture_output=True, text=True, timeout=600
                    )
                return result.returncode == 0, result.stdout + result.stderr
            except Exception as e:
                return False, str(e)
                
        return False, "No package manager available"
