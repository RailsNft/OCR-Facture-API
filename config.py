import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Clé secrète pour l'authentification RapidAPI (à configurer sur RapidAPI)
    rapidapi_proxy_secret: str = os.getenv("RAPIDAPI_PROXY_SECRET", "")
    # Mode développement (True = pas besoin d'authentification, False = production)
    debug_mode: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    # Langue par défaut pour OCR
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "fra")
    # Clé API Sirene (Insee) pour enrichissement SIREN/SIRET (optionnel)
    # Option 1 : OAuth2 avec Client ID + Certificate (recommandé)
    sirene_client_id: Optional[str] = os.getenv("SIRENE_CLIENT_ID", None)
    sirene_client_certificate: Optional[str] = os.getenv("SIRENE_CLIENT_CERTIFICATE", None)
    # Option 2 : Consumer Key/Secret (ancien système)
    sirene_api_key: Optional[str] = os.getenv("SIRENE_API_KEY", None)
    sirene_api_secret: Optional[str] = os.getenv("SIRENE_API_SECRET", None)
    # Redis URL pour le cache (optionnel, utilise cache mémoire si non configuré)
    redis_url: Optional[str] = os.getenv("REDIS_URL", None)
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    # Forcer l'utilisation du cache mémoire même si Redis disponible
    force_memory_cache: bool = os.getenv("FORCE_MEMORY_CACHE", "False").lower() == "true"
    
    class Config:
        env_file = ".env"


settings = Settings()

