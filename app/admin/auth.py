import bcrypt
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from loguru import logger
from ..config import config_manager
from ..models import LoginRequest, LoginResponse, LogoutResponse


class AdminAuth:
    """Gestionnaire d'authentification admin avec sessions signées"""
    
    def __init__(self):
        self.config = config_manager.config.security
        self.admin_config = config_manager.config.admin
        
        # Sérialiseur pour les sessions signées
        self.serializer = URLSafeTimedSerializer(
            self.config.secret_key,
            salt="admin-session"
        )
        
        # Stockage des sessions actives (en mémoire pour cette étape)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def authenticate(self, login_data: LoginRequest) -> LoginResponse:
        """Authentifie un utilisateur admin"""
        try:
            # Vérification du nom d'utilisateur
            if login_data.username != self.admin_config.username:
                logger.warning(f"Tentative de connexion avec un nom d'utilisateur invalide: {login_data.username}")
                return LoginResponse(
                    success=False,
                    message="Nom d'utilisateur ou mot de passe incorrect"
                )
            
            # Vérification du mot de passe avec bcrypt
            if not self._verify_password(login_data.password, self.admin_config.password_hash):
                logger.warning(f"Tentative de connexion avec un mot de passe invalide pour l'utilisateur: {login_data.username}")
                return LoginResponse(
                    success=False,
                    message="Nom d'utilisateur ou mot de passe incorrect"
                )
            
            # Génération du token de session
            session_data = {
                "username": login_data.username,
                "login_time": time.time(),
                "expires_at": time.time() + self.config.session_timeout
            }
            
            token = self.serializer.dumps(session_data)
            
            # Stockage de la session
            self.active_sessions[token] = session_data
            
            logger.info(f"Connexion admin réussie pour l'utilisateur: {login_data.username}")
            
            return LoginResponse(
                success=True,
                message="Connexion réussie",
                token=token
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {e}")
            return LoginResponse(
                success=False,
                message="Erreur interne lors de l'authentification"
            )
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Vérifie un mot de passe avec bcrypt"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
            return False
    
    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Valide un token de session"""
        try:
            # Vérification dans les sessions actives
            if token in self.active_sessions:
                session_data = self.active_sessions[token]
                
                # Vérification de l'expiration
                if time.time() > session_data["expires_at"]:
                    logger.info(f"Session expirée pour l'utilisateur: {session_data['username']}")
                    del self.active_sessions[token]
                    return None
                
                return session_data
            
            # Vérification du token signé (fallback)
            session_data = self.serializer.loads(
                token,
                max_age=self.config.session_timeout
            )
            
            # Si le token est valide, le stocker dans les sessions actives
            if session_data:
                self.active_sessions[token] = {
                    "username": session_data.get("username"),
                    "login_time": session_data.get("login_time", time.time()),
                    "expires_at": time.time() + self.config.session_timeout
                }
                return self.active_sessions[token]
            
            return None
            
        except SignatureExpired:
            logger.info("Token de session expiré")
            return None
        except BadSignature:
            logger.warning("Token de session invalide")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la session: {e}")
            return None
    
    def logout(self, token: str) -> LogoutResponse:
        """Déconnecte un utilisateur admin"""
        try:
            if token in self.active_sessions:
                username = self.active_sessions[token].get("username", "unknown")
                del self.active_sessions[token]
                logger.info(f"Déconnexion admin pour l'utilisateur: {username}")
                
                return LogoutResponse(
                    success=True,
                    message="Déconnexion réussie"
                )
            else:
                return LogoutResponse(
                    success=False,
                    message="Session non trouvée"
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            return LogoutResponse(
                success=False,
                message="Erreur lors de la déconnexion"
            )
    
    def refresh_session(self, token: str) -> Optional[str]:
        """Rafraîchit une session expirée"""
        try:
            if token in self.active_sessions:
                session_data = self.active_sessions[token]
                
                # Mise à jour de l'expiration
                session_data["expires_at"] = time.time() + self.config.session_timeout
                
                # Génération d'un nouveau token
                new_token = self.serializer.dumps(session_data)
                
                # Remplacer l'ancien token
                self.active_sessions[new_token] = session_data
                del self.active_sessions[token]
                
                logger.debug(f"Session rafraîchie pour l'utilisateur: {session_data['username']}")
                return new_token
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement de la session: {e}")
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """Nettoie les sessions expirées"""
        try:
            current_time = time.time()
            expired_tokens = []
            
            for token, session_data in self.active_sessions.items():
                if current_time > session_data["expires_at"]:
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del self.active_sessions[token]
            
            if expired_tokens:
                logger.info(f"{len(expired_tokens)} sessions expirées nettoyées")
            
            return len(expired_tokens)
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des sessions: {e}")
            return 0
    
    def get_session_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'une session"""
        try:
            if token in self.active_sessions:
                session_data = self.active_sessions[token]
                return {
                    "username": session_data["username"],
                    "login_time": datetime.fromtimestamp(session_data["login_time"]).isoformat(),
                    "expires_at": datetime.fromtimestamp(session_data["expires_at"]).isoformat(),
                    "remaining_time": max(0, session_data["expires_at"] - time.time())
                }
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos de session: {e}")
            return None
    
    def get_active_sessions_count(self) -> int:
        """Retourne le nombre de sessions actives"""
        return len(self.active_sessions)


# Instance globale du gestionnaire d'authentification
admin_auth = AdminAuth()
