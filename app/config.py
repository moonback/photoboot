import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from loguru import logger
from .models import Config, SecurityConfig, AdminConfig
import bcrypt


class ConfigManager:
    """Gestionnaire de configuration avec priorité: .env > config.yaml > défauts"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.yaml"
        self.env_file = self.config_dir / ".env"
        self._config: Optional[Config] = None
        self._start_time = None
        
        # Charger les variables d'environnement
        self._load_env()
        
        # Charger la configuration
        self._load_config()
        
        # Configurer les logs
        self._setup_logging()
    
    def _load_env(self):
        """Charge les variables d'environnement depuis .env"""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info(f"Variables d'environnement chargées depuis {self.env_file}")
        else:
            logger.warning(f"Fichier .env non trouvé dans {self.config_dir}")
    
    def _load_config(self):
        """Charge la configuration depuis config.yaml et surcharge avec .env"""
        config_data = self._load_yaml_config()
        
        # Surcharge avec les variables d'environnement
        config_data = self._override_with_env(config_data)
        
        # Validation et création de l'objet Config
        try:
            self._config = Config(**config_data)
            logger.info("Configuration chargée et validée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la configuration: {e}")
            raise
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier YAML"""
        if not self.config_file.exists():
            logger.error(f"Fichier de configuration {self.config_file} non trouvé")
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                logger.info(f"Configuration YAML chargée depuis {self.config_file}")
                return config_data
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier YAML: {e}")
            raise
    
    def _override_with_env(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Surcharge la configuration avec les variables d'environnement"""
        env_mappings = {
            'SECRET_KEY': ('security', 'secret_key'),
            'ADMIN_USERNAME': ('admin', 'username'),
            'ADMIN_PASSWORD': ('admin', 'password_hash'),
            'HOST': ('server', 'host'),
            'PORT': ('server', 'port'),
            'DEBUG': ('app', 'debug'),
            'SESSION_TIMEOUT': ('security', 'session_timeout'),
            'BCRYPT_ROUNDS': ('security', 'bcrypt_rounds'),
            'UPLOAD_DIR': ('storage', 'upload_dir'),
            'MAX_FILE_SIZE': ('storage', 'max_file_size'),
            'LOG_LEVEL': ('logging', 'level'),
            'LOG_ROTATION': ('logging', 'rotation'),
            'LOG_RETENTION': ('logging', 'retention')
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Navigation dans la structure de configuration
                current = config_data
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Conversion des types selon le chemin
                if config_path[-1] in ['port', 'session_timeout', 'bcrypt_rounds', 'max_file_size']:
                    try:
                        current[config_path[-1]] = int(env_value)
                    except ValueError:
                        logger.warning(f"Impossible de convertir {env_var}={env_value} en entier")
                        continue
                elif config_path[-1] in ['debug']:
                    current[config_path[-1]] = env_value.lower() in ['true', '1', 'yes', 'on']
                else:
                    current[config_path[-1]] = env_value
                
                logger.debug(f"Variable d'environnement {env_var} surcharge la configuration")
        
        # Gestion spéciale du mot de passe admin (hashage bcrypt)
        if 'ADMIN_PASSWORD' in os.environ:
            password = os.environ['ADMIN_PASSWORD']
            if password and not password.startswith('$2b$'):  # Pas déjà hashé
                rounds = int(os.getenv('BCRYPT_ROUNDS', 12))
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds))
                config_data['admin']['password_hash'] = password_hash.decode('utf-8')
                logger.info("Mot de passe admin hashé avec bcrypt")
        
        return config_data
    
    def _setup_logging(self):
        """Configure le système de logging avec loguru"""
        if not self._config:
            return
        
        # Supprimer le handler par défaut
        logger.remove()
        
        # Ajouter le handler personnalisé
        log_config = self._config.logging
        logger.add(
            "logs/photobooth.log",
            level=log_config.level,
            rotation=log_config.rotation,
            retention=log_config.retention,
            format=log_config.format,
            encoding="utf-8"
        )
        
        # Handler pour la console en mode debug
        if self._config.app.debug:
            logger.add(
                lambda msg: print(msg, end=""),
                level="DEBUG",
                format="{time:HH:mm:ss} | {level} | {message}"
            )
        
        logger.info("Système de logging configuré")
    
    @property
    def config(self) -> Config:
        """Retourne la configuration actuelle"""
        return self._config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration par chemin (ex: 'server.port')"""
        if not self._config:
            return default
        
        keys = key_path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = getattr(current, key)
            return current
        except AttributeError:
            return default
    
    def reload(self):
        """Recharge la configuration depuis les fichiers"""
        logger.info("Rechargement de la configuration...")
        self._load_env()
        self._load_config()
    
    def save_config(self, config_data: Dict[str, Any]):
        """Sauvegarde la configuration dans le fichier YAML"""
        try:
            # Créer le dossier de configuration s'il n'existe pas
            self.config_dir.mkdir(exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"Configuration sauvegardée dans {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False


# Instance globale du gestionnaire de configuration
config_manager = ConfigManager()
