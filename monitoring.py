"""
Monitoring et logging structuré pour l'API OCR Facture
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
from fastapi import Request
import sys

# Configuration du logging structuré
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ocr_facture_api")

# Métriques en mémoire (en production, utiliser Prometheus ou équivalent)
metrics: Dict[str, Any] = {
    "requests_total": 0,
    "requests_success": 0,
    "requests_errors": 0,
    "requests_by_endpoint": {},
    "requests_by_status": {},
    "latency_p50": [],
    "latency_p95": [],
    "latency_p99": [],
    "cache_hits": 0,
    "cache_misses": 0,
    "ocr_processing_times": [],
}


def log_request(request: Request, response_time: float, status_code: int, endpoint: str):
    """
    Log une requête avec toutes les informations pertinentes
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    method = request.method
    
    # Correlation ID (si présent dans les headers)
    correlation_id = request.headers.get("X-Correlation-ID", "none")
    
    # Log structuré en JSON
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "type": "request",
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "client_ip": client_ip,
        "user_agent": user_agent,
        "correlation_id": correlation_id,
    }
    
    # Ajouter les headers RapidAPI si présents
    if "X-RapidAPI-Plan" in request.headers:
        log_data["plan"] = request.headers.get("X-RapidAPI-Plan")
    
    # Logger selon le niveau
    if status_code >= 500:
        logger.error(json.dumps(log_data))
    elif status_code >= 400:
        logger.warning(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))
    
    # Mettre à jour les métriques
    update_metrics(endpoint, status_code, response_time)


def update_metrics(endpoint: str, status_code: int, response_time: float):
    """
    Met à jour les métriques de performance
    """
    metrics["requests_total"] += 1
    
    if 200 <= status_code < 400:
        metrics["requests_success"] += 1
    else:
        metrics["requests_errors"] += 1
    
    # Métriques par endpoint
    if endpoint not in metrics["requests_by_endpoint"]:
        metrics["requests_by_endpoint"][endpoint] = 0
    metrics["requests_by_endpoint"][endpoint] += 1
    
    # Métriques par statut
    status_group = f"{status_code // 100}xx"
    if status_group not in metrics["requests_by_status"]:
        metrics["requests_by_status"][status_group] = 0
    metrics["requests_by_status"][status_group] += 1
    
    # Latence
    response_time_ms = response_time * 1000
    metrics["ocr_processing_times"].append(response_time_ms)
    
    # Garder seulement les 1000 dernières mesures pour P50/P95/P99
    if len(metrics["ocr_processing_times"]) > 1000:
        metrics["ocr_processing_times"] = metrics["ocr_processing_times"][-1000:]
    
    # Calculer les percentiles
    if metrics["ocr_processing_times"]:
        sorted_times = sorted(metrics["ocr_processing_times"])
        n = len(sorted_times)
        metrics["latency_p50"] = sorted_times[int(n * 0.50)]
        metrics["latency_p95"] = sorted_times[int(n * 0.95)]
        metrics["latency_p99"] = sorted_times[int(n * 0.99)]


def log_cache_hit(endpoint: str):
    """
    Log un cache hit
    """
    metrics["cache_hits"] += 1
    logger.debug(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "type": "cache_hit",
        "endpoint": endpoint
    }))


def log_cache_miss(endpoint: str):
    """
    Log un cache miss
    """
    metrics["cache_misses"] += 1
    logger.debug(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "type": "cache_miss",
        "endpoint": endpoint
    }))


def log_error(error: Exception, context: Optional[Dict] = None):
    """
    Log une erreur avec contexte
    """
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "level": "ERROR",
        "type": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if context:
        log_data.update(context)
    
    logger.error(json.dumps(log_data))
    metrics["requests_errors"] += 1


def get_metrics() -> Dict[str, Any]:
    """
    Retourne les métriques actuelles
    """
    # Calculer le taux d'erreur
    total = metrics["requests_total"]
    errors = metrics["requests_errors"]
    success = metrics["requests_success"]
    
    error_rate = (errors / total * 100) if total > 0 else 0
    success_rate = (success / total * 100) if total > 0 else 0
    
    # Taux de cache hit
    cache_total = metrics["cache_hits"] + metrics["cache_misses"]
    cache_hit_rate = (metrics["cache_hits"] / cache_total * 100) if cache_total > 0 else 0
    
    return {
        "requests": {
            "total": total,
            "success": success,
            "errors": errors,
            "success_rate": round(success_rate, 2),
            "error_rate": round(error_rate, 2),
        },
        "latency": {
            "p50_ms": round(metrics["latency_p50"], 2) if metrics["latency_p50"] else None,
            "p95_ms": round(metrics["latency_p95"], 2) if metrics["latency_p95"] else None,
            "p99_ms": round(metrics["latency_p99"], 2) if metrics["latency_p99"] else None,
        },
        "cache": {
            "hits": metrics["cache_hits"],
            "misses": metrics["cache_misses"],
            "hit_rate": round(cache_hit_rate, 2),
        },
        "by_endpoint": metrics["requests_by_endpoint"],
        "by_status": metrics["requests_by_status"],
    }


async def monitoring_middleware(request: Request, call_next):
    """
    Middleware FastAPI pour le monitoring
    """
    start_time = time.time()
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        response_time = time.time() - start_time
        
        # Log la requête
        log_request(request, response_time, response.status_code, endpoint)
        
        return response
        
    except Exception as e:
        response_time = time.time() - start_time
        log_error(e, {
            "endpoint": endpoint,
            "method": request.method,
            "response_time_ms": round(response_time * 1000, 2)
        })
        raise





