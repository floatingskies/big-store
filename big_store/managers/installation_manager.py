"""
Big Store - Installation Manager
Handles real package installation with progress and authentication
"""

import subprocess
import os
import re
import threading
from typing import Callable, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class InstallStatus(Enum):
    PREPARING = "preparing"
    DOWNLOADING = "downloading"
    INSTALLING = "installing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class InstallProgress:
    """Installation progress data"""
    status: InstallStatus
    message: str
    percentage: int = 0
    details: str = ""


class InstallationManager:
    """Manages package installation with real progress"""
    
    def __init__(self):
        self._cancel_requested = False
        
    def install_package(
        self,
        pkg_id: str,
        source: str,
        progress_callback: Callable[[InstallProgress], None] = None,
        complete_callback: Callable[[bool, str], None] = None
    ):
        """Install a package with progress tracking"""
        self._cancel_requested = False
        
        def _install():
            try:
                if source == 'flatpak':
                    success, message = self._install_flatpak(pkg_id, progress_callback)
                elif source == 'snap':
                    success, message = self._install_snap(pkg_id, progress_callback)
                elif source == 'aur':
                    success, message = self._install_aur(pkg_id, progress_callback)
                elif source == 'native':
                    success, message = self._install_native(pkg_id, progress_callback)
                else:
                    success, message = False, f"Unknown source: {source}"
                    
                if complete_callback:
                    complete_callback(success, message)
                    
            except Exception as e:
                if complete_callback:
                    complete_callback(False, str(e))
                    
        thread = threading.Thread(target=_install, daemon=True)
        thread.start()
        
    def cancel(self):
        """Cancel ongoing installation"""
        self._cancel_requested = True
        
    def _install_flatpak(
        self,
        app_id: str,
        progress_callback: Callable[[InstallProgress], None]
    ) -> Tuple[bool, str]:
        """Install Flatpak with progress"""
        
        # Report preparing
        if progress_callback:
            progress_callback(InstallProgress(
                status=InstallStatus.PREPARING,
                message=f"Preparando instalação de {app_id}...",
                percentage=0
            ))
            
        try:
            # Run flatpak install with progress
            process = subprocess.Popen(
                ['flatpak', 'install', '--user', '-y', 'flathub', app_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            output_lines = []
            percentage = 0
            
            for line in process.stdout:
                if self._cancel_requested:
                    process.terminate()
                    return False, "Installation cancelled"
                    
                output_lines.append(line)
                
                # Parse progress from flatpak output
                if 'Downloading' in line or 'fetching' in line.lower():
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.DOWNLOADING,
                            message="Baixando pacote...",
                            percentage=min(percentage + 5, 50),
                            details=line.strip()
                        ))
                elif 'Installing' in line or 'installing' in line.lower():
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.INSTALLING,
                            message="Instalando...",
                            percentage=min(percentage + 10, 90),
                            details=line.strip()
                        ))
                        
            process.wait()
            output = ''.join(output_lines)
            
            if process.returncode == 0:
                if progress_callback:
                    progress_callback(InstallProgress(
                        status=InstallStatus.COMPLETED,
                        message="Instalação concluída!",
                        percentage=100
                    ))
                return True, "Instalação concluída com sucesso"
            else:
                if progress_callback:
                    progress_callback(InstallProgress(
                        status=InstallStatus.FAILED,
                        message="Falha na instalação",
                        details=output[-500:]  # Last 500 chars
                    ))
                return False, output[-1000:]
                
        except Exception as e:
            if progress_callback:
                progress_callback(InstallProgress(
                    status=InstallStatus.FAILED,
                    message=f"Erro: {str(e)}"
                ))
            return False, str(e)
            
    def _install_snap(
        self,
        snap_name: str,
        progress_callback: Callable[[InstallProgress], None]
    ) -> Tuple[bool, str]:
        """Install Snap with progress"""
        
        if progress_callback:
            progress_callback(InstallProgress(
                status=InstallStatus.PREPARING,
                message=f"Preparando instalação de {snap_name}...",
                percentage=0
            ))
            
        try:
            # Use pkexec for sudo authentication
            process = subprocess.Popen(
                ['pkexec', 'snap', 'install', snap_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            output_lines = []
            
            for line in process.stdout:
                if self._cancel_requested:
                    process.terminate()
                    return False, "Installation cancelled"
                    
                output_lines.append(line)
                
                if 'download' in line.lower():
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.DOWNLOADING,
                            message="Baixando snap...",
                            percentage=30,
                            details=line.strip()
                        ))
                elif 'install' in line.lower():
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.INSTALLING,
                            message="Instalando snap...",
                            percentage=70,
                            details=line.strip()
                        ))
                        
            process.wait()
            output = ''.join(output_lines)
            
            if process.returncode == 0:
                if progress_callback:
                    progress_callback(InstallProgress(
                        status=InstallStatus.COMPLETED,
                        message="Instalação concluída!",
                        percentage=100
                    ))
                return True, "Instalação concluída com sucesso"
            else:
                if progress_callback:
                    progress_callback(InstallProgress(
                        status=InstallStatus.FAILED,
                        message="Falha na instalação",
                        details=output[-500:]
                    ))
                return False, output[-1000:]
                
        except Exception as e:
            if progress_callback:
                progress_callback(InstallProgress(
                    status=InstallStatus.FAILED,
                    message=f"Erro: {str(e)}"
                ))
            return False, str(e)
            
    def _install_aur(
        self,
        pkg_name: str,
        progress_callback: Callable[[InstallProgress], None]
    ) -> Tuple[bool, str]:
        """Install AUR package with progress"""
        
        if progress_callback:
            progress_callback(InstallProgress(
                status=InstallStatus.PREPARING,
                message=f"Preparando instalação de {pkg_name}...",
                percentage=0
            ))
            
        # Find AUR helper
        helper = None
        for h in ['paru', 'yay', 'pamac']:
            try:
                subprocess.run(['which', h], capture_output=True, timeout=5)
                helper = h
                break
            except Exception:
                continue
                
        if not helper:
            if progress_callback:
                progress_callback(InstallProgress(
                    status=InstallStatus.FAILED,
                    message="Nenhum AUR helper encontrado (paru, yay, pamac)"
                ))
            return False, "No AUR helper found"
            
        try:
            if helper == 'pamac':
                cmd = ['pamac', 'build', '--no-confirm', pkg_name]
            elif helper == 'paru':
                cmd = ['paru', '-S', '--noconfirm', '--needed', pkg_name]
            else:  # yay
                cmd = ['yay', '-S', '--noconfirm', '--needed', pkg_name]
                
            if progress_callback:
                progress_callback(InstallProgress(
                    status=InstallStatus.DOWNLOADING,
                    message="Buscando pacote AUR...",
                    percentage=10
                ))
                
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            output_lines = []
            stage = "preparing"
            
            for line in process.stdout:
                if self._cancel_requested:
                    process.terminate()
                    return False, "Installation cancelled"
                    
                output_lines.append(line)
                line_lower = line.lower()
                
                # Detect stages
                if 'cloning' in line_lower or 'fetching' in line_lower:
                    stage = "downloading"
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.DOWNLOADING,
                            message="Baixando do AUR...",
                            percentage=20,
                            details=line.strip()[:100]
                        ))
                elif 'building' in line_lower or 'making' in line_lower:
                    stage = "building"
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.INSTALLING,
                            message="Compilando pacote...",
                            percentage=50,
                            details=line.strip()[:100]
                        ))
                elif 'installing' in line_lower or 'upgrading' in line_lower:
                    stage = "installing"
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.INSTALLING,
                            message="Instalando pacote...",
                            percentage=80,
                            details=line.strip()[:100]
                        ))
                        
            process.wait()
            output = ''.join(output_lines)
            
            if process.returncode == 0:
                if progress_callback:
                    progress_callback(InstallProgress(
                        status=InstallStatus.COMPLETED,
                        message="Instalação concluída!",
                        percentage=100
                    ))
                return True, "Instalação concluída com sucesso"
            else:
                if progress_callback:
                    progress_callback(InstallProgress(
                        status=InstallStatus.FAILED,
                        message="Falha na instalação",
                        details=output[-500:]
                    ))
                return False, output[-1000:]
                
        except Exception as e:
            if progress_callback:
                progress_callback(InstallProgress(
                    status=InstallStatus.FAILED,
                    message=f"Erro: {str(e)}"
                ))
            return False, str(e)
            
    def _install_native(
        self,
        pkg_name: str,
        progress_callback: Callable[[InstallProgress], None]
    ) -> Tuple[bool, str]:
        """Install native package with progress"""
        
        if progress_callback:
            progress_callback(InstallProgress(
                status=InstallStatus.PREPARING,
                message=f"Preparando instalação de {pkg_name}...",
                percentage=0
            ))
            
        # Detect package manager
        pm = None
        for p in ['pamac', 'pacman', 'apt', 'dnf']:
            try:
                subprocess.run(['which', p], capture_output=True, timeout=5)
                pm = p
                break
            except Exception:
                continue
                
        if not pm:
            if progress_callback:
                progress_callback(InstallProgress(
                    status=InstallStatus.FAILED,
                    message="Nenhum gerenciador de pacotes encontrado"
                ))
            return False, "No package manager found"
            
        try:
            if pm == 'pamac':
                # Pamac handles its own sudo
                cmd = ['pamac', 'install', '--no-confirm', pkg_name]
            elif pm == 'pacman':
                # Use pkexec for sudo
                cmd = ['pkexec', 'pacman', '-S', '--noconfirm', '--needed', pkg_name]
            elif pm == 'apt':
                cmd = ['pkexec', 'apt', 'install', '-y', pkg_name]
            elif pm == 'dnf':
                cmd = ['pkexec', 'dnf', 'install', '-y', pkg_name]
            else:
                return False, f"Unknown package manager: {pm}"
                
            if progress_callback:
                progress_callback(InstallProgress(
                    status=InstallStatus.DOWNLOADING,
                    message="Resolvendo dependências...",
                    percentage=20
                ))
                
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            output_lines = []
            
            for line in process.stdout:
                if self._cancel_requested:
                    process.terminate()
                    return False, "Installation cancelled"
                    
                output_lines.append(line)
                line_lower = line.lower()
                
                if 'downloading' in line_lower or 'fetching' in line_lower:
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.DOWNLOADING,
                            message="Baixando pacotes...",
                            percentage=40,
                            details=line.strip()[:100]
                        ))
                elif 'installing' in line_lower or 'unpacking' in line_lower:
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.INSTALLING,
                            message="Instalando pacotes...",
                            percentage=70,
                            details=line.strip()[:100]
                        ))
                elif 'setting up' in line_lower or 'configuring' in line_lower:
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.INSTALLING,
                            message="Configurando pacotes...",
                            percentage=90,
                            details=line.strip()[:100]
                        ))
                        
            process.wait()
            output = ''.join(output_lines)
            
            if process.returncode == 0:
                if progress_callback:
                    progress_callback(InstallProgress(
                        status=InstallStatus.COMPLETED,
                        message="Instalação concluída!",
                        percentage=100
                    ))
                return True, "Instalação concluída com sucesso"
            else:
                if progress_callback:
                    progress_callback(InstallProgress(
                        status=InstallStatus.FAILED,
                        message="Falha na instalação",
                        details=output[-500:]
                    ))
                return False, output[-1000:]
                
        except Exception as e:
            if progress_callback:
                progress_callback(InstallProgress(
                    status=InstallStatus.FAILED,
                    message=f"Erro: {str(e)}"
                ))
            return False, str(e)
            
    def uninstall_package(
        self,
        pkg_id: str,
        source: str,
        progress_callback: Callable[[InstallProgress], None] = None,
        complete_callback: Callable[[bool, str], None] = None
    ):
        """Uninstall a package"""
        
        def _uninstall():
            try:
                if source == 'flatpak':
                    cmd = ['flatpak', 'uninstall', '-y', pkg_id]
                elif source == 'snap':
                    cmd = ['pkexec', 'snap', 'remove', pkg_id]
                elif source in ('aur', 'native'):
                    # Detect package manager
                    pm = None
                    for p in ['pamac', 'pacman', 'apt', 'dnf']:
                        try:
                            subprocess.run(['which', p], capture_output=True, timeout=5)
                            pm = p
                            break
                        except Exception:
                            continue
                            
                    if pm == 'pamac':
                        cmd = ['pamac', 'remove', '--no-confirm', pkg_id]
                    elif pm == 'pacman':
                        cmd = ['pkexec', 'pacman', '-Rns', '--noconfirm', pkg_id]
                    elif pm == 'apt':
                        cmd = ['pkexec', 'apt', 'remove', '-y', pkg_id]
                    elif pm == 'dnf':
                        cmd = ['pkexec', 'dnf', 'remove', '-y', pkg_id]
                    else:
                        complete_callback(False, "No package manager found")
                        return
                else:
                    complete_callback(False, f"Unknown source: {source}")
                    return
                    
                if progress_callback:
                    progress_callback(InstallProgress(
                        status=InstallStatus.PREPARING,
                        message=f"Removendo {pkg_id}...",
                        percentage=0
                    ))
                    
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                output, _ = process.communicate()
                
                if process.returncode == 0:
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.COMPLETED,
                            message="Remoção concluída!",
                            percentage=100
                        ))
                    if complete_callback:
                        complete_callback(True, "Remoção concluída")
                else:
                    if progress_callback:
                        progress_callback(InstallProgress(
                            status=InstallStatus.FAILED,
                            message="Falha na remoção",
                            details=output[-500:]
                        ))
                    if complete_callback:
                        complete_callback(False, output[-1000:])
                        
            except Exception as e:
                if complete_callback:
                    complete_callback(False, str(e))
                    
        thread = threading.Thread(target=_uninstall, daemon=True)
        thread.start()


# Global instance
installation_manager = InstallationManager()
