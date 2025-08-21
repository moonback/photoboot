import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
import os
from pathlib import Path

from .config import config_manager
from .routes import health, config_api, auth, admin, upload, frames, printing, email
from .admin.auth import admin_auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Démarrage
    logger.info("Démarrage de l'application Photobooth...")
    
    # Créer les dossiers nécessaires
    os.makedirs("logs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    # Vérifier la configuration
    if not config_manager.config:
        logger.error("Configuration non disponible, arrêt de l'application")
        raise RuntimeError("Configuration invalide")
    
    logger.info(f"Application {config_manager.config.app.name} v{config_manager.config.app.version} démarrée")
    logger.info(f"Serveur configuré sur {config_manager.config.server.host}:{config_manager.config.server.port}")
    
    yield
    
    # Arrêt
    logger.info("Arrêt de l'application Photobooth...")
    
    # Nettoyer les sessions expirées
    expired_count = admin_auth.cleanup_expired_sessions()
    if expired_count > 0:
        logger.info(f"{expired_count} sessions expirées nettoyées lors de l'arrêt")


# Création de l'application FastAPI
app = FastAPI(
    title=config_manager.config.app.name if config_manager.config else "Photobooth",
    version=config_manager.config.app.version if config_manager.config else "1.0.0",
    description="Application photobooth avec FastAPI backend et interface web",
    docs_url="/docs" if (config_manager.config and config_manager.config.app.debug) else None,
    redoc_url="/redoc" if (config_manager.config and config_manager.config.app.debug) else None,
    lifespan=lifespan
)

# Configuration des middlewares
if config_manager.config:
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # À restreindre en production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted Host (sécurité)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # À restreindre en production
    )


# Middleware de logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log de la requête entrante
    logger.info(f"Requête {request.method} {request.url.path} depuis {request.client.host}")
    
    # Traitement de la requête
    response = await call_next(request)
    
    # Calcul du temps de traitement
    process_time = time.time() - start_time
    
    # Log de la réponse
    logger.info(f"Réponse {response.status_code} en {process_time:.3f}s pour {request.method} {request.url.path}")
    
    # Ajouter le temps de traitement dans les headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Middleware de gestion des erreurs
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erreur non gérée: {exc} pour {request.method} {request.url.path}")
    
    return HTTPException(
        status_code=500,
        detail="Erreur interne du serveur"
    )


# Inclusion des routes
app.include_router(health.router)
app.include_router(config_api.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(upload.router)
app.include_router(frames.router)
app.include_router(printing.router)
app.include_router(email.router)


# Route racine - page d'accueil
@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil du photobooth"""
    try:
        # Lire le fichier HTML statique
        html_file = Path("static/index.html")
        if html_file.exists():
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            # Page HTML de fallback
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Photobooth</title>
                <style>
                    body { 
                        margin: 0; 
                        padding: 20px; 
                        font-family: Arial, sans-serif; 
                        background: #1a1a1a; 
                        color: white; 
                        text-align: center;
                    }
                    .container { 
                        max-width: 600px; 
                        margin: 100px auto; 
                    }
                    h1 { color: #00ff88; }
                    .status { 
                        background: #333; 
                        padding: 20px; 
                        border-radius: 10px; 
                        margin: 20px 0; 
                    }
                    .error { color: #ff4444; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎉 Photobooth</h1>
                    <div class="status">
                        <h2>Application en cours de démarrage...</h2>
                        <p>Si ce message persiste, vérifiez les logs de l'application.</p>
                    </div>
                    <div class="error">
                        <p>Fichier index.html non trouvé dans le dossier static/</p>
                    </div>
                </div>
            </body>
            </html>
            """)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de la page d'accueil: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement de la page d'accueil")


