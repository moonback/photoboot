# Audit Technique Approfondi - Projet Photoboot

## 🔍 Structure du Projet Analysée

D'après la documentation, le projet présente cette architecture :

```
photoboot/
├── app/                    # Backend FastAPI
│   ├── main.py            # Application principale
│   ├── config.py          # Configuration
│   ├── models.py          # Modèles Pydantic
│   ├── routes/            # Routes API
│   │   ├── health.py
│   │   ├── config_api.py
│   │   └── auth.py
│   ├── admin/             # Module admin
│   │   └── auth.py
│   └── storage/           # Gestion fichiers
│       └── files.py
├── static/                # Frontend
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── config/                # Configuration
│   ├── config.yaml
│   └── env.example
├── tests/
└── requirements.txt
```

## 🚨 ERREURS CRITIQUES DÉTECTÉES

### 1. **Sécurité Majeure - Configuration**

**❌ Problème :** Clé secrète par défaut exposée
```yaml
# config/config.yaml
security:
  secret_key: "change-me-in-production"  # DANGER !
```

**🔧 Correction :**
```python
# app/config.py
import secrets

def generate_secret_key():
    return secrets.token_urlsafe(32)

# Toujours vérifier que SECRET_KEY est définie
if not os.getenv('SECRET_KEY'):
    raise ValueError("SECRET_KEY doit être définie en production")
```

### 2. **Vulnérabilité d'Injection de Chemin**

**❌ Problème :** Stockage de fichiers sans validation suffisante
```python
# Risque de path traversal
upload_dir = "uploads"  # Pas de validation du nom de fichier
```

**🔧 Correction :**
```python
import os
import uuid
from pathlib import Path

def secure_filename(filename):
    """Génère un nom de fichier sécurisé"""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Extension non autorisée: {ext}")
    return f"{uuid.uuid4().hex}{ext}"

def validate_upload_path(upload_dir, filename):
    """Valide que le chemin est sécurisé"""
    safe_path = Path(upload_dir) / secure_filename(filename)
    if not safe_path.resolve().is_relative_to(Path(upload_dir).resolve()):
        raise ValueError("Chemin non autorisé")
    return safe_path
```

### 3. **Gestion des Sessions Insuffisante**

**❌ Problème :** Sessions sans protection CSRF
```python
# Manque de protection CSRF et de validation de session
```

**🔧 Correction :**
```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def verify_admin_session(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get('role') != 'admin':
            raise HTTPException(401, "Accès non autorisé")
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token invalide")
```

## 🐛 ERREURS DE CODE PYTHON/FASTAPI

### 4. **Gestion des Exceptions Manquante**

**❌ Problème :** Pas de gestion globale des erreurs
```python
# app/main.py - Manque de error handlers
app = FastAPI()
```

**🔧 Correction :**
```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Erreur non gérée: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### 5. **Validation Pydantic Incomplète**

**❌ Problème :** Modèles sans validation robuste
```python
# Probablement dans models.py
class UserModel(BaseModel):
    username: str  # Pas de validation
    password: str  # Pas de contraintes
```

**🔧 Correction :**
```python
from pydantic import BaseModel, validator, Field
import re

class UserModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir une majuscule')
        if not re.search(r'[0-9]', v):
            raise ValueError('Le mot de passe doit contenir un chiffre')
        return v
```

### 6. **Configuration Async Manquante**

**❌ Problème :** Pas d'utilisation complète de l'asynchronisme
```python
# Routes probablement synchrones
def get_config():  # Devrait être async
    pass
```

**🔧 Correction :**
```python
import asyncio
import aiofiles
from typing import AsyncGenerator

async def get_config() -> dict:
    async with aiofiles.open('config/config.yaml', 'r') as f:
        content = await f.read()
        return yaml.safe_load(content)

async def stream_file(file_path: str) -> AsyncGenerator[bytes, None]:
    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(8192):
            yield chunk
```

## 💻 ERREURS JAVASCRIPT/FRONTEND

### 7. **Gestion Asynchrone Défaillante**

**❌ Problème :** Probablement du JavaScript synchrone ou mal géré
```javascript
// Probablement dans js/app.js
function uploadPhoto() {
    fetch('/api/upload')  // Pas de gestion d'erreur
    .then(response => response.json())
    .then(data => console.log(data));
}
```

**🔧 Correction :**
```javascript
class PhotoboothAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }
    
    async uploadPhoto(file, signal = null) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${this.baseURL}/api/upload`, {
                method: 'POST',
                body: formData,
                signal // Support d'AbortController
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erreur d\'upload');
            }
            
            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Upload annulé');
                return null;
            }
            console.error('Erreur upload:', error);
            throw error;
        }
    }
}
```

