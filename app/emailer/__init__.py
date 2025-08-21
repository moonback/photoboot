"""
Module d'envoi d'email pour Photobooth
Support SMTP avec gestion des pièces jointes et consentement RGPD
"""

from .send import EmailSender

__all__ = ["EmailSender"]
