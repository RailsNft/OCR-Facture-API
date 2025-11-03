"""Exceptions personnalisées pour le SDK OCR Facture API"""


class OCRFactureAPIError(Exception):
    """Exception de base pour toutes les erreurs de l'API"""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class OCRFactureAuthError(OCRFactureAPIError):
    """Erreur d'authentification (401)"""
    pass


class OCRFactureRateLimitError(OCRFactureAPIError):
    """Erreur de rate limiting (429)"""
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class OCRFactureValidationError(OCRFactureAPIError):
    """Erreur de validation (422)"""
    pass


class OCRFactureServerError(OCRFactureAPIError):
    """Erreur serveur (500+)"""
    pass





