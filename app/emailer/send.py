"""
Gestionnaire d'envoi d'email pour Photobooth
Support SMTP avec gestion des pièces jointes et consentement RGPD
"""

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger
from PIL import Image
import tempfile
import hashlib
import time


class EmailSender:
    """Gestionnaire d'envoi d'email avec support SMTP et pièces jointes"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.email_config = config.get("email", {})
        
        # Configuration SMTP
        self.smtp_server = self.email_config.get("smtp_server", "")
        self.smtp_port = self.email_config.get("smtp_port", 587)
        self.smtp_use_tls = self.email_config.get("smtp_use_tls", True)
        self.smtp_use_ssl = self.email_config.get("smtp_use_ssl", False)
        self.smtp_username = self.email_config.get("smtp_username", "")
        self.smtp_password = self.email_config.get("smtp_password", "")
        
        # Configuration de l'email
        self.from_email = self.email_config.get("from_email", "")
        self.from_name = self.email_config.get("from_name", "Photobooth")
        self.subject_template = self.email_config.get("subject_template", "Votre photo Photobooth")
        self.body_template = self.email_config.get("body_template", "")
        
        # Configuration des pièces jointes
        self.max_attachment_size = self.email_config.get("max_attachment_size", 10485760)  # 10MB
        self.thumbnail_size = self.email_config.get("thumbnail_size", (300, 300))
        self.thumbnail_quality = self.email_config.get("thumbnail_quality", 85)
        
        # Gestion des consentements RGPD
        self.gdpr_consent_required = self.email_config.get("gdpr_consent_required", True)
        self.gdpr_consent_text = self.email_config.get("gdpr_consent_text", "")
        self.gdpr_retention_days = self.email_config.get("gdpr_retention_days", 30)
        
        # Rate limiting
        self.rate_limit_emails = self.email_config.get("rate_limit_emails", 10)  # emails par heure
        self.rate_limit_window = self.email_config.get("rate_limit_window", 3600)  # 1 heure
        self._email_sent_times = []
        
        # Validation de la configuration
        self._validate_config()
    
    def _validate_config(self):
        """Valide la configuration email"""
        required_fields = ["smtp_server", "smtp_username", "smtp_password", "from_email"]
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        
        if missing_fields:
            logger.warning(f"Configuration email incomplète: champs manquants: {missing_fields}")
        
        if not self.smtp_server:
            logger.warning("Serveur SMTP non configuré - envoi d'email désactivé")
    
    def is_configured(self) -> bool:
        """Vérifie si l'envoi d'email est configuré"""
        return bool(self.smtp_server and self.smtp_username and self.smtp_password)
    
    def check_rate_limit(self) -> Tuple[bool, int]:
        """Vérifie le rate limiting pour l'envoi d'email"""
        current_time = time.time()
        
        # Nettoyer les anciens timestamps
        self._email_sent_times = [t for t in self._email_sent_times 
                                 if current_time - t < self.rate_limit_window]
        
        # Vérifier la limite
        if len(self._email_sent_times) >= self.rate_limit_emails:
            return False, len(self._email_sent_times)
        
        return True, len(self._email_sent_times)
    
    def send_photo_email(self, 
                        to_email: str, 
                        photo_path: str, 
                        download_link: str,
                        consent_given: bool = False,
                        user_name: str = "") -> Dict[str, any]:
        """Envoie un email avec la photo en pièce jointe"""
        
        # Vérification du consentement RGPD
        if self.gdpr_consent_required and not consent_given:
            return {
                "success": False,
                "error": "Consentement RGPD requis",
                "details": "L'utilisateur doit accepter les conditions d'utilisation"
            }
        
        # Vérification du rate limiting
        rate_ok, current_count = self.check_rate_limit()
        if not rate_ok:
            return {
                "success": False,
                "error": "Limite de taux dépassée",
                "details": f"Maximum {self.rate_limit_emails} emails par heure atteint"
            }
        
        # Vérification de la configuration
        if not self.is_configured():
            return {
                "success": False,
                "error": "Configuration email incomplète",
                "details": "Serveur SMTP ou identifiants manquants"
            }
        
        # Vérification du fichier photo
        if not os.path.exists(photo_path):
            return {
                "success": False,
                "error": "Fichier photo introuvable",
                "details": f"Chemin: {photo_path}"
            }
        
        try:
            # Création de la miniature
            thumbnail_path = self._create_thumbnail(photo_path)
            if not thumbnail_path:
                return {
                    "success": False,
                    "error": "Impossible de créer la miniature",
                    "details": "Erreur lors du traitement de l'image"
                }
            
            # Préparation du message
            msg = self._prepare_email_message(to_email, photo_path, thumbnail_path, 
                                           download_link, user_name)
            
            # Envoi de l'email
            result = self._send_email(msg)
            
            if result["success"]:
                # Enregistrer le timestamp pour le rate limiting
                self._email_sent_times.append(time.time())
                
                # Nettoyer la miniature temporaire
                if thumbnail_path != photo_path:
                    try:
                        os.remove(thumbnail_path)
                    except:
                        pass
                
                logger.info(f"Email envoyé avec succès à {to_email}")
                return result
            else:
                return result
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            return {
                "success": False,
                "error": "Erreur interne",
                "details": str(e)
            }
    
    def _create_thumbnail(self, photo_path: str) -> Optional[str]:
        """Crée une miniature de la photo pour l'email"""
        try:
            with Image.open(photo_path) as img:
                # Conversion en RGB si nécessaire
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Création de la miniature
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # Sauvegarde temporaire
                temp_path = tempfile.mktemp(suffix='.jpg')
                img.save(temp_path, 'JPEG', quality=self.thumbnail_quality)
                
                return temp_path
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de la miniature: {e}")
            return None
    
    def _prepare_email_message(self, 
                             to_email: str, 
                             photo_path: str, 
                             thumbnail_path: str,
                             download_link: str,
                             user_name: str) -> MIMEMultipart:
        """Prépare le message email avec pièces jointes"""
        msg = MIMEMultipart()
        msg['From'] = f"{self.from_name} <{self.from_email}>"
        msg['To'] = to_email
        msg['Subject'] = self.subject_template
        
        # Corps du message
        body = self._get_email_body(user_name, download_link)
        msg.attach(MIMEText(body, 'html'))
        
        # Pièce jointe: miniature
        if thumbnail_path and os.path.exists(thumbnail_path):
            with open(thumbnail_path, 'rb') as f:
                img_data = f.read()
                img_attachment = MIMEImage(img_data, name="photo_thumbnail.jpg")
                img_attachment.add_header('Content-Disposition', 'attachment', 
                                       filename="photo_thumbnail.jpg")
                msg.attach(img_attachment)
        
        # Pièce jointe: photo originale (si pas trop volumineuse)
        file_size = os.path.getsize(photo_path)
        if file_size <= self.max_attachment_size:
            with open(photo_path, 'rb') as f:
                photo_attachment = MIMEBase('application', 'octet-stream')
                photo_attachment.set_payload(f.read())
                encoders.encode_base64(photo_attachment)
                photo_attachment.add_header('Content-Disposition', 'attachment', 
                                         filename=os.path.basename(photo_path))
                msg.attach(photo_attachment)
        else:
            logger.info(f"Photo trop volumineuse pour pièce jointe: {file_size} bytes")
        
        return msg
    
    def _get_email_body(self, user_name: str, download_link: str) -> str:
        """Génère le corps de l'email HTML"""
        if self.body_template:
            return self.body_template.format(
                user_name=user_name,
                download_link=download_link
            )
        
        # Template par défaut
        return f"""
        <html>
        <body>
            <h2>Votre photo Photobooth</h2>
            <p>Bonjour {user_name or 'utilisateur'},</p>
            <p>Votre photo a été prise avec succès !</p>
            <p>Vous pouvez la télécharger en cliquant sur le lien suivant :</p>
            <p><a href="{download_link}">Télécharger ma photo</a></p>
            <p>La miniature est jointe à cet email.</p>
            <hr>
            <p><small>Cet email a été envoyé automatiquement par votre Photobooth.</small></p>
        </body>
        </html>
        """
    
    def _send_email(self, msg: MIMEMultipart) -> Dict[str, any]:
        """Envoie l'email via SMTP"""
        try:
            # Connexion au serveur SMTP
            if self.smtp_use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            # Configuration TLS si nécessaire
            if self.smtp_use_tls and not self.smtp_use_ssl:
                server.starttls(context=ssl.create_default_context())
            
            # Authentification
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Envoi de l'email
            text = msg.as_string()
            server.sendmail(self.from_email, msg['To'], text)
            server.quit()
            
            return {
                "success": True,
                "message": "Email envoyé avec succès",
                "to": msg['To'],
                "timestamp": time.time()
            }
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Erreur d'authentification SMTP: {e}")
            return {
                "success": False,
                "error": "Erreur d'authentification",
                "details": "Identifiants SMTP incorrects"
            }
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Destinataire refusé: {e}")
            return {
                "success": False,
                "error": "Destinataire invalide",
                "details": "Adresse email non valide ou refusée"
            }
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"Connexion SMTP perdue: {e}")
            return {
                "success": False,
                "error": "Connexion perdue",
                "details": "Le serveur SMTP a fermé la connexion"
            }
        except Exception as e:
            logger.error(f"Erreur SMTP: {e}")
            return {
                "success": False,
                "error": "Erreur SMTP",
                "details": str(e)
            }
    
    def get_gdpr_consent_text(self) -> str:
        """Récupère le texte de consentement RGPD"""
        if self.gdpr_consent_text:
            return self.gdpr_consent_text
        
        # Texte par défaut
        return """
        En utilisant ce service, vous consentez à ce que votre adresse email soit utilisée 
        pour l'envoi de votre photo. Vos données sont conservées pendant {} jours 
        et ne sont utilisées que pour ce service. Vous pouvez retirer votre consentement 
        à tout moment.
        """.format(self.gdpr_retention_days)
    
    def get_email_status(self) -> Dict[str, any]:
        """Récupère le statut du service email"""
        return {
            "configured": self.is_configured(),
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "from_email": self.from_email,
            "gdpr_required": self.gdpr_consent_required,
            "rate_limit": {
                "max_emails": self.rate_limit_emails,
                "window_seconds": self.rate_limit_window,
                "current_count": len(self._email_sent_times)
            }
        }
