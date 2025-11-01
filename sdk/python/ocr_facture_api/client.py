"""
Client principal pour l'API OCR Facture France
"""

import base64
import requests
from typing import Optional, List, Dict, Any, Union, BinaryIO
from pathlib import Path
import json

from .exceptions import (
    OCRFactureAPIError,
    OCRFactureAuthError,
    OCRFactureRateLimitError,
    OCRFactureValidationError,
    OCRFactureServerError,
)


class OCRFactureAPI:
    """
    Client Python pour l'API OCR Facture France
    
    Usage:
        >>> api = OCRFactureAPI(api_key="votre_cle_api", base_url="https://votre-api.com")
        >>> result = api.extract_from_file("facture.pdf")
        >>> print(result.invoice_number)
        >>> print(result.total_ttc)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://ocr-facture-api-production.up.railway.app",
        timeout: int = 60,
        verify_ssl: bool = True
    ):
        """
        Initialise le client API
        
        Args:
            api_key: Clé API RapidAPI ou X-RapidAPI-Proxy-Secret
            base_url: URL de base de l'API (optionnel)
            timeout: Timeout en secondes pour les requêtes (défaut: 60)
            verify_ssl: Vérifier les certificats SSL (défaut: True)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # Headers par défaut
        self.session.headers.update({
            "X-RapidAPI-Proxy-Secret": api_key,
            "Content-Type": "application/json"
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Effectue une requête HTTP vers l'API
        
        Args:
            method: Méthode HTTP (GET, POST, etc.)
            endpoint: Endpoint API (ex: "/v1/ocr/upload")
            **kwargs: Arguments supplémentaires pour requests
            
        Returns:
            Réponse JSON de l'API
            
        Raises:
            OCRFactureAPIError: En cas d'erreur API
        """
        url = f"{self.base_url}{endpoint}"
        
        # Timeout par défaut
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        # SSL verification
        kwargs["verify"] = self.verify_ssl
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Gérer les erreurs HTTP
            if response.status_code == 401:
                raise OCRFactureAuthError(
                    "Clé API invalide ou manquante",
                    status_code=401,
                    response=response.json() if response.content else None
                )
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise OCRFactureRateLimitError(
                    "Quota dépassé. Veuillez réessayer plus tard.",
                    status_code=429,
                    retry_after=retry_after,
                    response=response.json() if response.content else None
                )
            elif response.status_code == 422:
                raise OCRFactureValidationError(
                    response.json().get("detail", "Erreur de validation"),
                    status_code=422,
                    response=response.json() if response.content else None
                )
            elif response.status_code >= 500:
                raise OCRFactureServerError(
                    f"Erreur serveur: {response.status_code}",
                    status_code=response.status_code,
                    response=response.json() if response.content else None
                )
            
            # Erreur HTTP autre
            response.raise_for_status()
            
            # Retourner JSON
            if response.content:
                return response.json()
            return {}
            
        except OCRFactureAPIError:
            raise
        except requests.exceptions.Timeout:
            raise OCRFactureServerError(
                f"Timeout lors de la requête vers {endpoint}",
                status_code=504
            )
        except requests.exceptions.RequestException as e:
            raise OCRFactureAPIError(
                f"Erreur de connexion: {str(e)}",
                status_code=None
            )
    
    def extract_from_file(
        self,
        file_path: Union[str, Path, BinaryIO],
        language: str = "fra",
        check_compliance: bool = False,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extrait les données d'une facture depuis un fichier
        
        Args:
            file_path: Chemin vers le fichier (str/Path) ou objet fichier ouvert
            language: Code langue pour OCR (fra, eng, deu, spa, ita, por). Défaut: fra
            check_compliance: Activer validation conformité FR (défaut: False)
            idempotency_key: Clé d'idempotence (UUID recommandé, optionnel)
            
        Returns:
            Résultat OCR avec données extraites
            
        Example:
            >>> result = api.extract_from_file("facture.pdf")
            >>> print(result["extracted_data"]["invoice_number"])
            >>> print(result["extracted_data"]["total_ttc"])
        """
        # Ouvrir le fichier si c'est un chemin
        if isinstance(file_path, (str, Path)):
            file_obj = open(file_path, "rb")
            should_close = True
        else:
            file_obj = file_path
            should_close = False
        
        try:
            files = {"file": file_obj}
            data = {
                "language": language,
                "check_compliance": str(check_compliance).lower()
            }
            
            headers = {}
            if idempotency_key:
                headers["Idempotency-Key"] = idempotency_key
            
            return self._request(
                "POST",
                "/v1/ocr/upload",
                files=files,
                data=data,
                headers=headers
            )
        finally:
            if should_close:
                file_obj.close()
    
    def extract_from_base64(
        self,
        base64_string: str,
        language: str = "fra",
        check_compliance: bool = False,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extrait les données d'une facture depuis une image encodée en base64
        
        Args:
            base64_string: Image encodée en base64 (avec ou sans préfixe data:)
            language: Code langue pour OCR (défaut: fra)
            check_compliance: Activer validation conformité FR (défaut: False)
            idempotency_key: Clé d'idempotence (optionnel)
            
        Returns:
            Résultat OCR avec données extraites
        """
        # Nettoyer le préfixe data: si présent
        if base64_string.startswith("data:"):
            base64_string = base64_string.split(",", 1)[1]
        
        data = {
            "image_base64": base64_string,
            "language": language,
            "check_compliance": str(check_compliance).lower()
        }
        
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        
        return self._request(
            "POST",
            "/v1/ocr/base64",
            data=data,
            headers=headers
        )
    
    def batch_extract(
        self,
        files: List[Union[str, Path, BinaryIO]],
        language: str = "fra",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Traite plusieurs factures en une seule requête (batch processing)
        
        Args:
            files: Liste de chemins de fichiers ou objets fichiers
            language: Code langue pour OCR (défaut: fra)
            idempotency_key: Clé d'idempotence (optionnel)
            
        Returns:
            Résultats batch avec liste des résultats pour chaque fichier
            
        Note:
            Maximum 10 fichiers par requête batch
        """
        if len(files) > 10:
            raise OCRFactureValidationError(
                "Maximum 10 fichiers par requête batch",
                status_code=400
            )
        
        # Encoder tous les fichiers en base64
        files_base64 = []
        file_handles = []
        
        try:
            for file_path in files:
                if isinstance(file_path, (str, Path)):
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                else:
                    file_data = file_path.read()
                    file_path.seek(0)  # Reset pour réutilisation éventuelle
                
                # Détecter le type MIME
                if isinstance(file_path, (str, Path)):
                    path_str = str(file_path)
                    if path_str.lower().endswith('.pdf'):
                        mime_prefix = "data:application/pdf;base64,"
                    elif path_str.lower().endswith(('.jpg', '.jpeg')):
                        mime_prefix = "data:image/jpeg;base64,"
                    elif path_str.lower().endswith('.png'):
                        mime_prefix = "data:image/png;base64,"
                    else:
                        mime_prefix = "data:image/jpeg;base64,"
                else:
                    mime_prefix = "data:image/jpeg;base64,"
                
                file_base64 = mime_prefix + base64.b64encode(file_data).decode('utf-8')
                files_base64.append(file_base64)
            
            data = {
                "files": files_base64,
                "language": language
            }
            
            headers = {}
            if idempotency_key:
                headers["Idempotency-Key"] = idempotency_key
            
            return self._request(
                "POST",
                "/v1/ocr/batch",
                json=data,
                headers=headers
            )
        finally:
            # Fermer les handles si nécessaire
            for handle in file_handles:
                if hasattr(handle, 'close'):
                    handle.close()
    
    def check_compliance(
        self,
        invoice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Vérifie la conformité d'une facture française
        
        Args:
            invoice_data: Données extraites de la facture (format JSON)
            
        Returns:
            Résultat de validation de conformité
        """
        return self._request(
            "POST",
            "/v1/compliance/check",
            json=invoice_data
        )
    
    def validate_vat(
        self,
        invoice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valide les taux et calculs de TVA pour une facture française
        
        Args:
            invoice_data: Données extraites avec montants HT, TTC, TVA
            
        Returns:
            Résultat de validation TVA
        """
        return self._request(
            "POST",
            "/compliance/validate-vat",
            json=invoice_data
        )
    
    def enrich_siret(
        self,
        siret: str
    ) -> Dict[str, Any]:
        """
        Enrichit les données avec l'API Sirene (Insee) à partir d'un SIRET
        
        Args:
            siret: Numéro SIRET (14 chiffres)
            
        Returns:
            Données enrichies depuis l'API Sirene
        """
        return self._request(
            "POST",
            "/compliance/enrich-siret",
            json={"siret": siret}
        )
    
    def validate_vies(
        self,
        vat_number: str
    ) -> Dict[str, Any]:
        """
        Valide un numéro TVA intracommunautaire via l'API VIES
        
        Args:
            vat_number: Numéro TVA intracom (ex: FR47945319300)
            
        Returns:
            Résultat de validation VIES
        """
        return self._request(
            "POST",
            "/compliance/validate-vies",
            json={"vat_number": vat_number}
        )
    
    def generate_facturx(
        self,
        invoice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère un XML Factur-X (EN16931) à partir des données de facture
        
        Args:
            invoice_data: Données de facture extraites
            
        Returns:
            XML Factur-X conforme EN16931
        """
        return self._request(
            "POST",
            "/facturx/generate",
            json=invoice_data
        )
    
    def parse_facturx(
        self,
        file_path: Union[str, Path, BinaryIO]
    ) -> Dict[str, Any]:
        """
        Extrait le XML Factur-X embarqué dans un PDF/A-3
        
        Args:
            file_path: Chemin vers le PDF Factur-X
            
        Returns:
            XML extrait et données parsées
        """
        if isinstance(file_path, (str, Path)):
            file_obj = open(file_path, "rb")
            should_close = True
        else:
            file_obj = file_path
            should_close = False
        
        try:
            files = {"file": file_obj}
            return self._request(
                "POST",
                "/facturx/parse",
                files=files
            )
        finally:
            if should_close:
                file_obj.close()
    
    def validate_facturx_xml(
        self,
        xml_content: str
    ) -> Dict[str, Any]:
        """
        Valide un XML Factur-X contre le schéma EN16931
        
        Args:
            xml_content: Contenu XML Factur-X (string)
            
        Returns:
            Résultat de validation avec erreurs et avertissements
        """
        return self._request(
            "POST",
            "/facturx/validate",
            json={"xml_content": xml_content}
        )
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """
        Retourne la liste des langues supportées pour l'OCR
        
        Returns:
            Liste des langues avec codes et noms
        """
        return self._request("GET", "/v1/languages")
    
    def get_quota(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le quota restant
        
        Returns:
            Informations sur quota, limites, utilisations
        """
        return self._request("GET", "/v1/quota")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé de l'API
        
        Returns:
            Statut de santé de l'API et dépendances
        """
        return self._request("GET", "/health")

