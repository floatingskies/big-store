"""
Big Store - Icon Manager
Fetch and manage application icons from various sources
"""

import os
import subprocess
import urllib.request
import urllib.parse
import json
import threading
from typing import Optional, Tuple
from dataclasses import dataclass
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

# Icon cache directory
ICON_CACHE_DIR = os.path.expanduser('~/.cache/big-store/icons')
FLATHUB_ICON_URL = "https://dl.flathub.org/repo/appstream/x86_64/icons/128x128/{app_id}.png"
SNAP_STORE_API = "https://snapstore-api.canonical.com/api/v1/snaps/{snap_name}"
SNAP_ICON_URL = "https://dashboard.snapcraft.io/site_media/appmedia/{icon_name}"


@dataclass
class IconData:
    """Icon information"""
    name: str
    path: Optional[str] = None
    url: Optional[str] = None
    source: str = 'system'


class IconManager:
    """Manage application icons from multiple sources"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._cache = {}
        self._icon_theme = None
        self._fallback_icon = 'application-x-executable-symbolic'
        
        # Create cache directory
        os.makedirs(ICON_CACHE_DIR, exist_ok=True)
        
        # Load icon theme
        try:
            display = Gdk.Display.get_default()
            if display:
                self._icon_theme = Gtk.IconTheme.get_for_display(display)
        except Exception:
            pass
            
    def get_icon_name(self, app_id: str, app_name: str, source: str) -> str:
        """
        Get the best icon name for an application.
        
        Args:
            app_id: Application ID (e.g., org.mozilla.Firefox)
            app_name: Application name (e.g., Firefox)
            source: Package source (flatpak, snap, aur, native, distrobox)
            
        Returns:
            Icon name or path
        """
        # Check cache first
        cache_key = f"{app_id}:{source}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        icon_name = None
        
        if source == 'flatpak':
            icon_name = self._get_flatpak_icon(app_id, app_name)
        elif source == 'snap':
            icon_name = self._get_snap_icon(app_id, app_name)
        elif source in ('aur', 'native'):
            icon_name = self._get_native_icon(app_id, app_name)
        elif source == 'distrobox':
            icon_name = self._get_distrobox_icon(app_id, app_name)
        else:
            icon_name = self._get_native_icon(app_id, app_name)
            
        # Fallback to generic icon
        if not icon_name:
            icon_name = self._get_fallback_icon(app_name)
            
        # Cache result
        self._cache[cache_key] = icon_name
        return icon_name
        
    def _get_flatpak_icon(self, app_id: str, app_name: str) -> Optional[str]:
        """Get icon for Flatpak application"""
        # Try system theme first with Flatpak ID
        icon_names = [
            app_id,
            app_id.lower(),
            app_id.replace('org.', '').replace('com.', '').replace('io.github.', ''),
            app_name.lower(),
            self._extract_app_name(app_id),
        ]
        
        # Check system theme
        for name in icon_names:
            if self._icon_theme and self._icon_theme.has_icon(name):
                return name
                
        # Check for cached icon
        cached_path = os.path.join(ICON_CACHE_DIR, f"{app_id}.png")
        if os.path.exists(cached_path):
            return cached_path
            
        # Download from Flathub
        self._download_flatpak_icon_async(app_id)
        
        # Return app name as fallback while downloading
        return icon_names[-1] if icon_names else None
        
    def _get_snap_icon(self, app_id: str, app_name: str) -> Optional[str]:
        """Get icon for Snap package"""
        # Common snap icon names
        icon_names = [
            app_id,
            f"snap.{app_id}",
            app_name.lower(),
            app_id.replace('-', ''),
        ]
        
        # Check system theme
        for name in icon_names:
            if self._icon_theme and self._icon_theme.has_icon(name):
                return name
                
        # Check cached icon
        cached_path = os.path.join(ICON_CACHE_DIR, f"snap-{app_id}.png")
        if os.path.exists(cached_path):
            return cached_path
            
        # Download from Snap Store
        self._download_snap_icon_async(app_id)
        
        return icon_names[-1] if icon_names else None
        
    def _get_native_icon(self, app_id: str, app_name: str) -> Optional[str]:
        """Get icon for native/AUR package"""
        # Generate possible icon names
        icon_names = [
            app_id,
            app_id.lower(),
            app_id.replace('-', '').replace('_', ''),
            app_name.lower(),
            app_name.lower().replace(' ', '-'),
            app_name.lower().replace(' ', ''),
            # Common variations
            f"{app_id.lower()}-icon",
            f"{app_name.lower()}-icon",
        ]
        
        # Special icon name mappings
        special_mappings = {
            'google-chrome': ['google-chrome', 'chrome', 'google-chrome-stable'],
            'visual-studio-code': ['code', 'vscode', 'visual-studio-code', 'code-oss'],
            'mozilla-firefox': ['firefox', 'org.mozilla.firefox'],
            'firefox-esr': ['firefox', 'firefox-esr'],
            'libreoffice-fresh': ['libreoffice-main', 'libreoffice'],
            'libreoffice-still': ['libreoffice-main', 'libreoffice'],
            'gimp': ['gimp', 'gimp-2.10'],
            'vlc': ['vlc', 'vlc-client'],
            'obs-studio': ['obs', 'obs-studio', 'com.obsproject.Studio'],
            'blender': ['blender', 'blender-3d'],
            'discord': ['discord', 'com.discordapp.Discord', 'discord-canary'],
            'spotify': ['spotify', 'com.spotify.Client'],
            'steam': ['steam', 'com.valvesoftware.Steam', 'steam-native'],
            'telegram-desktop': ['telegram', 'telegram-desktop', 'org.telegram.desktop'],
            'zoom': ['zoom', 'zoom-client', 'us.zoom.Zoom'],
            'anydesk': ['anydesk', 'com.anydesk.Anydesk'],
            'teamviewer': ['teamviewer', 'com.teamviewer.TeamViewer'],
            'brave': ['brave', 'brave-browser', 'com.brave.Browser'],
            'microsoft-edge': ['microsoft-edge', 'edge', 'microsoft-edge-stable'],
            'skype': ['skype', 'skypeforlinux', 'com.skype.Client'],
            'slack': ['slack', 'slack-desktop', 'com.slack.Slack'],
            'postman': ['postman', 'postman-agent'],
            'notion': ['notion', 'notion-app'],
            'inkscape': ['inkscape', 'org.inkscape.Inkscape'],
            'kdenlive': ['kdenlive', 'org.kde.kdenlive'],
            'audacity': ['audacity', 'org.audacityteam.Audacity'],
        }
        
        # Check special mappings
        for key, icons in special_mappings.items():
            if key in app_id.lower() or key in app_name.lower():
                icon_names = icons + icon_names
                break
                
        # Check system theme
        for name in icon_names:
            if self._icon_theme and self._icon_theme.has_icon(name):
                return name
                
        # Check common icon directories
        icon_dirs = [
            '/usr/share/icons/hicolor/128x128/apps',
            '/usr/share/icons/hicolor/64x64/apps',
            '/usr/share/icons/hicolor/48x48/apps',
            '/usr/share/icons/hicolor/scalable/apps',
            '/usr/share/pixmaps',
            '/usr/share/icons',
            os.path.expanduser('~/.local/share/icons'),
        ]
        
        for icon_dir in icon_dirs:
            if os.path.exists(icon_dir):
                for name in icon_names:
                    for ext in ['.png', '.svg', '.xpm']:
                        icon_path = os.path.join(icon_dir, name + ext)
                        if os.path.exists(icon_path):
                            return icon_path
                            
        # Check Papirus specifically
        papirus_dirs = [
            '/usr/share/icons/Papirus/128x128/apps',
            '/usr/share/icons/Papirus/64x64/apps',
            '/usr/share/icons/Papirus/48x48/apps',
            '/usr/share/icons/Papirus/scalable/apps',
            '/usr/share/icons/Papirus-Dark/128x128/apps',
            '/usr/share/icons/Papirus-Light/128x128/apps',
        ]
        
        for icon_dir in papirus_dirs:
            if os.path.exists(icon_dir):
                for name in icon_names:
                    for ext in ['.png', '.svg']:
                        icon_path = os.path.join(icon_dir, name + ext)
                        if os.path.exists(icon_path):
                            return icon_path
                            
        return icon_names[-1] if icon_names else None
        
    def _get_distrobox_icon(self, app_id: str, app_name: str) -> Optional[str]:
        """Get icon for Distrobox application"""
        # Use system icons with distrobox prefix
        icon_names = [
            app_id,
            f"distrobox-{app_name}",
            app_name.lower(),
        ]
        
        for name in icon_names:
            if self._icon_theme and self._icon_theme.has_icon(name):
                return name
                
        # Fallback to generic box icon
        return 'box-symbolic'
        
    def _get_fallback_icon(self, app_name: str) -> str:
        """Get fallback icon based on app category"""
        categories = {
            'browser': ['web-browser', 'firefox', 'chrome', 'chromium', 'opera', 'brave', 'edge'],
            'editor': ['text-editor', 'code', 'editor', 'gedit', 'vim', 'emacs', 'sublime', 'atom'],
            'media': ['media-player', 'vlc', 'mpv', 'video', 'music', 'audio', 'rhythmbox'],
            'game': ['applications-games', 'steam', 'lutris', 'heroic', 'minecraft'],
            'office': ['applications-office', 'libreoffice', 'office', 'word', 'excel'],
            'graphics': ['applications-graphics', 'gimp', 'inkscape', 'blender', 'photoshop'],
            'development': ['applications-development', 'code', 'jetbrains', 'eclipse'],
            'terminal': ['utilities-terminal', 'terminal', 'konsole', 'gnome-terminal'],
            'files': ['system-file-manager', 'files', 'nautilus', 'dolphin', 'thunar'],
            'settings': ['preferences-system', 'settings', 'configuration'],
            'chat': ['im-message', 'discord', 'telegram', 'slack', 'skype'],
            'mail': ['mail', 'thunderbird', 'evolution', 'outlook'],
            'download': ['download', 'transmission', 'qbittorrent'],
        }
        
        app_lower = app_name.lower()
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in app_lower:
                    return keywords[0] if keywords[0] != keyword else keywords[0]
                    
        return 'application-x-executable-symbolic'
        
    def _extract_app_name(self, app_id: str) -> str:
        """Extract app name from Flatpak ID"""
        parts = app_id.split('.')
        if len(parts) > 1:
            return parts[-1].lower()
        return app_id.lower()
        
    def _download_flatpak_icon_async(self, app_id: str):
        """Download Flatpak icon asynchronously"""
        def download():
            try:
                url = f"https://dl.flathub.org/repo/appstream/x86_64/icons/128x128/{app_id}.png"
                cached_path = os.path.join(ICON_CACHE_DIR, f"{app_id}.png")
                
                if not os.path.exists(cached_path):
                    urllib.request.urlretrieve(url, cached_path)
            except Exception:
                pass
                
        thread = threading.Thread(target=download, daemon=True)
        thread.start()
        
    def _download_snap_icon_async(self, snap_name: str):
        """Download Snap icon asynchronously"""
        def download():
            try:
                # Get snap info from store
                url = f"https://api.snapcraft.io/v2/snaps/info/{snap_name}"
                headers = {'Snap-Device-Series': '16'}
                
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    
                # Find icon URL
                if 'channel-map' in data:
                    for channel in data['channel-map']:
                        if 'icon' in channel.get('download', {}):
                            icon_url = channel['download']['icon']
                            cached_path = os.path.join(ICON_CACHE_DIR, f"snap-{snap_name}.png")
                            
                            urllib.request.urlretrieve(icon_url, cached_path)
                            break
            except Exception:
                # Fallback: try direct URL
                try:
                    url = f"https://dashboard.snapcraft.io/site_media/appmedia/{snap_name}.png"
                    cached_path = os.path.join(ICON_CACHE_DIR, f"snap-{snap_name}.png")
                    urllib.request.urlretrieve(url, cached_path)
                except Exception:
                    pass
                    
        thread = threading.Thread(target=download, daemon=True)
        thread.start()
        
    def clear_cache(self):
        """Clear icon cache"""
        import shutil
        if os.path.exists(ICON_CACHE_DIR):
            shutil.rmtree(ICON_CACHE_DIR)
            os.makedirs(ICON_CACHE_DIR, exist_ok=True)


# Global instance
icon_manager = IconManager()
