"""
Routes pour l'envoi d'email des photos
Gestion SMTP avec consentement RGPD et rate limiting
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
import time
from typing import Dict, Any

from ..models import EmailRequest, EmailResponse, GdprConsentResponse
from ..emailer.send import EmailSender
from ..config import config_manager


router = APIRouter(prefix="/email", tags=["email"])

# Instance du gestionnaire d'email
email_sender = None

# Rate limiting pour l'email
email_rate_limit = 10  # emails par heure
email_rate_window = 3600  # 1 heure
email_attempts = {}


def get_email_sender() -> EmailSender:
    """Récupère l'instance du gestionnaire d'email"""
    global email_sender
    if email_sender is None:
        # Convertir la configuration en dictionnaire
        if config_manager.config:
            config = {
                "email": {
                    "smtp_server": config_manager.config.email.smtp_server,
                    "smtp_port": config_manager.config.email.smtp_port,
                    "smtp_use_tls": config_manager.config.email.smtp_use_tls,
                    "smtp_use_ssl": config_manager.config.email.smtp_use_ssl,
                    "smtp_username": config_manager.config.email.smtp_username,
                    "smtp_password": config_manager.config.email.smtp_password,
                    "from_email": config_manager.config.email.from_email,
                    "from_name": config_manager.config.email.from_name,
                    "subject_template": config_manager.config.email.subject_template,
                    "body_template": config_manager.config.email.body_template,
                    "max_attachment_size": config_manager.config.email.max_attachment_size,
                    "thumbnail_size": config_manager.config.email.thumbnail_size,
                    "thumbnail_quality": config_manager.config.email.thumbnail_quality,
                    "gdpr_consent_required": config_manager.config.email.gdpr_consent_required,
                    "gdpr_consent_text": config_manager.config.email.gdpr_consent_text,
                    "gdpr_retention_days": config_manager.config.email.gdpr_retention_days,
                    "rate_limit_emails": config_manager.config.email.rate_limit_emails,
                    "rate_limit_window": config_manager.config.email.rate_limit_window
                }
            }
        else:
            config = {}
        email_sender = EmailSender(config)
    return email_sender


def check_email_rate_limit(request: Request) -> bool:
    """Vérifie le rate limiting pour l'envoi d'email"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Nettoyer les anciennes tentatives
    if client_ip in email_attempts:
        email_attempts[client_ip] = [t for t in email_attempts[client_ip] 
                                    if current_time - t < email_rate_window]
    
    # Vérifier la limite
    if client_ip not in email_attempts:
        email_attempts[client_ip] = []
    
    if len(email_attempts[client_ip]) >= email_rate_limit:
        return False
    
    # Ajouter la tentative actuelle
    email_attempts[client_ip].append(current_time)
    return True


@router.get("/gdpr-consent", response_model=GdprConsentResponse)
async def get_gdpr_consent():
    """Récupère le texte de consentement RGPD"""
    try:
        email_mgr = get_email_sender()
        consent_text = email_mgr.get_gdpr_consent_text()
        
        return GdprConsentResponse(
            consent_text=consent_text,
            required=email_mgr.gdpr_consent_required,
            retention_days=email_mgr.gdpr_retention_days
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du consentement RGPD: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du consentement RGPD: {str(e)}"
        )


@router.post("/send", response_model=EmailResponse)
async def send_photo_email(
    request: EmailRequest,
    http_request: Request = None
):
    """Envoie un email avec la photo en pièce jointe"""
    
    # Vérification du rate limiting
    if not check_email_rate_limit(http_request):
        raise HTTPException(
            status_code=429,
            detail=f"Trop de demandes d'envoi d'email. Limite: {email_rate_limit} par heure"
        )
    
    try:
        email_mgr = get_email_sender()
        
        # Validation des paramètres
        if not request.to_email:
            raise HTTPException(
                status_code=400,
                detail="Adresse email de destination requise"
            )
        
        if not request.photo_path:
            raise HTTPException(
                status_code=400,
                detail="Chemin de la photo requis"
            )
        
        if not request.download_link:
            raise HTTPException(
                status_code=400,
                detail="Lien de téléchargement requis"
            )
        
        # Vérification du consentement RGPD si requis
        if email_mgr.gdpr_consent_required and not request.consent_given:
            raise HTTPException(
                status_code=400,
                detail="Consentement RGPD requis pour l'envoi d'email"
            )
        
        # Envoi de l'email
        result = email_mgr.send_photo_email(
            request.to_email,
            request.photo_path,
            request.download_link,
            request.consent_given,
            request.user_name
        )
        
        if result["success"]:
            return EmailResponse(
                success=True,
                message="Email envoyé avec succès",
                to=result.get("to"),
                timestamp=result.get("timestamp")
            )
        else:
            return EmailResponse(
                success=False,
                message="Échec de l'envoi de l'email",
                error=result.get("error"),
                details=result.get("details")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de l'envoi de l'email: {str(e)}"
        )


@router.get("/status")
async def get_email_status():
    """Récupère le statut du service email"""
    try:
        email_mgr = get_email_sender()
        status = email_mgr.get_email_status()
        return status
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du statut email: {str(e)}"
        )


@router.get("/test")
async def test_email():
    """Test de la connectivité email"""
    try:
        email_mgr = get_email_sender()
        
        # Vérifier la configuration
        is_configured = email_mgr.is_configured()
        
        # Vérifier le rate limiting
        rate_ok, current_count = email_mgr.check_rate_limit()
        
        return {
            "status": "ok" if is_configured else "not_configured",
            "configured": is_configured,
            "smtp_server": email_mgr.smtp_server,
            "smtp_port": email_mgr.smtp_port,
            "from_email": email_mgr.from_email,
            "gdpr_required": email_mgr.gdpr_consent_required,
            "rate_limit": {
                "ok": rate_ok,
                "current_count": current_count,
                "max_emails": email_mgr.rate_limit_emails
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du test email: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/validate-email")
async def validate_email_format(email: str):
    """Valide le format d'une adresse email"""
    import re
    
    # Pattern simple de validation email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(email_pattern, email):
        return {"valid": True, "email": email}
    else:
        return {"valid": False, "email": email, "error": "Format d'email invalide"}
