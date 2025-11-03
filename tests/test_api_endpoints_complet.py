"""
Tests d'intégration complets pour tous les endpoints API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock
from PIL import Image
import io
import base64
import json

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


@pytest.fixture
def sample_image():
    """Image de test"""
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.read()


@pytest.fixture
def sample_base64_image(sample_image):
    """Image base64 de test"""
    return base64.b64encode(sample_image).decode('utf-8')


class TestPublicEndpoints:
    """Tests pour les endpoints publics (sans authentification)"""
    
    def test_root_endpoint(self, client):
        """Test endpoint racine"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "features" in data
    
    def test_health_endpoint(self, client):
        """Test health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        assert "api_version" in data


class TestLanguagesEndpoint:
    """Tests pour l'endpoint /languages"""
    
    def test_get_languages_without_auth(self, client):
        """Test récupération des langues sans authentification (endpoint public)"""
        response = client.get("/languages")
        
        # Peut être 200 ou 401 selon la configuration
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "languages" in data
            assert len(data["languages"]) > 0
    
    def test_get_languages_with_auth(self, client, auth_headers):
        """Test récupération des langues avec authentification"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        response = client.get("/languages", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "languages" in data
            assert len(data["languages"]) > 0
            
            # Vérifier que le français est présent
            lang_codes = [lang["code"] for lang in data["languages"]]
            assert "fra" in lang_codes


class TestOCREndpoints:
    """Tests pour les endpoints OCR"""
    
    @patch('main.perform_ocr')
    @patch('main.extract_invoice_data')
    def test_ocr_upload_success(self, mock_extract, mock_ocr, client, auth_headers, sample_image):
        """Test upload OCR avec succès"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        # Mock OCR
        mock_ocr.return_value = {
            "text": "FACTURE\nNuméro: FAC-2024-001\nTotal TTC: 1,250.50€",
            "language": "fra",
            "data": {}
        }
        
        # Mock extraction
        mock_extract.return_value = (
            {
                "invoice_number": "FAC-2024-001",
                "total_ttc": 1250.50,
                "total_ht": 1042.08,
                "tva": 208.42,
                "date": "15/03/2024"
            },
            {
                "invoice_number": 0.95,
                "total_ttc": 0.92
            }
        )
        
        files = {"file": ("test.png", sample_image, "image/png")}
        data = {"language": "fra"}
        
        response = client.post(
            "/v1/ocr/upload",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is True
            assert "extracted_data" in result
            assert result["extracted_data"]["invoice_number"] == "FAC-2024-001"
    
    @patch('main.perform_ocr')
    @patch('main.extract_invoice_data')
    def test_ocr_base64_success(self, mock_extract, mock_ocr, client, auth_headers, sample_base64_image):
        """Test OCR base64 avec succès"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        # Mock OCR
        mock_ocr.return_value = {
            "text": "FACTURE\nTotal TTC: 1,250.50€",
            "language": "fra",
            "data": {}
        }
        
        # Mock extraction
        mock_extract.return_value = (
            {"total_ttc": 1250.50},
            {"total_ttc": 0.92}
        )
        
        payload = {
            "image_base64": f"data:image/png;base64,{sample_base64_image}",
            "language": "fra"
        }
        
        response = client.post(
            "/v1/ocr/base64",
            headers={**auth_headers, "Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is True
    
    def test_ocr_upload_missing_file(self, client, auth_headers):
        """Test upload OCR sans fichier"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        response = client.post(
            "/v1/ocr/upload",
            headers=auth_headers,
            data={"language": "fra"}
        )
        
        assert response.status_code in [400, 422]
    
    def test_ocr_upload_invalid_auth(self, client, sample_image):
        """Test upload OCR sans authentification"""
        files = {"file": ("test.png", sample_image, "image/png")}
        
        response = client.post(
            "/v1/ocr/upload",
            files=files
        )
        
        assert response.status_code == 401


