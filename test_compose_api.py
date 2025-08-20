#!/usr/bin/env python3
"""
Script de test pour l'API de composition
"""

import requests
import os

def test_compose_api():
    """Teste l'API de composition avec une photo de test"""
    
    url = "http://localhost:8000/api/compose"
    
    # Vérifier que la photo de test existe
    photo_path = "data/photos/test_photo.jpg"
    if not os.path.exists(photo_path):
        print(f"Erreur: Photo de test non trouvée: {photo_path}")
        return
    
    # Préparer les données
    files = {
        'photos': ('test_photo.jpg', open(photo_path, 'rb'), 'image/jpeg')
    }
    
    data = {
        'template': 'strip_2x6',
        'text_overlay': 'Test Photobooth'
    }
    
    try:
        print("Envoi de la requête à l'API de composition...")
        response = requests.post(url, files=files, data=data)
        
        print(f"Statut de la réponse: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Succès! Résultat: {result}")
        else:
            print(f"Erreur: {response.text}")
            
    except Exception as e:
        print(f"Erreur lors de la requête: {e}")
    
    finally:
        # Fermer le fichier
        files['photos'][1].close()

if __name__ == "__main__":
    test_compose_api()
