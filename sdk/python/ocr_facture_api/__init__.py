"""
OCR Facture API - SDK Python

SDK officiel pour l'API OCR Facture France.
Facilite l'intégration de l'extraction automatique de données de factures.
"""

from .client import OCRFactureAPI
from .exceptions import (
    OCRFactureAPIError,
    OCRFactureAuthError,
    OCRFactureRateLimitError,
    OCRFactureValidationError,
    OCRFactureServerError,
)

__version__ = "1.0.0"
__all__ = [
    "OCRFactureAPI",
    "OCRFactureAPIError",
    "OCRFactureAuthError",
    "OCRFactureRateLimitError",
    "OCRFactureValidationError",
    "OCRFactureServerError",
]

