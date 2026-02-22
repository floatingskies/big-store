"""
Big Store - Featured Banner Widget
Banner for featured/promoted applications
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk, GLib, Pango
from typing import List, Optional


class FeaturedBanner(Gtk.Box):
    """Featured apps carousel banner"""
    
    __gtype_name__ = 'FeaturedBanner'
    
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        
        self._build_ui()
        
    def _build_ui(self):
        """Build banner UI"""
        # Create a simple box with the featured app
        banner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        banner_box.add_css_class('featured-banner')
        
        # Apply gradient background via CSS
        css_provider = Gtk.CssProvider()
        css = """
        .featured-banner {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 24px;
            color: white;
        }
        """
        css_provider.load_from_data(css.encode('utf-8'))
        Gtk.StyleContext.add_provider(
            banner_box.get_style_context(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Left content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content_box.set_hexpand(True)
        content_box.set_valign(Gtk.Align.CENTER)
        content_box.set_margin_start(24)
        
        subtitle = Gtk.Label(label='Sua nova loja de aplicativos')
        subtitle.add_css_class('caption-heading')
        content_box.append(subtitle)
        
        title = Gtk.Label(label='Big Store')
        title.add_css_class('title-1')
        title.set_halign(Gtk.Align.START)
        content_box.append(title)
        
        desc = Gtk.Label(label='Instale apps de múltiplas fontes: Flatpak, Snap, AUR e mais!')
        desc.set_halign(Gtk.Align.START)
        content_box.append(desc)
        
        button = Gtk.Button(label='Explorar')
        button.add_css_class('pill')
        button.add_css_class('suggested-action')
        button.set_margin_top(8)
        button.set_halign(Gtk.Align.START)
        content_box.append(button)
        
        banner_box.append(content_box)
        
        # Right icon
        icon = Gtk.Image.new_from_icon_name('system-software-install-symbolic')
        icon.set_pixel_size(96)
        icon.set_margin_end(48)
        icon.set_valign(Gtk.Align.CENTER)
        banner_box.append(icon)
        
        self.append(banner_box)


class FeaturedCard(Gtk.Box):
    """Single featured app card"""
    
    __gtype_name__ = 'FeaturedCard'
    
    def __init__(self, app_data: dict, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        
        self.add_css_class('card')
        self.add_css_class('app-card')
        
        self.set_size_request(280, 180)
        self.set_margin_start(6)
        self.set_margin_end(6)
        
        self._build_ui(app_data)
        
    def _build_ui(self, app_data: dict):
        """Build card UI"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_hexpand(True)
        
        cat_label = Gtk.Label(label=app_data.get('category', 'Destaque'))
        cat_label.add_css_class('caption-heading')
        cat_label.add_css_class('dim-label')
        cat_label.set_halign(Gtk.Align.START)
        content.append(cat_label)
        
        name_label = Gtk.Label(label=app_data.get('name', 'App'))
        name_label.add_css_class('title-4')
        name_label.set_halign(Gtk.Align.START)
        content.append(name_label)
        
        desc_label = Gtk.Label(label=app_data.get('description', ''))
        desc_label.add_css_class('caption')
        desc_label.add_css_class('dim-label')
        desc_label.set_halign(Gtk.Align.START)
        desc_label.set_lines(2)
        desc_label.set_ellipsize(Pango.EllipsizeMode.END)
        content.append(desc_label)
        
        main_box.append(content)
        
        if app_data.get('icon'):
            icon = Gtk.Image.new_from_icon_name(app_data['icon'])
            icon.set_pixel_size(48)
            icon.set_margin_end(12)
            main_box.append(icon)
            
        self.append(main_box)
