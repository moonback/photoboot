import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from loguru import logger
from ..config import config_manager


class FileStorage:
    """Gestionnaire de stockage des fichiers pour le photobooth"""
    
    def __init__(self):
        self.config = config_manager.config.storage
        self.upload_dir = Path(self.config.upload_dir)
        self.max_file_size = self.config.max_file_size
        self.allowed_extensions = self.config.allowed_extensions
        
        # Créer le dossier d'upload s'il n'existe pas
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Crée le dossier d'upload s'il n'existe pas"""
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Dossier d'upload créé/vérifié: {self.upload_dir}")
        except Exception as e:
            logger.error(f"Erreur lors de la création du dossier d'upload: {e}")
            raise
    
    def validate_file(self, file_path: Path, file_size: int) -> Tuple[bool, str]:
        """Valide un fichier selon les règles de sécurité"""
        # Vérification de la taille
        if file_size > self.max_file_size:
            return False, f"Fichier trop volumineux: {file_size} > {self.max_file_size}"
        
        # Vérification de l'extension
        file_ext = file_path.suffix.lower()
        if file_ext not in self.allowed_extensions:
            return False, f"Extension non autorisée: {file_ext}"
        
        # Vérification du nom de fichier (sécurité)
        filename = file_path.name
        if any(char in filename for char in ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            return False, "Nom de fichier invalide"
        
        return True, "Fichier valide"
    
    def save_file(self, source_path: Path, filename: str) -> Optional[Path]:
        """Sauvegarde un fichier dans le dossier d'upload"""
        try:
            # Validation du fichier source
            if not source_path.exists():
                logger.error(f"Fichier source introuvable: {source_path}")
                return None
            
            file_size = source_path.stat().st_size
            is_valid, message = self.validate_file(Path(filename), file_size)
            
            if not is_valid:
                logger.warning(f"Fichier rejeté: {message}")
                return None
            
            # Créer un nom de fichier unique
            target_path = self._get_unique_filename(filename)
            
            # Copier le fichier
            shutil.copy2(source_path, target_path)
            logger.info(f"Fichier sauvegardé: {target_path}")
            
            return target_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier: {e}")
            return None
    
    def _get_unique_filename(self, filename: str) -> Path:
        """Génère un nom de fichier unique"""
        base_name = Path(filename).stem
        extension = Path(filename).suffix
        
        counter = 1
        target_path = self.upload_dir / filename
        
        while target_path.exists():
            new_filename = f"{base_name}_{counter}{extension}"
            target_path = self.upload_dir / new_filename
            counter += 1
        
        return target_path
    
    def delete_file(self, filename: str) -> bool:
        """Supprime un fichier du stockage"""
        try:
            file_path = self.upload_dir / filename
            
            # Vérification de sécurité
            if not file_path.exists():
                logger.warning(f"Fichier introuvable: {file_path}")
                return False
            
            # Vérifier que le fichier est bien dans le dossier d'upload
            try:
                file_path.relative_to(self.upload_dir)
            except ValueError:
                logger.error(f"Tentative d'accès à un fichier hors du dossier d'upload: {file_path}")
                return False
            
            file_path.unlink()
            logger.info(f"Fichier supprimé: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier: {e}")
            return False
    
    def list_files(self, pattern: str = "*") -> List[Path]:
        """Liste les fichiers dans le dossier d'upload"""
        try:
            files = list(self.upload_dir.glob(pattern))
            # Filtrer seulement les fichiers (pas les dossiers)
            files = [f for f in files if f.is_file()]
            return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
        except Exception as e:
            logger.error(f"Erreur lors de la liste des fichiers: {e}")
            return []
    
    def get_file_info(self, filename: str) -> Optional[dict]:
        """Récupère les informations d'un fichier"""
        try:
            file_path = self.upload_dir / filename
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            return {
                "name": filename,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos du fichier: {e}")
            return None
    
    def cleanup_old_files(self, max_age_days: int = 30) -> int:
        """Nettoie les anciens fichiers"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 3600
            
            deleted_count = 0
            files = self.list_files()
            
            for file_path in files:
                file_age = current_time - file_path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    if self.delete_file(file_path.name):
                        deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"{deleted_count} anciens fichiers supprimés")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des anciens fichiers: {e}")
            return 0
    
    def get_storage_stats(self) -> dict:
        """Récupère les statistiques du stockage"""
        try:
            files = self.list_files()
            total_size = sum(f.stat().st_size for f in files)
            
            return {
                "total_files": len(files),
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "upload_dir": str(self.upload_dir),
                "max_file_size": self.max_file_size,
                "allowed_extensions": self.allowed_extensions
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats du stockage: {e}")
            return {}


# Instance globale du gestionnaire de stockage
file_storage = FileStorage()
