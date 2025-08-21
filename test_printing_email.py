#!/usr/bin/env python3
"""
Script de test pour les fonctionnalités d'impression et d'email
Teste les endpoints et la connectivité des services
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PHOTO_PATH = "static/img/sample-photo.jpg"  # Photo de test

def test_health():
    """Test du healthcheck enrichi"""
    print("🔍 Test du healthcheck...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Healthcheck OK - Status: {data['status']}")
            print(f"   Caméra: {data['camera_status']['status']}")
            print(f"   Disque: {data['disk_space'].get('free_gb', 'N/A')} GB libre")
            print(f"   Imprimante: {data['printer_status']['available']}")
            print(f"   Email: {data['email_status']['configured']}")
            return True
        else:
            print(f"❌ Healthcheck échoué - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur healthcheck: {e}")
        return False

def test_printing():
    """Test des fonctionnalités d'impression"""
    print("\n🖨️ Test des fonctionnalités d'impression...")
    
    # Test 1: Lister les imprimantes
    try:
        response = requests.get(f"{BASE_URL}/print/printers")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Imprimantes trouvées: {len(data['printers'])}")
            for printer in data['printers']:
                print(f"   - {printer['name']} ({printer['platform']})")
            if data['default_printer']:
                print(f"   Imprimante par défaut: {data['default_printer']}")
        else:
            print(f"❌ Erreur récupération imprimantes: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test imprimantes: {e}")
    
    # Test 2: Statut d'impression
    try:
        response = requests.get(f"{BASE_URL}/print/test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test impression: {data['status']}")
            print(f"   Support Windows: {data.get('windows_support', False)}")
            print(f"   Support Unix: {data.get('unix_support', False)}")
        else:
            print(f"❌ Erreur test impression: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test impression: {e}")
    
    # Test 3: Impression (si photo de test disponible)
    if Path(TEST_PHOTO_PATH).exists():
        try:
            print(f"📸 Test impression avec {TEST_PHOTO_PATH}...")
            response = requests.post(f"{BASE_URL}/print/photo", json={
                "photo_path": TEST_PHOTO_PATH,
                "copies": 1
            })
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ Impression lancée: {data['message']}")
                else:
                    print(f"⚠️ Impression échouée: {data['error']}")
            else:
                print(f"❌ Erreur impression: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur test impression: {e}")
    else:
        print(f"⚠️ Photo de test non trouvée: {TEST_PHOTO_PATH}")

def test_email():
    """Test des fonctionnalités d'email"""
    print("\n📧 Test des fonctionnalités d'email...")
    
    # Test 1: Consentement RGPD
    try:
        response = requests.get(f"{BASE_URL}/email/gdpr-consent")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Consentement RGPD: {data['required']}")
            print(f"   Rétention: {data['retention_days']} jours")
            if data['consent_text']:
                print(f"   Texte: {data['consent_text'][:100]}...")
        else:
            print(f"❌ Erreur consentement RGPD: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test consentement: {e}")
    
    # Test 2: Statut email
    try:
        response = requests.get(f"{BASE_URL}/email/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statut email: {data['configured']}")
            if data['configured']:
                print(f"   Serveur: {data['smtp_server']}:{data['smtp_port']}")
                print(f"   Expéditeur: {data['from_email']}")
                print(f"   RGPD requis: {data['gdpr_required']}")
            else:
                print("   ⚠️ Service email non configuré")
        else:
            print(f"❌ Erreur statut email: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test statut email: {e}")
    
    # Test 3: Test de connectivité
    try:
        response = requests.get(f"{BASE_URL}/email/test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test email: {data['status']}")
            if 'rate_limit' in data:
                print(f"   Rate limit: {data['rate_limit']['current_count']}/{data['rate_limit']['max_emails']}")
        else:
            print(f"❌ Erreur test email: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test connectivité email: {e}")
    
    # Test 4: Validation email
    try:
        test_emails = ["test@example.com", "invalid-email", "user@domain.co.uk"]
        for email in test_emails:
            response = requests.post(f"{BASE_URL}/email/validate-email", data=email)
            if response.status_code == 200:
                data = response.json()
                status = "✅" if data['valid'] else "❌"
                print(f"   {status} {email}: {data['valid']}")
            else:
                print(f"   ❌ {email}: Erreur validation")
    except Exception as e:
        print(f"❌ Erreur test validation email: {e}")

def test_detailed_health():
    """Test du healthcheck détaillé"""
    print("\n📊 Test du healthcheck détaillé...")
    try:
        response = requests.get(f"{BASE_URL}/health/detailed")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Healthcheck détaillé OK")
            print(f"   Uptime: {data['uptime_formatted']}")
            print(f"   Composants: {len(data['components'])}")
            for name, component in data['components'].items():
                status = "✅" if component.get('available', False) else "❌"
                print(f"   {status} {name}: {component.get('status', 'N/A')}")
        else:
            print(f"❌ Healthcheck détaillé échoué: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur healthcheck détaillé: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 Test des fonctionnalités Photobooth - Impression et Email")
    print("=" * 60)
    
    # Vérifier la connectivité de base
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Serveur non accessible: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Impossible de se connecter au serveur: {e}")
        print(f"   Vérifiez que le serveur est démarré sur {BASE_URL}")
        sys.exit(1)
    
    # Tests
    health_ok = test_health()
    test_printing()
    test_email()
    test_detailed_health()
    
    print("\n" + "=" * 60)
    if health_ok:
        print("✅ Tests terminés avec succès")
    else:
        print("⚠️ Tests terminés avec des avertissements")
    
    print("\n💡 Conseils:")
    print("   - Vérifiez la configuration dans config/.env")
    print("   - Consultez les logs dans logs/")
    print("   - Testez les endpoints individuellement si nécessaire")

if __name__ == "__main__":
    main()
