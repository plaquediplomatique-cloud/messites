#!/usr/bin/env python3
"""Twilio Validator - SMS countries, quotas, live status"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any
from base64 import b64encode


class TwilioValidator(BaseValidator):
    """Professional Twilio validator with SMS countries and quotas"""

    def __init__(self):
        super().__init__("Twilio", timeout=10)
        self.api_url = "https://api.twilio.com/2010-04-01"

    def validate(self, credentials: str) -> ValidationResult:
        """Validate Twilio credentials (SID:Token)"""
        if ':' not in credentials:
            return self.create_result(
                credentials,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid format - use SID:TOKEN"},
                error="Missing colon separator"
            )

        sid, token = credentials.split(':', 1)

        if not (sid.startswith("AC") and len(sid) == 34 and len(token) > 20):
            return self.create_result(
                credentials,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid credential format"},
                error="SID must be 34 chars starting with AC"
            )

        details = self.get_detailed_info(sid, token)
        is_valid = details.get("is_valid", False)
        is_live = details.get("is_live", False)

        return self.create_result(
            credentials,
            is_valid=is_valid,
            is_live=is_live,
            details=details,
            error=details.get("error")
        )

    def get_detailed_info(self, account_sid: str, auth_token: str) -> Dict[str, Any]:
        """Get comprehensive Twilio account info"""
        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "account": {},
            "phone_numbers": [],
            "sms_info": {},
            "quotas": {}
        }

        # Create auth header
        credentials = f"{account_sid}:{auth_token}"
        encoded = b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {encoded}"}

        # Verify credentials
        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/Accounts/{account_sid}",
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
            info["is_live"] = account.get("status") == "active"

            # Account info
            info["account"]["friendly_name"] = account.get("friendly_name")
            info["account"]["type"] = account.get("type")
            info["account"]["status"] = account.get("status")
            info["account"]["date_created"] = str(account.get("date_created"))
            info["account"]["auth_token"] = f"{auth_token[:6]}...{auth_token[-4:]}"

            # Get phone numbers and countries
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/Accounts/{account_sid}/IncomingPhoneNumbers",
                headers=headers
            )

            countries = set()
            if response and response.status_code == 200:
                try:
                    numbers = response.json().get("incoming_phone_numbers", [])
                    for num in numbers:
                        info["phone_numbers"].append({
                            "number": num.get("phone_number"),
                            "country": num.get("address_country", "Unknown"),
                            "capabilities": num.get("capabilities", {})
                        })
                        countries.add(num.get("address_country", "Unknown"))
                except:
                    pass

            info["sms_info"]["countries"] = list(countries)
            info["sms_info"]["phone_count"] = len(info["phone_numbers"])

            # Get balance/billing
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/Accounts/{account_sid}",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    acc = response.json()
                    info["quotas"]["account_balance"] = float(acc.get("balance", 0))
                    info["quotas"]["currency"] = acc.get("preferred_currency", "USD")
                except:
                    pass

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info