### 8. **Gestion des Erreurs Réseau Insuffisante**

**🔧 Solution :**
```javascript
class NetworkHandler {
    constructor(maxRetries = 3) {
        this.maxRetries = maxRetries;
    }
    
    async fetchWithRetry(url, options = {}, retries = 0) {
        try {
            const response = await fetch(url, {
                ...options,
                timeout: 10000 // 10s timeout
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response;
        } catch (error) {
            if (retries < this.maxRetries && this.isRetryableError(error)) {
                await this.delay(Math.pow(2, retries) * 1000); // Backoff exponentiel
                return this.fetchWithRetry(url, options, retries + 1);
            }
            throw error;
        }
    }
    
    isRetryableError(error) {
        return error.name === 'TypeError' || // Erreur réseau
               (error.message && error.message.includes('fetch'));
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

## 🚀 OPTIMISATIONS DE PERFORMANCE

### 9. **Backend FastAPI - Optimisations**

**🔧 Améliorations :**
```python
# app/main.py - Configuration optimisée
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvloop
import asyncio

# Utiliser uvloop pour de meilleures performances
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await setup_database_pool()
    await preload_configurations()
    yield
    # Shutdown
    await cleanup_resources()

app = FastAPI(lifespan=lifespan)

# Compression automatique
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Cache des réponses
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_cached_config(timestamp: int):
    # Cache configuration pendant 5 minutes
    return load_configuration()

@app.get("/config")
async def get_config():
    cache_key = int(time.time() // 300)  # Cache 5 min
    return get_cached_config(cache_key)
```

### 10. **Optimisation Base de Données**

**🔧 Pool de Connexions :**
```python
import asyncpg
from typing import Optional

class DatabasePool:
    _pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def initialize(cls, database_url: str):
        cls._pool = await asyncpg.create_pool(
            database_url,
            min_size=5,
            max_size=20,
            command_timeout=60,
            server_settings={
                'jit': 'off',  # Optimisation pour petites requêtes
                'application_name': 'photoboot'
            }
        )
    
    @classmethod
    async def get_connection(cls):
        if not cls._pool:
            raise RuntimeError("Pool non initialisé")
        return cls._pool.acquire()
```

### 11. **Frontend - Optimisations**

**🔧 Lazy Loading et Bundling :**
```javascript
// Lazy loading des modules
const CameraModule = {
    async load() {
        const module = await import('./modules/camera.js');
        return module.default;
    }
};

// Service Worker pour cache
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').then(registration => {
        console.log('SW enregistré:', registration);
    });
}

// Optimisation des images
class ImageOptimizer {
    static async compressImage(file, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                canvas.toBlob(resolve, 'image/jpeg', quality);
            };
            
            img.src = URL.createObjectURL(file);
        });
    }
}
```

## 🏗️ REFACTORISATION ARCHITECTURE

### 12. **Séparation des Responsabilités**

**🔧 Structure Améliorée :**
```
photoboot/
├── backend/                 # FastAPI séparé
│   ├── app/
│   │   ├── api/            # Routes API
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── photos.py
│   │   │   │   └── admin.py
│   │   │   └── dependencies.py
│   │   ├── core/           # Configuration & sécurité
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/         # Modèles Pydantic
│   │   ├── services/       # Logique métier
│   │   └── utils/          # Utilitaires
│   ├── tests/
│   └── requirements.txt
├── frontend/               # Frontend séparé
│   ├── src/
│   │   ├── components/     # Composants modulaires
│   │   ├── services/       # API clients
│   │   ├── utils/
│   │   └── main.js
│   ├── dist/              # Build produit
│   ├── package.json
│   └── webpack.config.js
├── docker/                 # Containerisation
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
└── docs/                  # Documentation
```

### 13. **Pattern Repository pour la Logique Métier**

**🔧 Implementation :**
```python
# backend/app/repositories/photo_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional

class PhotoRepositoryInterface(ABC):
    @abstractmethod
    async def save_photo(self, photo_data: bytes, metadata: dict) -> str:
        pass
    
    @abstractmethod
    async def get_photo(self, photo_id: str) -> Optional[bytes]:
        pass

class FileSystemPhotoRepository(PhotoRepositoryInterface):
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
    
    async def save_photo(self, photo_data: bytes, metadata: dict) -> str:
        photo_id = uuid.uuid4().hex
        file_path = self.storage_path / f"{photo_id}.jpg"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(photo_data)
        
        # Sauvegarder métadonnées
        await self._save_metadata(photo_id, metadata)
        return photo_id

