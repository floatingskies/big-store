#!/usr/bin/env python3
"""
Big Store - Entry Point
Loja de Aplicativos Linux moderna e completa

Execute este arquivo para iniciar a aplicação.
"""

import sys
import os

# Garantir que o diretório do pacote está no path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Gio, Adw, Gdk

from big_store.window import BigStoreWindow
from big_store.managers.package_manager import PackageManager


class BigStoreApplication(Adw.Application):
    """Main Application Class"""
    
    __gtype_name__ = 'BigStoreApplication'
    
    def __init__(self):
        super().__init__(
            application_id='com.biglinux.bigstore',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        
        self.package_manager = None
        self.window = None
        
    def do_startup(self):
        """Initialize application on startup"""
        Adw.Application.do_startup(self)
        
        # Initialize package manager
        try:
            self.package_manager = PackageManager()
        except Exception as e:
            print(f"Warning: Could not initialize package manager: {e}")
        
        # Setup actions
        self._setup_actions()
        
        # Setup keyboard shortcuts
        self._setup_accels()
        
        # Load custom CSS
        self._load_css()
        
    def do_activate(self):
        """Show the main window"""
        if not self.window:
            self.window = BigStoreWindow(application=self)
        self.window.present()
        
    def _setup_actions(self):
        """Setup application actions"""
        # Search action
        search_action = Gio.SimpleAction.new('search', None)
        search_action.connect('activate', self._on_search)
        self.add_action(search_action)
        
        # Refresh action
        refresh_action = Gio.SimpleAction.new('refresh', None)
        refresh_action.connect('activate', self._on_refresh)
        self.add_action(refresh_action)
        
        # Preferences action
        prefs_action = Gio.SimpleAction.new('preferences', None)
        prefs_action.connect('activate', self._on_preferences)
        self.add_action(prefs_action)
        
        # About action
        about_action = Gio.SimpleAction.new('about', None)
        about_action.connect('activate', self._on_about)
        self.add_action(about_action)
        
        # Quit action
        quit_action = Gio.SimpleAction.new('quit', None)
        quit_action.connect('activate', self._on_quit)
        self.add_action(quit_action)
        
    def _setup_accels(self):
        """Setup keyboard shortcuts"""
        self.set_accels_for_action('app.search', ['<Control>f'])
        self.set_accels_for_action('app.refresh', ['<Control>r', 'F5'])
        self.set_accels_for_action('app.preferences', ['<Control>comma'])
        self.set_accels_for_action('app.quit', ['<Control>q'])
        
    def _load_css(self):
        """Load custom CSS styling"""
        provider = Gtk.CssProvider()
        
        css_content = self._get_css()
        
        try:
            provider.load_from_data(css_content.encode('utf-8'))
            display = Gdk.Display.get_default()
            if display:
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
        except Exception as e:
            print(f"Error loading CSS: {e}")
            
    def _get_css(self):
        """Return CSS styling"""
        return """
        /* Big Store Custom CSS - GNOME Software Style */
        
        /* Main Window */
        .bigstore-window {
            background-color: @background_color;
        }
        
        /* Header Bar */
        .title-header {
            font-weight: bold;
            font-size: 1.2em;
        }
        
        /* App Cards */
        .app-card {
            background-color: @card_bg_color;
            border-radius: 12px;
            padding: 12px;
            margin: 6px;
            transition: all 0.2s ease;
        }
        
        .app-card:hover {
            background-color: @hover_bg_color;
        }
        
        /* App Icon */
        .app-icon {
            border-radius: 12px;
        }
        
        .app-icon-large {
            border-radius: 16px;
        }
        
        /* Category Pills */
        .category-pill {
            background-color: @accent_bg_color;
            border-radius: 20px;
            padding: 8px 16px;
            font-weight: 500;
        }
        
        .category-pill:hover {
            background-color: @accent_color;
            color: white;
        }
        
        /* Source Badges */
        .badge-flatpak {
            background-color: #4A90D9;
            color: white;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 0.75em;
            font-weight: bold;
        }
        
        .badge-snap {
            background-color: #82BEA0;
            color: white;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 0.75em;
            font-weight: bold;
        }
        
        .badge-aur {
            background-color: #1793D1;
            color: white;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 0.75em;
            font-weight: bold;
        }
        
        .badge-native {
            background-color: #FF6B6B;
            color: white;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 0.75em;
            font-weight: bold;
        }
        
        .badge-distrobox {
            background-color: #9B59B6;
            color: white;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 0.75em;
            font-weight: bold;
        }
        
        /* Install Button */
        .install-button {
            background-color: @accent_bg_color;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        
        .install-button:hover {
            background-color: @accent_color;
        }
        
        /* Search Entry */
        .search-entry {
            border-radius: 24px;
            padding: 8px 16px;
        }
        
        /* Sidebar */
        .sidebar-item {
            padding: 12px 16px;
            border-radius: 8px;
        }
        
        .sidebar-item:hover {
            background-color: @hover_bg_color;
        }
        
        .sidebar-item.active {
            background-color: @accent_bg_color;
        }
        
        /* Featured Banner */
        .featured-banner {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 24px;
            color: white;
        }
        
        /* Scrollbar */
        scrollbar slider {
            background-color: alpha(@foreground_color, 0.3);
            border-radius: 4px;
            min-width: 8px;
            min-height: 8px;
        }
        
        scrollbar slider:hover {
            background-color: alpha(@foreground_color, 0.5);
        }
        """
        
    def _on_search(self, action, param):
        """Handle search action"""
        if self.window:
            self.window.focus_search()
            
    def _on_refresh(self, action, param):
        """Handle refresh action"""
        if self.package_manager:
            self.package_manager.refresh_cache()
        if self.window:
            self.window.refresh_content()
            
    def _on_preferences(self, action, param):
        """Handle preferences action"""
        if self.window:
            self.window.show_preferences()
            
    def _on_about(self, action, param):
        """Handle about action"""
        about = Adw.AboutWindow(
            transient_for=self.window,
            application_name='Big Store',
            application_icon='system-software-install-symbolic',
            version='1.0.0',
            comments='Loja de Aplicativos Linux moderna e completa\n'
                     'Suporta Flatpak, Snap, AUR e pacotes nativos',
            website='https://biglinux.com.br',
            issue_url='https://github.com/biglinux/bigstore/issues',
            developers=['BigLinux Team'],
            artists=['BigLinux Team'],
            license_type=Gtk.License.GPL_3_0,
            copyright='© 2024 BigLinux Team'
        )
        about.present()
        
    def _on_quit(self, action, param):
        """Handle quit action"""
        self.quit()


def main():
    """Main entry point"""
    app = BigStoreApplication()
    return app.run(sys.argv)


if __name__ == '__main__':
    main()
