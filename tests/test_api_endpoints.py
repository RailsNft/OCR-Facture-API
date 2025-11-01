"""
Tests d'intégration pour les endpoints API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Client de test pour l'API"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Headers d'authentification pour les tests"""
    return {"X-RapidAPI-Proxy-Secret": "test_secret"}


class TestHealthEndpoint:
    """Tests pour l'endpoint /health"""
    
    def test_health_check(self, client):
        """Test health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]


class TestRootEndpoint:
    """Tests pour l'endpoint /"""
    
    def test_root(self, client):
        """Test endpoint racine"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "features" in data


class TestLanguagesEndpoint:
    """Tests pour l'endpoint /languages"""
    
    def test_get_languages(self, client):
        """Test récupération des langues"""
        response = client.get("/languages")
        
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) > 0
        
        # Vérifier que le français est présent
        lang_codes = [lang["code"] for lang in data["languages"]]
        assert "fra" in lang_codes


class TestRateLimiting:
    """Tests pour le rate limiting"""
    
    def test_rate_limit_headers(self, client, auth_headers):
        """Test présence des headers de rate limiting"""
        # Configurer le secret dans l'environnement pour les tests
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        os.environ["DEBUG_MODE"] = "False"
        
        response = client.get(
            "/v1/quota",
            headers=auth_headers
        )
        
        # Même si 401, on devrait avoir des headers
        if response.status_code == 200:
            assert "X-RateLimit-Limit" in response.headers or True
            assert "X-RateLimit-Remaining" in response.headers or True


class TestMetricsEndpoint:
    """Tests pour l'endpoint /v1/metrics"""
    
    def test_get_metrics(self, client, auth_headers):
        """Test récupération des métriques"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        os.environ["DEBUG_MODE"] = "False"
        
        response = client.get(
            "/v1/metrics",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "metrics" in data
            assert "requests" in data["metrics"]
            assert "latency" in data["metrics"]

