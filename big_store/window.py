"""
Big Store - Main Window
Interface principal da loja de aplicativos
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, Gdk, GLib, Pango
from typing import Optional, List, Dict
import threading
import json

from big_store.widgets.app_card import AppCard
from big_store.widgets.category_row import CategoryRow
from big_store.widgets.featured_banner import FeaturedBanner
from big_store.widgets.distrobox_dialog import DistroboxDialog
from big_store.widgets.app_detail_view import AppDetailView
from big_store.widgets.install_dialog import InstallDialog
from big_store.models import AppInfo


class BigStoreWindow(Adw.ApplicationWindow):
    """Main Application Window"""
    
    __gtype_name__ = 'BigStoreWindow'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.set_title('Big Store')
        self.set_default_size(1200, 800)
        self.set_size_request(800, 600)
        
        # State
        self._current_category = 'all'
        self._current_source = 'all'
        self._search_text = ''
        self._loading = False
        self._apps_cache: List[AppInfo] = []
        self._filtered_apps: List[AppInfo] = []
        
        # Build UI
        self._build_ui()
        
        # Load initial data
        self._load_data()
        
    def _build_ui(self):
        """Build the main UI"""
        # Main Box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)
        
        # Header Bar
        self._build_header()
        
        # Main Content - Split View
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_min_sidebar_width(200)
        self.split_view.set_max_sidebar_width(280)
        self.split_view.set_sidebar_width_fraction(0.2)
        self.main_box.append(self.split_view)
        
        # Sidebar
        self._build_sidebar()
        
        # Content Area
        self._build_content()
        
    def _build_header(self):
        """Build the header bar"""
        self.header_bar = Adw.HeaderBar()
        self.header_bar.add_css_class('titlebar')
        self.main_box.append(self.header_bar)
        
        # Left - Menu Button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name('open-menu-symbolic')
        menu_button.set_tooltip_text('Menu')
        
        # Menu Model
        menu = Gio.Menu()
        menu.append('Atualizar Cache', 'app.refresh')
        menu.append('Preferências', 'app.preferences')
        menu.append('Sobre', 'app.about')
        menu_button.set_menu_model(menu)
        
        self.header_bar.pack_end(menu_button)
        
        # Center - Search
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text('Buscar aplicativos...')
        self.search_entry.add_css_class('search-entry')
        self.search_entry.connect('changed', self._on_search_changed)
        self.search_entry.connect('activate', self._on_search_activate)
        self.header_bar.set_title_widget(self.search_entry)
        
        # Right - Source Filter
        self.source_dropdown = Gtk.DropDown()
        self.source_dropdown.add_css_class('flat')
        
        sources = Gtk.StringList.new([
            'Todas Fontes',
            'Flatpak',
            'Snap',
            'AUR',
            'Nativo',
            'Distrobox'
        ])
        self.source_dropdown.set_model(sources)
        self.source_dropdown.connect('notify::selected', self._on_source_changed)
        
        self.header_bar.pack_start(self.source_dropdown)
        
    def _build_sidebar(self):
        """Build the sidebar"""
        # Sidebar Container
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sidebar_box.set_margin_top(12)
        sidebar_box.set_margin_bottom(12)
        sidebar_box.set_margin_start(12)
        sidebar_box.set_margin_end(12)
        
        # Scrollable
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        # Categories List
        self.categories_list = Gtk.ListBox()
        self.categories_list.add_css_class('navigation-sidebar')
        self.categories_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.categories_list.connect('row-selected', self._on_category_selected)
        
        # Category Items
        categories = [
            ('all', 'Todas as Categorias', 'applications-symbolic'),
            ('featured', 'Destaques', 'starred-symbolic'),
            ('audio-video', 'Áudio e Vídeo', 'folder-music-symbolic'),
            ('development', 'Desenvolvimento', 'applications-engineering-symbolic'),
            ('education', 'Educação', 'accessories-dictionary-symbolic'),
            ('games', 'Jogos', 'applications-games-symbolic'),
            ('graphics', 'Gráficos', 'applications-graphics-symbolic'),
            ('network', 'Internet', 'applications-internet-symbolic'),
            ('office', 'Escritório', 'applications-office-symbolic'),
            ('science', 'Ciência', 'applications-science-symbolic'),
            ('system', 'Sistema', 'applications-system-symbolic'),
            ('utilities', 'Utilitários', 'applications-utilities-symbolic'),
        ]
        
        for cat_id, cat_name, icon_name in categories:
            row = CategoryRow(cat_id, cat_name, icon_name)
            self.categories_list.append(row)
            
        scrolled.set_child(self.categories_list)
        sidebar_box.append(scrolled)
        
        # Distrobox Button
        distrobox_btn = Gtk.Button()
        distrobox_btn.set_label('Criar Distrobox')
        distrobox_btn.set_icon_name('box-symbolic')
        distrobox_btn.add_css_class('pill')
        distrobox_btn.add_css_class('suggested-action')
        distrobox_btn.set_margin_top(12)
        distrobox_btn.connect('clicked', self._on_distrobox_clicked)
        sidebar_box.append(distrobox_btn)
        
        # Package Counts
        self.counts_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.counts_box.set_margin_top(12)
        sidebar_box.append(self.counts_box)
        
        self.split_view.set_sidebar(sidebar_box)
        
    def _build_content(self):
        """Build the main content area"""
        # Main Content Box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Toolbar View
        self.toolbar_view = Adw.ToolbarView()
        
        # Content Stack
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        
        # Loading Page
        self._build_loading_page()
        
        # Main Page
        self._build_main_page()
        
        # Empty Page
        self._build_empty_page()
        
        # App Detail Page
        self._build_detail_page()
        
        content_box.append(self.content_stack)
        self.split_view.set_content(content_box)
        
    def _build_loading_page(self):
        """Build loading page"""
        loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        loading_box.set_valign(Gtk.Align.CENTER)
        loading_box.set_halign(Gtk.Align.CENTER)
        
        spinner = Gtk.Spinner()
        spinner.set_spinning(True)
        spinner.set_size_request(48, 48)
        loading_box.append(spinner)
        
        label = Gtk.Label(label='Carregando aplicativos...')
        label.add_css_class('title-2')
        loading_box.append(label)
        
        self.content_stack.add_named(loading_box, 'loading')
        
    def _build_main_page(self):
        """Build main apps grid page"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Featured Banner
        self.featured_banner = FeaturedBanner()
        main_box.append(self.featured_banner)
        
        # Filter Pills
        self._build_filter_pills(main_box)
        
        # Apps Grid
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        self.apps_flow = Gtk.FlowBox()
        self.apps_flow.set_homogeneous(True)
        self.apps_flow.set_column_spacing(12)
        self.apps_flow.set_row_spacing(12)
        self.apps_flow.set_margin_start(12)
        self.apps_flow.set_margin_end(12)
        self.apps_flow.set_margin_top(12)
        self.apps_flow.set_margin_bottom(12)
        self.apps_flow.set_valign(Gtk.Align.START)
        self.apps_flow.connect('child-activated', self._on_app_activated)
        
        scrolled.set_child(self.apps_flow)
        main_box.append(scrolled)
        
        self.content_stack.add_named(main_box, 'main')
        
    def _build_filter_pills(self, parent):
        """Build filter pills"""
        pills_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        pills_box.set_margin_start(12)
        pills_box.set_margin_top(12)
        
        pills_box.append(Gtk.Label(label='Ordenar:'))
        
        # Sort Dropdown
        sort_dropdown = Gtk.DropDown()
        sort_model = Gtk.StringList.new([
            'Nome (A-Z)',
            'Nome (Z-A)',
            'Mais Populares',
            'Melhor Avaliados',
            'Instalados Primeiro'
        ])
        sort_dropdown.set_model(sort_model)
        sort_dropdown.add_css_class('pill')
        sort_dropdown.connect('notify::selected', self._on_sort_changed)
        pills_box.append(sort_dropdown)
        
        self.sort_dropdown = sort_dropdown
        
        parent.append(pills_box)
        
    def _build_empty_page(self):
        """Build empty state page"""
        empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        empty_box.set_valign(Gtk.Align.CENTER)
        empty_box.set_halign(Gtk.Align.CENTER)
        
        icon = Gtk.Image.new_from_icon_name('edit-find-symbolic')
        icon.set_pixel_size(64)
        icon.add_css_class('dim-label')
        empty_box.append(icon)
        
        label = Gtk.Label(label='Nenhum aplicativo encontrado')
        label.add_css_class('title-2')
        empty_box.append(label)
        
        sublabel = Gtk.Label(label='Tente ajustar os filtros ou busca')
        sublabel.add_css_class('dim-label')
        empty_box.append(sublabel)
        
        self.content_stack.add_named(empty_box, 'empty')
        
    def _build_detail_page(self):
        """Build app detail page"""
        self.detail_view = AppDetailView()
        self.detail_view.connect('back-clicked', self._on_detail_back)
        self.content_stack.add_named(self.detail_view, 'detail')
        
    def _load_data(self):
        """Load apps data"""
        self.content_stack.set_visible_child_name('loading')
        self._loading = True
        
        def load_in_thread():
            app = self.get_application()
            if app and app.package_manager:
                self._apps_cache = app.package_manager.get_all_apps()
                GLib.idle_add(self._on_data_loaded)
            else:
                # Demo data for testing
                self._apps_cache = self._get_demo_apps()
                GLib.idle_add(self._on_data_loaded)
                
        thread = threading.Thread(target=load_in_thread, daemon=True)
        thread.start()
        
    def _get_demo_apps(self) -> List[AppInfo]:
        """Get demo apps for testing"""
        return [
            AppInfo(
                id='org.mozilla.Firefox',
                name='Firefox',
                summary='Navegador web rápido e seguro',
                description='O Firefox é um navegador web livre e de código aberto...',
                icon_name='firefox',
                version='122.0',
                developer='Mozilla',
                categories=['network', 'web'],
                source='flatpak',
                installed=True,
                size='150 MB',
                rating=4.8,
                downloads=1000000
            ),
            AppInfo(
                id='org.gimp.GIMP',
                name='GIMP',
                summary='Editor de imagens profissional',
                description='GIMP é um editor de imagens de código aberto...',
                icon_name='gimp',
                version='2.10.36',
                developer='GIMP Team',
                categories=['graphics'],
                source='flatpak',
                installed=False,
                size='280 MB',
                rating=4.6,
                downloads=500000
            ),
            AppInfo(
                id='com.visualstudio.code',
                name='VS Code',
                summary='Editor de código leve e poderoso',
                description='Visual Studio Code é um editor de código fonte...',
                icon_name='vscode',
                version='1.85.0',
                developer='Microsoft',
                categories=['development'],
                source='snap',
                installed=False,
                size='120 MB',
                rating=4.9,
                downloads=2000000
            ),
            AppInfo(
                id='spotify',
                name='Spotify',
                summary='Streaming de música',
                description='Ouvir música nunca foi tão fácil...',
                icon_name='spotify',
                version='1.2.0',
                developer='Spotify AB',
                categories=['audio-video'],
                source='snap',
                installed=True,
                size='180 MB',
                rating=4.7,
                downloads=5000000
            ),
            AppInfo(
                id='vlc',
                name='VLC Media Player',
                summary='Reprodutor multimídia universal',
                description='VLC é um reprodutor multimídia gratuito...',
                icon_name='vlc',
                version='3.0.20',
                developer='VideoLAN',
                categories=['audio-video'],
                source='native',
                installed=False,
                size='85 MB',
                rating=4.8,
                downloads=3000000
            ),
            AppInfo(
                id='discord',
                name='Discord',
                summary='Chat para comunidades',
                description='Discord é uma plataforma de comunicação...',
                icon_name='discord',
                version='0.0.35',
                developer='Discord Inc.',
                categories=['network'],
                source='flatpak',
                installed=False,
                size='150 MB',
                rating=4.5,
                downloads=4000000
            ),
            AppInfo(
                id='libreoffice',
                name='LibreOffice',
                summary='Suíte de escritório completa',
                description='LibreOffice é uma suíte de escritório...',
                icon_name='libreoffice-main',
                version='7.6.4',
                developer='The Document Foundation',
                categories=['office'],
                source='native',
                installed=True,
                size='450 MB',
                rating=4.4,
                downloads=2000000
            ),
            AppInfo(
                id='steam',
                name='Steam',
                summary='Plataforma de jogos',
                description='Steam é uma plataforma de distribuição...',
                icon_name='steam',
                version='1.0.0.78',
                developer='Valve',
                categories=['games'],
                source='flatpak',
                installed=False,
                size='6 MB',
                rating=4.9,
                downloads=10000000
            ),
            AppInfo(
                id='blender',
                name='Blender',
                summary='Modelagem 3D e animação',
                description='Blender é um software gratuito...',
                icon_name='blender',
                version='4.0.2',
                developer='Blender Foundation',
                categories=['graphics', '3d'],
                source='flatpak',
                installed=False,
                size='350 MB',
                rating=4.9,
                downloads=1500000
            ),
            AppInfo(
                id='obs-studio',
                name='OBS Studio',
                summary='Gravação e streaming',
                description='Open Broadcaster Software...',
                icon_name='obs',
                version='30.0.2',
                developer='OBS Project',
                categories=['audio-video'],
                source='flatpak',
                installed=False,
                size='120 MB',
                rating=4.8,
                downloads=2500000
            ),
            AppInfo(
                id='gitkraken',
                name='GitKraken',
                summary='Cliente Git visual',
                description='GitKraken é um cliente Git intuitivo...',
                icon_name='gitkraken',
                version='9.5.0',
                developer='Axosoft',
                categories=['development'],
                source='aur',
                installed=False,
                size='180 MB',
                rating=4.3,
                downloads=500000
            ),
            AppInfo(
                id='google-chrome',
                name='Google Chrome',
                summary='Navegador web do Google',
                description='Um navegador web rápido e seguro...',
                icon_name='google-chrome',
                version='120.0',
                developer='Google',
                categories=['network'],
                source='aur',
                installed=False,
                size='100 MB',
                rating=4.5,
                downloads=8000000
            ),
        ]
        
    def _on_data_loaded(self):
        """Handle data loaded"""
        self._loading = False
        self._apply_filters()
        self._update_counts()
        self.content_stack.set_visible_child_name('main')
        
    def _apply_filters(self):
        """Apply current filters"""
        self._filtered_apps = []
        
        for app in self._apps_cache:
            # Filter by category
            if self._current_category != 'all':
                if self._current_category == 'featured':
                    if not app.featured:
                        continue
                elif self._current_category not in app.categories:
                    continue
                    
            # Filter by source
            if self._current_source != 'all':
                if app.source != self._current_source:
                    continue
                    
            # Filter by search
            if self._search_text:
                search_lower = self._search_text.lower()
                if (search_lower not in app.name.lower() and
                    search_lower not in app.summary.lower() and
                    search_lower not in app.description.lower()):
                    continue
                    
            self._filtered_apps.append(app)
            
        # Apply sort
        self._apply_sort()
        
        # Update grid
        self._update_grid()
        
    def _apply_sort(self):
        """Apply current sort"""
        sort_idx = self.sort_dropdown.get_selected()
        
        if sort_idx == 0:  # Nome A-Z
            self._filtered_apps.sort(key=lambda a: a.name.lower() if a.name else '')
        elif sort_idx == 1:  # Nome Z-A
            self._filtered_apps.sort(key=lambda a: a.name.lower() if a.name else '', reverse=True)
        elif sort_idx == 2:  # Mais Populares (downloads)
            self._filtered_apps.sort(key=lambda a: a.downloads or 0, reverse=True)
        elif sort_idx == 3:  # Melhor Avaliados (rating)
            self._filtered_apps.sort(key=lambda a: a.rating or 0, reverse=True)
        elif sort_idx == 4:  # Instalados Primeiro
            self._filtered_apps.sort(key=lambda a: (not a.installed, a.name.lower() if a.name else ''))
            
    def _on_sort_changed(self, dropdown, param):
        """Handle sort selection changed"""
        self._apply_filters()
            
    def _update_grid(self):
        """Update the apps grid"""
        # Clear existing
        while child := self.apps_flow.get_first_child():
            self.apps_flow.remove(child)
            
        # Check if empty
        if not self._filtered_apps:
            self.content_stack.set_visible_child_name('empty')
            return
            
        self.content_stack.set_visible_child_name('main')
        
        # Add apps
        for app in self._filtered_apps:
            card = AppCard(app)
            self.apps_flow.append(card)
            
    def _update_counts(self):
        """Update package counts in sidebar"""
        # Clear existing
        while child := self.counts_box.get_first_child():
            self.counts_box.remove(child)
            
        # Count by source
        counts = {
            'flatpak': 0,
            'snap': 0,
            'aur': 0,
            'native': 0,
            'distrobox': 0
        }
        
        for app in self._apps_cache:
            if app.source in counts:
                counts[app.source] += 1
                
        # Installed count
        installed = sum(1 for app in self._apps_cache if app.installed)
        
        # Labels
        total_label = Gtk.Label(
            label=f'<b>{len(self._apps_cache)}</b> aplicativos disponíveis',
            use_markup=True
        )
        total_label.add_css_class('dim-label')
        total_label.add_css_class('caption')
        self.counts_box.append(total_label)
        
        installed_label = Gtk.Label(
            label=f'<b>{installed}</b> instalados',
            use_markup=True
        )
        installed_label.add_css_class('dim-label')
        installed_label.add_css_class('caption')
        self.counts_box.append(installed_label)
        
    def _on_search_changed(self, entry):
        """Handle search changed"""
        self._search_text = entry.get_text()
        self._apply_filters()
        
    def _on_search_activate(self, entry):
        """Handle search activate"""
        self._apply_filters()
        
    def _on_source_changed(self, dropdown, param):
        """Handle source filter changed"""
        idx = dropdown.get_selected()
        sources = ['all', 'flatpak', 'snap', 'aur', 'native', 'distrobox']
        self._current_source = sources[idx] if idx < len(sources) else 'all'
        self._apply_filters()
        
    def _on_category_selected(self, listbox, row):
        """Handle category selected"""
        if row:
            self._current_category = row.category_id
            self._apply_filters()
            
    def _on_app_activated(self, flowbox, child):
        """Handle app card activated"""
        card = child.get_child()
        if card and hasattr(card, 'app_info'):
            self.show_app_detail(card.app_info)
            
    def show_app_detail(self, app: AppInfo):
        """Show app detail view"""
        self.detail_view.set_app(app)
        self.content_stack.set_visible_child_name('detail')
        
    def _on_detail_back(self, widget):
        """Handle back from detail view"""
        self.content_stack.set_visible_child_name('main')
        
    def _on_distrobox_clicked(self, button):
        """Handle distrobox button clicked"""
        dialog = DistroboxDialog(self)
        dialog.present()
        
    def focus_search(self):
        """Focus the search entry"""
        self.search_entry.grab_focus()
        
    def refresh_content(self):
        """Refresh content"""
        self._load_data()
        
    def show_preferences(self):
        """Show preferences dialog"""
        # TODO: Implement preferences dialog
        pass
