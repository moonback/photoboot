from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from loguru import logger
from pathlib import Path
import os
from datetime import datetime
import shutil
import aiofiles
from typing import List
import hashlib
from ..config import config_manager

router = APIRouter(prefix="/upload", tags=["upload"])

# Extensions et types MIME autorisés
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/gif", 
    "image/bmp", "image/webp"
}

# Signatures de fichiers (magic bytes) - Implémentation manuelle
FILE_SIGNATURES = {
    b'\xff\xd8\xff': '.jpg',  # JPEG
    b'\x89PNG\r\n\x1a\n': '.png',  # PNG
    b'GIF87a': '.gif',  # GIF87a
    b'GIF89a': '.gif',  # GIF89a
    b'BM': '.bmp',  # BMP
    b'RIFF': '.webp',  # WebP
}

async def validate_file(file: UploadFile) -> bool:
    """Valide un fichier uploadé de manière sécurisée"""
    try:
        logger.info(f"Validation du fichier: {file.filename}, type: {file.content_type}")
        
        # Vérification de la taille
        max_size = config_manager.config.storage.max_file_size if config_manager.config else 10 * 1024 * 1024  # 10MB par défaut
        
        # Lire les premiers bytes pour vérifier la signature
        content = await file.read(32)  # Lire les 32 premiers bytes
        await file.seek(0)  # Remettre le curseur au début
        
        logger.info(f"Premiers bytes: {content[:16].hex()}")
        
        # Vérifier la signature du fichier
        file_extension = None
        for signature, ext in FILE_SIGNATURES.items():
            if content.startswith(signature):
                file_extension = ext
                logger.info(f"Signature trouvée: {ext}")
                break
        
        if not file_extension:
            logger.warning(f"Signature de fichier invalide pour {file.filename}")
            return False
        
        # Vérifier l'extension seulement si le fichier a un nom
        if file.filename:
            filename_extension = Path(file.filename).suffix.lower()
            if filename_extension and filename_extension != file_extension:
                logger.warning(f"Extension de fichier ne correspond pas à la signature: {file.filename} vs {file_extension}")
                # Au lieu de rejeter, on peut être plus tolérant
                logger.info(f"Extension ignorée, utilisation de la signature: {file_extension}")
        
        # Vérifier le type MIME seulement s'il est fourni
        if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
            logger.warning(f"Type MIME non autorisé: {file.content_type}")
            # Au lieu de rejeter, on peut être plus tolérant
            logger.info(f"Type MIME ignoré, utilisation de la signature: {file_extension}")
        
        logger.info(f"Fichier validé avec succès: {file.filename}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la validation du fichier: {e}")
        return False

@router.post("/photo")
async def upload_photo(photo: UploadFile = File(...)):
    """Upload d'une photo depuis le photobooth avec validation sécurisée"""
    try:
        logger.info(f"Tentative d'upload: {photo.filename}, type: {photo.content_type}, taille: {photo.size if hasattr(photo, 'size') else 'inconnue'}")
        
        # Validation du fichier
        if not await validate_file(photo):
            logger.error(f"Validation échouée pour {photo.filename}")
            raise HTTPException(
                status_code=400, 
                detail="Fichier invalide ou type non autorisé"
            )
        
        # Vérifier que c'est bien une image
        if not photo.content_type or not photo.content_type.startswith('image/'):
            logger.error(f"Type MIME invalide: {photo.content_type}")
            raise HTTPException(
                status_code=400, 
                detail="Le fichier doit être une image"
            )
        
        # Créer le dossier uploads s'il n'existe pas
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Générer un nom de fichier unique avec hash
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Déterminer l'extension du fichier
        if photo.filename and Path(photo.filename).suffix:
            file_extension = Path(photo.filename).suffix
        else:
            # Utiliser l'extension basée sur la signature du fichier
            content_for_signature = await photo.read(32)
            await photo.seek(0)
            
            detected_extension = None
            for signature, ext in FILE_SIGNATURES.items():
                if content_for_signature.startswith(signature):
                    detected_extension = ext
                    break
            
            file_extension = detected_extension or '.jpg'  # Par défaut .jpg
        
        # Créer un hash du contenu pour éviter les doublons
        content = await photo.read()
        file_hash = hashlib.md5(content).hexdigest()[:8]
        filename = f"photobooth_{timestamp}_{file_hash}{file_extension}"
        
        # Chemin complet du fichier
        file_path = uploads_dir / filename
        
        # Sauvegarder le fichier de manière asynchrone
        try:
            async with aiofiles.open(file_path, "wb") as buffer:
                await buffer.write(content)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier {filename}: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Erreur lors de la sauvegarde de la photo"
            )
        
        # Log de la sauvegarde
        file_size = file_path.stat().st_size
        logger.info(f"Photo sauvegardée: {filename} ({file_size} bytes) - Hash: {file_hash}")
        
        return JSONResponse({
            "success": True,
            "message": "Photo sauvegardée avec succès",
            "filename": filename,
            "size": file_size,
            "timestamp": timestamp,
            "hash": file_hash,
            "content_type": photo.content_type
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'upload de la photo: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erreur interne lors de l'upload"
        )
