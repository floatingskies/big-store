"""
Big Store - Popular Apps Database
Curated list of popular applications with metadata
"""

# Popular applications with complete metadata
POPULAR_APPS = {
    # Browsers
    'firefox': {
        'name': 'Firefox',
        'summary': 'Navegador web rápido, privado e seguro',
        'categories': ['network', 'web-browser'],
        'icon': 'firefox',
        'developer': 'Mozilla',
    },
    'google-chrome': {
        'name': 'Google Chrome',
        'summary': 'Navegador web rápido e seguro',
        'categories': ['network', 'web-browser'],
        'icon': 'google-chrome',
        'developer': 'Google',
    },
    'brave': {
        'name': 'Brave Browser',
        'summary': 'Navegador focado em privacidade',
        'categories': ['network', 'web-browser'],
        'icon': 'brave',
        'developer': 'Brave Software',
    },
    'chromium': {
        'name': 'Chromium',
        'summary': 'Navegador web de código aberto',
        'categories': ['network', 'web-browser'],
        'icon': 'chromium',
        'developer': 'Chromium Project',
    },
    'microsoft-edge': {
        'name': 'Microsoft Edge',
        'summary': 'Navegador web da Microsoft',
        'categories': ['network', 'web-browser'],
        'icon': 'microsoft-edge',
        'developer': 'Microsoft',
    },
    'opera': {
        'name': 'Opera',
        'summary': 'Navegador web rápido com VPN',
        'categories': ['network', 'web-browser'],
        'icon': 'opera',
        'developer': 'Opera',
    },
    'vivaldi': {
        'name': 'Vivaldi',
        'summary': 'Navegador personalizável',
        'categories': ['network', 'web-browser'],
        'icon': 'vivaldi',
        'developer': 'Vivaldi',
    },
    
    # Graphics
    'gimp': {
        'name': 'GIMP',
        'summary': 'Editor de imagens profissional',
        'categories': ['graphics', 'editor'],
        'icon': 'gimp',
        'developer': 'GIMP Team',
    },
    'inkscape': {
        'name': 'Inkscape',
        'summary': 'Editor de gráficos vetoriais',
        'categories': ['graphics', 'editor'],
        'icon': 'inkscape',
        'developer': 'Inkscape Project',
    },
    'blender': {
        'name': 'Blender',
        'summary': 'Suite 3D completa e gratuita',
        'categories': ['graphics', '3d'],
        'icon': 'blender',
        'developer': 'Blender Foundation',
    },
    'krita': {
        'name': 'Krita',
        'summary': 'Pintura digital e ilustração',
        'categories': ['graphics', 'editor'],
        'icon': 'krita',
        'developer': 'KDE',
    },
    'darktable': {
        'name': 'darktable',
        'summary': 'Editor de fotos RAW',
        'categories': ['graphics', 'photo'],
        'icon': 'darktable',
        'developer': 'darktable',
    },
    'rawtherapee': {
        'name': 'RawTherapee',
        'summary': 'Processamento de fotos RAW',
        'categories': ['graphics', 'photo'],
        'icon': 'rawtherapee',
        'developer': 'RawTherapee',
    },
    
    # Media Players
    'vlc': {
        'name': 'VLC Media Player',
        'summary': 'Reprodutor multimídia universal',
        'categories': ['audio-video', 'player'],
        'icon': 'vlc',
        'developer': 'VideoLAN',
    },
    'mpv': {
        'name': 'mpv',
        'summary': 'Reprodutor de mídia minimalista',
        'categories': ['audio-video', 'player'],
        'icon': 'mpv',
        'developer': 'mpv.io',
    },
    'smplayer': {
        'name': 'SMPlayer',
        'summary': 'Reprodutor de mídia com codecs',
        'categories': ['audio-video', 'player'],
        'icon': 'smplayer',
        'developer': 'SMPlayer',
    },
    
    # Development
    'code': {
        'name': 'VS Code',
        'summary': 'Editor de código da Microsoft',
        'categories': ['development', 'editor'],
        'icon': 'vscode',
        'developer': 'Microsoft',
    },
    'sublime-text': {
        'name': 'Sublime Text',
        'summary': 'Editor de texto sofisticado',
        'categories': ['development', 'editor'],
        'icon': 'sublime-text',
        'developer': 'Sublime HQ',
    },
    'atom': {
        'name': 'Atom',
        'summary': 'Editor de texto hackeável',
        'categories': ['development', 'editor'],
        'icon': 'atom',
        'developer': 'GitHub',
    },
    'android-studio': {
        'name': 'Android Studio',
        'summary': 'IDE para desenvolvimento Android',
        'categories': ['development', 'ide'],
        'icon': 'android-studio',
        'developer': 'Google',
    },
    'pycharm': {
        'name': 'PyCharm',
        'summary': 'IDE para Python',
        'categories': ['development', 'ide'],
        'icon': 'pycharm',
        'developer': 'JetBrains',
    },
    'intellij-idea': {
        'name': 'IntelliJ IDEA',
        'summary': 'IDE para Java e Kotlin',
        'categories': ['development', 'ide'],
        'icon': 'intellij-idea',
        'developer': 'JetBrains',
    },
    'gitkraken': {
        'name': 'GitKraken',
        'summary': 'Cliente Git visual',
        'categories': ['development', 'vcs'],
        'icon': 'gitkraken',
        'developer': 'Axosoft',
    },
    'github-desktop': {
        'name': 'GitHub Desktop',
        'summary': 'Cliente Git do GitHub',
        'categories': ['development', 'vcs'],
        'icon': 'github-desktop',
        'developer': 'GitHub',
    },
    
    # Communication
    'discord': {
        'name': 'Discord',
        'summary': 'Chat para comunidades e gamers',
        'categories': ['network', 'chat'],
        'icon': 'discord',
        'developer': 'Discord Inc.',
    },
    'telegram': {
        'name': 'Telegram',
        'summary': 'Mensageiro rápido e seguro',
        'categories': ['network', 'chat'],
        'icon': 'telegram',
        'developer': 'Telegram',
    },
    'slack': {
        'name': 'Slack',
        'summary': 'Comunicação para equipes',
        'categories': ['network', 'chat'],
        'icon': 'slack',
        'developer': 'Slack Technologies',
    },
    'skype': {
        'name': 'Skype',
        'summary': 'Chamadas e mensagens',
        'categories': ['network', 'chat'],
        'icon': 'skype',
        'developer': 'Microsoft',
    },
    'zoom': {
        'name': 'Zoom',
        'summary': 'Videoconferência',
        'categories': ['network', 'chat'],
        'icon': 'zoom',
        'developer': 'Zoom Video',
    },
    'teams': {
        'name': 'Microsoft Teams',
        'summary': 'Colaboração e videoconferência',
        'categories': ['network', 'chat'],
        'icon': 'teams',
        'developer': 'Microsoft',
    },
    'whatsapp': {
        'name': 'WhatsApp',
        'summary': 'Mensagens e chamadas',
        'categories': ['network', 'chat'],
        'icon': 'whatsapp',
        'developer': 'Meta',
    },
    'signal': {
        'name': 'Signal',
        'summary': 'Mensageiro privado',
        'categories': ['network', 'chat'],
        'icon': 'signal',
        'developer': 'Signal',
    },
    'element': {
        'name': 'Element',
        'summary': 'Cliente Matrix',
        'categories': ['network', 'chat'],
        'icon': 'element',
        'developer': 'Element',
    },
    
    # Music & Audio
    'spotify': {
        'name': 'Spotify',
        'summary': 'Streaming de música',
        'categories': ['audio-video', 'music'],
        'icon': 'spotify',
        'developer': 'Spotify AB',
    },
    'audacity': {
        'name': 'Audacity',
        'summary': 'Editor de áudio gratuito',
        'categories': ['audio-video', 'editor'],
        'icon': 'audacity',
        'developer': 'Audacity Team',
    },
    'rhythmbox': {
        'name': 'Rhythmbox',
        'summary': 'Player de música do GNOME',
        'categories': ['audio-video', 'music'],
        'icon': 'rhythmbox',
        'developer': 'GNOME',
    },
    'lollypop': {
        'name': 'Lollypop',
        'summary': 'Player de música moderno',
        'categories': ['audio-video', 'music'],
        'icon': 'lollypop',
        'developer': 'Lollypop',
    },
    
    # Games
    'steam': {
        'name': 'Steam',
        'summary': 'Plataforma de jogos',
        'categories': ['games', 'platform'],
        'icon': 'steam',
        'developer': 'Valve',
    },
    'lutris': {
        'name': 'Lutris',
        'summary': 'Gerenciador de jogos',
        'categories': ['games', 'platform'],
        'icon': 'lutris',
        'developer': 'Lutris',
    },
    'heroic': {
        'name': 'Heroic Games Launcher',
        'summary': 'Launcher para Epic Games',
        'categories': ['games', 'platform'],
        'icon': 'heroic',
        'developer': 'Heroic',
    },
    'prismlauncher': {
        'name': 'Prism Launcher',
        'summary': 'Launcher para Minecraft',
        'categories': ['games', 'platform'],
        'icon': 'prismlauncher',
        'developer': 'Prism',
    },
    'minecraft': {
        'name': 'Minecraft',
        'summary': 'Jogo de construção',
        'categories': ['games', 'sandbox'],
        'icon': 'minecraft',
        'developer': 'Mojang',
    },
    
    # Office
    'libreoffice': {
        'name': 'LibreOffice',
        'summary': 'Suite de escritório completa',
        'categories': ['office', 'suite'],
        'icon': 'libreoffice-main',
        'developer': 'The Document Foundation',
    },
    'onlyoffice': {
        'name': 'ONLYOFFICE',
        'summary': 'Suite de escritório moderna',
        'categories': ['office', 'suite'],
        'icon': 'onlyoffice',
        'developer': 'Ascensio System',
    },
    'obsidian': {
        'name': 'Obsidian',
        'summary': 'Aplicativo de notas',
        'categories': ['office', 'notes'],
        'icon': 'obsidian',
        'developer': 'Obsidian',
    },
    'notion': {
        'name': 'Notion',
        'summary': 'Workspace all-in-one',
        'categories': ['office', 'productivity'],
        'icon': 'notion',
        'developer': 'Notion Labs',
    },
    'joplin': {
        'name': 'Joplin',
        'summary': 'Aplicativo de notas open source',
        'categories': ['office', 'notes'],
        'icon': 'joplin',
        'developer': 'Joplin',
    },
    
    # Video & Streaming
    'obs-studio': {
        'name': 'OBS Studio',
        'summary': 'Gravação e streaming',
        'categories': ['audio-video', 'streaming'],
        'icon': 'obs',
        'developer': 'OBS Project',
    },
    'kdenlive': {
        'name': 'Kdenlive',
        'summary': 'Editor de vídeo gratuito',
        'categories': ['audio-video', 'editor'],
        'icon': 'kdenlive',
        'developer': 'KDE',
    },
    'shotcut': {
        'name': 'Shotcut',
        'summary': 'Editor de vídeo',
        'categories': ['audio-video', 'editor'],
        'icon': 'shotcut',
        'developer': 'Shotcut',
    },
    'openshot': {
        'name': 'OpenShot',
        'summary': 'Editor de vídeo fácil',
        'categories': ['audio-video', 'editor'],
        'icon': 'openshot',
        'developer': 'OpenShot',
    },
    
    # Download
    'qbittorrent': {
        'name': 'qBittorrent',
        'summary': 'Cliente BitTorrent avançado',
        'categories': ['network', 'download'],
        'icon': 'qbittorrent',
        'developer': 'qBittorrent',
    },
    'transmission': {
        'name': 'Transmission',
        'summary': 'Cliente BitTorrent leve',
        'categories': ['network', 'download'],
        'icon': 'transmission',
        'developer': 'Transmission',
    },
    'aria2': {
        'name': 'aria2',
        'summary': 'Download utility',
        'categories': ['network', 'download'],
        'icon': 'download',
        'developer': 'aria2',
    },
    'xdman': {
        'name': 'Xtreme Download Manager',
        'summary': 'Gerenciador de downloads',
        'categories': ['network', 'download'],
        'icon': 'xdman',
        'developer': 'XDM',
    },
    
    # Security & Password
    'bitwarden': {
        'name': 'Bitwarden',
        'summary': 'Gerenciador de senhas',
        'categories': ['utilities', 'security'],
        'icon': 'bitwarden',
        'developer': 'Bitwarden Inc.',
    },
    'keepassxc': {
        'name': 'KeePassXC',
        'summary': 'Gerenciador de senhas offline',
        'categories': ['utilities', 'security'],
        'icon': 'keepassxc',
        'developer': 'KeePassXC Team',
    },
    'veracrypt': {
        'name': 'VeraCrypt',
        'summary': 'Criptografia de disco',
        'categories': ['utilities', 'security'],
        'icon': 'veracrypt',
        'developer': 'VeraCrypt',
    },
    
    # Remote Desktop
    'anydesk': {
        'name': 'AnyDesk',
        'summary': 'Acesso remoto rápido',
        'categories': ['network', 'remote'],
        'icon': 'anydesk',
        'developer': 'AnyDesk',
    },
    'teamviewer': {
        'name': 'TeamViewer',
        'summary': 'Controle remoto',
        'categories': ['network', 'remote'],
        'icon': 'teamviewer',
        'developer': 'TeamViewer',
    },
    'remmina': {
        'name': 'Remmina',
        'summary': 'Cliente de desktop remoto',
        'categories': ['network', 'remote'],
        'icon': 'remmina',
        'developer': 'Remmina',
    },
    'rustdesk': {
        'name': 'RustDesk',
        'summary': 'Acesso remoto open source',
        'categories': ['network', 'remote'],
        'icon': 'rustdesk',
        'developer': 'RustDesk',
    },
    
    # System Tools
    'timeshift': {
        'name': 'Timeshift',
        'summary': 'Backup e restore do sistema',
        'categories': ['system', 'backup'],
        'icon': 'timeshift',
        'developer': 'Tony George',
    },
    'stacer': {
        'name': 'Stacer',
        'summary': 'Otimizador de sistema',
        'categories': ['system', 'utilities'],
        'icon': 'stacer',
        'developer': 'Oguzhan Ince',
    },
    'bleachbit': {
        'name': 'BleachBit',
        'summary': 'Limpeza de disco',
        'categories': ['system', 'utilities'],
        'icon': 'bleachbit',
        'developer': 'BleachBit',
    },
    'gparted': {
        'name': 'GParted',
        'summary': 'Editor de partições',
        'categories': ['system', 'utilities'],
        'icon': 'gparted',
        'developer': 'GParted',
    },
    'baobab': {
        'name': 'Disk Usage Analyzer',
        'summary': 'Analisador de uso de disco',
        'categories': ['system', 'utilities'],
        'icon': 'baobab',
        'developer': 'GNOME',
    },
    
    # DevOps
    'docker': {
        'name': 'Docker Desktop',
        'summary': 'Plataforma de containers',
        'categories': ['development', 'devops'],
        'icon': 'docker',
        'developer': 'Docker Inc.',
    },
    'postman': {
        'name': 'Postman',
        'summary': 'Plataforma de API',
        'categories': ['development', 'api'],
        'icon': 'postman',
        'developer': 'Postman Inc.',
    },
    'insomnia': {
        'name': 'Insomnia',
        'summary': 'Cliente REST API',
        'categories': ['development', 'api'],
        'icon': 'insomnia',
        'developer': 'Insomnia',
    },
    'virt-manager': {
        'name': 'Virtual Machine Manager',
        'summary': 'Gerenciador de VMs',
        'categories': ['system', 'virtualization'],
        'icon': 'virt-manager',
        'developer': 'virt-manager',
    },
    'virtualbox': {
        'name': 'VirtualBox',
        'summary': 'Virtualização',
        'categories': ['system', 'virtualization'],
        'icon': 'virtualbox',
        'developer': 'Oracle',
    },
    
    # Email
    'thunderbird': {
        'name': 'Thunderbird',
        'summary': 'Cliente de email',
        'categories': ['network', 'email'],
        'icon': 'thunderbird',
        'developer': 'Mozilla',
    },
    ' mailspring': {
        'name': 'Mailspring',
        'summary': 'Cliente de email moderno',
        'categories': ['network', 'email'],
        'icon': 'mailspring',
        'developer': 'Mailspring',
    },
    'geary': {
        'name': 'Geary',
        'summary': 'Cliente de email do GNOME',
        'categories': ['network', 'email'],
        'icon': 'geary',
        'developer': 'GNOME',
    },
    
    # File Managers
    'nautilus': {
        'name': 'Files',
        'summary': 'Gerenciador de arquivos do GNOME',
        'categories': ['system', 'file-manager'],
        'icon': 'system-file-manager',
        'developer': 'GNOME',
    },
    'dolphin': {
        'name': 'Dolphin',
        'summary': 'Gerenciador de arquivos do KDE',
        'categories': ['system', 'file-manager'],
        'icon': 'system-file-manager',
        'developer': 'KDE',
    },
    'thunar': {
        'name': 'Thunar',
        'summary': 'Gerenciador de arquivos do Xfce',
        'categories': ['system', 'file-manager'],
        'icon': 'system-file-manager',
        'developer': 'Xfce',
    },
    'nemo': {
        'name': 'Nemo',
        'summary': 'Gerenciador de arquivos do Cinnamon',
        'categories': ['system', 'file-manager'],
        'icon': 'system-file-manager',
        'developer': 'Cinnamon',
    },
    
    # Terminals
    'gnome-terminal': {
        'name': 'Terminal',
        'summary': 'Terminal do GNOME',
        'categories': ['system', 'terminal'],
        'icon': 'utilities-terminal',
        'developer': 'GNOME',
    },
    'konsole': {
        'name': 'Konsole',
        'summary': 'Terminal do KDE',
        'categories': ['system', 'terminal'],
        'icon': 'utilities-terminal',
        'developer': 'KDE',
    },
    'alacritty': {
        'name': 'Alacritty',
        'summary': 'Terminal acelerado por GPU',
        'categories': ['system', 'terminal'],
        'icon': 'utilities-terminal',
        'developer': 'Alacritty',
    },
    'kitty': {
        'name': 'Kitty',
        'summary': 'Terminal moderno com GPU',
        'categories': ['system', 'terminal'],
        'icon': 'utilities-terminal',
        'developer': 'Kovid Goyal',
    },
    'tilix': {
        'name': 'Tilix',
        'summary': 'Terminal em tiles',
        'categories': ['system', 'terminal'],
        'icon': 'utilities-terminal',
        'developer': 'Tilix',
    },
    
    # Archive
    'filezilla': {
        'name': 'FileZilla',
        'summary': 'Cliente FTP',
        'categories': ['network', 'ftp'],
        'icon': 'filezilla',
        'developer': 'FileZilla',
    },
    'peazip': {
        'name': 'PeaZip',
        'summary': 'Gerenciador de arquivos compactados',
        'categories': ['utilities', 'archive'],
        'icon': 'peazip',
        'developer': 'PeaZip',
    },
    '7zip': {
        'name': '7-Zip',
        'summary': 'Compactador de arquivos',
        'categories': ['utilities', 'archive'],
        'icon': 'package-x-generic',
        'developer': '7-Zip',
    },
    
    # Notes & Text
    'gedit': {
        'name': 'Text Editor',
        'summary': 'Editor de texto do GNOME',
        'categories': ['utilities', 'editor'],
        'icon': 'text-editor',
        'developer': 'GNOME',
    },
    'mousepad': {
        'name': 'Mousepad',
        'summary': 'Editor de texto simples',
        'categories': ['utilities', 'editor'],
        'icon': 'text-editor',
        'developer': 'Xfce',
    },
    'kate': {
        'name': 'Kate',
        'summary': 'Editor de texto avançado',
        'categories': ['utilities', 'editor'],
        'icon': 'kate',
        'developer': 'KDE',
    },
}

