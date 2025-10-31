import os
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
    
    class Config:
        env_file = ".env"


settings = Settings()

