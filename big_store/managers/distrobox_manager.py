"""
Big Store - Distrobox Manager
Manage Distrobox containers
"""

import subprocess
import os
from typing import List, Dict, Optional, Tuple

from big_store.models import AppInfo, DistroboxContainer
from big_store.utils.icon_manager import icon_manager


class DistroboxManager:
    """Manager for Distrobox containers"""
    
    DISTRO_IMAGES = {
        'archlinux': 'archlinux:latest',
        'ubuntu': 'ubuntu:latest',
        'ubuntu-22.04': 'ubuntu:22.04',
        'ubuntu-24.04': 'ubuntu:24.04',
        'fedora': 'fedora:latest',
        'fedora-40': 'fedora:40',
        'debian': 'debian:latest',
        'debian-12': 'debian:bookworm',
        'opensuse-tumbleweed': 'opensuse/tumbleweed:latest',
        'alpine': 'alpine:latest',
        'centos-stream9': 'quay.io/centos/centos:stream9',
        'rocky-linux-9': 'rockylinux:9',
        'alma-linux-9': 'almalinux:9',
        'void-linux': 'ghcr.io/void-linux/void-glibc:latest',
        'gentoo': 'gentoo/stage3:latest',
    }
    
    # Distro icons mapping
    DISTRO_ICONS = {
        'arch': 'archlinux-logo',
        'ubuntu': 'ubuntu-logo',
        'fedora': 'fedora-logo',
        'debian': 'debian-logo',
        'opensuse': 'opensuse-logo',
        'alpine': 'alpine-logo',
        'centos': 'centos-logo',
        'rocky': 'rocky-logo',
        'alma': 'almalinux-logo',
        'void': 'void-logo',
        'gentoo': 'gentoo-logo',
    }
    
    def __init__(self):
        self._available = self._check_available()
        
    def _check_available(self) -> bool:
        """Check if Distrobox is available"""
        try:
            result = subprocess.run(['distrobox', 'version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
            
    def is_available(self) -> bool:
        return self._available
        
    def _get_distro_icon(self, distro_name: str) -> str:
        """Get icon for distro"""
        distro_lower = distro_name.lower()
        
        for key, icon in self.DISTRO_ICONS.items():
            if key in distro_lower:
                # Try to get from system theme
                if icon_manager._icon_theme and icon_manager._icon_theme.has_icon(icon):
                    return icon
                # Fallback to generic
                return 'system-run-symbolic'
                
        return 'system-run-symbolic'
        
    def _run(self, args: List[str], timeout: int = 300) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ['distrobox'] + args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except FileNotFoundError:
            return False, "Distrobox is not installed"
        except Exception as e:
            return False, str(e)
            
    def get_containers(self) -> List[DistroboxContainer]:
        containers = []
        
        if not self._available:
            return containers
            
        success, output = self._run(['list', '--no-color'])
        
        if success:
            for line in output.strip().split('\n')[1:]:
                if line.strip():
                    container = self._parse_container_line(line)
                    if container:
                        containers.append(container)
        return containers
        
    def _parse_container_line(self, line: str) -> Optional[DistroboxContainer]:
        try:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                return DistroboxContainer(
                    name=parts[0],
                    image=parts[1],
                    status=parts[2],
                    distro=parts[3],
                    home=parts[4] if len(parts) > 4 else ''
                )
        except Exception:
            pass
        return None
        
    def get_apps(self) -> List[AppInfo]:
        apps = []
        
        if not self._available:
            return apps
            
        containers = self.get_containers()
        
        for container in containers:
            if 'running' in container.status.lower() or 'up' in container.status.lower():
                # Get icon for the distro
                icon_name = self._get_distro_icon(container.distro)
                
                # Add container as an "app"
                apps.append(AppInfo(
                    id=f'distrobox-{container.name}',
                    name=container.name.replace('-', ' ').title(),
                    summary=f'{container.distro} container',
                    description=f'Distrobox container running {container.distro} from {container.image}',
                    source='distrobox',
                    installed=True,
                    icon_name=icon_name,
                    categories=['container', 'running']
                ))
                
                # Check for exported apps
                home = os.path.expanduser('~')
                apps_dir = os.path.join(home, '.local', 'share', 'applications')
                
                if os.path.exists(apps_dir):
                    for filename in os.listdir(apps_dir):
                        if filename.startswith(f'distrobox-{container.name}'):
                            app_name = filename.replace(f'distrobox-{container.name}-', '').replace('.desktop', '')
                            
                            # Try to get icon for the app
                            app_icon = icon_manager.get_icon_name(app_name, app_name.replace('-', ' ').title(), 'distrobox')
                            
                            apps.append(AppInfo(
                                id=f'distrobox-{container.name}-{app_name}',
                                name=app_name.replace('-', ' ').title(),
                                summary=f'Application from {container.name}',
                                source='distrobox',
                                installed=True,
                                icon_name=app_icon,
                                categories=['exported']
                            ))
                            
        return apps
        
    def create(self, name: str, image: str = None) -> Tuple[bool, str]:
        if not self._available:
            return False, "Distrobox is not installed"
            
        if not image:
            image = self.DISTRO_IMAGES.get(name, 'ubuntu:latest')
        elif image in self.DISTRO_IMAGES:
            image = self.DISTRO_IMAGES[image]
            
        return self._run(['create', '--name', name, '--image', image, '--yes', '--pull'], timeout=600)
        
    def remove(self, name: str, force: bool = False) -> Tuple[bool, str]:
        if not self._available:
            return False, "Distrobox is not installed"
            
        args = ['rm', '--force', name] if force else ['rm', name]
        return self._run(args)
        
    def start(self, name: str) -> Tuple[bool, str]:
        if not self._available:
            return False, "Distrobox is not installed"
            
        return self._run(['start', name])
        
    def stop(self, name: str) -> Tuple[bool, str]:
        if not self._available:
            return False, "Distrobox is not installed"
            
        return self._run(['stop', name])
        
    def enter(self, name: str, command: str = None) -> Tuple[bool, str]:
        if not self._available:
            return False, "Distrobox is not installed"
            
        args = ['enter', name]
        if command:
            args.extend(['--', command])
        return self._run(args, timeout=3600)
        
    def run_command(self, name: str, command: str) -> Tuple[bool, str]:
        if not self._available:
            return False, "Distrobox is not installed"
            
        return self._run(['enter', name, '--', command], timeout=600)
        
    def export_app(self, container: str, app: str) -> Tuple[bool, str]:
        if not self._available:
            return False, "Distrobox is not installed"
            
        return self._run(['export', '--container', container, '--app', app])
        
    def list_available_distros(self) -> List[Dict]:
        return [
            {
                'id': key, 
                'image': value, 
                'name': key.replace('-', ' ').title(),
                'icon': self._get_distro_icon(key)
            }
            for key, value in self.DISTRO_IMAGES.items()
        ]
