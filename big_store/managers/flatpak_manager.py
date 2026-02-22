"""
Big Store - Flatpak Manager
Manage Flatpak applications with real system integration
"""

import subprocess
import os
from typing import List, Optional, Tuple

from big_store.models import AppInfo
from big_store.utils.icon_manager import icon_manager


class FlatpakManager:
    """Manager for Flatpak applications"""
    
    def __init__(self):
        self._available = self._check_available()
        
    def _check_available(self) -> bool:
        """Check if Flatpak is available"""
        try:
            result = subprocess.run(
                ['flatpak', '--version'],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
            
    def is_available(self) -> bool:
        return self._available
        
    def _get_icon(self, app_id: str, app_name: str) -> str:
        """Get icon for Flatpak app"""
        return icon_manager.get_icon_name(app_id, app_name, 'flatpak')
        
    def get_installed(self) -> List[AppInfo]:
        """Get list of installed Flatpak apps"""
        apps = []
        
        if not self._available:
            return apps
            
        try:
            result = subprocess.run(
                ['flatpak', 'list', '--app', '--columns=id,name,version,branch,description'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            app_id = parts[0]
                            name = parts[1] if len(parts) > 1 else app_id.split('.')[-1]
                            version = parts[2] if len(parts) > 2 else ''
                            description = parts[4] if len(parts) > 4 else ''
                            
                            apps.append(AppInfo(
                                id=app_id,
                                name=name,
                                summary=description[:100] if description else 'Flatpak application',
                                description=description,
                                version=version,
                                source='flatpak',
                                installed=True,
                                icon_name=self._get_icon(app_id, name),
                                categories=['installed']
                            ))
        except Exception as e:
            print(f"Flatpak get_installed error: {e}")
            
        return apps
        
    def get_apps(self) -> List[AppInfo]:
        """Get all available Flatpak apps"""
        all_apps = self.get_installed()
        installed_ids = {app.id for app in all_apps}
        
        if not self._available:
            return all_apps
            
        try:
            # Search for apps in different categories
            search_terms = ['browser', 'editor', 'media', 'game', 'office', 'graphics', 
                           'development', 'utilities', 'network', 'audio', 'video']
            
            for search_term in search_terms:
                try:
                    result = subprocess.run(
                        ['flatpak', 'search', search_term, '--columns=id,name,version,description,rating'],
                        capture_output=True, text=True, timeout=30
                    )
                    
                    if result.returncode == 0:
                        for line in result.stdout.strip().split('\n'):
                            if line and '\t' in line:
                                parts = line.split('\t')
                                if len(parts) >= 2:
                                    app_id = parts[0]
                                    
                                    if app_id not in installed_ids:
                                        name = parts[1] if len(parts) > 1 else app_id.split('.')[-1]
                                        version = parts[2] if len(parts) > 2 else ''
                                        summary = parts[3] if len(parts) > 3 else ''
                                        summary = summary[:150] if summary else 'Flatpak application'
                                        
                                        # Get icon
                                        icon_name = self._get_icon(app_id, name)
                                        
                                        all_apps.append(AppInfo(
                                            id=app_id,
                                            name=name,
                                            summary=summary,
                                            version=version,
                                            source='flatpak',
                                            installed=False,
                                            icon_name=icon_name,
                                            categories=['available']
                                        ))
                                        installed_ids.add(app_id)
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Flatpak get_apps error: {e}")
            
        return all_apps
        
    def install(self, app_id: str, remote: str = 'flathub') -> Tuple[bool, str]:
        """Install a Flatpak app"""
        if not self._available:
            return False, "Flatpak is not available"
            
        try:
            result = subprocess.run(
                ['flatpak', 'install', '-y', remote, app_id],
                capture_output=True, text=True, timeout=300
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
            
    def uninstall(self, app_id: str) -> Tuple[bool, str]:
        """Uninstall a Flatpak app"""
        if not self._available:
            return False, "Flatpak is not available"
            
        try:
            result = subprocess.run(
                ['flatpak', 'uninstall', '-y', app_id],
                capture_output=True, text=True, timeout=120
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
            
    def update(self, app_id: str = None) -> Tuple[bool, str]:
        """Update Flatpak apps"""
        if not self._available:
            return False, "Flatpak is not available"
            
        try:
            if app_id:
                result = subprocess.run(
                    ['flatpak', 'update', '-y', app_id],
                    capture_output=True, text=True, timeout=300
                )
            else:
                result = subprocess.run(
                    ['flatpak', 'update', '-y'],
                    capture_output=True, text=True, timeout=600
                )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