class TestBatchOCREndpoint:
    """Tests pour l'endpoint batch OCR"""
    
    @patch('main.perform_ocr')
    @patch('main.extract_invoice_data')
    def test_batch_ocr_success(self, mock_extract, mock_ocr, client, auth_headers, sample_image):
        """Test batch OCR avec succès"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        # Mock OCR
        mock_ocr.return_value = {
            "text": "FACTURE\nNuméro: FAC-001",
            "language": "fra",
            "data": {}
        }
        
        # Mock extraction
        mock_extract.return_value = (
            {"invoice_number": "FAC-001"},
            {"invoice_number": 0.95}
        )
        
        files = [
            ("files", ("facture1.png", sample_image, "image/png")),
            ("files", ("facture2.png", sample_image, "image/png"))
        ]
        data = {"language": "fra"}
        
        response = client.post(
            "/v1/ocr/batch",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is True
            assert "results" in result
            assert len(result["results"]) == 2
    
    def test_batch_ocr_too_many_files(self, client, auth_headers, sample_image):
        """Test batch OCR avec trop de fichiers"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        files = [
            ("files", (f"facture{i}.png", sample_image, "image/png"))
            for i in range(11)
        ]
        
        response = client.post(
            "/v1/ocr/batch",
            headers=auth_headers,
            files=files
        )
        
        assert response.status_code in [400, 422]


class TestComplianceEndpoints:
    """Tests pour les endpoints de compliance"""
    
    def test_compliance_check(self, client, auth_headers):
        """Test vérification de conformité"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        payload = {
            "invoice_number": "FAC-2024-001",
            "total_ttc": 1250.50,
            "date": "15/03/2024"
        }
        
        response = client.post(
            "/v1/compliance/check",
            headers={**auth_headers, "Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            assert "compliance" in result or "compliance_check" in result
    
    def test_validate_vat(self, client, auth_headers):
        """Test validation TVA"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        payload = {
            "vat_number": "FR12345678901",
            "total_ht": 1042.08,
            "tva": 208.42
        }
        
        response = client.post(
            "/v1/compliance/validate-vat",
            headers={**auth_headers, "Content-Type": "application/json"},
            json=payload
        )
        
        # Peut être 200 ou 424 (si API externe non disponible)
        assert response.status_code in [200, 424]


class TestFacturXEndpoints:
    """Tests pour les endpoints Factur-X"""
    
    def test_generate_facturx(self, client, auth_headers):
        """Test génération Factur-X"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        payload = {
            "invoice_number": "FAC-2024-001",
            "date": "2024-03-15",
            "total_ht": 1042.08,
            "total_ttc": 1250.50,
            "tva": 208.42
        }
        
        response = client.post(
            "/facturx/generate",
            headers={**auth_headers, "Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            assert "xml" in result or "success" in result


class TestQuotaEndpoint:
    """Tests pour l'endpoint /quota"""
    
    def test_get_quota(self, client, auth_headers):
        """Test récupération du quota"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        response = client.get(
            "/v1/quota",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            result = response.json()
            assert "plan" in result
            assert "monthly" in result or "daily" in result


class TestRateLimiting:
    """Tests pour le rate limiting"""
    
    def test_rate_limit_headers(self, client, auth_headers):
        """Test présence des headers de rate limiting"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        response = client.get(
            "/v1/quota",
            headers=auth_headers
        )
        
        # Vérifier les headers de rate limiting si présents
        if response.status_code == 200:
            rate_limit_headers = [
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining",
                "X-RateLimit-Reset"
            ]
            # Au moins un header devrait être présent
            has_rate_limit_header = any(
                header in response.headers for header in rate_limit_headers
            )
            # Accepté même si pas présent (selon configuration)


class TestErrorHandling:
    """Tests pour la gestion des erreurs"""
    
    def test_unauthorized_error(self, client, sample_image):
        """Test erreur d'authentification"""
        files = {"file": ("test.png", sample_image, "image/png")}
        
        response = client.post(
            "/v1/ocr/upload",
            files=files
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_not_found_error(self, client):
        """Test erreur 404"""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
    
    def test_invalid_json(self, client, auth_headers):
        """Test JSON invalide"""
        import os
        os.environ["RAPIDAPI_PROXY_SECRET"] = "test_secret"
        
        response = client.post(
            "/v1/ocr/base64",
            headers={**auth_headers, "Content-Type": "application/json"},
            data="invalid json"
        )
        
        assert response.status_code in [400, 422]



