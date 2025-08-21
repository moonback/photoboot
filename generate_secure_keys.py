#!/usr/bin/env python3
"""
Script de génération de clés sécurisées pour Photobooth
Utilisez ce script pour générer des clés sécurisées en production
"""

import secrets
import string
import hashlib
import base64
from pathlib import Path

def generate_secret_key(length: int = 64) -> str:
    """Génère une clé secrète aléatoire"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_bcrypt_salt() -> str:
    """Génère un salt bcrypt sécurisé"""
    return base64.b64encode(secrets.token_bytes(16)).decode('utf-8')

def generate_jwt_secret() -> str:
    """Génère un secret JWT sécurisé"""
    return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')

def generate_redis_password() -> str:
    """Génère un mot de passe Redis sécurisé"""
    return secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    import bcrypt
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def main():
    print("🔐 Génération de clés sécurisées pour Photobooth")
    print("=" * 50)
    
    # Générer les clés
    secret_key = generate_secret_key(64)
    bcrypt_salt = generate_bcrypt_salt()
    jwt_secret = generate_jwt_secret()
    redis_password = generate_redis_password()
    
    print(f"🔑 Clé secrète: {secret_key}")
    print(f"🧂 Salt bcrypt: {bcrypt_salt}")
    print(f"🎫 Secret JWT: {jwt_secret}")
    print(f"📡 Mot de passe Redis: {redis_password}")
    
    # Générer un mot de passe admin sécurisé
    admin_password = secrets.token_urlsafe(16)
    admin_password_hash = hash_password(admin_password)
    
    print(f"👤 Mot de passe admin: {admin_password}")
    print(f"🔒 Hash du mot de passe: {admin_password_hash}")
    
    # Créer le fichier de configuration sécurisé
    config_content = f"""# Configuration sécurisée générée automatiquement
# ATTENTION: Ne pas commiter ce fichier dans Git !

security:
  secret_key: "{secret_key}"
  bcrypt_rounds: 12
  session_timeout: 3600
  
  # Configuration CORS restrictive
  allowed_origins:
    - "https://votre-domaine.com"
    - "https://www.votre-domaine.com"
  
  allowed_hosts:
    - "votre-domaine.com"
    - "www.votre-domaine.com"
  
  # Limitation de débit
  rate_limit_requests: 50
  rate_limit_window: 60
  max_login_attempts: 3
  lockout_duration: 600

admin:
  username: "admin"
  password_hash: "{admin_password_hash}"

redis:
  host: "localhost"
  port: 6379
  db: 0
  password: "{redis_password}"
  ssl: false

# Variables d'environnement à définir
environment_variables:
  SECRET_KEY: "{secret_key}"
  ADMIN_PASSWORD: "{admin_password}"
  REDIS_PASSWORD: "{redis_password}"
  JWT_SECRET: "{jwt_secret}"
"""
    
    # Sauvegarder la configuration
    config_file = Path("config/secure_config.yaml")
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n✅ Configuration sauvegardée dans {config_file}")
    print("\n⚠️  IMPORTANT:")
    print("1. Changez le mot de passe admin par défaut")
    print("2. Ne commitez jamais ce fichier dans Git")
    print("3. Utilisez HTTPS en production")
    print("4. Configurez un pare-feu approprié")
    print("5. Surveillez les logs de sécurité")
    
    # Créer un fichier .env sécurisé
    env_content = f"""# Variables d'environnement sécurisées
# ATTENTION: Ne pas commiter ce fichier !

SECRET_KEY={secret_key}
ADMIN_PASSWORD={admin_password}
REDIS_PASSWORD={redis_password}
JWT_SECRET={jwt_secret}

# Configuration de production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Sécurité
SESSION_TIMEOUT=3600
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=3
LOCKOUT_DURATION=600

# CORS restrictif
ALLOWED_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
"""
    
    env_file = Path("config/.env.secure")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ Variables d'environnement sauvegardées dans {env_file}")
    print("\n🚀 Votre application est maintenant configurée de manière sécurisée !")

if __name__ == "__main__":
    main()
