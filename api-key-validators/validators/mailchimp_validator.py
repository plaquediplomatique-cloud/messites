#!/usr/bin/env python3
"""Mailchimp Validator - Live status, lists, quotas, datacenter"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any
from base64 import b64encode


class MailchimpValidator(BaseValidator):
    """Professional Mailchimp validator with lists and quotas"""

    def __init__(self):
        super().__init__("Mailchimp", timeout=10)

    def validate(self, api_key: str) -> ValidationResult:
        """Validate Mailchimp API key"""
        if '-' not in api_key or len(api_key) < 30:
            return self.create_result(
                api_key,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid key format"},
                error="Key must include datacenter (format: key-dc)"
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
        """Get comprehensive Mailchimp account info"""
        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "datacenter": None,
            "account": {},
            "lists": [],
            "quotas": {}
        }

        # Extract datacenter
        if '-' not in api_key:
            info["error"] = "Missing datacenter in API key"
            return info

        datacenter = api_key.split('-')[-1]
        info["datacenter"] = datacenter
        api_url = f"https://{datacenter}.api.mailchimp.com/3.0"

        # Create auth header
        credentials = f"anystring:{api_key}"
        encoded = b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {encoded}"}

        # Get account info
        response, error = self._safe_request(
            "GET",
            f"{api_url}/",
            headers=headers
        )

        if error or not response:
            info["error"] = error or "Unknown error"
            return info

        if response.status_code == 401:
            info["error"] = "Authentication failed (401)"
            return info

        if response.status_code == 404:
            info["error"] = "Invalid datacenter or key"
            return info

        if response.status_code not in [200, 403]:
            info["error"] = f"API error ({response.status_code})"
            return info

        try:
            # Get user info
            response, _ = self._safe_request(
                "GET",
                f"{api_url}/user",
                headers=headers
            )

            if response and response.status_code == 200:
                user = response.json()
                info["is_valid"] = True
                info["is_live"] = True

                info["account"]["username"] = user.get("username")
                info["account"]["account_name"] = user.get("account_name")
                info["account"]["email"] = user.get("email")
                info["account"]["role"] = user.get("role")
                info["account"]["member_since"] = str(user.get("member_since", ""))

            # Get lists
            response, _ = self._safe_request(
                "GET",
                f"{api_url}/lists?count=100",
                headers=headers
            )

            if response and response.status_code == 200:
                lists_data = response.json()
                for list_item in lists_data.get("lists", []):
                    info["lists"].append({
                        "id": list_item.get("id"),
                        "name": list_item.get("name"),
                        "members": list_item.get("stats", {}).get("member_count", 0),
                        "status": list_item.get("stats", {}).get("campaign_count", 0)
                    })

                info["quotas"]["total_lists"] = len(info["lists"])
                info["quotas"]["member_count"] = sum(l["members"] for l in info["lists"])

            # Get campaigns count
            response, _ = self._safe_request(
                "GET",
                f"{api_url}/campaigns?count=1",
                headers=headers
            )

            if response and response.status_code == 200:
                campaigns = response.json()
                info["quotas"]["total_campaigns"] = campaigns.get("total_items", 0)

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info
