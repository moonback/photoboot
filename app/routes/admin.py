from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import FileResponse
from loguru import logger
from typing import List, Optional
import os
import json
from pathlib import Path
from datetime import datetime
import shutil
import time

from ..admin.auth import admin_auth
from ..models import LoginRequest, LoginResponse, LogoutResponse

router = APIRouter(prefix="/admin", tags=["administration"])


async def get_current_admin(request: Request) -> Optional[dict]:
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


# Endpoint pour compter les photos
@router.get("/photos/count")
async def get_photos_count(current_admin: dict = Depends(get_current_admin)):
    """Récupère le nombre total de photos"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        uploads_dir = Path("uploads")
        if not uploads_dir.exists():
            return {"count": 0}
        
        # Compter les fichiers d'images
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        count = 0
        for file_path in uploads_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                count += 1
        
        return {"count": count}
        
    except Exception as e:
        logger.error(f"Erreur lors du comptage des photos: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du comptage des photos")


# Endpoint pour lister les photos
@router.get("/photos")
async def get_photos(current_admin: dict = Depends(get_current_admin)):
    """Récupère la liste des photos"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        uploads_dir = Path("uploads")
        if not uploads_dir.exists():
            return {"photos": []}
        
        # Lister les fichiers d'images
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        photos = []
        
        for file_path in uploads_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                stat = file_path.stat()
                photos.append({
                    "filename": file_path.name,
                    "size": f"{stat.st_size / 1024:.1f} KB",
                    "date": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M")
                })
        
        # Trier par date de modification (plus récent en premier)
        photos.sort(key=lambda x: x["date"], reverse=True)
        
        return {"photos": photos}
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des photos: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des photos")


# Endpoint pour supprimer une photo
@router.delete("/photos/{filename}")
async def delete_photo(filename: str, current_admin: dict = Depends(get_current_admin)):
    """Supprime une photo"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        file_path = Path("uploads") / filename
        
        # Vérifier que le fichier existe et est dans le dossier uploads
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Photo non trouvée")
        
        # Vérifier que le fichier est bien dans le dossier uploads
        if not str(file_path.resolve()).startswith(str(Path("uploads").resolve())):
            raise HTTPException(status_code=400, detail="Chemin de fichier invalide")
        
        # Supprimer le fichier
        file_path.unlink()
        
        logger.info(f"Photo supprimée: {filename} par {current_admin.get('username')}")
        return {"success": True, "message": "Photo supprimée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la photo {filename}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression de la photo")


# Endpoint pour l'activité récente
@router.get("/activity")
async def get_recent_activity(current_admin: dict = Depends(get_current_admin)):
    """Récupère l'activité récente"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        # Simuler une activité récente (à remplacer par une vraie implémentation)
        activities = [
            {
                "icon": "📸",
                "action": "Photo prise",
                "description": "Nouvelle photo capturée",
                "timestamp": datetime.now().strftime("%H:%M")
            },
            {
                "icon": "👤",
                "action": "Connexion admin",
                "description": f"Connexion de {current_admin.get('username')}",
                "timestamp": datetime.now().strftime("%H:%M")
            },
            {
                "icon": "💾",
                "action": "Sauvegarde",
                "description": "Sauvegarde automatique effectuée",
                "timestamp": datetime.now().strftime("%H:%M")
            }
        ]
        
        return {"activities": activities}
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'activité: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'activité")


# Endpoint pour les logs système
@router.get("/logs")
async def get_logs(
    level: str = Query("ALL", description="Niveau de log à filtrer"),
    current_admin: dict = Depends(get_current_admin)
):
    """Récupère les logs système"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {"logs": []}
        
        # Chercher le fichier de log le plus récent
        log_files = list(logs_dir.glob("*.log"))
        if not log_files:
            return {"logs": []}
        
        # Prendre le fichier le plus récent
        latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
        
        logs = []
        try:
            with open(latest_log, 'r', encoding='utf-8') as f:
                for line in f.readlines()[-100:]:  # Dernières 100 lignes
                    line = line.strip()
                    if line:
                        # Parser la ligne de log (format basique)
                        if " - " in line:
                            timestamp_part, rest = line.split(" - ", 1)
                            if " - " in rest:
                                level_part, message = rest.split(" - ", 1)
                                log_level = level_part.strip()
                                
                                # Filtrer par niveau si demandé
                                if level == "ALL" or level.upper() in log_level.upper():
                                    logs.append({
                                        "timestamp": timestamp_part.strip(),
                                        "level": log_level,
                                        "message": message.strip()
                                    })
                        else:
                            # Format simple
                            logs.append({
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                                "level": "INFO",
                                "message": line
                            })
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier de log: {e}")
        
        # Retourner les logs dans l'ordre chronologique
        logs.reverse()
        return {"logs": logs}
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des logs")


# Endpoint pour effacer les logs
@router.post("/logs/clear")
async def clear_logs(current_admin: dict = Depends(get_current_admin)):
    """Efface tous les logs"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {"success": True, "message": "Aucun log à effacer"}
        
        # Effacer tous les fichiers .log
        cleared_count = 0
        for log_file in logs_dir.glob("*.log"):
            try:
                log_file.unlink()
                cleared_count += 1
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de {log_file}: {e}")
        
        logger.info(f"Logs effacés par {current_admin.get('username')}: {cleared_count} fichiers")
        return {"success": True, "message": f"{cleared_count} fichiers de log effacés"}
        
    except Exception as e:
        logger.error(f"Erreur lors de l'effacement des logs: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'effacement des logs")


