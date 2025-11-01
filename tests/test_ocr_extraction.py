"""
Tests unitaires pour l'extraction OCR
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import extract_invoice_data, perform_ocr


class TestInvoiceDataExtraction:
    """Tests pour l'extraction de données de facture"""
    
    def test_extract_total(self):
        """Test extraction du total"""
        ocr_result = {
            "text": "Total TTC: 1,250.50€\nMontant HT: 1,041.67€",
            "data": {},
            "language": "fra"
        }
        
        extracted, confidence = extract_invoice_data(ocr_result)
        
        assert extracted["total_ttc"] == 1250.50
        assert extracted["total_ht"] == 1041.67
        assert confidence["total_ttc"] > 0
    
    def test_extract_invoice_number(self):
        """Test extraction du numéro de facture"""
        ocr_result = {
            "text": "Facture N° FAC-2024-001\nDate: 15/03/2024",
            "data": {},
            "language": "fra"
        }
        
        extracted, confidence = extract_invoice_data(ocr_result)
        
        assert "FAC-2024-001" in extracted["invoice_number"] or extracted["invoice_number"] is not None
        assert confidence["invoice_number"] > 0
    
    def test_extract_date(self):
        """Test extraction de la date"""
        ocr_result = {
            "text": "Date d'émission: 15/03/2024",
            "data": {},
            "language": "fra"
        }
        
        extracted, confidence = extract_invoice_data(ocr_result)
        
        assert extracted["date"] is not None
        assert "2024" in extracted["date"] or "03" in extracted["date"]
        assert confidence["date"] > 0
    
    def test_extract_items(self):
        """Test extraction des lignes de facture"""
        ocr_result = {
            "text": """
            Description    Qté    Prix    Total
            Article 1     2      500.00  1000.00
            Article 2     1      250.50  250.50
            """,
            "data": {},
            "language": "fra"
        }
        
        extracted, confidence = extract_invoice_data(ocr_result)
        
        assert len(extracted["items"]) > 0
        assert confidence["items"] > 0
    
    def test_empty_text(self):
        """Test avec texte vide"""
        ocr_result = {
            "text": "",
            "data": {},
            "language": "fra"
        }
        
        extracted, confidence = extract_invoice_data(ocr_result)
        
        assert extracted["text"] == ""
        assert extracted["total"] is None
        assert extracted["invoice_number"] is None


class TestOCRProcessing:
    """Tests pour le traitement OCR"""
    
    @patch('main.pytesseract')
    def test_perform_ocr_image(self, mock_tesseract):
        """Test OCR sur une image"""
        # Mock Tesseract
        mock_tesseract.get_tesseract_version.return_value = "5.0.0"
        mock_tesseract.image_to_string.return_value = "Test invoice text"
        mock_tesseract.image_to_data.return_value = {}
        mock_tesseract.get_languages.return_value = ["fra", "eng"]
        
        # Créer une image de test
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = perform_ocr(img_bytes.read(), language="fra", is_pdf=False)
        
        assert result["text"] == "Test invoice text"
        assert result["language"] == "fra"
        mock_tesseract.image_to_string.assert_called_once()
    
    @patch('main.pytesseract')
    def test_perform_ocr_language_fallback(self, mock_tesseract):
        """Test fallback de langue si langue non disponible"""
        mock_tesseract.get_tesseract_version.return_value = "5.0.0"
        mock_tesseract.get_languages.return_value = ["eng"]  # Pas de fra
        
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        mock_tesseract.image_to_string.return_value = "Test"
        mock_tesseract.image_to_data.return_value = {}
        
        result = perform_ocr(img_bytes.read(), language="fra", is_pdf=False)
        
        # Devrait fallback sur eng
        assert result["language"] == "eng"


class TestConfidenceScores:
    """Tests pour les scores de confiance"""
    
    def test_confidence_scores_present(self):
        """Test que les scores de confiance sont présents"""
        ocr_result = {
            "text": "Total TTC: 1,250.50€",
            "data": {},
            "language": "fra"
        }
        
        extracted, confidence = extract_invoice_data(ocr_result)
        
        assert "total" in confidence
        assert "total_ttc" in confidence
        assert "total_ht" in confidence
        assert "date" in confidence
        assert "invoice_number" in confidence
        assert all(0 <= v <= 1 for v in confidence.values() if v is not None)

