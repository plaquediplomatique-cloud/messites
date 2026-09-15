#!/usr/bin/env python3
"""Stripe Validator - Live status, balance in EUR, account info"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any
from base64 import b64encode


class StripeValidator(BaseValidator):
    """Professional Stripe validator with live status and EUR balance"""

    def __init__(self):
        super().__init__("Stripe", timeout=10)
        self.api_url = "https://api.stripe.com/v1"

    def validate(self, api_key: str) -> ValidationResult:
        """Validate Stripe API key"""
        if not (api_key.startswith("sk_") and len(api_key) > 50):
            return self.create_result(
                api_key,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid key format"},
                error="Key must start with sk_ (secret key)"
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

    def get_detailed_info(self, api_key: str) -> Dict[str, Any]:
        """Get comprehensive Stripe account info"""
        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "environment": "TEST" if api_key.startswith("sk_test") else "LIVE",
            "account": {},
            "balance": {},
            "quotas": {}
        }

        # Create auth header
        encoded = b64encode(f"{api_key}:".encode()).decode()
        headers = {"Authorization": f"Basic {encoded}"}

        # Test API access
        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/account",
            headers=headers
        )

        if error or not response:
            info["error"] = error or "Unknown error"
            return info

        if response.status_code == 401:
            info["error"] = "Invalid API key"
            return info

        if response.status_code == 403:
            info["error"] = "Access forbidden (restricted key)"
            return info

        if response.status_code != 200:
            info["error"] = f"API error ({response.status_code})"
            return info

        try:
            account = response.json()
            info["is_valid"] = True
            info["is_live"] = account.get("livemode", False)

            # Account details
            info["account"]["id"] = account.get("id")
            info["account"]["email"] = account.get("email")
            info["account"]["business_name"] = account.get("business_profile", {}).get("name")
            info["account"]["country"] = account.get("country")
            info["account"]["type"] = account.get("type")
            info["account"]["charges_enabled"] = account.get("charges_enabled")
            info["account"]["payouts_enabled"] = account.get("payouts_enabled")

            # Get balance in multiple currencies
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/balance",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    balance_data = response.json()
                    available = balance_data.get("available", [])
                    pending = balance_data.get("pending", [])

                    # Find EUR balance
                    for entry in available:
                        if entry.get("currency") == "eur":
                            # Convert cents to euros
                            amount_eur = entry.get("amount", 0) / 100
                            info["balance"]["available_eur"] = f"€{amount_eur:.2f}"
                            break

                    for entry in pending:
                        if entry.get("currency") == "eur":
                            amount_eur = entry.get("amount", 0) / 100
                            info["balance"]["pending_eur"] = f"€{amount_eur:.2f}"
                            break

                    # Get USD too
                    for entry in available:
                        if entry.get("currency") == "usd":
                            amount_usd = entry.get("amount", 0) / 100
                            info["balance"]["available_usd"] = f"${amount_usd:.2f}"
                            break
                except:
                    pass

            # Get charges count
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/charges?limit=1",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    charges = response.json()
                    info["quotas"]["total_charges"] = charges.get("total_count", 0)
                except:
                    pass

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info
