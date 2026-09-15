#!/usr/bin/env python3
"""
Mailchimp Validator - Complete and Optimized
Validates API keys and extracts: account, lists with stats, campaigns, datacenter
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any
from base64 import b64encode
import json


class MailchimpValidator(BaseValidator):
    """Professional Mailchimp validator - production ready"""

    def __init__(self):
        super().__init__("Mailchimp", timeout=10, max_retries=3)

    def validate(self, api_key: str) -> ValidationResult:
        """Validate Mailchimp API key"""
        # Format validation
        if not self._validate_format(api_key):
            return self.create_result(
                api_key,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid key format - must be key-datacenter (e.g., abc123-us1)"},
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
        """Validate basic Mailchimp key format"""
        if not isinstance(key, str) or '-' not in key:
            return False

        parts = key.rsplit('-', 1)
        if len(parts) != 2:
            return False

        key_part, datacenter = parts

        # Key part should be 32 chars alphanumeric
        if len(key_part) < 30:
            return False

        # Datacenter should be like us1, us2, eu1, etc
        if len(datacenter) < 2 or len(datacenter) > 4:
            return False

        return True

    def get_detailed_info(self, api_key: str) -> Dict[str, Any]:
        """Extract complete Mailchimp account information"""
        # Extract datacenter from key
        if '-' not in api_key:
            return {"is_valid": False, "error": "Invalid key format"}

        datacenter = api_key.split('-')[-1]
        api_url = f"https://{datacenter}.api.mailchimp.com/3.0"

        info = {
            "is_valid": False,
            "is_live": True,  # Mailchimp doesn't have test/live distinction
            "error": None,
            "datacenter": datacenter,
            "account": {},
            "lists": [],
            "quotas": {},
            "security": {},
            "capabilities": []
        }

        # Create Basic Auth header
        credentials = f"anystring:{api_key}"
        try:
            encoded = b64encode(credentials.encode()).decode('ascii')
        except Exception:
            info["error"] = "Failed to encode credentials"
            return info

        headers = {"Authorization": f"Basic {encoded}"}

        # Step 1: Test API access
        response, error = self._safe_request(
            "GET",
            f"{api_url}/",
            headers=headers
        )

        if error or not response:
            info["error"] = error or "Connection failed"
            return info

        if response.status_code == 401:
            info["error"] = "Invalid API key"
            return info

        if response.status_code == 404:
            info["error"] = "Invalid datacenter or key format"
            return info

        if response.status_code not in [200]:
            if response.status_code != 403:  # 403 is still valid, just no /account access
                info["error"] = f"API returned status {response.status_code}"
                return info

        # Step 2: Get user profile information
        response, _ = self._safe_request(
            "GET",
            f"{api_url}/user",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                user = response.json()
                info["is_valid"] = True

                info["account"]["username"] = user.get("username", "N/A")
                info["account"]["account_name"] = user.get("account_name", "N/A")
                info["account"]["email"] = user.get("email", "N/A")
                info["account"]["role"] = user.get("role", "N/A")
                info["account"]["member_since"] = str(user.get("member_since", "N/A"))

                # Check if email is verified
                email_verified = user.get("email_verified", False)
                info["account"]["email_verified"] = email_verified

                # Account ID
                account_id = user.get("account_id", "N/A")
                info["account"]["account_id"] = account_id

                # Account pending
                pending_change = user.get("account_pending", False)
                if pending_change:
                    info["security"]["account_pending_changes"] = True
            except json.JSONDecodeError:
                info["error"] = "Invalid JSON response"
                return info
        else:
            info["error"] = "Failed to authenticate with API key"
            return info

        # Step 3: Get email lists
        response, _ = self._safe_request(
            "GET",
            f"{api_url}/lists?count=100&fields=lists.id,lists.name,lists.stats.member_count,lists.stats.campaign_count,lists.subscribe_url_long,lists.permission_reminder",
            headers=headers
        )

        total_members = 0
        if response and response.status_code == 200:
            try:
                lists_data = response.json()
                for list_item in lists_data.get("lists", []):
                    list_stats = list_item.get("stats", {})
                    members = list_stats.get("member_count", 0)
                    campaigns = list_stats.get("campaign_count", 0)

                    list_info = {
                        "id": list_item.get("id"),
                        "name": list_item.get("name"),
                        "members": members,
                        "campaigns": campaigns,
                        "subscribe_url": list_item.get("subscribe_url_long", ""),
                        "permission_reminder": list_item.get("permission_reminder", "")
                    }
                    info["lists"].append(list_info)
                    total_members += members

                info["quotas"]["total_lists"] = len(info["lists"])
                info["quotas"]["total_members"] = total_members
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 4: Get campaigns
        response, _ = self._safe_request(
            "GET",
            f"{api_url}/campaigns?count=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                campaigns = response.json()
                campaign_count = campaigns.get("total_items", 0)
                info["quotas"]["total_campaigns"] = campaign_count

                if campaign_count > 0:
                    info["capabilities"].append("Campaigns")
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 5: Get automations count
        response, _ = self._safe_request(
            "GET",
            f"{api_url}/automations?count=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                automations = response.json()
                automation_count = automations.get("total_items", 0)
                info["quotas"]["total_automations"] = automation_count

                if automation_count > 0:
                    info["capabilities"].append("Automations")
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 6: Get templates
        response, _ = self._safe_request(
            "GET",
            f"{api_url}/templates?count=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                templates = response.json()
                template_count = templates.get("total_items", 0)
                info["quotas"]["total_templates"] = template_count

                if template_count > 0:
                    info["capabilities"].append("Templates")
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 7: Get file manager (content)
        response, _ = self._safe_request(
            "GET",
            f"{api_url}/file-manager/files?count=1",
            headers=headers
        )

        if response and response.status_code == 200:
            try:
                files = response.json()
                file_count = files.get("total_items", 0)
                info["quotas"]["total_files"] = file_count

                if file_count > 0:
                    info["capabilities"].append("File Manager")
            except (json.JSONDecodeError, KeyError):
                pass

        # Step 8: Verify key is actually valid by checking if at least one call succeeded
        if not info["is_valid"] and len(info["lists"]) == 0:
            # Try one more endpoint to confirm
            response, _ = self._safe_request(
                "GET",
                f"{api_url}/lists?count=1",
                headers=headers
            )

            if response and response.status_code == 200:
                info["is_valid"] = True
            elif response and response.status_code in [403, 401]:
                info["error"] = "API key is valid but permissions are restricted"
                info["is_valid"] = False

        return info
