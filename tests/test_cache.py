"""
Tests pour le système de cache
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cache_redis import (
    MemoryCacheBackend,
    get_cached,
    set_cached,
    delete_cached,
    init_cache_backend,
    get_cache_backend,
    get_cache_info
)


class TestMemoryCacheBackend:
    """Tests pour le cache mémoire"""
    
    def test_set_and_get(self):
        """Test stockage et récupération"""
        cache = MemoryCacheBackend()
        
        cache.set("test_key", {"data": "test_value"})
        result = cache.get("test_key")
        
        assert result is not None
        assert result["data"] == "test_value"
    
    def test_cache_expiration(self):
        """Test expiration du cache"""
        cache = MemoryCacheBackend()
        
        # Utiliser un TTL très court pour le test
        cache.set("test_key", {"data": "test_value"}, ttl_hours=0.0001)  # ~0.36 secondes
        
        # Attendre que le cache expire
        import time
        time.sleep(0.5)
        
        result = cache.get("test_key")
        assert result is None
    
    def test_delete(self):
        """Test suppression d'une clé"""
        cache = MemoryCacheBackend()
        
        cache.set("test_key", {"data": "test_value"})
        cache.delete("test_key")
        
        result = cache.get("test_key")
        assert result is None
    
    def test_clear(self):
        """Test vidage du cache"""
        cache = MemoryCacheBackend()
        
        cache.set("key1", {"data": "value1"})
        cache.set("key2", {"data": "value2"})
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cache_size_limit(self):
        """Test limite de taille du cache"""
        cache = MemoryCacheBackend()
        
        # Ajouter plus de 1000 entrées
        for i in range(1100):
            cache.set(f"key_{i}", {"data": f"value_{i}"})
        
        # Le cache devrait avoir été nettoyé (max 1000)
        assert len(cache.cache) <= 1000


class TestCacheFunctions:
    """Tests pour les fonctions de cache"""
    
    def test_get_set_cached(self):
        """Test fonctions get_cached et set_cached"""
        # Initialiser avec mémoire
        init_cache_backend(force_memory=True)
        
        set_cached("test_key", {"data": "test_value"})
        result = get_cached("test_key")
        
        assert result is not None
        assert result["data"] == "test_value"
    
    def test_delete_cached(self):
        """Test fonction delete_cached"""
        init_cache_backend(force_memory=True)
        
        set_cached("test_key", {"data": "test_value"})
        delete_cached("test_key")
        
        result = get_cached("test_key")
        assert result is None
    
    def test_get_cache_info(self):
        """Test récupération d'infos sur le cache"""
        init_cache_backend(force_memory=True)
        
        info = get_cache_info()
        
        assert "backend_type" in info
        assert "redis_available" in info
        assert info["backend_type"] == "MemoryCacheBackend"

