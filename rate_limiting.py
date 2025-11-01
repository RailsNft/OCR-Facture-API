"""
Rate Limiting intelligent pour l'API OCR Facture
Gère les quotas par plan, par IP, et par clé API
Support Redis pour scalabilité
"""

from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import hashlib
import json

# Tentative d'import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Cache mémoire de fallback pour rate limiting
rate_limit_cache: Dict[str, Dict] = {}
_redis_client: Optional[redis.Redis] = None


# Limites par plan (requêtes par mois)
PLAN_LIMITS = {
    "BASIC": {
        "monthly": 100,
        "daily": None,  # Calculé automatiquement (100/30 = ~3-4/jour)
        "per_minute": 1,
    },
    "PRO": {
        "monthly": 20000,
        "daily": 666,  # ~666/jour
        "per_minute": 10,
    },
    "ULTRA": {
        "monthly": 80000,
        "daily": 2666,  # ~2666/jour
        "per_minute": 50,
    },
    "MEGA": {
        "monthly": 250000,
        "daily": 8333,  # ~8333/jour
        "per_minute": 150,
    },
}

# Limites par IP (protection anti-abus)
IP_LIMITS = {
    "per_minute": 20,  # Max 20 requêtes/minute par IP
    "per_hour": 200,   # Max 200 requêtes/heure par IP
    "per_day": 1000,   # Max 1000 requêtes/jour par IP
}


def init_rate_limit_redis(redis_url: Optional[str] = None, redis_db: int = 0):
    """
    Initialise Redis pour le rate limiting (optionnel)
    
    Args:
        redis_url: URL Redis (ex: redis://localhost:6379)
        redis_db: Numéro de base de données Redis
    """
    global _redis_client
    
    if not REDIS_AVAILABLE:
        return False
    
    if not redis_url:
        return False
    
    try:
        _redis_client = redis.from_url(redis_url, db=redis_db, decode_responses=True)
        _redis_client.ping()
        return True
    except Exception:
        _redis_client = None
        return False


def _get_rate_limit_counter(cache_key: str) -> Optional[Dict]:
    """Récupère un compteur depuis Redis ou mémoire"""
    if _redis_client:
        try:
            data = _redis_client.get(cache_key)
            if data:
                return json.loads(data)
        except Exception:
            pass
    
    # Fallback mémoire
    return rate_limit_cache.get(cache_key)


def _set_rate_limit_counter(cache_key: str, counter_data: Dict, ttl_seconds: Optional[int] = None):
    """Stocke un compteur dans Redis ou mémoire"""
    if _redis_client and ttl_seconds:
        try:
            _redis_client.setex(cache_key, ttl_seconds, json.dumps(counter_data))
            return
        except Exception:
            pass
    
    # Fallback mémoire
    rate_limit_cache[cache_key] = counter_data
    
    # Nettoyer le cache mémoire si trop grand
    if len(rate_limit_cache) > 10000:
        expired_keys = [
            k for k, v in rate_limit_cache.items()
            if datetime.fromisoformat(v.get("reset_time", "2000-01-01")) < datetime.now()
        ]
        for k in expired_keys[:1000]:
            del rate_limit_cache[k]


def get_client_identifier(request: Request) -> str:
    """
    Génère un identifiant unique pour le client
    Utilise la clé API si disponible, sinon l'IP
    """
    api_key = request.headers.get("X-RapidAPI-Proxy-Secret")
    if api_key:
        # Utiliser un hash de la clé API comme identifiant
        return f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
    
    # Fallback sur IP
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


def get_plan_from_request(request: Request) -> str:
    """
    Détermine le plan de l'utilisateur depuis les headers RapidAPI
    En production, RapidAPI ajoute des headers avec les infos du plan
    """
    # Headers RapidAPI standard
    plan = request.headers.get("X-RapidAPI-Plan", "BASIC")
    
    # Normaliser le nom du plan
    plan = plan.upper()
    if plan not in PLAN_LIMITS:
        plan = "BASIC"  # Plan par défaut
    
    return plan


