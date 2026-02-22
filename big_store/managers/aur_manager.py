"""
Big Store - AUR Manager
Manage AUR packages for Arch-based distributions
"""

import subprocess
import urllib.request
import urllib.parse
import json
import os
from typing import List, Optional, Tuple

from big_store.models import AppInfo
from big_store.utils.icon_manager import icon_manager


class AURManager:
    """Manager for AUR packages"""
    
    AUR_RPC_URL = "https://aur.archlinux.org/rpc/"
    HELPERS = ['paru', 'yay', 'pamac', 'pacman']
    
    def __init__(self):
        self._helper = self._detect_helper()
        self._available = self._helper is not None
        
    def _detect_helper(self) -> Optional[str]:
        """Detect available AUR helper"""
        for helper in self.HELPERS:
            try:
                result = subprocess.run(
                    ['which', helper],
                    capture_output=True, timeout=5
                )
                if result.returncode == 0:
                    return helper
            except Exception:
                continue
        return None
        
    def is_available(self) -> bool:
        return self._available
        
    def _get_icon(self, pkg_name: str, app_name: str) -> str:
        """Get icon for AUR package"""
        return icon_manager.get_icon_name(pkg_name, app_name, 'aur')
        
    def _aur_rpc_call(self, method: str, args: dict) -> Optional[dict]:
        """Make an AUR RPC call"""
        try:
            params = urllib.parse.urlencode({'v': 5, 'type': method, **args})
            url = f"{self.AUR_RPC_URL}?{params}"
            
            with urllib.request.urlopen(url, timeout=15) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"AUR RPC error: {e}")
            return None
            
    def get_installed(self) -> List[AppInfo]:
        """Get list of installed AUR packages"""
        apps = []
        
        # Get foreign packages (usually AUR)
        try:
            result = subprocess.run(
                ['pacman', '-Qm'],
                capture_output=True, text=True, timeout=30
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
                                summary='AUR package',
                                version=version,
                                source='aur',
                                installed=True,
                                icon_name=icon_name,
                                categories=['installed']
                            ))
        except Exception as e:
            print(f"AUR get_installed error: {e}")
            
        return apps
        
    def get_apps(self) -> List[AppInfo]:
        """Get all available AUR packages"""
        all_apps = self.get_installed()
        installed_ids = {app.id for app in all_apps}
        
        # Search AUR for popular terms
        search_terms = ['browser', 'editor', 'media', 'game', 'tools', 'theme', 'font', 
                       'vpn', 'download', 'music', 'video', 'chat', 'office']
        
        for term in search_terms:
            try:
                result = self._aur_rpc_call('search', {'arg': term})
                
                if result and result.get('results'):
                    for pkg in result['results'][:15]:  # Limit per search
                        pkg_name = pkg.get('Name', '')
                        
                        if pkg_name and pkg_name not in installed_ids:
                            name = pkg_name.replace('-', ' ').title()
                            
                            # Get icon
                            icon_name = self._get_icon(pkg_name, name)
                            
                            all_apps.append(AppInfo(
                                id=pkg_name,
                                name=name,
                                summary=pkg.get('Description', 'AUR package')[:150],
                                description=pkg.get('Description', ''),
                                version=pkg.get('Version', ''),
                                source='aur',
                                installed=False,
                                icon_name=icon_name,
                                downloads=pkg.get('NumVotes', 0),
                                rating=min(5.0, (pkg.get('Popularity', 0) / 10)) if pkg.get('Popularity') else None,
                                categories=['available']
                            ))
                            installed_ids.add(pkg_name)
                            
            except Exception as e:
                print(f"AUR search error for {term}: {e}")
                continue
                    
        return all_apps
        
    def install(self, pkg_name: str) -> Tuple[bool, str]:
        """Install an AUR package"""
        if not self._helper:
            return False, "No AUR helper available"
            
        try:
            if self._helper == 'pamac':
                result = subprocess.run(
                    ['pamac', 'build', '--no-confirm', pkg_name],
                    capture_output=True, text=True, timeout=600
                )
            elif self._helper in ['paru', 'yay']:
                result = subprocess.run(
                    [self._helper, '-S', '--noconfirm', pkg_name],
                    capture_output=True, text=True, timeout=600
                )
            else:
                return False, "AUR helper doesn't support direct install"
                
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
            
    def uninstall(self, pkg_name: str) -> Tuple[bool, str]:
        """Uninstall an AUR package"""
        try:
            result = subprocess.run(
                ['sudo', 'pacman', '-Rns', '--noconfirm', pkg_name],
                capture_output=True, text=True, timeout=120
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
            
    def update(self, pkg_name: str = None) -> Tuple[bool, str]:
        """Update AUR packages"""
        if not self._helper:
            return False, "No AUR helper available"
            
        try:
            if pkg_name:
                result = subprocess.run(
                    [self._helper, '-S', '--noconfirm', pkg_name],
                    capture_output=True, text=True, timeout=600
                )
            else:
                if self._helper == 'pamac':
                    result = subprocess.run(
                        ['pamac', 'update', '--aur', '--no-confirm'],
                        capture_output=True, text=True, timeout=900
                    )
                else:
                    result = subprocess.run(
                        [self._helper, '-Sua', '--noconfirm'],
                        capture_output=True, text=True, timeout=900
                    )
                    
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
