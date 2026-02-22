"""
Big Store - App Detail View Widget
Detailed view for a single application
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk, GLib, Pango, GObject
from typing import Optional, List
import threading

from big_store.models import AppInfo


class AppDetailView(Adw.Bin):
    """Detailed view for an application"""
    
    __gtype_name__ = 'AppDetailView'
    
    __gsignals__ = {
        'back-clicked': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._app: Optional[AppInfo] = None
        
        self._build_ui()
        
    def _build_ui(self):
        """Build detail view UI"""
        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Header
        self._build_header()
        
        # Content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.content_box.set_margin_top(24)
        self.content_box.set_margin_bottom(24)
        self.content_box.set_margin_start(24)
        self.content_box.set_margin_end(24)
        
        scrolled.set_child(self.content_box)
        self.main_box.append(scrolled)
        
        self.set_child(self.main_box)
        
    def _build_header(self):
        """Build header bar"""
        self.header_bar = Adw.HeaderBar()
        self.header_bar.add_css_class('flat')
        
        # Back button
        back_button = Gtk.Button()
        back_button.set_icon_name('go-previous-symbolic')
        back_button.set_tooltip_text('Voltar')
        back_button.connect('clicked', self._on_back_clicked)
        self.header_bar.pack_start(back_button)
        
        self.main_box.append(self.header_bar)
        
    def set_app(self, app: AppInfo):
        """Set the app to display"""
        self._app = app
        self._update_content()
        
    def _update_content(self):
        """Update content with app info"""
        # Clear existing
        while child := self.content_box.get_first_child():
            self.content_box.remove(child)
            
        if not self._app:
            return
            
        app = self._app
        
        # Title section
        title_section = self._create_title_section(app)
        self.content_box.append(title_section)
        
        # Action buttons
        action_section = self._create_action_section(app)
        self.content_box.append(action_section)
        
        # Screenshots (placeholder)
        screenshots_section = self._create_screenshots_section(app)
        self.content_box.append(screenshots_section)
        
        # Description
        desc_section = self._create_description_section(app)
        self.content_box.append(desc_section)
        
        # Details
        details_section = self._create_details_section(app)
        self.content_box.append(details_section)
        
        # Reviews (placeholder)
        reviews_section = self._create_reviews_section(app)
        self.content_box.append(reviews_section)
        
    def _create_title_section(self, app: AppInfo) -> Gtk.Box:
        """Create title section with icon and basic info"""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        
        # Icon
        icon = Gtk.Image()
        icon.set_pixel_size(128)
        icon.add_css_class('app-icon-large')
        icon.add_css_class('card')
        icon.set_from_icon_name(app.icon_name or 'application-x-executive-symbolic')
        box.append(icon)
        
        # Info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_hexpand(True)
        info_box.set_valign(Gtk.Align.CENTER)
        
        # Title
        title = Gtk.Label(label=app.name)
        title.add_css_class('title-1')
        title.set_halign(Gtk.Align.START)
        info_box.append(title)
        
        # Developer
        if app.developer:
            dev_label = Gtk.Label(label=f'por {app.developer}')
            dev_label.add_css_class('dim-label')
            dev_label.set_halign(Gtk.Align.START)
            info_box.append(dev_label)
            
        # Rating row
        if app.rating:
            rating_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            rating_box.set_halign(Gtk.Align.START)
            
            for i in range(5):
                star = Gtk.Image()
                if i < int(app.rating):
                    star.set_from_icon_name('star-filled-symbolic')
                    star.add_css_class('warning')
                else:
                    star.set_from_icon_name('star-outline-symbolic')
                    star.add_css_class('dim-label')
                star.set_pixel_size(16)
                rating_box.append(star)
                
            rating_text = Gtk.Label(label=f' {app.rating:.1f}')
            rating_box.append(rating_text)
            
            info_box.append(rating_box)
            
        # Source badge
        badge = self._create_source_badge(app.source)
        badge.set_halign(Gtk.Align.START)
        info_box.append(badge)
        
        box.append(info_box)
        
        return box
        
    def _create_source_badge(self, source: str) -> Gtk.Label:
        """Create source badge"""
        source_labels = {
            'flatpak': 'Flatpak',
            'snap': 'Snap',
            'aur': 'AUR',
            'native': 'Nativo',
            'distrobox': 'Distrobox'
        }
        
        label = Gtk.Label(label=source_labels.get(source, source))
        label.add_css_class(f'badge-{source}')
        label.add_css_class('heading')
        return label
        
    def _create_action_section(self, app: AppInfo) -> Gtk.Box:
        """Create action buttons section"""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_halign(Gtk.Align.START)
        
        # Install/Remove button
        if app.installed:
            self.main_button = Gtk.Button(label='Remover')
            self.main_button.add_css_class('destructive-action')
            self.main_button.add_css_class('pill')
            self.main_button.connect('clicked', self._on_remove_clicked)
        else:
            self.main_button = Gtk.Button(label='Instalar')
            self.main_button.add_css_class('suggested-action')
            self.main_button.add_css_class('pill')
            self.main_button.connect('clicked', self._on_install_clicked)
            
        box.append(self.main_button)
        
        # Launch button (if installed)
        if app.installed:
            launch_button = Gtk.Button()
            launch_button.set_icon_name('media-playback-start-symbolic')
            launch_button.set_tooltip_text('Executar')
            launch_button.add_css_class('pill')
            launch_button.connect('clicked', self._on_launch_clicked)
            box.append(launch_button)
            
        # Size info
        if app.size:
            size_label = Gtk.Label(label=f'Tamanho: {app.size}')
            size_label.add_css_class('dim-label')
            size_label.set_margin_start(12)
            size_label.set_valign(Gtk.Align.CENTER)
            box.append(size_label)
            
        return box
        
    def _create_screenshots_section(self, app: AppInfo) -> Gtk.Box:
        """Create screenshots section"""
        section = Adw.PreferencesGroup()
        section.set_title('Capturas de Tela')
        
        # Horizontal scrolling container
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scroll.set_margin_top(12)
        
        screenshots_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        # Placeholder screenshots
        for i in range(3):
            placeholder = Gtk.Box()
            placeholder.set_size_request(300, 180)
            placeholder.add_css_class('card')
            
            icon = Gtk.Image.new_from_icon_name('image-missing-symbolic')
            icon.set_pixel_size(48)
            icon.set_hexpand(True)
            icon.set_vexpand(True)
            icon.set_valign(Gtk.Align.CENTER)
            icon.set_halign(Gtk.Align.CENTER)
            placeholder.append(icon)
            
            screenshots_box.append(placeholder)
            
        scroll.set_child(screenshots_box)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(Gtk.Label(label='Capturas de Tela'))
        box.append(scroll)
        
        return box
        
    def _create_description_section(self, app: AppInfo) -> Gtk.Box:
        """Create description section"""
        section = Adw.PreferencesGroup()
        section.set_title('Descrição')
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Summary
        summary = Gtk.Label(label=app.summary)
        summary.add_css_class('title-4')
        summary.set_halign(Gtk.Align.START)
        summary.set_wrap(True)
        box.append(summary)
        
        # Full description
        description = Gtk.Label(label=app.description or app.summary)
        description.set_halign(Gtk.Align.START)
        description.set_wrap(True)
        description.set_margin_top(8)
        box.append(description)
        
        return box
        
    def _create_details_section(self, app: AppInfo) -> Adw.PreferencesGroup:
        """Create details section"""
        group = Adw.PreferencesGroup()
        group.set_title('Detalhes')
        
        # Version
        if app.version:
            row = Adw.ActionRow(title='Versão')
            row.add_suffix(Gtk.Label(label=app.version))
            group.add(row)
            
        # Developer
        if app.developer:
            row = Adw.ActionRow(title='Desenvolvedor')
            row.add_suffix(Gtk.Label(label=app.developer))
            group.add(row)
            
        # Source
        row = Adw.ActionRow(title='Fonte')
        row.add_suffix(self._create_source_badge(app.source))
        group.add(row)
            
        # Size
        if app.size:
            row = Adw.ActionRow(title='Tamanho')
            row.add_suffix(Gtk.Label(label=app.size))
            group.add(row)
            
        # Downloads
        if app.downloads:
            row = Adw.ActionRow(title='Downloads')
            downloads_text = f'{app.downloads:,}'.replace(',', '.')
            row.add_suffix(Gtk.Label(label=downloads_text))
            group.add(row)
            
        # License
        if app.license:
            row = Adw.ActionRow(title='Licença')
            row.add_suffix(Gtk.Label(label=app.license))
            group.add(row)
            
        # Categories
        if app.categories:
            row = Adw.ActionRow(title='Categorias')
            cats = ', '.join(c.title() for c in app.categories[:3])
            row.add_suffix(Gtk.Label(label=cats))
            group.add(row)
            
        return group
        
    def _create_reviews_section(self, app: AppInfo) -> Adw.PreferencesGroup:
        """Create reviews section"""
        group = Adw.PreferencesGroup()
        group.set_title('Avaliações')
        
        # Placeholder
        row = Adw.ActionRow(
            title='Seja o primeiro a avaliar!',
            subtitle='Ainda não há avaliações para este aplicativo'
        )
        group.add(row)
        
        return group
        
    def _on_back_clicked(self, button):
        """Handle back button click"""
        self.emit('back-clicked')
        
    def _on_install_clicked(self, button):
        """Handle install click"""
        if not self._app:
            return
            
        button.set_label('Instalando...')
        button.set_sensitive(False)
        button.add_css_class('installing')
        
        def do_install():
            # TODO: Actual installation
            GLib.idle_add(self._on_install_complete, button)
            
        thread = threading.Thread(target=do_install, daemon=True)
        thread.start()
        
    def _on_install_complete(self, button):
        """Handle install complete"""
        button.set_label('Instalado')
        button.remove_css_class('installing')
        button.remove_css_class('suggested-action')
        button.add_css_class('success')
        return False
        
    def _on_remove_clicked(self, button):
        """Handle remove click"""
        if not self._app:
            return
            
        # Show confirmation dialog
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            heading=f'Remover {self._app.name}?',
            body='Este aplicativo será removido do seu sistema.'
        )
        dialog.add_response('cancel', 'Cancelar')
        dialog.add_response('remove', 'Remover')
        dialog.set_response_appearance('remove', Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect('response', self._on_remove_confirmed)
        dialog.present()
        
    def _on_remove_confirmed(self, dialog, response):
        """Handle remove confirmation"""
        if response == 'remove' and self._app:
            # TODO: Actual removal
            pass
            
    def _on_launch_clicked(self, button):
        """Handle launch click"""
        if self._app:
            # TODO: Launch app
            pass
