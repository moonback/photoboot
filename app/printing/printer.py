"""
Gestionnaire d'impression pour Photobooth
Support Windows-first avec win32print et fallback lpr
"""

import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger
from PIL import Image
import time

try:
    import win32print
    import win32api
    import win32con
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    logger.warning("win32print non disponible - impression Windows désactivée")

try:
    # Test si lpr est disponible
    subprocess.run(["lpr", "--version"], capture_output=True, check=True)
    LPR_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    LPR_AVAILABLE = False
    logger.warning("lpr non disponible - impression Unix désactivée")


class PrinterManager:
    """Gestionnaire d'impression multi-plateforme"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.printing_config = config.get("printing", {})
        self.default_printer = self.printing_config.get("default_printer", "")
        self.paper_size = self.printing_config.get("paper_size", "4x6")
        self.quality = self.printing_config.get("quality", "normal")
        self.max_copies = self.printing_config.get("max_copies", 5)
        self.retry_attempts = self.printing_config.get("retry_attempts", 3)
        self.retry_delay = self.printing_config.get("retry_delay", 2)
        
        # Vérifier la disponibilité des méthodes d'impression
        self._check_printing_availability()
    
    def _check_printing_availability(self):
        """Vérifie la disponibilité des méthodes d'impression"""
        if WINDOWS_AVAILABLE:
            logger.info("Support d'impression Windows activé")
        if LPR_AVAILABLE:
            logger.info("Support d'impression Unix (lpr) activé")
        
        if not WINDOWS_AVAILABLE and not LPR_AVAILABLE:
            logger.warning("Aucune méthode d'impression disponible")
    
    def get_available_printers(self) -> List[Dict[str, str]]:
        """Récupère la liste des imprimantes disponibles"""
        printers = []
        
        if WINDOWS_AVAILABLE:
            try:
                for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
                    printers.append({
                        "name": printer[2],
                        "port": printer[1],
                        "description": printer[3] or "",
                        "platform": "windows"
                    })
                logger.info(f"{len(printers)} imprimantes Windows trouvées")
            except Exception as e:
                logger.error(f"Erreur lors de l'énumération des imprimantes Windows: {e}")
        
        elif LPR_AVAILABLE:
            try:
                # Tentative de récupération des imprimantes via lpr
                result = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('printer'):
                            parts = line.split()
                            if len(parts) >= 2:
                                printers.append({
                                    "name": parts[1],
                                    "port": "unknown",
                                    "description": " ".join(parts[2:]) if len(parts) > 2 else "",
                                    "platform": "unix"
                                })
                    logger.info(f"{len(printers)} imprimantes Unix trouvées")
            except Exception as e:
                logger.error(f"Erreur lors de l'énumération des imprimantes Unix: {e}")
        
        return printers
    
    def get_default_printer(self) -> Optional[str]:
        """Récupère l'imprimante par défaut"""
        if WINDOWS_AVAILABLE:
            try:
                return win32print.GetDefaultPrinter()
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de l'imprimante par défaut: {e}")
        
        return self.default_printer or None
    
    def print_photo(self, image_path: str, copies: int = 1, printer_name: Optional[str] = None) -> Dict[str, any]:
        """Imprime une photo avec gestion des erreurs et retry"""
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": "Fichier image introuvable",
                "details": f"Chemin: {image_path}"
            }
        
        # Validation du nombre de copies
        if copies < 1 or copies > self.max_copies:
            return {
                "success": False,
                "error": "Nombre de copies invalide",
                "details": f"Copies: {copies}, Max: {self.max_copies}"
            }
        
        # Préparation de l'image pour l'impression
        prepared_image = self._prepare_image_for_printing(image_path)
        if not prepared_image:
            return {
                "success": False,
                "error": "Impossible de préparer l'image pour l'impression"
            }
        
        # Tentatives d'impression avec retry
        for attempt in range(self.retry_attempts):
            try:
                if WINDOWS_AVAILABLE:
                    result = self._print_windows(prepared_image, copies, printer_name)
                elif LPR_AVAILABLE:
                    result = self._print_unix(prepared_image, copies, printer_name)
                else:
                    return {
                        "success": False,
                        "error": "Aucune méthode d'impression disponible"
                    }
                
                if result["success"]:
                    logger.info(f"Impression réussie: {image_path}, {copies} copie(s)")
                    return result
                
                # Si échec, attendre avant de réessayer
                if attempt < self.retry_attempts - 1:
                    logger.warning(f"Tentative {attempt + 1} échouée, nouvelle tentative dans {self.retry_delay}s")
                    time.sleep(self.retry_delay)
                
            except Exception as e:
                logger.error(f"Erreur lors de la tentative {attempt + 1}: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
        
        # Nettoyage du fichier temporaire
        if prepared_image != image_path:
            try:
                os.remove(prepared_image)
            except:
                pass
        
        return {
            "success": False,
            "error": "Échec de l'impression après toutes les tentatives",
            "details": f"Tentatives: {self.retry_attempts}"
        }
    
    def _prepare_image_for_printing(self, image_path: str) -> Optional[str]:
        """Prépare l'image pour l'impression (redimensionnement, format)"""
        try:
            with Image.open(image_path) as img:
                # Conversion en RGB si nécessaire
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionnement selon le format papier
                target_size = self._get_paper_dimensions()
                if target_size:
                    img.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                # Sauvegarde temporaire si modifications
                if img.size != Image.open(image_path).size or img.mode != Image.open(image_path).mode:
                    temp_path = tempfile.mktemp(suffix='.jpg')
                    img.save(temp_path, 'JPEG', quality=95)
                    return temp_path
                
                return image_path
                
        except Exception as e:
            logger.error(f"Erreur lors de la préparation de l'image: {e}")
            return None
    
    def _get_paper_dimensions(self) -> Optional[Tuple[int, int]]:
        """Récupère les dimensions du papier selon la configuration"""
        paper_sizes = {
            "4x6": (2400, 3600),      # 4x6 pouces à 600 DPI
            "5x7": (3000, 4200),      # 5x7 pouces à 600 DPI
            "6x8": (3600, 4800),      # 6x8 pouces à 600 DPI
            "A4": (4961, 7016),       # A4 à 600 DPI
            "letter": (5100, 6600)    # Letter à 600 DPI
        }
        return paper_sizes.get(self.paper_size)
    
    def _print_windows(self, image_path: str, copies: int, printer_name: Optional[str]) -> Dict[str, any]:
        """Impression sur Windows via win32print"""
        try:
            # Sélection de l'imprimante
            if printer_name:
                win32print.SetDefaultPrinter(printer_name)
            else:
                printer_name = win32print.GetDefaultPrinter()
            
            # Impression via l'API Windows
            win32api.ShellExecute(
                0,
                "print",
                image_path,
                f'"{printer_name}"',
                ".",
                0
            )
            
            return {
                "success": True,
                "printer": printer_name,
                "copies": copies,
                "method": "windows"
            }
            
        except Exception as e:
            logger.error(f"Erreur d'impression Windows: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "windows"
            }
    
    def _print_unix(self, image_path: str, copies: int, printer_name: Optional[str]) -> Dict[str, any]:
        """Impression sur Unix via lpr"""
        try:
            cmd = ["lpr"]
            
            if printer_name:
                cmd.extend(["-P", printer_name])
            
            if copies > 1:
                cmd.extend(["-#", str(copies)])
            
            cmd.append(image_path)
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "printer": printer_name or "default",
                "copies": copies,
                "method": "unix"
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur d'impression Unix: {e}")
            return {
                "success": False,
                "error": e.stderr or str(e),
                "method": "unix"
            }
        except Exception as e:
            logger.error(f"Erreur d'impression Unix: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "unix"
            }
    
    def get_printer_status(self, printer_name: Optional[str] = None) -> Dict[str, any]:
        """Récupère le statut de l'imprimante"""
        if not printer_name:
            printer_name = self.get_default_printer()
        
        if not printer_name:
            return {
                "available": False,
                "error": "Aucune imprimante configurée"
            }
        
        try:
            if WINDOWS_AVAILABLE:
                return self._get_windows_printer_status(printer_name)
            elif LPR_AVAILABLE:
                return self._get_unix_printer_status(printer_name)
            else:
                return {
                    "available": False,
                    "error": "Aucune méthode d'impression disponible"
                }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def _get_windows_printer_status(self, printer_name: str) -> Dict[str, any]:
        """Récupère le statut d'une imprimante Windows"""
        try:
            handle = win32print.OpenPrinter(printer_name)
            info = win32print.GetPrinter(handle, 2)
            win32print.ClosePrinter(handle)
            
            return {
                "available": True,
                "name": printer_name,
                "status": info["Status"],
                "jobs": info["cJobs"],
                "platform": "windows"
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "platform": "windows"
            }
    
    def _get_unix_printer_status(self, printer_name: str) -> Dict[str, any]:
        """Récupère le statut d'une imprimante Unix"""
        try:
            cmd = ["lpstat", "-p", printer_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "available": True,
                    "name": printer_name,
                    "status": "idle",
                    "jobs": 0,
                    "platform": "unix"
                }
            else:
                return {
                    "available": False,
                    "error": result.stderr or "Imprimante non trouvée",
                    "platform": "unix"
                }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "platform": "unix"
            }
