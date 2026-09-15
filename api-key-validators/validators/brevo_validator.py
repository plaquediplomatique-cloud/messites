#!/usr/bin/env python3
"""Brevo Validator - Live status, quotas, IP restrictions, reputation"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any


class BrevoValidator(BaseValidator):
    """Professional Brevo validator with IP restrictions and quotas"""

    def __init__(self):
        super().__init__("Brevo", timeout=10)
        self.api_url = "https://api.brevo.com/v3"

    def validate(self, api_key: str) -> ValidationResult:
        """Validate Brevo API key"""
        if not (api_key.startswith("xkeysib_") and len(api_key) > 30):
            return self.create_result(
                api_key,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid key format"},
                error="Key must start with xkeysib_"
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
        """Get comprehensive Brevo account info"""
        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "account": {},
            "quotas": {},
            "ip_restrictions": [],
            "features": []
        }

        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }

        # Get account info
        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/account",
            headers=headers
        )

        if error or not response:
            info["error"] = error or "Unknown error"
            return info

        if response.status_code == 401:
            info["error"] = "Authentication failed (401)"
            return info

        if response.status_code == 403:
            info["error"] = "Access forbidden (403)"
            return info

        if response.status_code != 200:
            info["error"] = f"API error ({response.status_code})"
            return info

        try:
            account = response.json()
            info["is_valid"] = True
            info["is_live"] = account.get("plan", "").lower() != "test"

            # Account details
            info["account"]["email"] = account.get("email")
            info["account"]["first_name"] = account.get("first_name")
            info["account"]["last_name"] = account.get("last_name")
            info["account"]["company_name"] = account.get("company_name")
            info["account"]["plan"] = account.get("plan")
            info["account"]["language"] = account.get("language")

            # SMS/Email credits
            credits = account.get("credits", {})
            info["quotas"]["sms_credits"] = credits.get("smsCredits", 0)
            info["quotas"]["email_credits"] = credits.get("emailCredits", 0)

            # Contacts
            info["quotas"]["contacts"] = account.get("contacts", {}).get("count", 0)
            info["quotas"]["contacts_limit"] = account.get("contacts", {}).get("limit", 0)

            # Relay configuration (IP restrictions)
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/smtp/configuration",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    config = response.json()
                    if config.get("relay"):
                        relay = config["relay"]
                        info["ip_restrictions"] = relay.get("ip_whitelist", [])
                        info["features"].append("SMTP Relay Configured")
                except:
                    pass

            # Get lists count
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/contacts/lists",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    lists = response.json()
                    info["quotas"]["contact_lists"] = len(lists.get("lists", []))
                except:
                    pass

            # Get templates count
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/smtp/templates",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    templates = response.json()
                    info["quotas"]["email_templates"] = len(templates.get("templates", []))
                except:
                    pass

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info
