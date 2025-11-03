"""
Cache Redis avec fallback sur cache mémoire
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

# Tentative d'import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Cache mémoire de fallback
memory_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_HOURS = 24


class CacheBackend:
    """Interface abstraite pour le cache"""
    
    def get(self, key: str) -> Optional[Dict]:
        """Récupère une valeur depuis le cache"""
        raise NotImplementedError
    
    def set(self, key: str, value: Dict, ttl_hours: int = CACHE_TTL_HOURS):
        """Stocke une valeur dans le cache"""
        raise NotImplementedError
    
    def delete(self, key: str):
        """Supprime une clé du cache"""
        raise NotImplementedError
    
    def clear(self):
        """Vide tout le cache"""
        raise NotImplementedError


class RedisCacheBackend(CacheBackend):
    """Backend Redis pour le cache"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", db: int = 0):
        """
        Initialise le backend Redis
        
        Args:
            redis_url: URL Redis (ex: redis://localhost:6379)
            db: Numéro de base de données Redis
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis package not installed. Install with: pip install redis")
        
        try:
            self.redis_client = redis.from_url(redis_url, db=db, decode_responses=True)
            # Tester la connexion
            self.redis_client.ping()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    def get(self, key: str) -> Optional[Dict]:
        """Récupère une valeur depuis Redis"""
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            # En cas d'erreur, retourner None (fallback sera utilisé)
            return None
        return None
    
    def set(self, key: str, value: Dict, ttl_hours: int = CACHE_TTL_HOURS):
        """Stocke une valeur dans Redis"""
        try:
            ttl_seconds = int(ttl_hours * 3600)
            self.redis_client.setex(
                key,
                ttl_seconds,
                json.dumps(value)
            )
        except Exception as e:
            # En cas d'erreur, ne rien faire (fallback sera utilisé)
            pass
    
    def delete(self, key: str):
        """Supprime une clé de Redis"""
        try:
            self.redis_client.delete(key)
        except Exception:
            pass
    
    def clear(self):
        """Vide tout le cache Redis (dangerous!)"""
        try:
            self.redis_client.flushdb()
        except Exception:
            pass


class MemoryCacheBackend(CacheBackend):
    """Backend mémoire pour le cache (fallback)"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Dict]:
        """Récupère une valeur depuis le cache mémoire"""
        if key in self.cache:
            cached_data = self.cache[key]
            cache_time = cached_data.get("timestamp")
            if cache_time:
                cache_dt = datetime.fromisoformat(cache_time)
                if datetime.now() - cache_dt < timedelta(hours=CACHE_TTL_HOURS):
                    return cached_data.get("result")
                else:
                    # Cache expiré
                    del self.cache[key]
        return None
    
    def set(self, key: str, value: Dict, ttl_hours: int = CACHE_TTL_HOURS):
        """Stocke une valeur dans le cache mémoire"""
        self.cache[key] = {
            "result": value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Limiter la taille du cache (garder seulement les 1000 derniers)
        if len(self.cache) > 1000:
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1].get("timestamp", ""))
            for key_to_delete, _ in sorted_items[:100]:
                del self.cache[key_to_delete]
    
    def delete(self, key: str):
        """Supprime une clé du cache mémoire"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Vide tout le cache mémoire"""
        self.cache.clear()


# Instance globale du cache backend
_cache_backend: Optional[CacheBackend] = None


def init_cache_backend(redis_url: Optional[str] = None, redis_db: int = 0, force_memory: bool = False):
    """
    Initialise le backend de cache
    
    Args:
        redis_url: URL Redis (si None, utilise redis://localhost:6379)
        redis_db: Numéro de base de données Redis
        force_memory: Forcer l'utilisation du cache mémoire même si Redis disponible
    """
    global _cache_backend
    
    if force_memory:
        _cache_backend = MemoryCacheBackend()
        return
    
    # Essayer Redis d'abord
    if REDIS_AVAILABLE and redis_url:
        try:
            _cache_backend = RedisCacheBackend(redis_url, redis_db)
            return
        except Exception:
            # Fallback sur mémoire si Redis échoue
            pass
    
    # Fallback sur mémoire
    _cache_backend = MemoryCacheBackend()


def get_cache_backend() -> CacheBackend:
    """Retourne le backend de cache actuel"""
    global _cache_backend
    
    if _cache_backend is None:
        # Initialiser avec mémoire par défaut
        _cache_backend = MemoryCacheBackend()
    
    return _cache_backend


def get_cached(key: str) -> Optional[Dict]:
    """Récupère une valeur depuis le cache"""
    return get_cache_backend().get(key)


def set_cached(key: str, value: Dict, ttl_hours: int = CACHE_TTL_HOURS):
    """Stocke une valeur dans le cache"""
    get_cache_backend().set(key, value, ttl_hours)


def delete_cached(key: str):
    """Supprime une clé du cache"""
    get_cache_backend().delete(key)


def clear_cache():
    """Vide tout le cache"""
    get_cache_backend().clear()


def get_cache_info() -> Dict[str, Any]:
    """Retourne des informations sur le cache"""
    backend = get_cache_backend()
    
    info = {
        "backend_type": type(backend).__name__,
        "redis_available": REDIS_AVAILABLE,
    }
    
    if isinstance(backend, MemoryCacheBackend):
        info["cache_size"] = len(backend.cache)
    elif isinstance(backend, RedisCacheBackend):
        try:
            info["redis_connected"] = backend.redis_client.ping()
            info["redis_db_size"] = backend.redis_client.dbsize()
        except:
            info["redis_connected"] = False
    
    return info





