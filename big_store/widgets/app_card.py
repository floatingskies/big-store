"""
Big Store - App Card Widget
Card widget for displaying app information
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk, GLib, Pango
from typing import Optional

from big_store.managers.package_manager import AppInfo


class AppCard(Gtk.Box):
    """App card widget showing app info"""
    
    __gtype_name__ = 'AppCard'
    
    def __init__(self, app_info: AppInfo, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        
        self.app_info = app_info
        
        self.set_size_request(200, 220)
        self.add_css_class('app-card')
        self.add_css_class('card')
        
        self._build_ui()
        
    def _build_ui(self):
        """Build card UI"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        main_box.set_margin_top(8)
        main_box.set_margin_bottom(8)
        main_box.set_margin_start(8)
        main_box.set_margin_end(8)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        
        # Top row: Icon + Badge
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        top_row.set_halign(Gtk.Align.CENTER)
        
        # App Icon
        icon = Gtk.Image()
        icon.set_pixel_size(64)
        icon.add_css_class('app-icon')
        
        # Try to load app icon or use fallback
        icon_name = self.app_info.icon_name or 'application-x-executable-symbolic'
        icon.set_from_icon_name(icon_name)
        
        top_row.append(icon)
        main_box.append(top_row)
        
        # Source Badge
        badge = self._create_source_badge()
        badge.set_halign(Gtk.Align.CENTER)
        main_box.append(badge)
        
        # App Name
        name_label = Gtk.Label(label=self.app_info.name)
        name_label.add_css_class('title-4')
        name_label.set_ellipsize(Pango.EllipsizeMode.END)
        name_label.set_max_width_chars(20)
        name_label.set_halign(Gtk.Align.CENTER)
        main_box.append(name_label)
        
        # Summary
        summary_label = Gtk.Label(label=self.app_info.summary)
        summary_label.add_css_class('caption')
        summary_label.add_css_class('dim-label')
        summary_label.set_ellipsize(Pango.EllipsizeMode.END)
        summary_label.set_max_width_chars(25)
        summary_label.set_halign(Gtk.Align.CENTER)
        summary_label.set_lines(2)
        main_box.append(summary_label)
        
        # Spacer
        main_box.append(Gtk.Box())
        
        # Bottom row: Rating + Button
        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        bottom_row.set_halign(Gtk.Align.CENTER)
        
        # Rating
        if self.app_info.rating:
            rating_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            star_icon = Gtk.Image.new_from_icon_name('star-filled-symbolic')
            star_icon.set_pixel_size(12)
            star_icon.add_css_class('warning')
            rating_box.append(star_icon)
            
            rating_label = Gtk.Label(label=f'{self.app_info.rating:.1f}')
            rating_label.add_css_class('caption')
            rating_box.append(rating_label)
            
            bottom_row.append(rating_box)
            
        # Install Button
        self.button = self._create_action_button()
        bottom_row.append(self.button)
        
        main_box.append(bottom_row)
        
        self.append(main_box)
        
    def _create_source_badge(self) -> Gtk.Label:
        """Create source badge label"""
        source_colors = {
            'flatpak': ('flatpak', 'Flatpak'),
            'snap': ('snap', 'Snap'),
            'aur': ('aur', 'AUR'),
            'native': ('native', 'Nativo'),
            'distrobox': ('distrobox', 'Distrobox')
        }
        
        source = self.app_info.source or 'native'
        css_class, text = source_colors.get(source, ('native', 'Nativo'))
        
        badge = Gtk.Label(label=text)
        badge.add_css_class(f'badge-{css_class}')
        badge.add_css_class('caption-heading')
        
        return badge
        
    def _create_action_button(self) -> Gtk.Button:
        """Create action button"""
        if self.app_info.installed:
            button = Gtk.Button()
            button.set_icon_name('object-select-symbolic')
            button.add_css_class('success')
            button.set_tooltip_text('Instalado')
            button.set_sensitive(False)
        else:
            button = Gtk.Button(label='Instalar')
            button.add_css_class('pill')
            button.add_css_class('suggested-action')
            button.set_tooltip_text('Instalar aplicativo')
            button.connect('clicked', self._on_install_clicked)
            
        return button
        
    def _on_install_clicked(self, button):
        """Handle install button clicked"""
        button.set_label('Instalando...')
        button.set_sensitive(False)
        button.add_css_class('installing')
        
        # TODO: Implement actual installation
        GLib.timeout_add(2000, self._on_install_complete, button)
        
    def _on_install_complete(self, button):
        """Handle install complete"""
        button.set_label('Instalado')
        button.remove_css_class('installing')
        button.add_css_class('success')
        return False


class AppCardCompact(Gtk.Box):
    """Compact app card for list view"""
    
    __gtype_name__ = 'AppCardCompact'
    
    def __init__(self, app_info: AppInfo, **kwargs):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, **kwargs)
        
        self.app_info = app_info
        self.set_spacing(12)
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        
        self._build_ui()
        
    def _build_ui(self):
        """Build compact card UI"""
        # Icon
        icon = Gtk.Image()
        icon.set_pixel_size(48)
        icon.set_from_icon_name(self.app_info.icon_name or 'application-x-executive-symbolic')
        self.append(icon)
        
        # Info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info_box.set_hexpand(True)
        
        # Title row
        title_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        name_label = Gtk.Label(label=self.app_info.name)
        name_label.add_css_class('heading')
        title_row.append(name_label)
        
        # Source badge
        badge = self._create_source_badge()
        title_row.append(badge)
        
        info_box.append(title_row)
        
        # Summary
        summary_label = Gtk.Label(label=self.app_info.summary)
        summary_label.add_css_class('dim-label')
        summary_label.add_css_class('caption')
        summary_label.set_ellipsize(Pango.EllipsizeMode.END)
        info_box.append(summary_label)
        
        self.append(info_box)
        
        # Action button
        if self.app_info.installed:
            btn = Gtk.Button(label='Instalado')
            btn.add_css_class('success')
            btn.set_sensitive(False)
        else:
            btn = Gtk.Button(label='Instalar')
            btn.add_css_class('suggested-action')
            
        self.append(btn)
        
    def _create_source_badge(self) -> Gtk.Label:
        """Create source badge"""
        source = self.app_info.source or 'native'
        badge = Gtk.Label(label=source.upper())
        badge.add_css_class(f'badge-{source}')
        badge.add_css_class('caption-heading')
        return badge