# Package name mappings across sources
PACKAGE_IDS = {
    'firefox': {
        'flatpak': 'org.mozilla.firefox',
        'snap': 'firefox',
        'aur': 'firefox',
        'native': 'firefox',
    },
    'google-chrome': {
        'flatpak': 'com.google.Chrome',
        'snap': 'google-chrome',
        'aur': 'google-chrome',
        'native': None,
    },
    'brave': {
        'flatpak': 'com.brave.Browser',
        'snap': 'brave',
        'aur': 'brave-bin',
        'native': None,
    },
    'chromium': {
        'flatpak': 'org.chromium.Chromium',
        'snap': 'chromium',
        'aur': 'chromium',
        'native': 'chromium',
    },
    'microsoft-edge': {
        'flatpak': 'com.microsoft.Edge',
        'snap': 'microsoft-edge',
        'aur': 'microsoft-edge-stable-bin',
        'native': None,
    },
    'opera': {
        'flatpak': 'com.opera.Opera',
        'snap': 'opera',
        'aur': 'opera',
        'native': None,
    },
    'vivaldi': {
        'flatpak': 'com.vivaldi.Vivaldi',
        'snap': 'vivaldi',
        'aur': 'vivaldi',
        'native': None,
    },
    'gimp': {
        'flatpak': 'org.gimp.GIMP',
        'snap': 'gimp',
        'aur': 'gimp',
        'native': 'gimp',
    },
    'inkscape': {
        'flatpak': 'org.inkscape.Inkscape',
        'snap': 'inkscape',
        'aur': 'inkscape',
        'native': 'inkscape',
    },
    'blender': {
        'flatpak': 'org.blender.Blender',
        'snap': 'blender',
        'aur': 'blender',
        'native': 'blender',
    },
    'krita': {
        'flatpak': 'org.kde.krita',
        'snap': 'krita',
        'aur': 'krita',
        'native': 'krita',
    },
    'vlc': {
        'flatpak': 'org.videolan.VLC',
        'snap': 'vlc',
        'aur': 'vlc',
        'native': 'vlc',
    },
    'mpv': {
        'flatpak': 'io.mpv.Mpv',
        'snap': 'mpv',
        'aur': 'mpv',
        'native': 'mpv',
    },
    'code': {
        'flatpak': 'com.visualstudio.code',
        'snap': 'code',
        'aur': 'visual-studio-code-bin',
        'native': None,
    },
    'sublime-text': {
        'flatpak': 'com.sublimetext.three',
        'snap': 'sublime-text',
        'aur': 'sublime-text-4',
        'native': None,
    },
    'android-studio': {
        'flatpak': 'com.google.AndroidStudio',
        'snap': 'android-studio',
        'aur': 'android-studio',
        'native': None,
    },
    'pycharm': {
        'flatpak': 'com.jetbrains.PyCharm-Community',
        'snap': 'pycharm-community',
        'aur': 'pycharm-community-edition',
        'native': None,
    },
    'discord': {
        'flatpak': 'com.discordapp.Discord',
        'snap': 'discord',
        'aur': 'discord',
        'native': None,
    },
    'telegram': {
        'flatpak': 'org.telegram.desktop',
        'snap': 'telegram-desktop',
        'aur': 'telegram-desktop',
        'native': 'telegram-desktop',
    },
    'slack': {
        'flatpak': 'com.slack.Slack',
        'snap': 'slack',
        'aur': 'slack-desktop',
        'native': None,
    },
    'skype': {
        'flatpak': 'com.skype.Client',
        'snap': 'skype',
        'aur': 'skypeforlinux-stable-bin',
        'native': None,
    },
    'zoom': {
        'flatpak': 'us.zoom.Zoom',
        'snap': 'zoom-client',
        'aur': 'zoom',
        'native': None,
    },
    'spotify': {
        'flatpak': 'com.spotify.Client',
        'snap': 'spotify',
        'aur': 'spotify',
        'native': None,
    },
    'steam': {
        'flatpak': 'com.valvesoftware.Steam',
        'snap': 'steam',
        'aur': 'steam',
        'native': 'steam',
    },
    'lutris': {
        'flatpak': 'net.lutris.Lutris',
        'snap': 'lutris',
        'aur': 'lutris',
        'native': 'lutris',
    },
    'heroic': {
        'flatpak': 'com.heroicgameslauncher.hgl',
        'snap': 'heroic',
        'aur': 'heroic-games-launcher-bin',
        'native': None,
    },
    'libreoffice': {
        'flatpak': 'org.libreoffice.LibreOffice',
        'snap': 'libreoffice',
        'aur': 'libreoffice-fresh',
        'native': 'libreoffice',
    },
    'obs-studio': {
        'flatpak': 'com.obsproject.Studio',
        'snap': 'obs-studio',
        'aur': 'obs-studio',
        'native': 'obs-studio',
    },
    'kdenlive': {
        'flatpak': 'org.kde.kdenlive',
        'snap': 'kdenlive',
        'aur': 'kdenlive',
        'native': 'kdenlive',
    },
    'audacity': {
        'flatpak': 'org.audacityteam.Audacity',
        'snap': 'audacity',
        'aur': 'audacity',
        'native': 'audacity',
    },
    'bitwarden': {
        'flatpak': 'com.bitwarden.desktop',
        'snap': 'bitwarden',
        'aur': 'bitwarden',
        'native': None,
    },
    'keepassxc': {
        'flatpak': 'org.keepassxc.KeePassXC',
        'snap': 'keepassxc',
        'aur': 'keepassxc',
        'native': 'keepassxc',
    },
    'anydesk': {
        'flatpak': None,
        'snap': 'anydesk',
        'aur': 'anydesk',
        'native': 'anydesk',
    },
    'teamviewer': {
        'flatpak': 'com.teamviewer.TeamViewer',
        'snap': 'teamviewer',
        'aur': 'teamviewer',
        'native': None,
    },
    'remmina': {
        'flatpak': 'org.remmina.Remmina',
        'snap': 'remmina',
        'aur': 'remmina',
        'native': 'remmina',
    },
    'rustdesk': {
        'flatpak': None,
        'snap': 'rustdesk',
        'aur': 'rustdesk',
        'native': None,
    },
    'postman': {
        'flatpak': 'com.getpostman.Postman',
        'snap': 'postman',
        'aur': 'postman-bin',
        'native': None,
    },
    'thunderbird': {
        'flatpak': 'org.mozilla.Thunderbird',
        'snap': 'thunderbird',
        'aur': 'thunderbird',
        'native': 'thunderbird',
    },
    'qbittorrent': {
        'flatpak': 'org.qbittorrent.qBittorrent',
        'snap': 'qbittorrent',
        'aur': 'qbittorrent',
        'native': 'qbittorrent',
    },
    'transmission': {
        'flatpak': 'com.transmissionbt.Transmission',
        'snap': 'transmission',
        'aur': 'transmission-gtk',
        'native': 'transmission-gtk',
    },
    'virt-manager': {
        'flatpak': 'org.virt_manager.virt-manager',
        'snap': None,
        'aur': 'virt-manager',
        'native': 'virt-manager',
    },
    'virtualbox': {
        'flatpak': None,
        'snap': 'virtualbox',
        'aur': 'virtualbox',
        'native': 'virtualbox',
    },
    'timeshift': {
        'flatpak': None,
        'snap': 'timeshift',
        'aur': 'timeshift',
        'native': 'timeshift',
    },
    'obsidian': {
        'flatpak': 'md.obsidian.Obsidian',
        'snap': 'obsidian',
        'aur': 'obsidian-appimage',
        'native': None,
    },
    'notion': {
        'flatpak': None,
        'snap': 'notion-snap',
        'aur': 'notion-app',
        'native': None,
    },
    'filezilla': {
        'flatpak': 'org.filezillaproject.Filezilla',
        'snap': 'filezilla',
        'aur': 'filezilla',
        'native': 'filezilla',
    },
    'signal': {
        'flatpak': 'org.signal.Signal',
        'snap': 'signal-desktop',
        'aur': 'signal-desktop',
        'native': None,
    },
    'element': {
        'flatpak': 'im.riot.Riot',
        'snap': 'element-desktop',
        'aur': 'element-desktop',
        'native': None,
    },
    'whatsapp': {
        'flatpak': 'io.github.mimbrero.WhatsAppDesktop',
        'snap': 'whatsapp',
        'aur': 'whatsapp-nativefier',
        'native': None,
    },
    'darktable': {
        'flatpak': 'org.darktable.Darktable',
        'snap': 'darktable',
        'aur': 'darktable',
        'native': 'darktable',
    },
    'shotcut': {
        'flatpak': 'org.shotcut.Shotcut',
        'snap': 'shotcut',
        'aur': 'shotcut',
        'native': None,
    },
}

def get_popular_app_keys():
    return list(POPULAR_APPS.keys())

def get_app_metadata(key):
    return POPULAR_APPS.get(key)

def get_package_id(key, source):
    if key in PACKAGE_IDS:
        return PACKAGE_IDS[key].get(source)
    return None

def search_popular_apps(query):
    """Search popular apps by name"""
    results = []
    query_lower = query.lower()
    
    for key, info in POPULAR_APPS.items():
        name = info.get('name', '').lower()
        summary = info.get('summary', '').lower()
        
        if query_lower in key or query_lower in name or query_lower in summary:
            results.append((key, info))
            
    return results

def get_apps_by_category(category):
    """Get apps by category"""
    results = []
    
    for key, info in POPULAR_APPS.items():
        if category in info.get('categories', []):
            results.append((key, info))
            
    return results