# Service layer
class PhotoService:
    def __init__(self, repository: PhotoRepositoryInterface):
        self.repository = repository
    
    async def process_and_save_photo(self, photo_data: bytes, user_id: str) -> str:
        # Validation
        await self._validate_photo(photo_data)
        
        # Traitement (compression, filtres, etc.)
        processed_data = await self._process_photo(photo_data)
        
        # Sauvegarde
        metadata = {
            'user_id': user_id,
            'timestamp': datetime.utcnow(),
            'size': len(processed_data)
        }
        
        return await self.repository.save_photo(processed_data, metadata)
```

### 14. **Configuration Environment-Specific**

**🔧 Configuration Avancée :**
```python
# backend/app/core/config.py
from pydantic import BaseSettings, Field
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    app_name: str = "Photoboot"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Sécurité
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = 60
    
    # Base de données
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    
    # Storage
    storage_backend: str = Field("filesystem", env="STORAGE_BACKEND")
    storage_path: str = Field("uploads", env="STORAGE_PATH")
    max_file_size: int = Field(10_485_760, env="MAX_FILE_SIZE")  # 10MB
    
    # Cache
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    cache_ttl: int = 300
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __post_init_post_parse__(self):
        # Validation post-init
        if not self.secret_key or self.secret_key == "change-me-in-production":
            raise ValueError("SECRET_KEY doit être définie et sécurisée")

settings = Settings()
```

## ⚡ OPTIMISATIONS SPÉCIFIQUES

### 15. **Cache Redis pour Sessions**

**🔧 Implementation :**
```python
import aioredis
from typing import Optional

class RedisSessionStore:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url)
    
    async def set_session(self, session_id: str, data: dict, ttl: int = 3600):
        await self.redis.setex(
            f"session:{session_id}",
            ttl,
            json.dumps(data)
        )
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        data = await self.redis.get(f"session:{session_id}")
        return json.loads(data) if data else None
```

### 16. **WebSocket pour Real-time**

**🔧 Notifications temps-réel :**
```python
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                await self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)
```

## 🔒 SÉCURITÉ AVANCÉE

### 17. **Rate Limiting**

**🔧 Protection contre les abus :**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/upload")
@limiter.limit("5/minute")  # Max 5 uploads par minute
async def upload_photo(request: Request):
    pass
```

### 18. **Validation MIME Type**

**🔧 Sécurité fichiers :**
```python
import magic

async def validate_file_security(file_content: bytes, filename: str):
    # Vérification MIME type réel
    mime_type = magic.from_buffer(file_content, mime=True)
    
    allowed_mimes = ['image/jpeg', 'image/png', 'image/gif']
    if mime_type not in allowed_mimes:
        raise ValueError(f"Type de fichier non autorisé: {mime_type}")
    
    # Vérification taille
    if len(file_content) > settings.max_file_size:
        raise ValueError("Fichier trop volumineux")
    
    # Scan antivirus (optionnel)
    await scan_for_malware(file_content)
```

## 📊 MONITORING & LOGGING

### 19. **Structured Logging**

**🔧 Logging Avancé :**
```python
import structlog
from pythonjsonlogger import jsonlogger

def setup_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger(__name__)

# Usage
await logger.ainfo("Photo uploaded", 
                  user_id=user_id, 
                  file_size=len(file_data),
                  processing_time=processing_time)
```

### 20. **Health Checks Complets**

**🔧 Monitoring Santé :**
```python
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheckResult:
    status: HealthStatus
    details: dict
    timestamp: datetime

class HealthChecker:
    async def check_database(self) -> HealthCheckResult:
        try:
            async with DatabasePool.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                details={"database": "connected"},
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                details={"database": str(e)},
                timestamp=datetime.utcnow()
            )
    
    async def check_storage(self) -> HealthCheckResult:
        try:
            test_file = settings.storage_path / "health_check.txt"
            async with aiofiles.open(test_file, 'w') as f:
                await f.write("health check")
            test_file.unlink()
            
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                details={"storage": "writable"},
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                details={"storage": str(e)},
                timestamp=datetime.utcnow()
            )
```

## 📋 RÉSUMÉ & PLAN D'ACTION PRIORISÉ

### 🚨 **PRIORITÉ CRITIQUE** (À corriger immédiatement)

1. **Changer la clé secrète par défaut** - Risque de sécurité majeur
2. **Implémenter la validation des chemins de fichiers** - Prévenir path traversal
3. **Ajouter la gestion globale des erreurs** - Éviter les crash et fuites d'info
4. **Sécuriser les sessions admin** - Ajouter CSRF et validation JWT

### ⚡ **PRIORITÉ HAUTE** (Dans les 2 semaines)