def check_rate_limit(
    request: Request,
    limit_type: str = "monthly"
) -> Tuple[bool, Optional[Dict]]:
    """
    Vérifie si la requête respecte les limites de rate limiting
    
    Args:
        request: Requête FastAPI
        limit_type: Type de limite ("monthly", "daily", "per_minute")
    
    Returns:
        Tuple (is_allowed, rate_limit_info)
        rate_limit_info contient: limit, remaining, reset_time
    """
    client_id = get_client_identifier(request)
    plan = get_plan_from_request(request)
    
    # Récupérer les limites du plan
    plan_limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["BASIC"])
    
    # Déterminer la limite selon le type
    if limit_type == "monthly":
        limit = plan_limits["monthly"]
        window = timedelta(days=30)
        key_suffix = "monthly"
    elif limit_type == "daily":
        # Calculer la limite quotidienne : monthly / 30, arrondi au supérieur pour être plus généreux
        if plan_limits.get("daily") is not None:
            limit = plan_limits["daily"]
        else:
            # Arrondir au supérieur pour éviter les limites trop restrictives
            import math
            limit = math.ceil(plan_limits["monthly"] / 30)
        window = timedelta(days=1)
        key_suffix = "daily"
    elif limit_type == "per_minute":
        limit = plan_limits["per_minute"]
        window = timedelta(minutes=1)
        key_suffix = "minute"
    else:
        limit = plan_limits["monthly"]
        window = timedelta(days=30)
        key_suffix = "monthly"
    
    # Clé de cache pour ce client et cette fenêtre
    cache_key = f"{client_id}:{key_suffix}"
    
    # Récupérer les compteurs actuels
    now = datetime.now()
    
    # Récupérer depuis Redis ou mémoire
    counter_data = _get_rate_limit_counter(cache_key)
    
    if counter_data:
        reset_time = datetime.fromisoformat(counter_data["reset_time"])
        
        # Si la fenêtre est expirée, réinitialiser
        if now >= reset_time:
            counter_data = {
                "count": 0,
                "reset_time": (now + window).isoformat(),
                "first_request": now.isoformat()
            }
        else:
            counter_data["count"] = counter_data.get("count", 0) + 1
    else:
        # Première requête pour ce client
        counter_data = {
            "count": 1,
            "reset_time": (now + window).isoformat(),
            "first_request": now.isoformat()
        }
    
    # Sauvegarder dans Redis ou mémoire avec TTL
    ttl_seconds = int(window.total_seconds())
    _set_rate_limit_counter(cache_key, counter_data, ttl_seconds)
    
    # Nettoyer le cache si trop grand (garder seulement les 10000 dernières entrées)
    if len(rate_limit_cache) > 10000:
        # Supprimer les entrées expirées
        expired_keys = [
            k for k, v in rate_limit_cache.items()
            if datetime.fromisoformat(v["reset_time"]) < now
        ]
        for k in expired_keys[:1000]:  # Supprimer max 1000 à la fois
            del rate_limit_cache[k]
    
    # Vérifier si la limite est dépassée
    count = counter_data["count"]
    remaining = max(0, limit - count)
    reset_time = datetime.fromisoformat(counter_data["reset_time"])
    
    rate_limit_info = {
        "limit": limit,
        "remaining": remaining,
        "reset_time": reset_time.isoformat(),
        "plan": plan
    }
    
    if count > limit:
        return False, rate_limit_info
    
    return True, rate_limit_info


