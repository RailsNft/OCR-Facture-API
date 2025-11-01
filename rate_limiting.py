"""
Rate Limiting intelligent pour l'API OCR Facture
Gère les quotas par plan, par IP, et par clé API
"""

from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import hashlib


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

# Cache pour stocker les compteurs (en production, utiliser Redis)
rate_limit_cache: Dict[str, Dict] = {}


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
        limit = plan_limits.get("daily") or (plan_limits["monthly"] // 30)
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
    if cache_key in rate_limit_cache:
        counter_data = rate_limit_cache[cache_key]
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
    
    # Sauvegarder dans le cache
    rate_limit_cache[cache_key] = counter_data
    
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
        
        if cache_key in rate_limit_cache:
            counter_data = rate_limit_cache[cache_key]
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
        
        rate_limit_cache[cache_key] = counter_data
        
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
    
    # Ajouter les headers de rate limiting à la réponse
    rate_limit_headers = get_rate_limit_headers(rate_limit_info)
    for key, value in rate_limit_headers.items():
        response.headers[key] = value
    
    return response

