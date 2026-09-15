#!/usr/bin/env python3
"""
Twilio Validator - Complete and Optimized
Validates credentials and extracts: account, phone numbers, SMS countries, balance
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any, List
from base64 import b64encode
import json


class TwilioValidator(BaseValidator):
    """Professional Twilio validator - production ready"""

    def __init__(self):
        super().__init__("Twilio", timeout=10, max_retries=3)
        self.api_url = "https://api.twilio.com/2010-04-01"

    def validate(self, credentials: str) -> ValidationResult:
        """Validate Twilio credentials (SID:TOKEN format)"""
        # Format validation
        if not self._validate_format(credentials):
            return self.create_result(
                credentials,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid format - use ACCOUNT_SID:AUTH_TOKEN"},
                error="Format validation failed"
            )

        sid, token = credentials.split(':', 1)
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

    def _validate_format(self, credentials: str) -> bool:
        """Validate basic Twilio credentials format"""
        if not isinstance(credentials, str) or ':' not in credentials:
            return False

        parts = credentials.split(':', 1)
        if len(parts) != 2:
            return False

        sid, token = parts

        # Twilio SID: AC + 32 alphanumeric characters = 34 total
        if not (sid.startswith("AC") and len(sid) == 34):
            return False

        # Auth token: typically 32+ chars
        if len(token) < 32:
            return False

        return True

    def get_detailed_info(self, account_sid: str, auth_token: str) -> Dict[str, Any]:
        """Extract complete Twilio account information"""
        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "account": {},
            "phone_numbers": [],
            "sms_info": {},
            "quotas": {},
            "capabilities": {}
        }

        # Create Basic Auth header
        credentials = f"{account_sid}:{auth_token}"
        try:
            encoded = b64encode(credentials.encode()).decode('ascii')
        except Exception:
            info["error"] = "Failed to encode credentials"
            return info

        headers = {"Authorization": f"Basic {encoded}"}

        # Step 1: Verify credentials via GET /Accounts/{SID}
        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/Accounts/{account_sid}",
            headers=headers
        )

        if error or not response:
            info["error"] = error or "Connection failed"
            return info

        if response.status_code == 401:
            info["error"] = "Invalid credentials (authentication failed)"
            return info

        if response.status_code == 403:
            info["error"] = "Access forbidden"
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

        # Check if account is active (live)
        account_status = account.get("status", "").lower()
        info["is_live"] = account_status == "active"

        # Extract account information
        info["account"]["friendly_name"] = account.get("friendly_name", "N/A")
        info["account"]["type"] = account.get("type", "Trial")
        info["account"]["status"] = account_status
        info["account"]["date_created"] = str(account.get("date_created", "N/A"))
        info["account"]["date_updated"] = str(account.get("date_updated", "N/A"))
        info["account"]["sid"] = account_sid
        info["account"]["auth_token_sample"] = f"{auth_token[:6]}...{auth_token[-4:]}"
        info["account"]["owner_account_sid"] = account.get("owner_account_sid", account_sid)

        # Step 2: Get all incoming phone numbers
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/Accounts/{account_sid}/IncomingPhoneNumbers",
            headers=headers
        )

        sms_enabled_countries = set()
        voice_enabled_countries = set()

        if response and response.status_code == 200:
            try:
                numbers_data = response.json()
                incoming_numbers = numbers_data.get("incoming_phone_numbers", [])

                for number in incoming_numbers:
                    phone_info = {
                        "phone_number": number.get("phone_number"),
                        "friendly_name": number.get("friendly_name", ""),
                        "country_code": number.get("address_country", "Unknown"),
                        "capabilities": number.get("capabilities", {})
                    }

                    # Check capabilities
                    capabilities = number.get("capabilities", {})
                    if capabilities.get("sms"):
                        sms_enabled_countries.add(number.get("address_country", "Unknown"))
                        phone_info["sms_capable"] = True
                    if capabilities.get("voice"):
                        voice_enabled_countries.add(number.get("address_country", "Unknown"))
                        phone_info["voice_capable"] = True

                    info["phone_numbers"].append(phone_info)
            except (json.JSONDecodeError, KeyError):
                pass

        # Aggregate SMS information
        info["sms_info"]["sms_enabled"] = len(sms_enabled_countries) > 0
        info["sms_info"]["countries_with_sms"] = sorted(list(sms_enabled_countries))
        info["sms_info"]["countries_with_voice"] = sorted(list(voice_enabled_countries))
        info["sms_info"]["phone_numbers_count"] = len(info["phone_numbers"])

        # Step 3: Get balance information
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/Accounts/{account_sid}",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                acc = response.json()
                balance = float(acc.get("balance", 0))
                currency = acc.get("preferred_currency", "USD")

                info["quotas"]["account_balance"] = balance
                info["quotas"]["balance_currency"] = currency
                info["quotas"]["balance_status"] = (
                    "CRITICAL" if balance < 0 else
                    "LOW" if balance < 5 else
                    "NORMAL"
                )
            except (ValueError, KeyError):
                pass

        # Step 4: Get available phone number list (check if can purchase)
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/Accounts/{account_sid}/AvailablePhoneNumbers/US/Local?AreaCode=415&Limit=1",
            headers=headers
        )

        can_purchase = False
        if response and response.status_code == 200:
            try:
                data = response.json()
                available = data.get("available_phone_numbers", [])
                can_purchase = len(available) > 0
            except (json.JSONDecodeError, KeyError):
                pass

        info["capabilities"]["can_purchase_numbers"] = can_purchase

        # Step 5: Check if SMS is enabled (via capabilities)
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/Accounts/{account_sid}/Messages",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                messages_data = response.json()
                message_count = messages_data.get("total", 0)
                info["quotas"]["total_messages_sent"] = message_count
                info["capabilities"]["sms_enabled"] = True
            except (json.JSONDecodeError, KeyError):
                info["capabilities"]["sms_enabled"] = False

        # Step 6: Check calls
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/Accounts/{account_sid}/Calls",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                calls_data = response.json()
                call_count = calls_data.get("total", 0)
                info["quotas"]["total_calls_made"] = call_count
                info["capabilities"]["voice_enabled"] = True
            except (json.JSONDecodeError, KeyError):
                info["capabilities"]["voice_enabled"] = False

        return info
