import time
import os
import shutil
from datetime import datetime
from fastapi import APIRouter, HTTPException
from loguru import logger
from ..models import HealthResponse
from ..config import config_manager
from ..storage.files import file_storage
from pathlib import Path

router = APIRouter(prefix="/health", tags=["health"])

# Variable globale pour stocker le temps de démarrage
_start_time = None


def get_camera_status():
    """Récupère le statut de la caméra"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                return {
                    "available": True,
                    "device_id": 0,
                    "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                    "status": "operational"
                }
            else:
                return {
                    "available": False,
                    "error": "Impossible de capturer une image",
                    "status": "error"
                }
        else:
            return {
                "available": False,
                "error": "Caméra non accessible",
                "status": "unavailable"
            }
    except ImportError:
        return {
            "available": False,
            "error": "OpenCV non installé",
            "status": "not_installed"
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "status": "error"
        }


def get_disk_space():
    """Récupère l'espace disque disponible"""
    try:
        # Utiliser le dossier uploads comme référence
        upload_path = Path(config_manager.config.storage.upload_dir)
        if not upload_path.exists():
            upload_path = Path("uploads")
        
        # Trouver le disque contenant ce dossier
        disk_path = upload_path.resolve()
        while disk_path.parent != disk_path:
            if os.path.ismount(disk_path):
                break
            disk_path = disk_path.parent
        
        total, used, free = shutil.disk_usage(disk_path)
        
        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "usage_percent": round((used / total) * 100, 1),
            "path": str(disk_path)
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "unavailable"
        }


def get_printer_status():
    """Récupère le statut de l'imprimante"""
    try:
        from ..printing.printer import PrinterManager
        config = config_manager.get_config_dict() if config_manager.config else {}
        printer_mgr = PrinterManager(config)
        
        # Vérifier la disponibilité des imprimantes
        printers = printer_mgr.get_available_printers()
        default_printer = printer_mgr.get_default_printer()
        
        if printers:
            # Vérifier le statut de l'imprimante par défaut
            status = printer_mgr.get_printer_status(default_printer)
            return {
                "available": True,
                "printers_count": len(printers),
                "default_printer": default_printer,
                "default_status": status,
                "platforms": list(set(p["platform"] for p in printers))
            }
        else:
            return {
                "available": False,
                "error": "Aucune imprimante trouvée",
                "printers_count": 0
            }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "status": "error"
        }


def get_email_status():
    """Récupère le statut du service email"""
    try:
        from ..emailer.send import EmailSender
        config = config_manager.get_config_dict() if config_manager.config else {}
        email_mgr = EmailSender(config)
        
        status = email_mgr.get_email_status()
        return {
            "configured": status["configured"],
            "smtp_server": status["smtp_server"],
            "smtp_port": status["smtp_port"],
            "from_email": status["from_email"],
            "gdpr_required": status["gdpr_required"],
            "rate_limit": status["rate_limit"]
        }
    except Exception as e:
        return {
            "configured": False,
            "error": str(e),
            "status": "error"
        }


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état de santé du système"""
    global _start_time
    
    try:
        # Initialiser le temps de démarrage si c'est la première fois
        if _start_time is None:
            _start_time = time.time()
        
        # Calculer le temps de fonctionnement
        uptime = time.time() - _start_time
        
        # Vérifications de base
        checks = {
            "config_loaded": config_manager.config is not None,
            "storage_accessible": file_storage.upload_dir.exists(),
            "admin_configured": bool(config_manager.config.admin.username),
            "secret_key_set": bool(config_manager.config.security.secret_key)
        }
        
        # Vérifier que tous les composants sont opérationnels
        all_healthy = all(checks.values())
        
        if not all_healthy:
            failed_checks = [k for k, v in checks.items() if not v]
            logger.warning(f"Vérifications de santé échouées: {failed_checks}")
            raise HTTPException(
                status_code=503,
                detail=f"Service non disponible. Échecs: {failed_checks}"
            )
        
        # Récupérer les informations détaillées
        camera_status = get_camera_status()
        disk_space = get_disk_space()
        printer_status = get_printer_status()
        email_status = get_email_status()
        
        logger.debug(f"Vérification de santé réussie. Uptime: {uptime:.2f}s")
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version=config_manager.config.app.version,
            uptime=uptime,
            camera_status=camera_status,
            disk_space=disk_space,
            printer_status=printer_status,
            email_status=email_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la vérification de santé"
        )


@router.get("/detailed")
async def detailed_health_check():
    """Vérification détaillée de l'état de santé du système"""
    try:
        global _start_time
        
        if _start_time is None:
            _start_time = time.time()
        
        uptime = time.time() - _start_time
        
        # Informations détaillées sur la configuration
        config_info = {
            "app": {
                "name": config_manager.config.app.name,
                "version": config_manager.config.app.version,
                "debug": config_manager.config.app.debug
            },
            "server": {
                "host": config_manager.config.server.host,
                "port": config_manager.config.server.port,
                "workers": config_manager.config.server.workers
            },
            "security": {
                "session_timeout": config_manager.config.security.session_timeout,
                "bcrypt_rounds": config_manager.config.security.bcrypt_rounds,
                "secret_key_set": bool(config_manager.config.security.secret_key)
            },
            "storage": {
                "upload_dir": str(config_manager.config.storage.upload_dir),
                "max_file_size": config_manager.config.storage.max_file_size,
                "allowed_extensions": config_manager.config.storage.allowed_extensions
            },
            "logging": {
                "level": config_manager.config.logging.level,
                "rotation": config_manager.config.logging.rotation,
                "retention": config_manager.config.logging.retention
            }
        }
        
        # Statistiques du stockage
        storage_stats = file_storage.get_storage_stats()
        
        # Informations système
        try:
            import psutil
            system_info = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else None
            }
        except ImportError:
            system_info = {"error": "psutil non disponible"}
        
        # Informations détaillées des composants
        camera_status = get_camera_status()
        disk_space = get_disk_space()
        printer_status = get_printer_status()
        email_status = get_email_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
            "config": config_info,
            "storage": storage_stats,
            "system": system_info,
            "components": {
                "camera": camera_status,
                "disk": disk_space,
                "printer": printer_status,
                "email": email_status
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé détaillée: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la vérification de santé détaillée: {str(e)}"
        )