# Route d'administration - page d'administration
@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """Page d'administration du photobooth"""
    try:
        # Lire le fichier HTML d'administration
        html_file = Path("static/admin.html")
        if html_file.exists():
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            # Page HTML de fallback
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Administration - Photobooth</title>
                <style>
                    body { 
                        margin: 0; 
                        padding: 20px; 
                        font-family: Arial, sans-serif; 
                        background: #1a1a1a; 
                        color: white; 
                        text-align: center;
                    }
                    .container { 
                        max-width: 600px; 
                        margin: 100px auto; 
                    }
                    h1 { color: #00ff88; }
                    .status { 
                        background: #333; 
                        padding: 20px; 
                        border-radius: 10px; 
                        margin: 20px 0; 
                    }
                    .error { color: #ff4444; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚙️ Administration Photobooth</h1>
                    <div class="status">
                        <h2>Page d'administration non trouvée</h2>
                        <p>Le fichier admin.html n'existe pas dans le dossier static/</p>
                    </div>
                    <div class="error">
                        <p>Veuillez vérifier l'installation de l'application</p>
                    </div>
                </div>
            </body>
            </html>
            """)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de la page d'administration: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement de la page d'administration")


# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")


# Route de test simple
@app.get("/test")
async def test_endpoint():
    """Endpoint de test simple"""
    return {
        "message": "Photobooth API fonctionne !",
        "timestamp": time.time(),
        "config_loaded": config_manager.config is not None
    }


# Route pour vérifier l'état de la configuration
@app.get("/status")
async def status():
    """État général de l'application"""
    try:
        config_status = {
            "loaded": config_manager.config is not None,
            "app_name": config_manager.config.app.name if config_manager.config else None,
            "version": config_manager.config.app.version if config_manager.config else None,
            "debug": config_manager.config.app.debug if config_manager.config else None
        }
        
        storage_status = {
            "upload_dir_exists": Path("uploads").exists(),
            "static_dir_exists": Path("static").exists()
        }
        
        return {
            "status": "running",
            "config": config_status,
            "storage": storage_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du statut: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }


# Route pour servir les photos uploadées
@app.get("/uploads/{filename}")
async def serve_uploaded_file(filename: str):
    """Sert les fichiers uploadés (photos)"""
    try:
        file_path = Path("uploads") / filename
        
        # Vérifier que le fichier existe et est dans le dossier uploads
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        # Vérifier que le fichier est bien dans le dossier uploads (sécurité)
        if not str(file_path.resolve()).startswith(str(Path("uploads").resolve())):
            raise HTTPException(status_code=400, detail="Chemin de fichier invalide")
        
        # Déterminer le type MIME
        content_type = "image/jpeg"  # Par défaut
        if filename.lower().endswith('.png'):
            content_type = "image/png"
        elif filename.lower().endswith('.gif'):
            content_type = "image/gif"
        elif filename.lower().endswith('.bmp'):
            content_type = "image/bmp"
        
        # Retourner le fichier
        return FileResponse(
            file_path,
            media_type=content_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {filename}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la lecture du fichier")


# Route pour servir les fichiers des cadres
@app.get("/frames/{filename}")
async def serve_frame_file(filename: str):
    """Sert les fichiers des cadres"""
    try:
        file_path = Path("frames") / filename
        
        # Vérifier que le fichier existe et est dans le dossier frames
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        # Vérifier que le fichier est bien dans le dossier frames (sécurité)
        if not str(file_path.resolve()).startswith(str(Path("frames").resolve())):
            raise HTTPException(status_code=400, detail="Chemin de fichier invalide")
        
        # Retourner le fichier PNG
        return FileResponse(
            file_path,
            media_type="image/png",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier de cadre {filename}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la lecture du fichier de cadre")


if __name__ == "__main__":
    import uvicorn
    
    if config_manager.config:
        uvicorn.run(
            "app.main:app",
            host=config_manager.config.server.host,
            port=config_manager.config.server.port,
            reload=config_manager.config.app.debug,
            log_level=config_manager.config.logging.level.lower()
        )
    else:
        # Configuration par défaut si le gestionnaire n'est pas disponible
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
