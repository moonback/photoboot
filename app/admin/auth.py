import bcrypt
import time
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from loguru import logger
from ..config import config_manager
from ..models import LoginRequest, LoginResponse, LogoutResponse

# Import conditionnel pour Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis non disponible, utilisation du stockage en mémoire")

class AdminAuth:
    """Gestionnaire d'authentification admin avec sessions sécurisées et support Redis"""
    
    def __init__(self):
        self.config = config_manager.config.security
        self.admin_config = config_manager.config.admin
        
        # Sérialiseur pour les sessions signées
        self.serializer = URLSafeTimedSerializer(
            self.config.secret_key,
            salt="admin-session"
        )
        
        # Configuration Redis
        self.redis_client = None
        self.use_redis = False
        
        if REDIS_AVAILABLE and hasattr(config_manager.config, 'redis'):
            try:
                self.redis_client = redis.Redis(
                    host=config_manager.config.redis.host,
                    port=config_manager.config.redis.port,
                    db=config_manager.config.redis.db,
                    password=config_manager.config.redis.password,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # Test de connexion
                self.redis_client.ping()
                self.use_redis = True
                logger.info("Redis connecté pour la gestion des sessions")
            except Exception as e:
                logger.warning(f"Impossible de se connecter à Redis: {e}, utilisation du stockage en mémoire")
                self.redis_client = None
                self.use_redis = False
        
        # Stockage des sessions actives (fallback en mémoire)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Nettoyage périodique des sessions expirées
        self._cleanup_expired_sessions()
    
    def _get_session_key(self, token: str) -> str:
        """Génère une clé Redis pour une session"""
        return f"admin_session:{token}"
    
    def _store_session(self, token: str, session_data: Dict[str, Any]) -> bool:
        """Stocke une session dans Redis ou en mémoire"""
        try:
            if self.use_redis and self.redis_client:
                # Stockage dans Redis avec expiration
                session_key = self._get_session_key(token)
                session_json = json.dumps(session_data)
                self.redis_client.setex(
                    session_key,
                    self.config.session_timeout,
                    session_json
                )
                return True
            else:
                # Stockage en mémoire
                self.active_sessions[token] = session_data
                return True
        except Exception as e:
            logger.error(f"Erreur lors du stockage de la session: {e}")
            # Fallback en mémoire
            self.active_sessions[token] = session_data
            return True
    
    def _get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Récupère une session depuis Redis ou la mémoire"""
        try:
            if self.use_redis and self.redis_client:
                # Récupération depuis Redis
                session_key = self._get_session_key(token)
                session_json = self.redis_client.get(session_key)
                if session_json:
                    return json.loads(session_json)
                return None
            else:
                # Récupération depuis la mémoire
                return self.active_sessions.get(token)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la session: {e}")
            # Fallback en mémoire
            return self.active_sessions.get(token)
    
    def _delete_session(self, token: str) -> bool:
        """Supprime une session depuis Redis ou la mémoire"""
        try:
            if self.use_redis and self.redis_client:
                # Suppression depuis Redis
                session_key = self._get_session_key(token)
                return bool(self.redis_client.delete(session_key))
            else:
                # Suppression depuis la mémoire
                if token in self.active_sessions:
                    del self.active_sessions[token]
                    return True
                return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la session: {e}")
            # Fallback en mémoire
            if token in self.active_sessions:
                del self.active_sessions[token]
                return True
            return False
    
    def _cleanup_expired_sessions(self) -> int:
        """Nettoie les sessions expirées"""
        try:
            if self.use_redis and self.redis_client:
                # Redis gère automatiquement l'expiration
                return 0
            else:
                # Nettoyage manuel en mémoire
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
            self._store_session(token, session_data)
            
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
            session_data = self._get_session(token)
            
            if session_data:
                # Vérification de l'expiration
                if time.time() > session_data["expires_at"]:
                    logger.info(f"Session expirée pour l'utilisateur: {session_data['username']}")
                    self._delete_session(token)
                    return None
                
                return session_data
            
            # Vérification du token signé (fallback)
            session_data = self.serializer.loads(
                token,
                max_age=self.config.session_timeout
            )
            
            # Si le token est valide, le stocker dans les sessions actives
            if session_data:
                self._store_session(token, session_data)
                return self._get_session(token)
            
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
            if self._delete_session(token):
                username = self._get_session(token).get("username", "unknown")
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
            session_data = self._get_session(token)
            
            if session_data:
                # Mise à jour de l'expiration
                session_data["expires_at"] = time.time() + self.config.session_timeout
                
                # Génération d'un nouveau token
                new_token = self.serializer.dumps(session_data)
                
                # Remplacer l'ancien token
                self._store_session(new_token, session_data)
                self._delete_session(token)
                
                logger.debug(f"Session rafraîchie pour l'utilisateur: {session_data['username']}")
                return new_token
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement de la session: {e}")
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """Nettoie les sessions expirées"""
        return self._cleanup_expired_sessions()
    
    def get_session_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'une session"""
        try:
            session_data = self._get_session(token)
            if session_data:
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
    
    def get_authorization(self) -> Optional[str]:
        """Récupère l'autorisation depuis la requête (pour FastAPI Depends)"""
        # Cette méthode sera utilisée par FastAPI pour injecter l'autorisation
        return None
    
    def get_session_token(self) -> Optional[str]:
        """Récupère le token de session depuis les cookies (pour FastAPI Depends)"""
        # Cette méthode sera utilisée par FastAPI pour injecter le token de session
        return None


# Instance globale du gestionnaire d'authentification
admin_auth = AdminAuth()
