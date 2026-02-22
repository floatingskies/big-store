"""
Big Store - Data Models
Application data structures
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class PackageSource(Enum):
    """Package source types"""
    FLATPAK = 'flatpak'
    SNAP = 'snap'
    AUR = 'aur'
    NATIVE = 'native'
    DISTROBOX = 'distrobox'


class DistroType(Enum):
    """Supported distributions"""
    ARCH = 'arch'
    MANJARO = 'manjaro'
    BIGLINUX = 'biglinux'
    ENDEAVOUROS = 'endeavouros'
    GARUDA = 'garuda'
    FEDORA = 'fedora'
    UBUNTU = 'ubuntu'
    DEBIAN = 'debian'
    OPENSUSE = 'opensuse'
    GENTOO = 'gentoo'
    VOID = 'void'
    ALPINE = 'alpine'
    UNKNOWN = 'unknown'


@dataclass
class AppInfo:
    """Application information dataclass"""
    id: str
    name: str
    summary: str
    description: str = ''
    icon_name: Optional[str] = None
    version: Optional[str] = None
    developer: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    source: str = 'native'
    installed: bool = False
    size: Optional[str] = None
    rating: Optional[float] = None
    downloads: Optional[int] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    featured: bool = False
    update_available: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'summary': self.summary,
            'description': self.description,
            'icon_name': self.icon_name,
            'version': self.version,
            'developer': self.developer,
            'categories': self.categories,
            'source': self.source,
            'installed': self.installed,
            'size': self.size,
            'rating': self.rating,
            'downloads': self.downloads,
            'license': self.license,
            'homepage': self.homepage,
            'screenshots': self.screenshots,
            'featured': self.featured,
            'update_available': self.update_available
        }


@dataclass
class DistroInfo:
    """Distribution information"""
    name: str
    distro_type: DistroType
    version: str
    codename: str = ''
    base: str = ''  # arch, debian, rhel, etc.
    package_manager: str = ''  # pacman, apt, dnf, etc.
    supports_aur: bool = False
    supports_flatpak: bool = True
    supports_snap: bool = True


@dataclass
class DistroboxContainer:
    """Distrobox container information"""
    name: str
    image: str
    status: str
    distro: str
    home: str = ''
    volumes: List[str] = None
    
    def __post_init__(self):
        if self.volumes is None:
            self.volumes = []