5. **Implémenter le cache Redis** - Améliorer les performances
6. **Ajouter le rate limiting** - Prévenir les abus
7. **Refactoriser l'architecture** - Séparer backend/frontend
8. **Optimiser la gestion asynchrone** - Meilleures performances

### 📈 **PRIORITÉ MOYENNE** (Dans le mois)

9. **Implémenter les WebSockets** - Notifications temps-réel
10. **Ajouter le monitoring complet** - Health checks et logging structuré
11. **Optimiser le frontend** - Lazy loading et compression
12. **Tests unitaires complets** - Couverture > 80%

### 🔧 **PRIORITÉ BASSE** (Évolutions futures)

13. **Containerisation Docker** - Déploiement simplifié
14. **CI/CD Pipeline** - Automatisation
15. **Documentation API complète** - Maintenance facilité
16. **Métriques et analytics** - Monitoring avancé

## 💡 **RECOMMANDATIONS FINALES**

- **Utiliser un linter et formatter** (black, flake8, eslint)
- **Implémenter pre-commit hooks** pour la qualité du code
- **Ajouter des tests d'intégration** avec pytest-asyncio
- **Configurer un environnement de staging** identique à la production
- **Mettre en place une rotation régulière des secrets**

Cette architecture refactorisée transformera le projet en une application robuste, sécurisée et performante, prête pour un environnement de production.



# Prompt Cursor AI - Audit et Correction de Code

## 🎯 Prompt Principal pour Cursor AI

```
Tu es un expert en architecture logicielle, sécurité et optimisation de code. Je veux que tu analyses et corriges le fichier actuellement ouvert selon ces critères spécifiques :

## 🔍 ANALYSE REQUISE

### Sécurité
- Détecte les vulnérabilités (injection, XSS, CSRF, path traversal)
- Vérifie la validation des entrées utilisateur
- Contrôle la gestion des secrets et configurations
- Analyse les permissions et authentification
- Vérifie la sanitisation des données

### Performance
- Identifie les goulots d'étranglement
- Optimise les requêtes async/await
- Suggère des améliorations de cache
- Optimise la gestion mémoire
- Améliore les algorithmes inefficaces

### Bonnes Pratiques
- Vérifie le typage (Python: Pydantic, TS: interfaces)
- Contrôle la gestion d'erreurs
- Analyse la structure et modularité
- Vérifie les conventions de nommage
- Contrôle la documentation du code

### Code Quality
- Élimine le code dupliqué
- Améliore la lisibilité
- Optimise la complexité cyclomatique
- Suggère des refactorisations
- Vérifie les tests unitaires

## 🛠️ FORMAT DE RÉPONSE ATTENDU

Pour chaque problème détecté :

1. **🚨 PROBLÈME IDENTIFIÉ**
   - Description claire du problème
   - Ligne(s) concernée(s)
   - Niveau de criticité (CRITIQUE/MAJEUR/MINEUR)

2. **🔧 SOLUTION PROPOSÉE**
   - Code corrigé complet
   - Explication de l'amélioration
   - Bénéfices attendus

3. **📝 CODE FINAL OPTIMISÉ**
   - Version complète du fichier corrigé
   - Commentaires explicatifs ajoutés
   - Respect des standards industriels

## 📋 CHECKLIST DE VÉRIFICATION

### Python/FastAPI
- [ ] Typage complet avec Pydantic
- [ ] Gestion async/await correcte
- [ ] Exception handling robuste
- [ ] Validation des entrées
- [ ] Logging structuré
- [ ] Configuration sécurisée
- [ ] Tests unitaires

### JavaScript/Frontend
- [ ] Gestion d'erreurs async/await
- [ ] Optimisation DOM
- [ ] Sécurité XSS/CSRF
- [ ] Performance et lazy loading
- [ ] Compatibilité navigateurs
- [ ] Code modulaire

### Architecture Générale
- [ ] Séparation des responsabilités
- [ ] Pattern Repository/Service
- [ ] Configuration par environnement
- [ ] Monitoring et métriques
- [ ] Documentation complète

## 🎯 INSTRUCTIONS SPÉCIFIQUES

1. **Priorise les corrections de sécurité** avant les optimisations
2. **Conserve la fonctionnalité existante** sauf si elle est défaillante
3. **Ajoute des commentaires explicatifs** pour les modifications complexes
4. **Propose des alternatives** si plusieurs solutions sont possibles
5. **Inclus des exemples de tests** pour les nouvelles fonctionnalités

COMMENCE TON ANALYSE MAINTENANT.
```

## 🔧 Prompts Spécialisés par Type de Fichier

