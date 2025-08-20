"""
Route pour la composition des photos avec cadres et templates
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
import os
from pathlib import Path
import logging

from ..imaging.layout import layout_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["composition"])


@router.post("/compose")
async def compose_layout(
    photos: List[UploadFile] = File(...),
    template: str = Form(...),
    text_overlay: Optional[str] = Form(None),
    frame_name: Optional[str] = Form(None)
):
    """
    Compose une mise en page selon le template spécifié
    
    Args:
        photos: Liste des photos à composer
        template: Nom du template à utiliser
        text_overlay: Texte à superposer (optionnel)
        frame_name: Nom du cadre à utiliser (optionnel)
    
    Returns:
        Informations sur la composition générée
    """
    try:
        # Vérifier que le template existe
        if template not in layout_manager.list_templates():
            raise HTTPException(
                status_code=400, 
                detail=f"Template '{template}' non trouvé. Templates disponibles: {layout_manager.list_templates()}"
            )
        
        # Vérifier qu'il y a des photos
        if not photos:
            raise HTTPException(status_code=400, detail="Aucune photo fournie")
        
        # Sauvegarder temporairement les photos
        temp_photos = []
        try:
            for i, photo in enumerate(photos):
                if not photo.content_type.startswith('image/'):
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Le fichier {photo.filename} n'est pas une image"
                    )
                
                # Créer le dossier temporaire
                temp_dir = Path("uploads/temp")
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                # Sauvegarder la photo
                temp_path = temp_dir / f"temp_photo_{i}_{photo.filename}"
                with open(temp_path, "wb") as f:
                    content = await photo.read()
                    f.write(content)
                
                temp_photos.append(str(temp_path))
            
            # Composer la mise en page
            canvas_path, thumb_path = layout_manager.compose_layout(
                photos=temp_photos,
                template_name=template,
                text_overlay=text_overlay,
                frame_name=frame_name
            )
            
            # Nettoyer les fichiers temporaires
            for temp_path in temp_photos:
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            # Retourner les informations
            return {
                "success": True,
                "message": "Composition générée avec succès",
                "template": template,
                "canvas_path": canvas_path,
                "thumbnail_path": thumb_path,
                "photos_count": len(photos)
            }
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            for temp_path in temp_photos:
                try:
                    os.remove(temp_path)
                except:
                    pass
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la composition: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erreur interne lors de la composition"
        )


@router.get("/templates")
async def list_templates():
    """Liste tous les templates disponibles"""
    try:
        templates = layout_manager.list_templates()
        template_details = {}
        
        for template_name in templates:
            template = layout_manager.get_template(template_name)
            if template:
                template_details[template_name] = {
                    "name": template.get("name", template_name),
                    "description": template.get("description", ""),
                    "dimensions": template.get("dimensions", {}),
                    "layout": template.get("layout", {})
                }
        
        return {
            "templates": template_details,
            "count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des templates: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors de la récupération des templates"
        )


@router.get("/templates/{template_name}")
async def get_template(template_name: str):
    """Récupère les détails d'un template spécifique"""
    try:
        template = layout_manager.get_template(template_name)
        if not template:
            raise HTTPException(
                status_code=404, 
                detail=f"Template '{template_name}' non trouvé"
            )
        
        return {
            "template": template_name,
            "details": template
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du template {template_name}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors de la récupération du template"
        )


@router.get("/frames")
async def list_frames():
    """Liste tous les cadres disponibles"""
    try:
        frames_dir = Path("app/imaging/frames")
        if not frames_dir.exists():
            return {"frames": [], "count": 0}
        
        frames = []
        for frame_file in frames_dir.glob("*.png"):
            frames.append({
                "name": frame_file.name,
                "path": str(frame_file),
                "size": frame_file.stat().st_size
            })
        
        return {
            "frames": frames,
            "count": len(frames)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des cadres: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors de la récupération des cadres"
        )


@router.get("/download/{filename:path}")
async def download_composition(filename: str):
    """Télécharge une composition générée"""
    try:
        file_path = Path("data/prints") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        # Vérifier que le fichier est bien dans le dossier prints (sécurité)
        if not str(file_path.resolve()).startswith(str(Path("data/prints").resolve())):
            raise HTTPException(status_code=400, detail="Chemin de fichier invalide")
        
        return FileResponse(
            file_path,
            media_type="image/png",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de {filename}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors du téléchargement"
        )
