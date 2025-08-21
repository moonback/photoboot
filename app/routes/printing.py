"""
Routes pour l'impression des photos
Gestion des imprimantes et impression avec rate limiting
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from loguru import logger
import time
from typing import Dict, Any

from ..models import PrintRequest, PrintResponse, PrintersResponse, PrinterInfo
from ..printing.printer import PrinterManager
from ..config import config_manager
from ..admin.auth import admin_auth


router = APIRouter(prefix="/print", tags=["impression"])

# Instance du gestionnaire d'impression
printer_manager = None

# Rate limiting pour l'impression
print_rate_limit = 5  # impressions par minute
print_rate_window = 60  # 1 minute
print_attempts = {}


def get_printer_manager() -> PrinterManager:
    """Récupère l'instance du gestionnaire d'impression"""
    global printer_manager
    if printer_manager is None:
        # Convertir la configuration en dictionnaire
        if config_manager.config:
            config = {
                "printing": {
                    "default_printer": config_manager.config.printing.default_printer,
                    "paper_size": config_manager.config.printing.paper_size,
                    "quality": config_manager.config.printing.quality,
                    "max_copies": config_manager.config.printing.max_copies,
                    "retry_attempts": config_manager.config.printing.retry_attempts,
                    "retry_delay": config_manager.config.printing.retry_delay
                }
            }
        else:
            config = {}
        printer_manager = PrinterManager(config)
    return printer_manager


def check_print_rate_limit(request: Request) -> bool:
    """Vérifie le rate limiting pour l'impression"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Nettoyer les anciennes tentatives
    if client_ip in print_attempts:
        print_attempts[client_ip] = [t for t in print_attempts[client_ip] 
                                    if current_time - t < print_rate_window]
    
    # Vérifier la limite
    if client_ip not in print_attempts:
        print_attempts[client_ip] = []
    
    if len(print_attempts[client_ip]) >= print_rate_limit:
        return False
    
    # Ajouter la tentative actuelle
    print_attempts[client_ip].append(current_time)
    return True


@router.get("/printers", response_model=PrintersResponse)
async def get_printers():
    """Récupère la liste des imprimantes disponibles"""
    try:
        printer_mgr = get_printer_manager()
        printers = printer_mgr.get_available_printers()
        default_printer = printer_mgr.get_default_printer()
        
        # Conversion en modèles Pydantic
        printer_models = [
            PrinterInfo(
                name=p["name"],
                port=p["port"],
                description=p["description"],
                platform=p["platform"]
            )
            for p in printers
        ]
        
        return PrintersResponse(
            printers=printer_models,
            default_printer=default_printer
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des imprimantes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des imprimantes: {str(e)}"
        )


@router.get("/status/{printer_name}")
async def get_printer_status(printer_name: str = None):
    """Récupère le statut d'une imprimante"""
    try:
        printer_mgr = get_printer_manager()
        status = printer_mgr.get_printer_status(printer_name)
        return status
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du statut: {str(e)}"
        )


@router.post("/photo", response_model=PrintResponse)
async def print_photo(
    request: PrintRequest,
    http_request: Request = None
):
    """Imprime une photo avec gestion des erreurs et retry"""
    
    # Vérification du rate limiting
    if not check_print_rate_limit(http_request):
        raise HTTPException(
            status_code=429,
            detail=f"Trop de demandes d'impression. Limite: {print_rate_limit} par minute"
        )
    
    try:
        printer_mgr = get_printer_manager()
        
        # Validation des paramètres
        if not request.photo_path:
            raise HTTPException(
                status_code=400,
                detail="Chemin de la photo requis"
            )
        
        if request.copies < 1 or request.copies > 10:
            raise HTTPException(
                status_code=400,
                detail="Nombre de copies invalide (1-10)"
            )
        
        # Impression
        result = printer_mgr.print_photo(
            request.photo_path,
            request.copies,
            request.printer_name
        )
        
        if result["success"]:
            return PrintResponse(
                success=True,
                message="Impression lancée avec succès",
                printer=result.get("printer"),
                copies=result.get("copies"),
                method=result.get("method")
            )
        else:
            return PrintResponse(
                success=False,
                message="Échec de l'impression",
                error=result.get("error"),
                details=result.get("details")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'impression: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de l'impression: {str(e)}"
        )


@router.get("/test")
async def test_printing():
    """Test de la connectivité d'impression"""
    try:
        printer_mgr = get_printer_manager()
        
        # Vérifier la disponibilité des imprimantes
        printers = printer_mgr.get_available_printers()
        default_printer = printer_mgr.get_default_printer()
        
        return {
            "status": "ok",
            "printers_available": len(printers),
            "default_printer": default_printer,
            "windows_support": hasattr(printer_mgr, 'WINDOWS_AVAILABLE') and printer_mgr.WINDOWS_AVAILABLE,
            "unix_support": hasattr(printer_mgr, 'LPR_AVAILABLE') and printer_mgr.LPR_AVAILABLE
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du test d'impression: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
