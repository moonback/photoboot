import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests pour l'endpoint de santé du système"""
    
    def test_health_check_success(self):
        """Test de la vérification de santé réussie"""
        response = client.get("/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "uptime" in data
        
        # Vérifier les valeurs
        assert data["status"] == "healthy"
        assert isinstance(data["uptime"], (int, float))
        assert data["uptime"] >= 0
    
    def test_health_detailed_success(self):
        """Test de la vérification de santé détaillée"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert "status" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "uptime_formatted" in data
        assert "config" in data
        assert "storage" in data
        
        # Vérifier les valeurs
        assert data["status"] == "healthy"
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0
        assert "h" in data["uptime_formatted"]  # Format: "Xh Ym Zs"
    
    def test_health_endpoint_available(self):
        """Test que l'endpoint de santé est accessible"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_response_format(self):
        """Test du format de la réponse de santé"""
        response = client.get("/health/")
        data = response.json()
        
        # Vérifier que tous les champs requis sont présents
        required_fields = ["status", "timestamp", "version", "uptime"]
        for field in required_fields:
            assert field in data, f"Champ manquant: {field}"
        
        # Vérifier les types des champs
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["uptime"], (int, float))
    
    def test_health_uptime_increases(self):
        """Test que le temps de fonctionnement augmente"""
        response1 = client.get("/health/")
        data1 = response1.json()
        uptime1 = data1["uptime"]
        
        # Attendre un peu
        import time
        time.sleep(0.1)
        
        response2 = client.get("/health/")
        data2 = response2.json()
        uptime2 = data2["uptime"]
        
        # Le temps de fonctionnement doit avoir augmenté
        assert uptime2 >= uptime1
    
    def test_health_status_always_healthy(self):
        """Test que le statut est toujours 'healthy' quand le système fonctionne"""
        response = client.get("/health/")
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_health_version_format(self):
        """Test du format de la version"""
        response = client.get("/health/")
        data = response.json()
        
        # La version doit être une chaîne non vide
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0
        
        # Format de version typique: X.Y.Z
        assert "." in data["version"]
    
    def test_health_timestamp_format(self):
        """Test du format du timestamp"""
        response = client.get("/health/")
        data = response.json()
        
        # Le timestamp doit être une chaîne de date ISO
        assert isinstance(data["timestamp"], str)
        
        # Vérifier que c'est un format de date valide
        from datetime import datetime
        try:
            datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Format de timestamp invalide: {data['timestamp']}")


class TestHealthDetailedEndpoint:
    """Tests pour l'endpoint de santé détaillée"""
    
    def test_detailed_health_config_section(self):
        """Test de la section configuration dans la santé détaillée"""
        response = client.get("/health/detailed")
        data = response.json()
        
        config = data.get("config", {})
        
        # Vérifier la structure de la configuration
        expected_config_sections = ["app", "server", "security", "storage", "logging"]
        for section in expected_config_sections:
            assert section in config, f"Section de configuration manquante: {section}"
    
    def test_detailed_health_storage_section(self):
        """Test de la section stockage dans la santé détaillée"""
        response = client.get("/health/detailed")
        data = response.json()
        
        storage = data.get("storage", {})
        
        # Vérifier que les informations de stockage sont présentes
        assert "total_files" in storage
        assert "total_size" in storage
        assert "upload_dir" in storage
        
        # Vérifier les types
        assert isinstance(storage["total_files"], int)
        assert isinstance(storage["total_size"], int)
        assert isinstance(storage["upload_dir"], str)
    
    def test_detailed_health_system_section(self):
        """Test de la section système dans la santé détaillée"""
        response = client.get("/health/detailed")
        data = response.json()
        
        system = data.get("system", {})
        
        # Le système peut ne pas avoir psutil, donc on vérifie juste la structure
        if "error" not in system:
            # Si psutil est disponible, vérifier les champs
            if "cpu_percent" in system:
                assert isinstance(system["cpu_percent"], (int, float))
                assert 0 <= system["cpu_percent"] <= 100
            
            if "memory_percent" in system:
                assert isinstance(system["memory_percent"], (int, float))
                assert 0 <= system["memory_percent"] <= 100


class TestHealthEndpointIntegration:
    """Tests d'intégration pour l'endpoint de santé"""
    
    def test_health_with_main_app(self):
        """Test que l'endpoint de santé fonctionne avec l'application principale"""
        # Test de l'endpoint racine
        response = client.get("/")
        assert response.status_code == 200
        
        # Test de l'endpoint de santé
        response = client.get("/health/")
        assert response.status_code == 200
        
        # Test de l'endpoint de statut
        response = client.get("/status")
        assert response.status_code == 200
    
    def test_health_endpoints_consistency(self):
        """Test de la cohérence entre les différents endpoints de santé"""
        # Endpoint de santé simple
        health_response = client.get("/health/")
        health_data = health_response.json()
        
        # Endpoint de santé détaillée
        detailed_response = client.get("/health/detailed")
        detailed_data = detailed_response.json()
        
        # Les deux doivent avoir le même statut
        assert health_data["status"] == detailed_data["status"]
        
        # Les temps de fonctionnement doivent être cohérents
        assert abs(health_data["uptime"] - detailed_data["uptime_seconds"]) < 1
    
    def test_health_error_handling(self):
        """Test de la gestion des erreurs dans l'endpoint de santé"""
        # L'endpoint de santé ne doit pas planter même en cas d'erreur
        # (il doit retourner une erreur HTTP appropriée)
        response = client.get("/health/")
        
        # Si le système est configuré correctement, on doit avoir 200
        # Si il y a un problème de configuration, on peut avoir 500 ou 503
        assert response.status_code in [200, 500, 503]
        
        if response.status_code != 200:
            # En cas d'erreur, vérifier que c'est une erreur structurée
            data = response.json()
            assert "detail" in data


if __name__ == "__main__":
    pytest.main([__file__])
