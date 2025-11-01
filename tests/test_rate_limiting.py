"""
Tests pour le rate limiting
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rate_limiting import (
    check_rate_limit,
    check_ip_rate_limit,
    get_plan_from_request,
    get_client_identifier,
    PLAN_LIMITS
)


class TestRateLimiting:
    """Tests pour le rate limiting"""
    
    def test_get_plan_from_request(self):
        """Test détection du plan depuis les headers"""
        request = Mock()
        request.headers = {"X-RapidAPI-Plan": "PRO"}
        
        plan = get_plan_from_request(request)
        assert plan == "PRO"
    
    def test_get_plan_default(self):
        """Test plan par défaut si header absent"""
        request = Mock()
        request.headers = {}
        
        plan = get_plan_from_request(request)
        assert plan == "BASIC"
    
    def test_check_rate_limit_basic(self):
        """Test rate limiting pour plan BASIC"""
        request = Mock()
        request.headers = {"X-RapidAPI-Plan": "BASIC"}
        request.client = Mock()
        request.client.host = "127.0.0.1"
        
        # Première requête devrait passer
        allowed, info = check_rate_limit(request, limit_type="monthly")
        assert allowed is True
        assert info["plan"] == "BASIC"
        assert info["limit"] == PLAN_LIMITS["BASIC"]["monthly"]
    
    def test_check_rate_limit_exceeded(self):
        """Test dépassement de limite"""
        request = Mock()
        request.headers = {"X-RapidAPI-Plan": "BASIC"}
        request.client = Mock()
        request.client.host = "127.0.0.1"
        
        # Dépasser la limite mensuelle
        limit = PLAN_LIMITS["BASIC"]["monthly"]
        for _ in range(limit + 1):
            allowed, info = check_rate_limit(request, limit_type="monthly")
        
        assert allowed is False
        assert info["remaining"] == 0
    
    def test_check_ip_rate_limit(self):
        """Test rate limiting par IP"""
        request = Mock()
        request.client = Mock()
        request.client.host = "192.168.1.100"
        
        # Première requête devrait passer
        allowed, info = check_ip_rate_limit(request)
        assert allowed is True
        
        # Dépasser la limite par minute (20 req/min)
        for _ in range(21):
            allowed, info = check_ip_rate_limit(request)
        
        assert allowed is False


class TestRateLimitHeaders:
    """Tests pour les headers de rate limiting"""
    
    def test_rate_limit_info_structure(self):
        """Test structure des infos de rate limiting"""
        request = Mock()
        request.headers = {"X-RapidAPI-Plan": "PRO"}
        request.client = Mock()
        request.client.host = "127.0.0.1"
        
        allowed, info = check_rate_limit(request, limit_type="monthly")
        
        assert "limit" in info
        assert "remaining" in info
        assert "reset_time" in info
        assert "plan" in info
        assert isinstance(info["limit"], int)
        assert isinstance(info["remaining"], int)
        assert info["remaining"] >= 0

