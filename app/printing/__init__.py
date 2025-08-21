"""
Module d'impression pour Photobooth
Support Windows-first avec fallback pour autres plateformes
"""

from .printer import PrinterManager

__all__ = ["PrinterManager"]
