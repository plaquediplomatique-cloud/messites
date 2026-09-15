#!/usr/bin/env python3
"""SendGrid API Key Validator - Complete validation with quota info"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any


class SendGridValidator(BaseValidator):
    """Professional SendGrid validator with comprehensive info"""

    def __init__(self):
        super().__init__("SendGrid", timeout=10)
        self.api_url = "https://api.sendgrid.com/v3"

    def validate(self, api_key: str) -> ValidationResult:
        """Validate SendGrid API key"""
        if not self._is_valid_format(api_key):
            return self.create_result(
                api_key,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid key format"},
                error="Key must start with 'SG.'"
            )

        details = self.get_detailed_info(api_key)
        is_valid = details.get("is_valid", False)
        is_live = details.get("is_live", False)

        return self.create_result(
            api_key,
            is_valid=is_valid,
            is_live=is_live,
            details=details,
            error=details.get("error")
        )

    def _is_valid_format(self, key: str) -> bool:
        """Check basic format"""
        return key.startswith("SG.") and len(key) > 20

    def get_detailed_info(self, api_key: str) -> Dict[str, Any]:
        """Get comprehensive SendGrid account info"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "account": {},
            "scopes": [],
            "quota": {}
        }

        # Test API access
        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/user/account",
            headers=headers
        )

        if error or not response:
            info["error"] = error or "Unknown error"
            return info

        if response.status_code == 401:
            info["error"] = "Authentication failed (401)"
            return info

        if response.status_code != 200:
            info["error"] = f"API error ({response.status_code})"
            return info

        try:
            account = response.json()
            info["is_valid"] = True
            info["is_live"] = not account.get("type") == "test"

            # Account details
            info["account"]["email"] = account.get("email", "N/A")
            info["account"]["name"] = account.get("name", "N/A")
            info["account"]["phone"] = account.get("phone", "N/A")
            info["account"]["website"] = account.get("website", "N/A")
            info["account"]["reputation"] = account.get("reputation", "N/A")

            # Get API key details for scopes
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/api_keys",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    keys_data = response.json()
                    for key in keys_data.get("result", []):
                        if api_key in str(key):
                            info["scopes"] = key.get("scopes", [])
                            info["account"]["api_key_name"] = key.get("name")
                            break
                except:
                    pass

            # Get usage stats
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/stats?aggregated_by=day&limit=1",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    stats = response.json()
                    if stats.get("stats"):
                        stat = stats["stats"][0]
                        info["quota"]["emails_sent_today"] = stat.get("delivered", 0) + stat.get("bounce", 0)
                        info["quota"]["bounces"] = stat.get("bounce", 0)
                        info["quota"]["clicks"] = stat.get("click", 0)
                        info["quota"]["opens"] = stat.get("open", 0)
                except:
                    pass

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info
