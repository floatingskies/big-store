"""
Big Store - Distrobox Dialog
Dialog for creating and managing Distrobox containers
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
from typing import Optional, List, Dict
import threading
import subprocess
import json


class DistroboxDialog(Adw.Window):
    """Dialog for creating Distrobox containers"""
    
    __gtype_name__ = 'DistroboxDialog'
    
    # Available distros
    DISTROS = [
        {'id': 'archlinux', 'name': 'Arch Linux', 'image': 'archlinux:latest', 'icon': 'archlinux-logo'},
        {'id': 'ubuntu', 'name': 'Ubuntu', 'image': 'ubuntu:latest', 'icon': 'ubuntu-logo'},
        {'id': 'ubuntu-22.04', 'name': 'Ubuntu 22.04 LTS', 'image': 'ubuntu:22.04', 'icon': 'ubuntu-logo'},
        {'id': 'ubuntu-24.04', 'name': 'Ubuntu 24.04 LTS', 'image': 'ubuntu:24.04', 'icon': 'ubuntu-logo'},
        {'id': 'fedora', 'name': 'Fedora', 'image': 'fedora:latest', 'icon': 'fedora-logo'},
        {'id': 'fedora-40', 'name': 'Fedora 40', 'image': 'fedora:40', 'icon': 'fedora-logo'},
        {'id': 'debian', 'name': 'Debian', 'image': 'debian:latest', 'icon': 'debian-logo'},
        {'id': 'debian-12', 'name': 'Debian 12 (Bookworm)', 'image': 'debian:bookworm', 'icon': 'debian-logo'},
        {'id': 'opensuse', 'name': 'openSUSE Tumbleweed', 'image': 'opensuse/tumbleweed:latest', 'icon': 'opensuse-logo'},
        {'id': 'alpine', 'name': 'Alpine Linux', 'image': 'alpine:latest', 'icon': 'alpine-logo'},
        {'id': 'centos', 'name': 'CentOS Stream 9', 'image': 'quay.io/centos/centos:stream9', 'icon': 'centos-logo'},
        {'id': 'rocky', 'name': 'Rocky Linux 9', 'image': 'rockylinux:9', 'icon': 'rocky-logo'},
        {'id': 'almalinux', 'name': 'AlmaLinux 9', 'image': 'almalinux:9', 'icon': 'almalinux-logo'},
        {'id': 'void', 'name': 'Void Linux', 'image': 'ghcr.io/void-linux/void-glibc:latest', 'icon': 'void-logo'},
        {'id': 'gentoo', 'name': 'Gentoo Linux', 'image': 'gentoo/stage3:latest', 'icon': 'gentoo-logo'},
    ]
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(**kwargs)
        
        self.set_title('Criar Distrobox')
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(500, 600)
        self.set_size_request(400, 500)
        
        self._selected_distro: Optional[Dict] = None
        self._is_creating = False
        
        self._build_ui()
        self._check_distrobox()
        
    def _build_ui(self):
        """Build dialog UI"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Header
        header = Adw.HeaderBar()
        header.add_css_class('flat')
        main_box.append(header)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)
        
        # Info card
        info_group = Adw.PreferencesGroup()
        
        info_row = Adw.ActionRow(
            title='O que é Distrobox?',
            subtitle='Execute qualquer distribuição Linux em containers e acesse seus aplicativos nativamente'
        )
        info_row.add_suffix(Gtk.Image.new_from_icon_name('info-symbolic'))
        info_group.add(info_row)
        
        content.append(info_group)
        
        # Name entry
        name_group = Adw.PreferencesGroup()
        name_group.set_title('Nome do Container')
        
        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text('Ex: arch-toolbox, ubuntu-dev')
        self.name_entry.add_css_class('card')
        
        name_row = Adw.ActionRow()
        name_row.add_suffix(self.name_entry)
        name_group.add(name_row)
        
        content.append(name_group)
        
        # Distro selection
        distro_group = Adw.PreferencesGroup()
        distro_group.set_title('Escolha a Distribuição')
        
        # Search entry
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text('Buscar distribuição...')
        self.search_entry.add_css_class('search-entry')
        self.search_entry.connect('changed', self._on_search_changed)
        distro_group.add(self.search_entry)
        
        # Distro list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(250)
        
        self.distro_list = Gtk.ListBox()
        self.distro_list.add_css_class('navigation-sidebar')
        self.distro_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.distro_list.connect('row-selected', self._on_distro_selected)
        
        # Add distros
        self._populate_distro_list()
        
        scrolled.set_child(self.distro_list)
        
        distro_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        distro_box.append(scrolled)
        distro_group.add(distro_box)
        
        content.append(distro_group)
        
        # Status label
        self.status_label = Gtk.Label()
        self.status_label.add_css_class('dim-label')
        self.status_label.set_margin_top(12)
        content.append(self.status_label)
        
        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(12)
        
        cancel_btn = Gtk.Button(label='Cancelar')
        cancel_btn.add_css_class('flat')
        cancel_btn.connect('clicked', self._on_cancel)
        button_box.append(cancel_btn)
        
        self.create_btn = Gtk.Button(label='Criar Distrobox')
        self.create_btn.add_css_class('suggested-action')
        self.create_btn.set_sensitive(False)
        self.create_btn.connect('clicked', self._on_create)
        button_box.append(self.create_btn)
        
        content.append(button_box)
        
        main_box.append(content)
        self.set_content(main_box)
        
    def _populate_distro_list(self, filter_text: str = ''):
        """Populate distro list with optional filter"""
        # Clear existing
        while row := self.distro_list.get_first_child():
            self.distro_list.remove(row)
            
        # Add matching distros
        filter_lower = filter_text.lower()
        
        for distro in self.DISTROS:
            if filter_lower:
                if (filter_lower not in distro['name'].lower() and
                    filter_lower not in distro['id'].lower()):
                    continue
                    
            row = self._create_distro_row(distro)
            self.distro_list.append(row)
            
    def _create_distro_row(self, distro: Dict) -> Gtk.ListBoxRow:
        """Create a distro list row"""
        row = Gtk.ListBoxRow()
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)
        
        # Icon
        icon = Gtk.Image()
        icon.set_pixel_size(32)
        icon.set_from_icon_name(distro.get('icon') or 'application-x-executive-symbolic')
        box.append(icon)
        
        # Info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        name_label = Gtk.Label(label=distro['name'])
        name_label.set_halign(Gtk.Align.START)
        info_box.append(name_label)
        
        image_label = Gtk.Label(label=distro['image'])
        image_label.add_css_class('dim-label')
        image_label.add_css_class('caption')
        image_label.set_halign(Gtk.Align.START)
        info_box.append(image_label)
        
        box.append(info_box)
        
        row.set_child(box)
        row.distro_data = distro
        
        return row
        
    def _check_distrobox(self):
        """Check if Distrobox is installed"""
        def check():
            try:
                result = subprocess.run(
                    ['distrobox', 'version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                installed = result.returncode == 0
                GLib.idle_add(self._on_distrobox_checked, installed)
            except Exception as e:
                GLib.idle_add(self._on_distrobox_checked, False)
                
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
        
    def _on_distrobox_checked(self, installed: bool):
        """Handle distrobox check result"""
        if not installed:
            self.status_label.set_label('⚠️ Distrobox não está instalado')
            self.status_label.add_css_class('warning')
            self.create_btn.set_sensitive(False)
        else:
            self.status_label.set_label('✓ Distrobox detectado')
            self.status_label.add_css_class('success')
            
    def _on_search_changed(self, entry):
        """Handle search entry changed"""
        text = entry.get_text()
        self._populate_distro_list(text)
        
    def _on_distro_selected(self, listbox, row):
        """Handle distro selection"""
        if row and hasattr(row, 'distro_data'):
            self._selected_distro = row.distro_data
            self._update_create_button()
        else:
            self._selected_distro = None
            
    def _update_create_button(self):
        """Update create button sensitivity"""
        name = self.name_entry.get_text().strip()
        has_distro = self._selected_distro is not None
        has_name = len(name) >= 2
        
        self.create_btn.set_sensitive(has_distro and has_name)
        
        # Connect name entry
        self.name_entry.connect('changed', lambda e: self._update_create_button())
        
    def _on_cancel(self, button):
        """Handle cancel button"""
        self.close()
        
    def _on_create(self, button):
        """Handle create button"""
        if not self._selected_distro:
            return
            
        name = self.name_entry.get_text().strip()
        if not name:
            return
            
        self._is_creating = True
        button.set_label('Criando...')
        button.set_sensitive(False)
        self.status_label.set_label('⏳ Criando container...')
        
        def create():
            try:
                # Run distrobox-create
                cmd = [
                    'distrobox-create',
                    '--name', name,
                    '--image', self._selected_distro['image'],
                    '--yes',
                    '--pull'
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode == 0:
                    GLib.idle_add(self._on_create_success, name)
                else:
                    GLib.idle_add(self._on_create_error, result.stderr)
                    
            except subprocess.TimeoutExpired:
                GLib.idle_add(self._on_create_error, 'Timeout - operação demorou muito')
            except Exception as e:
                GLib.idle_add(self._on_create_error, str(e))
                
        thread = threading.Thread(target=create, daemon=True)
        thread.start()
        
    def _on_create_success(self, name: str):
        """Handle successful creation"""
        self._is_creating = False
        self.status_label.set_label(f'✓ Container "{name}" criado com sucesso!')
        self.status_label.add_css_class('success')
        
        # Show success dialog
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading='Distrobox Criado!',
            body=f'O container "{name}" foi criado com sucesso.\n\n'
                 f'Você pode iniciá-lo com:\ndistrobox-enter {name}'
        )
        dialog.add_response('ok', 'OK')
        dialog.connect('response', lambda d, r: self.close())
        dialog.present()
        
    def _on_create_error(self, error: str):
        """Handle creation error"""
        self._is_creating = False
        self.create_btn.set_label('Criar Distrobox')
        self.create_btn.set_sensitive(True)
        
        self.status_label.set_label(f'❌ Erro: {error}')
        self.status_label.add_css_class('error')


class DistroboxManagerDialog(Adw.Window):
    """Dialog for managing existing Distrobox containers"""
    
    __gtype_name__ = 'DistroboxManagerDialog'
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(**kwargs)
        
        self.set_title('Gerenciar Distrobox')
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(600, 500)
        
        self._containers: List[Dict] = []
        
        self._build_ui()
        self._load_containers()
        
    def _build_ui(self):
        """Build UI"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Header
        header = Adw.HeaderBar()
        header.add_css_class('flat')
        
        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name('view-refresh-symbolic')
        refresh_btn.set_tooltip_text('Atualizar')
        refresh_btn.connect('clicked', self._on_refresh)
        header.pack_end(refresh_btn)
        
        main_box.append(header)
        
        # Content
        self.content_stack = Gtk.Stack()
        
        # Loading
        loading = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        loading.set_valign(Gtk.Align.CENTER)
        loading.set_halign(Gtk.Align.CENTER)
        spinner = Gtk.Spinner()
        spinner.set_spinning(True)
        loading.append(spinner)
        loading.append(Gtk.Label(label='Carregando containers...'))
        self.content_stack.add_named(loading, 'loading')
        
        # Empty
        empty = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        empty.set_valign(Gtk.Align.CENTER)
        empty.set_halign(Gtk.Align.CENTER)
        empty.append(Gtk.Image.new_from_icon_name('box-symbolic'))
        empty.append(Gtk.Label(label='Nenhum container encontrado'))
        self.content_stack.add_named(empty, 'empty')
        
        # List
        scrolled = Gtk.ScrolledWindow()
        self.container_list = Gtk.ListBox()
        self.container_list.add_css_class('navigation-sidebar')
        scrolled.set_child(self.container_list)
        self.content_stack.add_named(scrolled, 'list')
        
        main_box.append(self.content_stack)
        self.set_content(main_box)
        
    def _load_containers(self):
        """Load containers"""
        self.content_stack.set_visible_child_name('loading')
        
        def load():
            try:
                result = subprocess.run(
                    ['distrobox', 'list', '--no-color'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    containers = self._parse_containers(result.stdout)
                    GLib.idle_add(self._on_containers_loaded, containers)
                else:
                    GLib.idle_add(self._on_containers_loaded, [])
            except Exception:
                GLib.idle_add(self._on_containers_loaded, [])
                
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
        
    def _parse_containers(self, output: str) -> List[Dict]:
        """Parse distrobox list output"""
        containers = []
        lines = output.strip().split('\n')
        
        for line in lines[1:]:  # Skip header
            parts = line.split('|')
            if len(parts) >= 4:
                containers.append({
                    'name': parts[0].strip(),
                    'image': parts[1].strip(),
                    'status': parts[2].strip(),
                    'distro': parts[3].strip()
                })
                
        return containers
        
    def _on_containers_loaded(self, containers: List[Dict]):
        """Handle containers loaded"""
        self._containers = containers
        
        # Clear list
        while row := self.container_list.get_first_child():
            self.container_list.remove(row)
            
        if not containers:
            self.content_stack.set_visible_child_name('empty')
            return
            
        # Add containers
        for container in containers:
            row = self._create_container_row(container)
            self.container_list.append(row)
            
        self.content_stack.set_visible_child_name('list')
        
    def _create_container_row(self, container: Dict) -> Gtk.ListBoxRow:
        """Create container row"""
        row = Gtk.ListBoxRow()
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name('box-symbolic')
        icon.set_pixel_size(32)
        box.append(icon)
        
        # Info
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info.set_hexpand(True)
        
        name_label = Gtk.Label(label=container['name'])
        name_label.set_halign(Gtk.Align.START)
        info.append(name_label)
        
        details = f"{container['distro']} • {container['image']}"
        details_label = Gtk.Label(label=details)
        details_label.add_css_class('dim-label')
        details_label.add_css_class('caption')
        details_label.set_halign(Gtk.Align.START)
        info.append(details_label)
        
        box.append(info)
        
        # Status
        status = Gtk.Label(label=container['status'])
        if 'running' in container['status'].lower():
            status.add_css_class('success')
        else:
            status.add_css_class('dim-label')
        box.append(status)
        
        # Actions
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        enter_btn = Gtk.Button()
        enter_btn.set_icon_name('media-playback-start-symbolic')
        enter_btn.set_tooltip_text('Entrar')
        enter_btn.add_css_class('flat')
        actions.append(enter_btn)
        
        stop_btn = Gtk.Button()
        stop_btn.set_icon_name('media-playback-stop-symbolic')
        stop_btn.set_tooltip_text('Parar')
        stop_btn.add_css_class('flat')
        actions.append(stop_btn)
        
        box.append(actions)
        
        row.set_child(box)
        return row
        
    def _on_refresh(self, button):
        """Handle refresh"""
        self._load_containers()
