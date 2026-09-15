#!/usr/bin/env python3
"""
Brevo Validator - Complete and Optimized
Validates API keys and extracts: account, credits, lists, IP whitelist, SMTP config
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any
import json


class BrevoValidator(BaseValidator):
    """Professional Brevo validator - production ready"""

    def __init__(self):
        super().__init__("Brevo", timeout=10, max_retries=3)
        self.api_url = "https://api.brevo.com/v3"

    def validate(self, api_key: str) -> ValidationResult:
        """Validate Brevo API key"""
        # Format validation
        if not self._validate_format(api_key):
            return self.create_result(
                api_key,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid key format - must be xkeysib_xxxxx"},
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
        """Validate basic Brevo key format"""
        if not isinstance(key, str):
            return False
        if not key.startswith("xkeysib_"):
            return False
        if len(key) < 40:
            return False
        return True

    def get_detailed_info(self, api_key: str) -> Dict[str, Any]:
        """Extract complete Brevo account information"""
        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "account": {},
            "quotas": {},
            "email_info": {},
            "sms_info": {},
            "lists": [],
            "ip_restrictions": [],
            "smtp_config": {},
            "features": []
        }

        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }

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

        # Check if account is live (not test/free tier)
        plan = account.get("plan", "").lower()
        info["is_live"] = plan not in ["test", "free", "trial"]
        info["account"]["plan"] = account.get("plan", "Unknown")

        # Extract account information
        info["account"]["email"] = account.get("email", "N/A")
        info["account"]["first_name"] = account.get("first_name", "N/A")
        info["account"]["last_name"] = account.get("last_name", "N/A")
        info["account"]["company_name"] = account.get("company_name", "N/A")
        info["account"]["language"] = account.get("language", "N/A")
        info["account"]["creation_date"] = str(account.get("creation_utc", "N/A"))

        # Credits information
        credits = account.get("credits", {})
        sms_credits = credits.get("smsCredits", 0)
        email_credits = credits.get("emailCredits", 0)

        info["quotas"]["sms_credits"] = sms_credits
        info["quotas"]["email_credits"] = email_credits
        info["quotas"]["sms_credits_status"] = (
            "CRITICAL" if sms_credits < 100 else
            "LOW" if sms_credits < 500 else
            "NORMAL"
        )

        # Contacts
        contacts = account.get("contacts", {})
        info["quotas"]["contact_count"] = contacts.get("count", 0)
        info["quotas"]["contact_limit"] = contacts.get("limit", 0)

        # Step 2: Get contact lists
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/contacts/lists?limit=100",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                lists_data = response.json()
                for list_item in lists_data.get("lists", []):
                    list_info = {
                        "id": list_item.get("id"),
                        "name": list_item.get("name"),
                        "total_subscribers": list_item.get("totalSubscribers", 0)
                    }
                    info["lists"].append(list_info)

                info["quotas"]["total_lists"] = len(info["lists"])
                info["quotas"]["total_subscribers"] = sum(l.get("total_subscribers", 0) for l in info["lists"])
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 3: Get SMTP relay configuration
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
                    info["smtp_config"]["enabled"] = True
                    info["smtp_config"]["ip_whitelist"] = relay.get("ip_whitelist", [])
                    info["smtp_config"]["available_quota"] = relay.get("relay_available_quota", 0)

                    # Store IP restrictions for easy reference
                    info["ip_restrictions"] = relay.get("ip_whitelist", [])

                    if info["smtp_config"]["ip_whitelist"]:
                        info["features"].append("SMTP Relay with IP Whitelist")
                else:
                    info["smtp_config"]["enabled"] = False
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 4: Get email templates count
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/smtp/templates?limit=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                templates = response.json()
                template_count = len(templates.get("templates", []))
                info["quotas"]["email_templates"] = template_count
                if template_count > 0:
                    info["features"].append("Email Templates")
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 5: Get email campaigns
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/emailCampaigns?limit=1&status=all",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                campaigns = response.json()
                campaign_count = campaigns.get("count", 0)
                info["quotas"]["email_campaigns"] = campaign_count
                if campaign_count > 0:
                    info["features"].append("Email Campaigns")
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 6: Get SMS campaign info
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/smsCampaigns?limit=1",
            headers=headers
        )

        sms_enabled = False
        if response and response.status_code == 200:
            try:
                sms_campaigns = response.json()
                sms_campaign_count = sms_campaigns.get("count", 0)
                info["quotas"]["sms_campaigns"] = sms_campaign_count
                sms_enabled = sms_campaign_count > 0
                if sms_enabled:
                    info["features"].append("SMS Campaigns")
            except (json.JSONDecodeError, KeyError):
                pass

        # SMS information
        info["sms_info"]["sms_enabled"] = sms_enabled
        info["sms_info"]["credits_available"] = sms_credits > 0

        # Step 7: Check Transactional SMS
        response, _ = self._safe_request(
            "GET",
            f"{self.api_url}/transactionalSMS/senders",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                senders = response.json()
                sender_count = len(senders.get("sendersList", []))
                if sender_count > 0:
                    info["features"].append("Transactional SMS")
                    info["sms_info"]["transactional_sms_enabled"] = True
            except (json.JSONDecodeError, KeyError):
                pass

        # Email information
        info["email_info"]["credits_available"] = email_credits > 0
        info["email_info"]["templates_configured"] = info["quotas"].get("email_templates", 0) > 0

        return info
