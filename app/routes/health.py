import time
from datetime import datetime
from fastapi import APIRouter, HTTPException
from loguru import logger
from ..models import HealthResponse
from ..config import config_manager
from ..storage.files import file_storage

router = APIRouter(prefix="/health", tags=["health"])

# Variable globale pour stocker le temps de démarrage
_start_time = None


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
        
        # Récupérer les statistiques du stockage
        storage_stats = file_storage.get_storage_stats()
        
        logger.debug(f"Vérification de santé réussie. Uptime: {uptime:.2f}s")
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version=config_manager.config.app.version,
            uptime=uptime
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
        import psutil
        system_info = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else None
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
            "config": config_info,
            "storage": storage_stats,
            "system": system_info
        }
        
    except ImportError:
        # psutil n'est pas installé, on l'omet
        system_info = {"error": "psutil non disponible"}
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé détaillée: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la vérification de santé détaillée: {str(e)}"
        )
