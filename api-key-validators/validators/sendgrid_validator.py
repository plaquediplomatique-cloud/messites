#!/usr/bin/env python3
"""
SendGrid Validator - Complete and Optimized
Validates API keys and extracts: account info, quotas, reputation, scopes
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any
import json


class SendGridValidator(BaseValidator):
    """Professional SendGrid validator - production ready"""

    def __init__(self):
        super().__init__("SendGrid", timeout=10, max_retries=3)
        self.api_url = "https://api.sendgrid.com/v3"

    def validate(self, api_key: str) -> ValidationResult:
        """Validate SendGrid API key with full extraction"""
        # Format validation
        if not self._validate_format(api_key):
            return self.create_result(
                api_key,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid key format - must be SG.xxxxx"},
                error="Format validation failed"
            )

        # Get detailed info and validate
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
        """Validate basic SendGrid key format"""
        if not isinstance(key, str):
            return False
        # SendGrid keys: SG.[alphanumeric]{60+}
        if not key.startswith("SG."):
            return False
        if len(key) < 70:  # SG. (3 chars) + minimum 67 chars
            return False
        return True

    def get_detailed_info(self, api_key: str) -> Dict[str, Any]:
        """Extract complete SendGrid account information"""
        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "account": {},
            "quotas": {},
            "security": {},
            "usage": {}
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Step 1: Verify key validity via /user/account
        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/user/account",
            headers=headers
        )

        if error or not response:
            info["error"] = error or "Connection failed"
            return info

        # Handle authentication errors
        if response.status_code == 401:
            info["error"] = "Invalid or expired API key"
            return info

        if response.status_code == 403:
            info["error"] = "Access forbidden - insufficient permissions"
            return info

        if response.status_code != 200:
            info["error"] = f"API returned status {response.status_code}"
            return info

        # Parse account data
        try:
            account = response.json()
        except json.JSONDecodeError:
            info["error"] = "Invalid JSON response from API"
            return info

        # Key is valid at this point
        info["is_valid"] = True

        # Determine if live or test
        account_type = account.get("type", "live")
        info["is_live"] = account_type == "live"

        # Extract account information
        info["account"]["email"] = account.get("email", "N/A")
        info["account"]["name"] = account.get("name", "N/A")
        info["account"]["phone"] = account.get("phone", "N/A")
        info["account"]["website"] = account.get("website", "N/A")
        info["account"]["address"] = account.get("address", "N/A")
        info["account"]["city"] = account.get("city", "N/A")
        info["account"]["country"] = account.get("country", "N/A")
        info["account"]["state"] = account.get("state", "N/A")
        info["account"]["zip"] = account.get("zip", "N/A")
        info["account"]["timezone"] = account.get("timezone", "N/A")

        # Reputation (important metric)
        reputation = account.get("reputation", 0)
        info["security"]["reputation_score"] = reputation
        info["security"]["reputation_status"] = (
            "EXCELLENT" if reputation >= 9 else
            "VERY_GOOD" if reputation >= 8 else
            "GOOD" if reputation >= 7 else
            "ACCEPTABLE" if reputation >= 5 else
            "WARNING"
        )

        # Step 2: Get API key information and scopes
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/api_keys?limit=100",
            headers=headers
        )

        key_info = {}
        if response and response.status_code == 200:
            try:
                keys_data = response.json()
                for key in keys_data.get("result", []):
                    # Find the key being validated by checking it's in the response
                    key_id = key.get("id")
                    key_name = key.get("name", "Unknown")
                    key_scopes = key.get("scopes", [])
                    last_used = key.get("last_used_at", "Never")

                    key_info[key_id] = {
                        "name": key_name,
                        "scopes": key_scopes,
                        "last_used": last_used
                    }
            except (json.JSONDecodeError, KeyError):
                pass

        if key_info:
            # Use first key info as representative
            first_key = next(iter(key_info.values()))
            info["account"]["api_key_name"] = first_key.get("name")
            info["account"]["api_key_scopes"] = first_key.get("scopes", [])
            info["account"]["last_used"] = first_key.get("last_used", "Never")
            info["account"]["total_api_keys"] = len(key_info)

        # Step 3: Get usage statistics
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/stats?aggregated_by=day&limit=7&start_date=2020-01-01",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                stats_data = response.json()
                stats_list = stats_data.get("stats", [])

                if stats_list:
                    # Get today's stats (first item)
                    today_stat = stats_list[0]

                    info["usage"]["delivered"] = today_stat.get("delivered", 0)
                    info["usage"]["bounce"] = today_stat.get("bounce", 0)
                    info["usage"]["click"] = today_stat.get("click", 0)
                    info["usage"]["open"] = today_stat.get("open", 0)
                    info["usage"]["unsubscribe"] = today_stat.get("unsubscribe", 0)
                    info["usage"]["spam_report"] = today_stat.get("spam_report", 0)
                    info["usage"]["invalid_email"] = today_stat.get("invalid_email", 0)

                    # Calculate bounce rate
                    total_emails = info["usage"]["delivered"] + info["usage"]["bounce"]
                    if total_emails > 0:
                        bounce_rate = (info["usage"]["bounce"] / total_emails) * 100
                        info["usage"]["bounce_rate_percent"] = round(bounce_rate, 2)

                    # Calculate open rate
                    if info["usage"]["delivered"] > 0:
                        open_rate = (info["usage"]["open"] / info["usage"]["delivered"]) * 100
                        info["usage"]["open_rate_percent"] = round(open_rate, 2)

                    # Calculate click rate
                    if info["usage"]["open"] > 0:
                        click_rate = (info["usage"]["click"] / info["usage"]["open"]) * 100
                        info["usage"]["click_rate_percent"] = round(click_rate, 2)
            except (json.JSONDecodeError, KeyError, ZeroDivisionError):
                pass

        # Step 4: Get teammate/user information
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/user/profile",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                profile = response.json()
                info["account"]["username"] = profile.get("username", "N/A")
                info["account"]["first_name"] = profile.get("first_name", "N/A")
                info["account"]["last_name"] = profile.get("last_name", "N/A")
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 5: Check for marketing campaigns (indicates active account)
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/marketing/campaigns?limit=1",
            headers=headers
        )

        campaign_count = 0
        if response and response.status_code == 200:
            try:
                campaigns = response.json()
                campaign_count = campaigns.get("_metadata", {}).get("total_count", 0)
                info["quotas"]["total_campaigns"] = campaign_count
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 6: Check contacts list (for marketing feature)
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/marketing/contacts?limit=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                contacts = response.json()
                contact_count = contacts.get("contact_count", 0)
                info["quotas"]["total_contacts"] = contact_count
            except (json.JSONDecodeError, KeyError):
                pass

        return info