# Endpoint pour exporter les logs
@router.get("/logs/export")
async def export_logs(current_admin: dict = Depends(get_current_admin)):
    """Exporte les logs en fichier texte"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            raise HTTPException(status_code=404, detail="Aucun log disponible")
        
        # Chercher le fichier de log le plus récent
        log_files = list(logs_dir.glob("*.log"))
        if not log_files:
            raise HTTPException(status_code=404, detail="Aucun fichier de log trouvé")
        
        latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
        
        # Créer un fichier d'export temporaire
        export_file = Path("logs") / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(latest_log, 'r', encoding='utf-8') as source, \
                 open(export_file, 'w', encoding='utf-8') as target:
                target.write(f"Export des logs - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                target.write(f"Exporté par: {current_admin.get('username')}\n")
                target.write("=" * 50 + "\n\n")
                target.write(source.read())
            
            # Retourner le fichier
            return FileResponse(
                export_file,
                media_type='text/plain',
                filename=f"photobooth_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
        finally:
            # Nettoyer le fichier temporaire
            if export_file.exists():
                export_file.unlink()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'export des logs: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'export des logs")


# Endpoint pour redémarrer le système
@router.post("/system/restart")
async def restart_system(current_admin: dict = Depends(get_current_admin)):
    """Redémarre le système (simulation)"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        logger.info(f"Demande de redémarrage par {current_admin.get('username')}")
        
        # Ici, vous pourriez implémenter un vrai redémarrage
        # Pour l'instant, on simule juste
        
        return {"success": True, "message": "Redémarrage en cours..."}
        
    except Exception as e:
        logger.error(f"Erreur lors de la demande de redémarrage: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la demande de redémarrage")


# Endpoint pour la sauvegarde du système
@router.post("/system/backup")
async def backup_system(current_admin: dict = Depends(get_current_admin)):
    """Crée une sauvegarde du système"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        logger.info(f"Demande de sauvegarde par {current_admin.get('username')}")
        
        # Créer un dossier de sauvegarde
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Créer un nom de fichier unique
        backup_name = f"photobooth_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = backup_dir / backup_name
        
        # Créer la sauvegarde (simulation)
        try:
            # Copier les dossiers importants
            if Path("uploads").exists():
                shutil.copytree("uploads", backup_path / "uploads", dirs_exist_ok=True)
            
            if Path("config").exists():
                shutil.copytree("config", backup_path / "config", dirs_exist_ok=True)
            
            # Créer un fichier d'information
            info_file = backup_path / "backup_info.txt"
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"Sauvegarde créée le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Créée par: {current_admin.get('username')}\n")
                f.write("Contenu: uploads, config\n")
            
            # Créer l'archive ZIP
            shutil.make_archive(str(backup_path), 'zip', backup_path)
            zip_path = Path(f"{backup_path}.zip")
            
            # Nettoyer le dossier temporaire
            shutil.rmtree(backup_path)
            
            # Retourner le fichier ZIP
            return FileResponse(
                zip_path,
                media_type='application/zip',
                filename=f"{backup_name}.zip"
            )
            
        finally:
            # Nettoyer le fichier ZIP temporaire
            if zip_path.exists():
                zip_path.unlink()
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la sauvegarde")


# Endpoint pour vider le cache
@router.post("/system/cache/clear")
async def clear_cache(current_admin: dict = Depends(get_current_admin)):
    """Vide le cache système"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        logger.info(f"Demande de vidage du cache par {current_admin.get('username')}")
        
        # Ici, vous pourriez implémenter un vrai vidage de cache
        # Pour l'instant, on simule juste
        
        return {"success": True, "message": "Cache vidé avec succès"}
        
    except Exception as e:
        logger.error(f"Erreur lors du vidage du cache: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du vidage du cache")


# Endpoint pour terminer toutes les sessions
@router.post("/sessions/terminate-all")
async def terminate_all_sessions(current_admin: dict = Depends(get_current_admin)):
    """Termine toutes les sessions actives"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        # Nettoyer toutes les sessions
        terminated_count = admin_auth.cleanup_expired_sessions()
        
        logger.info(f"Toutes les sessions terminées par {current_admin.get('username')}: {terminated_count} sessions")
        return {"success": True, "message": f"{terminated_count} sessions terminées"}
        
    except Exception as e:
        logger.error(f"Erreur lors de la terminaison des sessions: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la terminaison des sessions")


# Endpoint pour terminer une session spécifique
@router.delete("/sessions/{username}")
async def terminate_session(username: str, current_admin: dict = Depends(get_current_admin)):
    """Termine une session spécifique"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        # Chercher et terminer la session de l'utilisateur
        terminated = False
        for token, session_data in admin_auth.active_sessions.items():
            if session_data.get("username") == username:
                del admin_auth.active_sessions[token]
                terminated = True
                break
        
        if terminated:
            logger.info(f"Session de {username} terminée par {current_admin.get('username')}")
            return {"success": True, "message": f"Session de {username} terminée"}
        else:
            return {"success": False, "message": f"Aucune session trouvée pour {username}"}
        
    except Exception as e:
        logger.error(f"Erreur lors de la terminaison de la session de {username}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la terminaison de la session")





# Endpoint pour les sessions actives
@router.get("/sessions")
async def get_active_sessions(current_admin: dict = Depends(get_current_admin)):
    """Récupère les sessions actives"""
    if not current_admin:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    try:
        sessions = []
        current_time = time.time()
        
        for token, session_data in admin_auth.active_sessions.items():
            if current_time < session_data["expires_at"]:
                sessions.append({
                    "username": session_data["username"],
                    "login_time": datetime.fromtimestamp(session_data["login_time"]).strftime("%d/%m/%Y %H:%M:%S"),
                    "expires_at": datetime.fromtimestamp(session_data["expires_at"]).strftime("%d/%m/%Y %H:%M:%S"),
                    "remaining_time": max(0, session_data["expires_at"] - current_time)
                })
        
        return {"sessions": sessions}
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des sessions: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des sessions")
