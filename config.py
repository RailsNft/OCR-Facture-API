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
    sirene_api_key: Optional[str] = os.getenv("SIRENE_API_KEY", None)
    sirene_api_secret: Optional[str] = os.getenv("SIRENE_API_SECRET", None)
    
    class Config:
        env_file = ".env"


settings = Settings()

