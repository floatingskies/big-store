"""
Big Store - Install Dialog
Dialog showing installation progress with real-time output
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import Optional

from big_store.models import AppInfo
from big_store.managers.installation_manager import InstallationManager, InstallProgress, InstallStatus


class InstallDialog(Adw.Window):
    """Dialog for showing installation progress"""
    
    def __init__(self, app: AppInfo, parent=None, **kwargs):
        super().__init__(**kwargs)
        
        self._app = app
        self._manager = InstallationManager()
        self._completed = False
        
        self.set_title(f'Instalar {app.name}')
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(450, 300)
        self.set_resizable(False)
        
        self._build_ui()
        
    def _build_ui(self):
        """Build dialog UI"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Header
        header = Adw.HeaderBar()
        header.add_css_class('flat')
        main_box.append(header)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_valign(Gtk.Align.CENTER)
        content.set_halign(Gtk.Align.CENTER)
        
        # App icon and name
        app_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        app_box.set_halign(Gtk.Align.CENTER)
        
        icon = Gtk.Image()
        icon.set_pixel_size(48)
        icon.set_from_icon_name(self._app.icon_name or 'application-x-executive-symbolic')
        app_box.append(icon)
        
        name_label = Gtk.Label(label=self._app.name)
        name_label.add_css_class('title-2')
        app_box.append(name_label)
        
        source_label = Gtk.Label(label=f'({self._app.source.upper()})')
        source_label.add_css_class('dim-label')
        source_label.add_css_class('caption')
        app_box.append(source_label)
        
        content.append(app_box)
        
        # Status label
        self.status_label = Gtk.Label(label='Preparando instalação...')
        self.status_label.add_css_class('heading')
        content.append(self.status_label)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text('0%')
        content.append(self.progress_bar)
        
        # Details text view (collapsible)
        expander = Gtk.Expander(label='Detalhes')
        expander.set_vexpand(True)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(100)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.details_view = Gtk.TextView()
        self.details_view.set_editable(False)
        self.details_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.details_buffer = self.details_view.get_buffer()
        scrolled.set_child(self.details_view)
        
        expander.set_child(scrolled)
        content.append(expander)
        
        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(12)
        
        self.cancel_button = Gtk.Button(label='Cancelar')
        self.cancel_button.add_css_class('destructive-action')
        self.cancel_button.connect('clicked', self._on_cancel)
        button_box.append(self.cancel_button)
        
        self.close_button = Gtk.Button(label='Fechar')
        self.close_button.connect('clicked', self._on_close)
        self.close_button.set_visible(False)
        button_box.append(self.close_button)
        
        content.append(button_box)
        
        main_box.append(content)
        self.set_content(main_box)
        
        # Start installation
        GLib.idle_add(self._start_installation)
        
    def _start_installation(self):
        """Start the installation process"""
        self._manager.install_package(
            self._app.id,
            self._app.source,
            progress_callback=self._on_progress,
            complete_callback=self._on_complete
        )
        
    def _on_progress(self, progress: InstallProgress):
        """Handle progress update"""
        GLib.idle_add(self._update_progress, progress)
        
    def _update_progress(self, progress: InstallProgress):
        """Update UI with progress"""
        # Update status label
        self.status_label.set_label(progress.message)
        
        # Update progress bar
        self.progress_bar.set_fraction(progress.percentage / 100.0)
        self.progress_bar.set_text(f'{progress.percentage}%')
        
        # Add pulsing animation for indeterminate progress
        if progress.percentage == 0:
            self.progress_bar.pulse()
        else:
            self.progress_bar.set_fraction(progress.percentage / 100.0)
            
        # Update details
        if progress.details:
            end_iter = self.details_buffer.get_end_iter()
            self.details_buffer.insert(end_iter, progress.details + '\n')
            
            # Auto-scroll to end
            mark = self.details_buffer.create_mark(None, end_iter, False)
            self.details_view.scroll_to_mark(mark, 0.0, False, 0.0, 0.0)
            
        # Handle status changes
        if progress.status == InstallStatus.COMPLETED:
            self._completed = True
            self.cancel_button.set_visible(False)
            self.close_button.set_visible(True)
            self.close_button.add_css_class('suggested-action')
            self.close_button.set_label('Concluído')
            self._app.installed = True
        elif progress.status == InstallStatus.FAILED:
            self._completed = True
            self.cancel_button.set_visible(False)
            self.close_button.set_visible(True)
            self.close_button.add_css_class('destructive-action')
            self.close_button.set_label('Fechar')
            
        return False
        
    def _on_complete(self, success: bool, message: str):
        """Handle installation complete"""
        GLib.idle_add(self._show_complete, success, message)
        
    def _show_complete(self, success: bool, message: str):
        """Show completion state"""
        if success:
            self.status_label.set_label('✓ Instalação concluída!')
            self.progress_bar.set_fraction(1.0)
            self._app.installed = True
        else:
            self.status_label.set_label('✗ Falha na instalação')
            
        return False
        
    def _on_cancel(self, button):
        """Handle cancel button"""
        self._manager.cancel()
        self.close()
        
    def _on_close(self, button):
        """Handle close button"""
        self.close()


class UninstallDialog(Adw.Window):
    """Dialog for showing uninstallation progress"""
    
    def __init__(self, app: AppInfo, parent=None, **kwargs):
        super().__init__(**kwargs)
        
        self._app = app
        self._manager = InstallationManager()
        
        self.set_title(f'Remover {app.name}')
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(400, 200)
        
        self._build_ui()
        
    def _build_ui(self):
        """Build dialog UI"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Header
        header = Adw.HeaderBar()
        header.add_css_class('flat')
        main_box.append(header)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_valign(Gtk.Align.CENTER)
        
        # Status
        self.status_label = Gtk.Label(label=f'Removendo {self._app.name}...')
        self.status_label.add_css_class('title-3')
        content.append(self.status_label)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        content.append(self.progress_bar)
        
        # Button
        self.close_button = Gtk.Button(label='Fechar')
        self.close_button.add_css_class('suggested-action')
        self.close_button.connect('clicked', lambda b: self.close())
        self.close_button.set_visible(False)
        content.append(self.close_button)
        
        main_box.append(content)
        self.set_content(main_box)
        
        # Start uninstallation
        GLib.idle_add(self._start_uninstallation)
        
    def _start_uninstallation(self):
        """Start uninstallation"""
        self._manager.uninstall_package(
            self._app.id,
            self._app.source,
            progress_callback=self._on_progress,
            complete_callback=self._on_complete
        )
        
    def _on_progress(self, progress: InstallProgress):
        """Handle progress"""
        GLib.idle_add(self._update_ui, progress)
        
    def _update_ui(self, progress: InstallProgress):
        """Update UI"""
        self.status_label.set_label(progress.message)
        self.progress_bar.set_fraction(progress.percentage / 100.0)
        return False
        
    def _on_complete(self, success: bool, message: str):
        """Handle complete"""
        GLib.idle_add(self._show_complete, success)
        
    def _show_complete(self, success: bool):
        """Show complete state"""
        if success:
            self.status_label.set_label('✓ Remoção concluída!')
            self._app.installed = False
        else:
            self.status_label.set_label('✗ Falha na remoção')
            
        self.close_button.set_visible(True)
        return False
