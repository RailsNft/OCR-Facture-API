"""
Tests unitaires pour le client SDK Python
"""

import pytest
import responses
from unittest.mock import Mock, patch, mock_open
from ocr_facture_api import OCRFactureAPI
from ocr_facture_api.exceptions import (
    OCRFactureAPIError,
    OCRFactureAuthError,
    OCRFactureRateLimitError,
    OCRFactureValidationError,
)


class TestOCRFactureAPI:
    """Tests pour la classe OCRFactureAPI"""
    
    @pytest.fixture
    def api(self):
        """Fixture pour créer une instance de l'API"""
        return OCRFactureAPI(api_key="test_api_key")
    
    @pytest.fixture
    def mock_response_success(self):
        """Mock d'une réponse réussie"""
        return {
            "success": True,
            "cached": False,
            "data": {
                "text": "FACTURE\nNuméro: FAC-2024-001",
                "language": "fra"
            },
            "extracted_data": {
                "invoice_number": "FAC-2024-001",
                "total_ttc": 1250.50,
                "total_ht": 1042.08,
                "tva": 208.42,
                "date": "15/03/2024",
                "vendor": "Société Example SARL",
                "client": "Client ABC"
            },
            "confidence_scores": {
                "invoice_number": 0.95,
                "total_ttc": 0.92
            }
        }
    
    @responses.activate
    def test_extract_from_file_success(self, api, mock_response_success):
        """Test extraction depuis fichier avec succès"""
        responses.add(
            responses.POST,
            "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload",
            json=mock_response_success,
            status=200
        )
        
        with patch("builtins.open", mock_open(read_data=b"fake image data")):
            result = api.extract_from_file("test_facture.pdf", language="fra")
        
        assert result["success"] is True
        assert result["extracted_data"]["invoice_number"] == "FAC-2024-001"
        assert result["extracted_data"]["total_ttc"] == 1250.50
    
    @responses.activate
    def test_extract_from_base64_success(self, api, mock_response_success):
        """Test extraction depuis base64 avec succès"""
        responses.add(
            responses.POST,
            "https://ocr-facture-api-production.up.railway.app/v1/ocr/base64",
            json=mock_response_success,
            status=200
        )
        
        base64_data = "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
        result = api.extract_from_base64(base64_data, language="fra")
        
        assert result["success"] is True
        assert result["extracted_data"]["invoice_number"] == "FAC-2024-001"
    
    @responses.activate
    def test_batch_extract_success(self, api):
        """Test traitement par lot avec succès"""
        mock_batch_response = {
            "success": True,
            "results": [
                {
                    "success": True,
                    "extracted_data": {"invoice_number": "FAC-001"}
                },
                {
                    "success": True,
                    "extracted_data": {"invoice_number": "FAC-002"}
                }
            ],
            "total_processed": 2,
            "total_cached": 0
        }
        
        responses.add(
            responses.POST,
            "https://ocr-facture-api-production.up.railway.app/v1/ocr/batch",
            json=mock_batch_response,
            status=200
        )
        
        with patch("builtins.open", mock_open(read_data=b"fake image data")):
            result = api.batch_extract(["facture1.pdf", "facture2.pdf"])
        
        assert result["success"] is True
        assert result["total_processed"] == 2
        assert len(result["results"]) == 2
    
    @responses.activate
    def test_batch_extract_too_many_files(self, api):
        """Test que batch_extract rejette plus de 10 fichiers"""
        files = [f"facture{i}.pdf" for i in range(11)]
        
        with pytest.raises(OCRFactureValidationError) as exc_info:
            api.batch_extract(files)
        
        assert "Maximum 10 fichiers" in str(exc_info.value)
    
    @responses.activate
    def test_auth_error(self, api):
        """Test gestion erreur d'authentification"""
        responses.add(
            responses.POST,
            "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload",
            json={"error": "Unauthorized"},
            status=401
        )
        
        with patch("builtins.open", mock_open(read_data=b"fake image data")):
            with pytest.raises(OCRFactureAuthError):
                api.extract_from_file("test.pdf")
    
    @responses.activate
    def test_rate_limit_error(self, api):
        """Test gestion erreur rate limit"""
        responses.add(
            responses.POST,
            "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload",
            json={"error": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": "60"}
        )
        
        with patch("builtins.open", mock_open(read_data=b"fake image data")):
            with pytest.raises(OCRFactureRateLimitError) as exc_info:
                api.extract_from_file("test.pdf")
            
            assert exc_info.value.retry_after == 60
    
    @responses.activate
    def test_validation_error(self, api):
        """Test gestion erreur de validation"""
        responses.add(
            responses.POST,
            "https://ocr-facture-api-production.up.railway.app/v1/compliance/check",
            json={"detail": "Facture non conforme"},
            status=422
        )
        
        with pytest.raises(OCRFactureValidationError):
            api.check_compliance({"invoice_number": "TEST"})
    
    @responses.activate
    def test_check_compliance(self, api):
        """Test validation de conformité"""
        mock_compliance = {
            "success": True,
            "compliance": {
                "compliance_check": {
                    "compliant": True,
                    "score": 95.0,
                    "missing_fields": []
                }
            }
        }
        
        responses.add(
            responses.POST,
            "https://ocr-facture-api-production.up.railway.app/v1/compliance/check",
            json=mock_compliance,
            status=200
        )
        
        result = api.check_compliance({"invoice_number": "FAC-001"})
        assert result["compliance"]["compliance_check"]["compliant"] is True
    
    @responses.activate
    def test_generate_facturx(self, api):
        """Test génération Factur-X"""
        mock_facturx = {
            "success": True,
            "xml": "<?xml version='1.0'?><Invoice>...</Invoice>",
            "format": "Factur-X EN16931"
        }
        
        responses.add(
            responses.POST,
            "https://ocr-facture-api-production.up.railway.app/facturx/generate",
            json=mock_facturx,
            status=200
        )
        
        result = api.generate_facturx({"invoice_number": "FAC-001"})
        assert result["success"] is True
        assert "xml" in result
    
    @responses.activate
    def test_get_supported_languages(self, api):
        """Test récupération langues supportées"""
        mock_languages = {
            "languages": [
                {"code": "fra", "name": "Français"},
                {"code": "eng", "name": "English"}
            ]
        }
        
        responses.add(
            responses.GET,
            "https://ocr-facture-api-production.up.railway.app/v1/languages",
            json=mock_languages,
            status=200
        )
        
        result = api.get_supported_languages()
        assert len(result["languages"]) > 0
        assert any(lang["code"] == "fra" for lang in result["languages"])
    
    @responses.activate
    def test_get_quota(self, api):
        """Test récupération quota"""
        mock_quota = {
            "plan": "PRO",
            "monthly": {"limit": 20000, "remaining": 19500},
            "daily": {"limit": 666, "remaining": 600}
        }
        
        responses.add(
            responses.GET,
            "https://ocr-facture-api-production.up.railway.app/v1/quota",
            json=mock_quota,
            status=200
        )
        
        result = api.get_quota()
        assert "plan" in result
        assert "monthly" in result
    
    @responses.activate
    def test_health_check(self, api):
        """Test health check"""
        mock_health = {
            "status": "healthy",
            "api_version": "2.0.0"
        }
        
        responses.add(
            responses.GET,
            "https://ocr-facture-api-production.up.railway.app/health",
            json=mock_health,
            status=200
        )
        
        result = api.health_check()
        assert result["status"] == "healthy"
    
    def test_custom_base_url(self):
        """Test utilisation d'une URL de base personnalisée"""
        api = OCRFactureAPI(
            api_key="test_key",
            base_url="https://custom-api.example.com"
        )
        assert api.base_url == "https://custom-api.example.com"
    
    def test_timeout_configuration(self):
        """Test configuration du timeout"""
        api = OCRFactureAPI(api_key="test_key", timeout=120)
        assert api.timeout == 120
    
    @responses.activate
    def test_idempotency_key(self, api, mock_response_success):
        """Test utilisation d'une clé d'idempotence"""
        responses.add(
            responses.POST,
            "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload",
            json=mock_response_success,
            status=200
        )
        
        with patch("builtins.open", mock_open(read_data=b"fake image data")):
            result = api.extract_from_file(
                "test.pdf",
                idempotency_key="test-uuid-123"
            )
        
        # Vérifier que le header Idempotency-Key a été envoyé
        request = responses.calls[0].request
        assert request.headers.get("Idempotency-Key") == "test-uuid-123"

