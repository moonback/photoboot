#!/usr/bin/env python3
"""
Script de test pour l'API des cadres
"""

import requests
import json

def test_frames_api():
    """Teste l'API des cadres"""
    base_url = "http://localhost:8000"
    
    print("🧪 Test de l'API des cadres")
    print("=" * 40)
    
    # 1. Test de santé
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check échoué: {e}")
        return
    
    # 2. Test de connexion admin
    login_data = {
        "username": "admin",
        "password": "admin"  # Utilisez le mot de passe de votre .env
    }
    
    try:
        response = requests.post(f"{base_url}/admin/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Connexion admin réussie")
                session_token = result.get("token")
                
                # 3. Test de récupération des cadres
                headers = {"Authorization": f"Bearer {session_token}"}
                response = requests.get(f"{base_url}/admin/frames", headers=headers)
                
                if response.status_code == 200:
                    frames = response.json()
                    print(f"✅ Récupération des cadres: {len(frames.get('frames', []))} cadres trouvés")
                    
                    for frame in frames.get('frames', []):
                        print(f"   - {frame['name']} ({frame['position']}) - {'✅ Actif' if frame['active'] else '🔘 Inactif'}")
                else:
                    print(f"❌ Erreur lors de la récupération des cadres: {response.status_code}")
                    print(response.text)
            else:
                print(f"❌ Échec de la connexion: {result.get('message')}")
        else:
            print(f"❌ Erreur de connexion: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    test_frames_api()