def check_ip_rate_limit(request: Request) -> Tuple[bool, Optional[Dict]]:
    """
    Vérifie les limites par IP (protection anti-abus)
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Vérifier les limites par minute, heure, jour
    for period, limit in [
        ("minute", IP_LIMITS["per_minute"]),
        ("hour", IP_LIMITS["per_hour"]),
        ("day", IP_LIMITS["per_day"]),
    ]:
        if period == "minute":
            window = timedelta(minutes=1)
        elif period == "hour":
            window = timedelta(hours=1)
        else:
            window = timedelta(days=1)
        
        cache_key = f"ip:{client_ip}:{period}"
        now = datetime.now()
        
        # Récupérer depuis Redis ou mémoire
        counter_data = _get_rate_limit_counter(cache_key)
        
        if counter_data:
            reset_time = datetime.fromisoformat(counter_data["reset_time"])
            
            if now >= reset_time:
                counter_data = {
                    "count": 0,
                    "reset_time": (now + window).isoformat()
                }
            else:
                counter_data["count"] = counter_data.get("count", 0) + 1
        else:
            counter_data = {
                "count": 1,
                "reset_time": (now + window).isoformat()
            }
        
        # Sauvegarder avec TTL
        ttl_seconds = int(window.total_seconds())
        _set_rate_limit_counter(cache_key, counter_data, ttl_seconds)
        
        # Vérifier limite
        if counter_data["count"] > limit:
            return False, {
                "limit": limit,
                "period": period,
                "reset_time": counter_data["reset_time"]
            }
    
    return True, None


def get_rate_limit_headers(rate_limit_info: Dict) -> Dict[str, str]:
    """
    Génère les headers HTTP pour les informations de rate limiting
    """
    headers = {
        "X-RateLimit-Limit": str(rate_limit_info["limit"]),
        "X-RateLimit-Remaining": str(rate_limit_info["remaining"]),
        "X-RateLimit-Reset": str(int(datetime.fromisoformat(rate_limit_info["reset_time"]).timestamp())),
        "X-RateLimit-Plan": rate_limit_info["plan"]
    }
    return headers


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware FastAPI pour le rate limiting
    """
    # Skip rate limiting pour les endpoints publics
    public_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/"]
    if request.url.path in public_paths or request.url.path.startswith("/v1/languages"):
        response = await call_next(request)
        return response
    
    # Vérifier les limites par IP (protection anti-abus)
    ip_allowed, ip_info = check_ip_rate_limit(request)
    if not ip_allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": f"Rate limit exceeded. Max {ip_info['limit']} requests per {ip_info['period']}.",
                "retry_after": int((datetime.fromisoformat(ip_info["reset_time"]) - datetime.now()).total_seconds())
            },
            headers={"Retry-After": str(int((datetime.fromisoformat(ip_info["reset_time"]) - datetime.now()).total_seconds()))}
        )
    
    # Vérifier les limites par plan (mensuel principalement)
    allowed, rate_limit_info = check_rate_limit(request, limit_type="monthly")
    
    if not allowed:
        reset_time = datetime.fromisoformat(rate_limit_info["reset_time"])
        retry_after = int((reset_time - datetime.now()).total_seconds())
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Quota Exceeded",
                "message": f"Monthly quota exceeded for plan {rate_limit_info['plan']}. Limit: {rate_limit_info['limit']} requests/month.",
                "plan": rate_limit_info["plan"],
                "limit": rate_limit_info["limit"],
                "reset_time": rate_limit_info["reset_time"],
                "retry_after": retry_after
            },
            headers={
                **get_rate_limit_headers(rate_limit_info),
                "Retry-After": str(retry_after)
            }
        )
    
    # Vérifier aussi les limites quotidiennes
    daily_allowed, daily_info = check_rate_limit(request, limit_type="daily")
    if not daily_allowed:
        reset_time = datetime.fromisoformat(daily_info["reset_time"])
        retry_after = int((reset_time - datetime.now()).total_seconds())
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Daily Quota Exceeded",
                "message": f"Daily quota exceeded for plan {daily_info['plan']}.",
                "plan": daily_info["plan"],
                "limit": daily_info["limit"],
                "reset_time": daily_info["reset_time"],
                "retry_after": retry_after
            },
            headers={
                **get_rate_limit_headers(daily_info),
                "Retry-After": str(retry_after)
            }
        )
    
    # Appeler le handler suivant
    response = await call_next(request)
    
    # Ajouter les headers de rate limiting à la réponse (mensuel)
    if rate_limit_info:
        rate_limit_headers = get_rate_limit_headers(rate_limit_info)
        for key, value in rate_limit_headers.items():
            response.headers[key] = value
    
    # Ajouter aussi les headers quotidiens
    if daily_info:
        daily_headers = get_rate_limit_headers(daily_info)
        # Préfixer avec Daily- pour différencier
        response.headers["X-RateLimit-Daily-Limit"] = daily_headers["X-RateLimit-Limit"]
        response.headers["X-RateLimit-Daily-Remaining"] = daily_headers["X-RateLimit-Remaining"]
        response.headers["X-RateLimit-Daily-Reset"] = daily_headers["X-RateLimit-Reset"]
    
    return response