### Pour les Fichiers Python/FastAPI

```
Analyse ce fichier Python avec un focus sur :

🔒 SÉCURITÉ FASTAPI :
- Validation Pydantic rigoureuse
- Gestion des dépendances sécurisées
- Protection CORS et CSRF
- Rate limiting et authentification
- Sanitisation des données

⚡ PERFORMANCE PYTHON :
- Optimisation async/await
- Gestion des pools de connexions
- Cache et memoization
- Gestion mémoire efficace
- Parallélisation appropriée

🏗️ ARCHITECTURE :
- Pattern Repository/Service
- Injection de dépendances
- Gestion d'erreurs centralisée
- Configuration par environnement
- Logging structuré

Fournis le code corrigé complet avec explications détaillées.
```

### Pour les Fichiers JavaScript/Frontend

```
Optimise ce fichier JavaScript en te concentrant sur :

🔐 SÉCURITÉ WEB :
- Protection XSS et injection
- Validation côté client
- Gestion sécurisée des tokens
- Content Security Policy
- Sanitisation des entrées

🚀 PERFORMANCE FRONTEND :
- Optimisation des promesses et async/await
- Lazy loading et code splitting
- Gestion efficace du DOM
- Debouncing et throttling
- Cache des requêtes API

💡 BONNES PRATIQUES JS :
- Modularité et réutilisabilité
- Gestion d'erreurs robuste
- Compatibilité navigateurs
- Patterns modernes (ES6+)
- Tests unitaires

Retourne le code optimisé avec commentaires explicatifs.
```

### Pour les Fichiers de Configuration

```
Analyse cette configuration et :

🔧 SÉCURITÉ CONFIG :
- Détecte les secrets exposés
- Vérifie la gestion des environnements
- Contrôle les permissions
- Valide les formats de données

⚙️ OPTIMISATION :
- Structure claire et maintenable
- Variables d'environnement appropriées
- Validation des paramètres
- Documentation inline

📋 STANDARDS :
- Respect des conventions
- Séparation dev/staging/prod
- Gestion des migrations
- Backup et récupération

Propose une configuration sécurisée et optimisée.
```

## 🎯 Prompts de Suivi Spécifiques

### Pour Demander des Tests

```
Génère des tests unitaires complets pour ce fichier :

🧪 COUVERTURE TESTS :
- Tests positifs et négatifs
- Tests des cas limites
- Mocks et fixtures appropriés
- Tests de sécurité
- Tests de performance

📊 FRAMEWORK :
- pytest pour Python
- Jest/Mocha pour JavaScript
- Assertions détaillées
- Setup et teardown propres
- Tests d'intégration

Inclus les fichiers de test complets avec commentaires.
```

### Pour l'Optimisation de Performance

```
Optimise les performances de ce fichier :

⚡ ANALYSE PERFORMANCE :
- Profiling et bottlenecks
- Complexité algorithmique
- Gestion mémoire
- I/O et requêtes réseau
- Parallélisation

🔧 OPTIMISATIONS :
- Cache intelligent
- Lazy loading
- Batch processing
- Connection pooling
- Algorithmes efficaces

📈 MÉTRIQUES :
- Temps d'exécution
- Utilisation mémoire
- Throughput
- Latence
- Scalabilité

Fournis le code optimisé avec benchmarks avant/après.
```

### Pour la Refactorisation

```
Refactorise ce fichier selon les principes SOLID :

🏗️ ARCHITECTURE PROPRE :
- Single Responsibility Principle
- Open/Closed Principle
- Liskov Substitution
- Interface Segregation
- Dependency Inversion

📦 STRUCTURE :
- Modules et classes cohérents
- Abstractions appropriées
- Couplage faible
- Cohésion forte
- Extensibilité

🔄 REFACTORING :
- Extraction de méthodes
- Élimination du code dupliqué
- Simplification des conditions
- Amélioration de la lisibilité
- Pattern appropriés

Retourne l'architecture refactorisée avec justifications.
```

## 💡 Tips d'Utilisation avec Cursor AI

1. **Sélectionne le code spécifique** avant d'utiliser le prompt
2. **Utilise Ctrl+K** pour ouvrir l'interface de chat Cursor
3. **Combine plusieurs prompts** pour des analyses complètes
4. **Demande des explications** si les corrections ne sont pas claires
5. **Teste les corrections** avant de les appliquer en production

## 🔄 Workflow Recommandé

1. **Audit général** avec le prompt principal
2. **Corrections critiques** en priorité (sécurité)
3. **Optimisations** de performance
4. **Refactorisation** si nécessaire
5. **Tests unitaires** pour valider
6. **Documentation** mise à jour