from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from loguru import logger
from typing import List, Optional
import os
import json
from pathlib import Path
from datetime import datetime
import uuid
from PIL import Image
import io

from ..admin.auth import admin_auth
from ..models import FrameCreate, FrameUpdate, Frame

router = APIRouter(prefix="/admin/frames", tags=["frames"])

# Dossier de stockage des cadres
FRAMES_DIR = Path("frames")
FRAMES_DIR.mkdir(exist_ok=True)

# Fichier de configuration des cadres
FRAMES_CONFIG_FILE = Path("config/frames.json")

def load_frames_config():
    """Charge la configuration des cadres depuis le fichier JSON"""
    if FRAMES_CONFIG_FILE.exists():
        try:
            with open(FRAMES_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration des cadres: {e}")
            return {"frames": []}
    return {"frames": []}

def save_frames_config(config):
    """Sauvegarde la configuration des cadres dans le fichier JSON"""
    try:
        FRAMES_CONFIG_FILE.parent.mkdir(exist_ok=True)
        with open(FRAMES_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la configuration des cadres: {e}")
        return False

async def get_current_admin(request):
    """Dépendance pour récupérer l'utilisateur admin actuel"""
    try:
        # Récupérer le token depuis les cookies
        session_token = request.cookies.get("session_token")
        
        if session_token:
            session_data = admin_auth.validate_session(session_token)
            if session_data:
                return session_data
        
        # Récupérer le token depuis les headers Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Enlever "Bearer "
            session_data = admin_auth.validate_session(token)
            if session_data:
                return session_data
        
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la validation de la session: {e}")
        return None

@router.get("/")
async def get_frames(request: Request, current_admin: dict = Depends(get_current_admin)):
    """Récupère la liste de tous les cadres"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        config = load_frames_config()
        return config
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des cadres: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des cadres")

@router.get("/active")
async def get_active_frame(request: Request, current_admin: dict = Depends(get_current_admin)):
    """Récupère le cadre actif"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        config = load_frames_config()
        active_frame = next((frame for frame in config["frames"] if frame.get("active", False)), None)
        return {"frame": active_frame}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du cadre actif: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du cadre actif")

@router.get("/{frame_id}")
async def get_frame(frame_id: str, request: Request, current_admin: dict = Depends(get_current_admin)):
    """Récupère un cadre spécifique"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        config = load_frames_config()
        frame = next((f for f in config["frames"] if f["id"] == frame_id), None)
        
        if not frame:
            raise HTTPException(status_code=404, detail="Cadre non trouvé")
        
        return {"frame": frame}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du cadre {frame_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du cadre")

@router.post("/")
async def create_frame(
    name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    position: str = Form("center"),
    size: int = Form(100),
    active: bool = Form(False),
    x: Optional[int] = Form(None),
    y: Optional[int] = Form(None),
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """Crée un nouveau cadre"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        # Vérifier le type de fichier
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Le fichier doit être une image")
        
        # Vérifier l'extension
        if not file.filename.lower().endswith('.png'):
            raise HTTPException(status_code=400, detail="Seuls les fichiers PNG sont acceptés")
        
        # Générer un ID unique
        frame_id = str(uuid.uuid4())
        
        # Créer le nom de fichier
        file_extension = Path(file.filename).suffix
        filename = f"{frame_id}{file_extension}"
        file_path = FRAMES_DIR / filename
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Charger l'image pour obtenir les dimensions
        try:
            with Image.open(file_path) as img:
                width, height = img.size
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de l'image: {e}")
            width, height = 100, 100
        
        # Créer l'objet cadre
        frame_data = {
            "id": frame_id,
            "name": name,
            "description": description,
            "filename": filename,
            "position": position,
            "size": size,
            "active": active,
            "width": width,
            "height": height,
            "created_at": datetime.now().isoformat(),
            "created_by": current_admin.get("username", "admin")
        }
        
        # Ajouter les coordonnées personnalisées si nécessaire
        if position == "custom" and x is not None and y is not None:
            frame_data["x"] = x
            frame_data["y"] = y
        
        # Charger la configuration existante
        config = load_frames_config()
        
        # Désactiver tous les autres cadres si celui-ci est actif
        if active:
            for frame in config["frames"]:
                frame["active"] = False
        
        # Ajouter le nouveau cadre
        config["frames"].append(frame_data)
        
        # Sauvegarder la configuration
        if not save_frames_config(config):
            # Supprimer le fichier si la sauvegarde échoue
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde de la configuration")
        
        logger.info(f"Cadre créé: {name} par {current_admin.get('username')}")
        return {"success": True, "frame": frame_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la création du cadre: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création du cadre")

@router.post("/{frame_id}/toggle")
async def toggle_frame_active(frame_id: str, request: Request, current_admin: dict = Depends(get_current_admin)):
    """Active/désactive un cadre"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        config = load_frames_config()
        frame = next((f for f in config["frames"] if f["id"] == frame_id), None)
        
        if not frame:
            raise HTTPException(status_code=404, detail="Cadre non trouvé")
        
        # Désactiver tous les autres cadres
        for f in config["frames"]:
            f["active"] = False
        
        # Activer le cadre sélectionné
        frame["active"] = True
        
        # Sauvegarder la configuration
        if not save_frames_config(config):
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde de la configuration")
        
        logger.info(f"Cadre activé: {frame['name']} par {current_admin.get('username')}")
        return {"success": True, "message": "Cadre activé avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'activation du cadre {frame_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'activation du cadre")

@router.delete("/{frame_id}")
async def delete_frame(frame_id: str, request: Request, current_admin: dict = Depends(get_current_admin)):
    """Supprime un cadre"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        config = load_frames_config()
        frame = next((f for f in config["frames"] if f["id"] == frame_id), None)
        
        if not frame:
            raise HTTPException(status_code=404, detail="Cadre non trouvé")
        
        # Supprimer le fichier
        file_path = FRAMES_DIR / frame["filename"]
        if file_path.exists():
            file_path.unlink()
        
        # Supprimer de la configuration
        config["frames"] = [f for f in config["frames"] if f["id"] != frame_id]
        
        # Sauvegarder la configuration
        if not save_frames_config(config):
            raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde de la configuration")
        
        logger.info(f"Cadre supprimé: {frame['name']} par {current_admin.get('username')}")
        return {"success": True, "message": "Cadre supprimé avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du cadre {frame_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression du cadre")

@router.get("/file/{filename}")
async def get_frame_file(filename: str):
    """Récupère le fichier d'un cadre"""
    try:
        file_path = FRAMES_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        return FileResponse(file_path, media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du fichier {filename}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du fichier")
