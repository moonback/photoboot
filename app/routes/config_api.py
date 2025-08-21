from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from typing import Dict, Any
from ..models import ConfigResponse, ConfigUpdateRequest, ErrorResponse
from ..config import config_manager
from ..admin.auth import admin_auth
from ..routes.auth import get_current_admin

router = APIRouter(prefix="/config", tags=["configuration"])


@router.get("/", response_model=ConfigResponse)
async def get_config():
    """Récupère la configuration actuelle du système"""
    try:
        if not config_manager.config:
            raise HTTPException(
                status_code=500,
                detail="Configuration non disponible"
            )
        
        logger.debug("Configuration récupérée avec succès")
        
        return ConfigResponse(
            config=config_manager.config,
            message="Configuration récupérée avec succès"
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de la configuration: {str(e)}"
        )


@router.put("/", response_model=ConfigResponse)
async def update_config(
    config_update: ConfigUpdateRequest,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Met à jour la configuration du système (admin uniquement)"""
    try:
        if not current_admin:
            raise HTTPException(
                status_code=401,
                detail="Authentification requise"
            )
        
        logger.info(f"Mise à jour de la configuration par l'admin: {current_admin.get('username')}")
        
        # Validation de la nouvelle configuration
        try:
            # Créer un objet Config temporaire pour validation
            from ..models import Config
            validated_config = Config(**config_update.config)
        except Exception as validation_error:
            logger.warning(f"Configuration invalide reçue: {validation_error}")
            raise HTTPException(
                status_code=400,
                detail=f"Configuration invalide: {str(validation_error)}"
            )
        
        # Sauvegarder la configuration
        if config_manager.save_config(config_update.config):
            # Recharger la configuration
            config_manager.reload()
            
            logger.info("Configuration mise à jour et rechargée avec succès")
            
            return ConfigResponse(
                config=config_manager.config,
                message="Configuration mise à jour avec succès"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la sauvegarde de la configuration"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour de la configuration: {str(e)}"
        )


@router.get("/reload")
async def reload_config(current_admin: Dict[str, Any] = Depends(get_current_admin)):
    """Recharge la configuration depuis les fichiers (admin uniquement)"""
    try:
        if not current_admin:
            raise HTTPException(
                status_code=401,
                detail="Authentification requise"
            )
        
        logger.info(f"Rechargement de la configuration par l'admin: {current_admin.get('username')}")
        
        # Recharger la configuration
        config_manager.reload()
        
        logger.info("Configuration rechargée avec succès")
        
        return {
            "message": "Configuration rechargée avec succès",
            "timestamp": config_manager.config.app.version if config_manager.config else "N/A"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du rechargement de la configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du rechargement de la configuration: {str(e)}"
        )


@router.get("/validate")
async def validate_config():
    """Valide la configuration actuelle sans la modifier"""
    try:
        if not config_manager.config:
            raise HTTPException(
                status_code=500,
                detail="Configuration non disponible"
            )
        
        # La configuration est déjà validée lors du chargement
        # On peut ajouter des validations supplémentaires ici si nécessaire
        
        logger.debug("Configuration validée avec succès")
        
        return {
            "valid": True,
            "message": "Configuration valide",
            "config_summary": {
                "app_name": config_manager.config.app.name,
                "version": config_manager.config.app.version,
                "server_host": config_manager.config.server.host,
                "server_port": config_manager.config.server.port,
                "storage_dir": str(config_manager.config.storage.upload_dir),
                "admin_configured": bool(config_manager.config.admin.username)
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la validation de la configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la validation de la configuration: {str(e)}"
        )


@router.get("/schema")
async def get_config_schema():
    """Retourne le schéma de la configuration (pour documentation)"""
    try:
        from ..models import Config
        
        # Générer le schéma JSON de la configuration
        schema = Config.model_json_schema()
        
        return {
            "schema": schema,
            "description": "Schéma JSON de la configuration du photobooth",
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du schéma: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du schéma: {str(e)}"
        )


@router.put("/app")
async def update_app_config(
    app_config: Dict[str, Any],
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Met à jour la configuration de l'application (admin uniquement)"""
    try:
        if not current_admin:
            raise HTTPException(status_code=401, detail="Authentification requise")
        
        logger.info(f"Mise à jour de la configuration app par l'admin: {current_admin.get('username')}")
        
        # Mettre à jour la configuration de l'application
        if config_manager.config:
            # Mettre à jour les champs de l'application
            if 'name' in app_config:
                config_manager.config.app.name = app_config['name']
            if 'version' in app_config:
                config_manager.config.app.version = app_config['version']
            if 'debug' in app_config:
                config_manager.config.app.debug = app_config['debug']
            
            # Sauvegarder la configuration
            if config_manager.save_config(config_manager.config.model_dump()):
                logger.info("Configuration de l'application mise à jour avec succès")
                return {
                    "success": True,
                    "message": "Configuration de l'application mise à jour avec succès"
                }
            else:
                raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde")
        else:
            raise HTTPException(status_code=500, detail="Configuration non disponible")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la configuration app: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.put("/security")
async def update_security_config(
    security_config: Dict[str, Any],
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Met à jour la configuration de sécurité (admin uniquement)"""
    try:
        if not current_admin:
            raise HTTPException(status_code=401, detail="Authentification requise")
        
        logger.info(f"Mise à jour de la configuration sécurité par l'admin: {current_admin.get('username')}")
        
        # Mettre à jour la configuration de sécurité
        if config_manager.config:
            # Mettre à jour les champs de sécurité
            if 'session_timeout' in security_config:
                config_manager.config.security.session_timeout = security_config['session_timeout']
            if 'bcrypt_rounds' in security_config:
                config_manager.config.security.bcrypt_rounds = security_config['bcrypt_rounds']
            
            # Sauvegarder la configuration
            if config_manager.save_config(config_manager.config.model_dump()):
                logger.info("Configuration de sécurité mise à jour avec succès")
                return {
                    "success": True,
                    "message": "Configuration de sécurité mise à jour avec succès"
                }
            else:
                raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde")
        else:
            raise HTTPException(status_code=500, detail="Configuration non disponible")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la configuration sécurité: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")
