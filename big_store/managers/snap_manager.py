"""
Big Store - Snap Manager
Manage Snap packages with real system integration
"""

import subprocess
import os
import json
import urllib.request
from typing import List, Optional, Tuple

from big_store.models import AppInfo
from big_store.utils.icon_manager import icon_manager


class SnapManager:
    """Manager for Snap packages"""
    
    def __init__(self):
        self._available = self._check_available()
        
    def _check_available(self) -> bool:
        """Check if Snap is available"""
        try:
            result = subprocess.run(
                ['snap', '--version'],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
            
    def is_available(self) -> bool:
        return self._available
        
    def _get_icon(self, snap_name: str) -> str:
        """Get icon for Snap package"""
        return icon_manager.get_icon_name(snap_name, snap_name.replace('-', ' ').title(), 'snap')
        
    def get_installed(self) -> List[AppInfo]:
        """Get list of installed Snap packages"""
        apps = []
        
        if not self._available:
            return apps
            
        try:
            result = subprocess.run(
                ['snap', 'list'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            version = parts[1]
                            
                            apps.append(AppInfo(
                                id=name,
                                name=name.replace('-', ' ').title(),
                                summary='Snap package',
                                version=version,
                                source='snap',
                                installed=True,
                                icon_name=self._get_icon(name),
                                categories=['installed']
                            ))
        except Exception as e:
            print(f"Snap get_installed error: {e}")
            
        return apps
        
    def get_apps(self) -> List[AppInfo]:
        """Get all available Snap packages"""
        all_apps = self.get_installed()
        installed_ids = {app.id for app in all_apps}
        
        if not self._available:
            return all_apps
            
        try:
            # Search for apps in different categories
            search_terms = ['editor', 'media', 'browser', 'game', 'tools', 'social', 
                           'productivity', 'development', 'utilities']
            
            for search_term in search_terms:
                try:
                    result = subprocess.run(
                        ['snap', 'find', search_term],
                        capture_output=True, text=True, timeout=20
                    )
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines[1:]:  # Skip header
                            if line.strip():
                                parts = line.split(None, 4)  # Split into max 5 parts
                                if len(parts) >= 2:
                                    name = parts[0]
                                    
                                    if name not in installed_ids:
                                        version = parts[1] if len(parts) > 1 else ''
                                        summary = parts[4] if len(parts) > 4 else 'Snap package'
                                        summary = summary[:100] if summary else 'Snap package'
                                        
                                        # Get icon
                                        icon_name = self._get_icon(name)
                                        
                                        all_apps.append(AppInfo(
                                            id=name,
                                            name=name.replace('-', ' ').title(),
                                            summary=summary,
                                            version=version,
                                            source='snap',
                                            installed=False,
                                            icon_name=icon_name,
                                            categories=['available']
                                        ))
                                        installed_ids.add(name)
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Snap get_apps error: {e}")
            
        return all_apps
        
    def install(self, snap_name: str, channel: str = 'stable', classic: bool = False) -> Tuple[bool, str]:
        """Install a Snap package"""
        if not self._available:
            return False, "Snap is not available"
            
        try:
            args = ['sudo', 'snap', 'install', snap_name]
            if channel != 'stable':
                args.extend(['--channel', channel])
            if classic:
                args.append('--classic')
                
            result = subprocess.run(args, capture_output=True, text=True, timeout=300)
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
            
    def uninstall(self, snap_name: str) -> Tuple[bool, str]:
        """Uninstall a Snap package"""
        if not self._available:
            return False, "Snap is not available"
            
        try:
            result = subprocess.run(
                ['sudo', 'snap', 'remove', snap_name],
                capture_output=True, text=True, timeout=120
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
            
    def update(self, snap_name: str = None) -> Tuple[bool, str]:
        """Update Snap packages"""
        if not self._available:
            return False, "Snap is not available"
            
        try:
            if snap_name:
                result = subprocess.run(
                    ['sudo', 'snap', 'refresh', snap_name],
                    capture_output=True, text=True, timeout=300
                )
            else:
                result = subprocess.run(
                    ['sudo', 'snap', 'refresh'],
                    capture_output=True, text=True, timeout=600
                )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
