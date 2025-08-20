from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from loguru import logger
from pathlib import Path
import os
from datetime import datetime
import shutil

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/photo")
async def upload_photo(photo: UploadFile = File(...)):
    """Upload d'une photo depuis le photobooth"""
    try:
        # Vérifier que c'est bien une image
        if not photo.content_type or not photo.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Le fichier doit être une image")
        
        # Créer le dossier uploads s'il n'existe pas
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Générer un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(photo.filename).suffix if photo.filename else '.jpg'
        filename = f"photobooth_{timestamp}{file_extension}"
        
        # Chemin complet du fichier
        file_path = uploads_dir / filename
        
        # Sauvegarder le fichier
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier {filename}: {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde de la photo")
        
        # Log de la sauvegarde
        file_size = file_path.stat().st_size
        logger.info(f"Photo sauvegardée: {filename} ({file_size} bytes)")
        
        return JSONResponse({
            "success": True,
            "message": "Photo sauvegardée avec succès",
            "filename": filename,
            "size": file_size,
            "timestamp": timestamp
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'upload de la photo: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne lors de l'upload")
