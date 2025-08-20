from fastapi import APIRouter, HTTPException, Response, Depends, Cookie
from fastapi.security import HTTPBearer
from loguru import logger
from typing import Optional, Dict, Any
from ..models import LoginRequest, LoginResponse, LogoutResponse
from ..admin.auth import admin_auth
from ..config import config_manager

router = APIRouter(prefix="/admin", tags=["administration"])
security = HTTPBearer(auto_error=False)


async def get_current_admin(
    authorization: Optional[str] = Depends(security),
    session_token: Optional[str] = Cookie(None, alias="session_token")
) -> Optional[Dict[str, Any]]:
    """Dépendance pour récupérer l'utilisateur admin actuel"""
    try:
        # Essayer d'abord le token Bearer
        if authorization:
            token = authorization.credentials
            session_data = admin_auth.validate_session(token)
            if session_data:
                return session_data
        
        # Essayer ensuite le cookie de session
        if session_token:
            session_data = admin_auth.validate_session(session_token)
            if session_data:
                return session_data
        
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la validation de la session: {e}")
        return None


@router.post("/login", response_model=LoginResponse)
async def admin_login(
    login_data: LoginRequest,
    response: Response
):
    """Connexion administrateur"""
    try:
        # Authentification
        auth_result = admin_auth.authenticate(login_data)
        
        if not auth_result.success:
            logger.warning(f"Tentative de connexion échouée pour l'utilisateur: {login_data.username}")
            return auth_result
        
        # Configuration du cookie de session sécurisé
        if auth_result.token:
            response.set_cookie(
                key="session_token",
                value=auth_result.token,
                httponly=True,
                secure=False,  # False pour le développement local, True en production avec HTTPS
                samesite="lax",
                max_age=config_manager.config.security.session_timeout,
                path="/"
            )
            
            logger.info(f"Connexion admin réussie pour l'utilisateur: {login_data.username}")
        
        return auth_result
        
    except Exception as e:
        logger.error(f"Erreur lors de la connexion admin: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la connexion"
        )


@router.post("/logout", response_model=LogoutResponse)
async def admin_logout(
    response: Response,
    current_admin: Optional[Dict[str, Any]] = Depends(get_current_admin)
):
    """Déconnexion administrateur"""
    try:
        # Récupérer le token depuis le cookie
        session_token = None
        if current_admin:
            # Chercher le token dans les sessions actives
            for token, session_data in admin_auth.active_sessions.items():
                if session_data.get("username") == current_admin.get("username"):
                    session_token = token
                    break
        
        # Déconnexion
        if session_token:
            logout_result = admin_auth.logout(session_token)
        else:
            logout_result = LogoutResponse(
                success=True,
                message="Déconnexion réussie (session non trouvée)"
            )
        
        # Supprimer le cookie de session
        response.delete_cookie(
            key="session_token",
            path="/"
        )
        
        logger.info(f"Déconnexion admin pour l'utilisateur: {current_admin.get('username') if current_admin else 'unknown'}")
        
        return logout_result
        
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion admin: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la déconnexion"
        )


@router.get("/me")
async def get_admin_info(
    current_admin: Optional[Dict[str, Any]] = Depends(get_current_admin)
):
    """Récupère les informations de l'administrateur connecté"""
    try:
        if not current_admin:
            raise HTTPException(
                status_code=401,
                detail="Non authentifié"
            )
        
        # Récupérer les informations détaillées de la session
        session_token = None
        for token, session_data in admin_auth.active_sessions.items():
            if session_data.get("username") == current_admin.get("username"):
                session_token = token
                break
        
        session_info = None
        if session_token:
            session_info = admin_auth.get_session_info(session_token)
        
        return {
            "authenticated": True,
            "username": current_admin.get("username"),
            "session_info": session_info,
            "config": {
                "session_timeout": config_manager.config.security.session_timeout,
                "bcrypt_rounds": config_manager.config.security.bcrypt_rounds
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des infos admin: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la récupération des informations"
        )


@router.post("/refresh")
async def refresh_session(
    current_admin: Optional[Dict[str, Any]] = Depends(get_current_admin),
    response: Response = None
):
    """Rafraîchit la session administrateur"""
    try:
        if not current_admin:
            raise HTTPException(
                status_code=401,
                detail="Non authentifié"
            )
        
        # Chercher le token dans les sessions actives
        session_token = None
        for token, session_data in admin_auth.active_sessions.items():
            if session_data.get("username") == current_admin.get("username"):
                session_token = token
                break
        
        if not session_token:
            raise HTTPException(
                status_code=400,
                detail="Token de session non trouvé"
            )
        
        # Rafraîchir la session
        new_token = admin_auth.refresh_session(session_token)
        
        if new_token and response:
            # Mettre à jour le cookie
            response.set_cookie(
                key="session_token",
                value=new_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=config_manager.config.security.session_timeout,
                path="/"
            )
            
            logger.info(f"Session rafraîchie pour l'utilisateur: {current_admin.get('username')}")
            
            return {
                "success": True,
                "message": "Session rafraîchie avec succès",
                "new_token": new_token
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Erreur lors du rafraîchissement de la session"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement de la session: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors du rafraîchissement de la session"
        )


@router.get("/sessions")
async def get_sessions_info(
    current_admin: Optional[Dict[str, Any]] = Depends(get_current_admin)
):
    """Récupère les informations sur les sessions actives (admin uniquement)"""
    try:
        if not current_admin:
            raise HTTPException(
                status_code=401,
                detail="Non authentifié"
            )
        
        # Nettoyer les sessions expirées
        expired_count = admin_auth.cleanup_expired_sessions()
        
        # Récupérer les informations sur les sessions
        active_sessions = []
        for token, session_data in admin_auth.active_sessions.items():
            session_info = admin_auth.get_session_info(token)
            if session_info:
                active_sessions.append(session_info)
        
        return {
            "total_sessions": len(active_sessions),
            "expired_cleaned": expired_count,
            "sessions": active_sessions
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des infos de session: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la récupération des informations de session"
        )
