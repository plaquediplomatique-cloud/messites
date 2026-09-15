#!/usr/bin/env python3
"""
Base Validator - Professional API Key Validation Framework
Production-grade validation with comprehensive error handling
"""
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
import time


class ValidationStatus(Enum):
    """Validation status enumeration"""
    VALID = "✓ VALID"
    INVALID = "✗ INVALID"
    ERROR = "⚠ ERROR"
    RATE_LIMITED = "⏱ RATE_LIMITED"


@dataclass
class ValidationResult:
    """Standardized validation result"""
    status: str
    service: str
    key_sample: str
    is_valid: bool
    is_live: bool
    details: Dict[str, Any]
    error: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


class BaseValidator(ABC):
    """
    Base validator class with professional error handling
    All validators should inherit from this
    """

    def __init__(self, service_name: str, timeout: int = 10, max_retries: int = 2):
        self.service_name = service_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()
        self.results = []

    def _create_session(self) -> requests.Session:
        """Create a requests session with proper headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'APIKeyValidator/1.0 (Professional Security Audit)'
        })
        return session

    def _safe_request(self, method: str, url: str, **kwargs) -> Tuple[Optional[requests.Response], Optional[str]]:
        """
        Safe HTTP request with retry logic and comprehensive error handling
        Returns: (response, error_message)
        """
        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=self.timeout, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, timeout=self.timeout, **kwargs)
                else:
                    return None, f"Unsupported HTTP method: {method}"

                # Check for rate limiting
                if response.status_code == 429:
                    if attempt < self.max_retries - 1:
                        wait_time = int(response.headers.get('Retry-After', 2 ** attempt))
                        time.sleep(wait_time)
                        continue
                    return response, "Rate limited"

                return response, None

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None, "Request timeout"

            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None, f"Connection error: {str(e)[:50]}"

            except Exception as e:
                return None, f"{type(e).__name__}: {str(e)[:50]}"

        return None, "Max retries exceeded"

    def _truncate_key(self, key: str, start: int = 6, end: int = 4) -> str:
        """Safely truncate API key for logging"""
        if len(key) <= start + end:
            return f"{key[:3]}...***"
        return f"{key[:start]}...{key[-end:]}"

    @abstractmethod
    def validate(self, api_key: str) -> ValidationResult:
        """Validate API key - must be implemented by subclass"""
        pass

    @abstractmethod
    def get_detailed_info(self, api_key: str) -> Dict[str, Any]:
        """Get detailed information about the API key"""
        pass

    def create_result(
        self,
        api_key: str,
        is_valid: bool,
        is_live: bool,
        details: Dict[str, Any],
        error: Optional[str] = None
    ) -> ValidationResult:
        """Create a standardized validation result"""
        status = (
            ValidationStatus.VALID.value if is_valid
            else ValidationStatus.INVALID.value if error
            else ValidationStatus.ERROR.value
        )

        return ValidationResult(
            status=status,
            service=self.service_name,
            key_sample=self._truncate_key(api_key),
            is_valid=is_valid,
            is_live=is_live,
            details=details,
            error=error
        )
