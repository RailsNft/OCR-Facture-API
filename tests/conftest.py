"""
Configuration pytest pour les tests
"""

import pytest
import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Configure l'environnement pour les tests"""
    # Variables d'environnement pour les tests
    monkeypatch.setenv("RAPIDAPI_PROXY_SECRET", "test_secret")
    monkeypatch.setenv("DEBUG_MODE", "True")
    monkeypatch.setenv("FORCE_MEMORY_CACHE", "True")
    
    # Initialiser le cache mémoire pour les tests
    from cache_redis import init_cache_backend
    init_cache_backend(force_memory=True)

