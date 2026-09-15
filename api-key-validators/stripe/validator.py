#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
from pathlib import Path
from base64 import b64encode

class StripeValidator:
    def __init__(self):
        self.api_url = "https://api.stripe.com/v1"

    def validate_key(self, api_key):
        """Validate a Stripe API key (secret or restricted)"""
        if not api_key or len(api_key) < 10:
            return {
                "status": "INVALID",
                "reason": "Key format invalid (too short)",
                "key_sample": f"{api_key[:4]}...***",
                "details": None
            }

        try:
            # Stripe uses Basic Auth with key as username and empty password
            encoded = b64encode(f"{api_key}:".encode()).decode()
            headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            # Test API access
            response = requests.get(
                f"{self.api_url}/charges",
                headers=headers,
                timeout=5,
                params={"limit": 1}
            )

            if response.status_code == 401:
                return {
                    "status": "INVALID",
                    "reason": "Authentication failed (401)",
                    "key_sample": f"{api_key[:4]}...***",
                    "details": None
                }

            if response.status_code == 403:
                return {
                    "status": "INVALID",
                    "reason": "Access forbidden (403) - Possibly restricted key",
                    "key_sample": f"{api_key[:4]}...***",
                    "details": None
                }

            if response.status_code not in [200]:
                return {
                    "status": "ERROR",
                    "reason": f"API error ({response.status_code})",
                    "key_sample": f"{api_key[:4]}...***",
                    "details": response.text[:100]
                }

            # Get account info
            response = requests.get(
                f"{self.api_url}/account",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                account = response.json()

                account_info = {
                    "account_id": account.get("id", "N/A"),
                    "business_name": account.get("business_profile", {}).get("name", "N/A"),
                    "country": account.get("country", "N/A"),
                    "type": account.get("type", "N/A"),
                    "key_type": "SECRET_KEY" if api_key.startswith("sk_") else "RESTRICTED_KEY",
                    "key_sample": f"{api_key[:4]}...{api_key[-4:]}",
                }

                if api_key.startswith("sk_live"):
                    account_info["environment"] = "LIVE"
                elif api_key.startswith("sk_test"):
                    account_info["environment"] = "TEST"

                return {
                    "status": "VALID",
                    "reason": "API key is active",
                    "key_sample": f"{api_key[:4]}...{api_key[-4:]}",
                    "details": account_info,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "VALID",
                    "reason": "Key is valid (account access denied)",
                    "key_sample": f"{api_key[:4]}...{api_key[-4:]}",
                    "details": {
                        "key_type": "SECRET_KEY" if api_key.startswith("sk_") else "RESTRICTED_KEY",
                        "environment": "LIVE" if api_key.startswith("sk_live") else "TEST",
                    },
                    "timestamp": datetime.now().isoformat()
                }

        except requests.exceptions.Timeout:
            return {
                "status": "ERROR",
                "reason": "Request timeout",
                "key_sample": f"{api_key[:4]}...***",
                "details": None
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "reason": str(type(e).__name__),
                "key_sample": f"{api_key[:4]}...***",
                "details": str(e)[:100]
            }

    def validate_file(self, input_file):
        """Validate keys from file"""
        output_file = Path(__file__).parent / "results.txt"
        valid_count = 0
        invalid_count = 0

        with open(input_file, 'r') as f:
            keys = [line.strip() for line in f if line.strip()]

        print(f"[Stripe] Found {len(keys)} keys to validate...")

        with open(output_file, 'w') as out:
            out.write(f"=== Stripe API Key Validation Results ===\n")
            out.write(f"Timestamp: {datetime.now().isoformat()}\n")
            out.write(f"Total Keys Checked: {len(keys)}\n\n")

            for i, key in enumerate(keys, 1):
                print(f"[{i}/{len(keys)}] Validating...", end='\r')
                result = self.validate_key(key)

                status = result['status']
                if status == "VALID":
                    valid_count += 1
                    out.write(f"✓ VALID - {result['key_sample']}\n")
                    out.write(f"  Environment: {result['details'].get('environment', 'N/A')}\n")
                    out.write(f"  Type: {result['details'].get('key_type', 'N/A')}\n")
                    out.write(f"  Business: {result['details'].get('business_name', 'N/A')}\n")
                    out.write(f"  Country: {result['details'].get('country', 'N/A')}\n")
                elif status == "INVALID":
                    invalid_count += 1
                    out.write(f"✗ INVALID - {result['key_sample']}\n")
                    out.write(f"  Reason: {result['reason']}\n")
                else:
                    out.write(f"⚠ ERROR - {result['key_sample']}\n")
                    out.write(f"  Reason: {result['reason']}\n")
                out.write("\n")

            out.write(f"\n=== SUMMARY ===\n")
            out.write(f"Valid: {valid_count}\n")
            out.write(f"Invalid: {invalid_count}\n")
            out.write(f"Success Rate: {(valid_count/len(keys)*100):.1f}%\n")

        print(f"\n✓ Results saved to {output_file}")
        print(f"  Valid: {valid_count} | Invalid: {invalid_count}")


if __name__ == "__main__":
    validator = StripeValidator()
    input_file = Path(__file__).parent / "list.txt"

    if input_file.exists():
        validator.validate_file(input_file)
    else:
        print(f"Error: {input_file} not found")
        sys.exit(1)
