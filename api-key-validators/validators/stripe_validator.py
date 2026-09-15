#!/usr/bin/env python3
"""
Stripe Validator - Complete and Optimized
Validates API keys and extracts: account, balance (EUR/USD), charges, settings
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any
from base64 import b64encode
import json


class StripeValidator(BaseValidator):
    """Professional Stripe validator - production ready"""

    def __init__(self):
        super().__init__("Stripe", timeout=10, max_retries=3)
        self.api_url = "https://api.stripe.com/v1"

    def validate(self, api_key: str) -> ValidationResult:
        """Validate Stripe API key"""
        # Format validation
        if not self._validate_format(api_key):
            return self.create_result(
                api_key,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid key format - must be sk_live or sk_test"},
                error="Format validation failed"
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

    def _validate_format(self, key: str) -> bool:
        """Validate basic Stripe key format"""
        if not isinstance(key, str):
            return False

        # Secret keys start with sk_live or sk_test
        if not (key.startswith("sk_live_") or key.startswith("sk_test_")):
            return False

        # Minimum length for secret key is 80+ chars
        if len(key) < 80:
            return False

        return True

    def get_detailed_info(self, api_key: str) -> Dict[str, Any]:
        """Extract complete Stripe account information"""
        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "environment": "TEST" if api_key.startswith("sk_test") else "LIVE",
            "account": {},
            "balance": {},
            "pending_balance": {},
            "quotas": {},
            "capabilities": {}
        }

        # Create Basic Auth header (Stripe uses key as username, empty password)
        try:
            encoded = b64encode(f"{api_key}:".encode()).decode('ascii')
        except Exception:
            info["error"] = "Failed to encode credentials"
            return info

        headers = {"Authorization": f"Basic {encoded}"}

        # Step 1: Verify API key via GET /account
        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/account",
            headers=headers
        )

        if error or not response:
            info["error"] = error or "Connection failed"
            return info

        if response.status_code == 401:
            info["error"] = "Invalid API key"
            return info

        if response.status_code == 403:
            info["error"] = "Access forbidden - restricted key"
            return info

        if response.status_code != 200:
            info["error"] = f"API returned status {response.status_code}"
            return info

        try:
            account = response.json()
        except json.JSONDecodeError:
            info["error"] = "Invalid JSON response"
            return info

        # Key is valid at this point
        info["is_valid"] = True
        info["is_live"] = account.get("livemode", False)

        # Extract account information
        info["account"]["id"] = account.get("id")
        info["account"]["type"] = account.get("type")
        info["account"]["email"] = account.get("email", "N/A")

        # Business profile
        business_profile = account.get("business_profile", {})
        info["account"]["business_name"] = business_profile.get("name", "N/A")
        info["account"]["business_url"] = business_profile.get("url", "N/A")
        info["account"]["business_product_description"] = business_profile.get("product_description", "N/A")

        # Location
        info["account"]["country"] = account.get("country", "N/A")
        info["account"]["timezone"] = account.get("timezone", "N/A")

        # Status and capabilities
        info["account"]["charges_enabled"] = account.get("charges_enabled", False)
        info["account"]["payouts_enabled"] = account.get("payouts_enabled", False)
        info["account"]["requirements"] = account.get("requirements", {}).get("past_due", [])

        # Account creation date
        created = account.get("created", 0)
        if created:
            from datetime import datetime
            info["account"]["created_date"] = datetime.utcfromtimestamp(created).isoformat()

        # Step 2: Get balance information
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/balance",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                balance_data = response.json()
                available_balances = balance_data.get("available", [])
                pending_balances = balance_data.get("pending", [])

                # Process available balances
                for entry in available_balances:
                    currency = entry.get("currency", "").upper()
                    amount_cents = entry.get("amount", 0)
                    amount = amount_cents / 100  # Convert cents to dollars/euros

                    if currency == "EUR":
                        info["balance"]["available_eur"] = f"€{amount:.2f}"
                        info["balance"]["available_eur_amount"] = amount
                    elif currency == "USD":
                        info["balance"]["available_usd"] = f"${amount:.2f}"
                        info["balance"]["available_usd_amount"] = amount
                    elif currency == "GBP":
                        info["balance"]["available_gbp"] = f"£{amount:.2f}"
                        info["balance"]["available_gbp_amount"] = amount
                    else:
                        info["balance"][f"available_{currency.lower()}"] = f"{amount:.2f} {currency}"

                # Process pending balances
                for entry in pending_balances:
                    currency = entry.get("currency", "").upper()
                    amount_cents = entry.get("amount", 0)
                    amount = amount_cents / 100

                    if currency == "EUR":
                        info["pending_balance"]["pending_eur"] = f"€{amount:.2f}"
                        info["pending_balance"]["pending_eur_amount"] = amount
                    elif currency == "USD":
                        info["pending_balance"]["pending_usd"] = f"${amount:.2f}"
                        info["pending_balance"]["pending_usd_amount"] = amount
                    elif currency == "GBP":
                        info["pending_balance"]["pending_gbp"] = f"£{amount:.2f}"
                        info["pending_balance"]["pending_gbp_amount"] = amount
                    else:
                        info["pending_balance"][f"pending_{currency.lower()}"] = f"{amount:.2f} {currency}"

                # Set total available
                total_available = sum(entry.get("amount", 0) for entry in available_balances if entry.get("currency") == "eur")
                if total_available > 0:
                    info["quotas"]["primary_currency_available"] = "EUR"
                    info["quotas"]["total_available_cents"] = total_available
            except (json.JSONDecodeError, KeyError, ZeroDivisionError):
                pass

        # Step 3: Get recent charges
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/charges?limit=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                charges_data = response.json()
                info["quotas"]["total_charges"] = charges_data.get("total_count", 0)

                # Get latest charge for reference
                charges = charges_data.get("data", [])
                if charges:
                    latest_charge = charges[0]
                    info["quotas"]["latest_charge_amount"] = f"{latest_charge.get('amount', 0) / 100} {latest_charge.get('currency', 'USD').upper()}"
                    info["quotas"]["latest_charge_status"] = latest_charge.get("status")
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 4: Get customer count
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/customers?limit=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                customers_data = response.json()
                info["quotas"]["total_customers"] = customers_data.get("total_count", 0)
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 5: Get payment methods info
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/payment_methods?limit=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                pm_data = response.json()
                info["quotas"]["total_payment_methods"] = pm_data.get("total_count", 0)
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 6: Check subscriptions
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/subscriptions?limit=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                subs_data = response.json()
                info["quotas"]["total_subscriptions"] = subs_data.get("total_count", 0)
                info["capabilities"]["subscriptions_enabled"] = True
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 7: Check if API key has required capabilities
        if info["account"]["charges_enabled"]:
            info["capabilities"]["charges"] = "enabled"
        else:
            info["capabilities"]["charges"] = "disabled"

        if info["account"]["payouts_enabled"]:
            info["capabilities"]["payouts"] = "enabled"
        else:
            info["capabilities"]["payouts"] = "disabled"

        return info
