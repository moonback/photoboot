# Routes API pour le photobooth

from . import health, config_api, auth, admin, upload, frames, printing, email

__all__ = [
    "health",
    "config_api", 
    "auth",
    "admin",
    "upload",
    "frames",
    "printing",
    "email"
]
