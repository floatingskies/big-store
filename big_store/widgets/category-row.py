"""
Big Store - Category Row Widget
Sidebar category navigation item
"""

import gi

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Pango


class CategoryRow(Gtk.ListBoxRow):
    """Category row for sidebar navigation"""
    
    __gtype_name__ = 'CategoryRow'
    
    def __init__(self, category_id: str, name: str, icon_name: str, **kwargs):
        super().__init__(**kwargs)
        
        self.category_id = category_id
        self.category_name = name
        self.icon_name = icon_name
        
        self._build_ui()
        
    def _build_ui(self):
        """Build row UI"""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name(self.icon_name)
        icon.set_pixel_size(20)
        icon.add_css_class('dim-label')
        box.append(icon)
        
        # Label
        label = Gtk.Label(label=self.category_name)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        box.append(label)
        
        # Count badge (optional)
        self.count_label = Gtk.Label()
        self.count_label.add_css_class('dim-label')
        self.count_label.add_css_class('caption')
        self.count_label.set_visible(False)
        box.append(self.count_label)
        
        self.set_child(box)
        
    def set_count(self, count: int):
        """Set count badge"""
        if count > 0:
            self.count_label.set_label(str(count))
            self.count_label.set_visible(True)
        else:
            self.count_label.set_visible(False)


class CategoryPill(Gtk.Button):
    """Category pill button for horizontal scrolling"""
    
    __gtype_name__ = 'CategoryPill'
    
    def __init__(self, category_id: str, name: str, icon_name: str = None, **kwargs):
        super().__init__(**kwargs)
        
        self.category_id = category_id
        
        self.add_css_class('category-pill')
        self.add_css_class('pill')
        
        self._build_ui(name, icon_name)
        
    def _build_ui(self, name: str, icon_name: str = None):
        """Build pill UI"""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        if icon_name:
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(16)
            box.append(icon)
            
        label = Gtk.Label(label=name)
        box.append(label)
        
        self.set_child(box)
