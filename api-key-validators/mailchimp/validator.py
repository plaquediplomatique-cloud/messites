#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
from pathlib import Path
from base64 import b64encode

class MailchimpValidator:
    def __init__(self):
        pass

    def get_datacenter(self, api_key):
        """Extract datacenter from API key"""
        if '-' in api_key:
            return api_key.split('-')[-1]
        return None

    def validate_key(self, api_key):
        """Validate a Mailchimp API key"""
        if not api_key or len(api_key) < 10 or '-' not in api_key:
            return {
                "status": "INVALID",
                "reason": "Key format invalid (should be: xxxxx-xx)",
                "key_sample": f"{api_key[:4]}...***",
                "details": None
            }

        try:
            datacenter = self.get_datacenter(api_key)
            if not datacenter:
                return {
                    "status": "INVALID",
                    "reason": "Cannot extract datacenter from key",
                    "key_sample": f"{api_key[:4]}...***",
                    "details": None
                }

            api_url = f"https://{datacenter}.api.mailchimp.com/3.0"

            # Create Basic Auth
            credentials = f"anystring:{api_key}"
            encoded = b64encode(credentials.encode()).decode()
            headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/json"
            }

            # Test API access
            response = requests.get(
                f"{api_url}/",
                headers=headers,
                timeout=5
            )

            if response.status_code == 401:
                return {
                    "status": "INVALID",
                    "reason": "Authentication failed (401)",
                    "key_sample": f"{api_key[:4]}...***",
                    "details": None
                }

            if response.status_code == 404:
                return {
                    "status": "INVALID",
                    "reason": "Invalid datacenter or key",
                    "key_sample": f"{api_key[:4]}...***",
                    "details": None
                }

            if response.status_code not in [200, 403]:
                return {
                    "status": "ERROR",
                    "reason": f"API error ({response.status_code})",
                    "key_sample": f"{api_key[:4]}...***",
                    "details": response.text[:100]
                }

            data = response.json()

            # Get account info
            try:
                response = requests.get(
                    f"{api_url}/user",
                    headers=headers,
                    timeout=5
                )

                account_info = {
                    "datacenter": datacenter,
                    "key_sample": f"{api_key[:4]}...{api_key[-4:]}",
                }

                if response.status_code == 200:
                    user = response.json()
                    account_info["account_name"] = user.get("account_name", "N/A")
                    account_info["email"] = user.get("email", "N/A")
                    account_info["username"] = user.get("username", "N/A")

                # Get lists
                response = requests.get(
                    f"{api_url}/lists",
                    headers=headers,
                    timeout=5
                )

                if response.status_code == 200:
                    lists = response.json().get("lists", [])
                    account_info["lists_count"] = len(lists)
                    if lists:
                        account_info["sample_lists"] = [l["name"] for l in lists[:3]]

                return {
                    "status": "VALID",
                    "reason": "API key is active",
                    "key_sample": f"{api_key[:4]}...{api_key[-4:]}",
                    "details": account_info,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "status": "VALID",
                    "reason": "API key is active (partial info)",
                    "key_sample": f"{api_key[:4]}...{api_key[-4:]}",
                    "details": {"datacenter": datacenter},
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

        print(f"[Mailchimp] Found {len(keys)} keys to validate...")

        with open(output_file, 'w') as out:
            out.write(f"=== Mailchimp API Key Validation Results ===\n")
            out.write(f"Timestamp: {datetime.now().isoformat()}\n")
            out.write(f"Total Keys Checked: {len(keys)}\n\n")

            for i, key in enumerate(keys, 1):
                print(f"[{i}/{len(keys)}] Validating...", end='\r')
                result = self.validate_key(key)

                status = result['status']
                if status == "VALID":
                    valid_count += 1
                    out.write(f"✓ VALID - {result['key_sample']}\n")
                    out.write(f"  Datacenter: {result['details'].get('datacenter')}\n")
                    out.write(f"  Email: {result['details'].get('email', 'N/A')}\n")
                    out.write(f"  Lists: {result['details'].get('lists_count', 'N/A')}\n")
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
    validator = MailchimpValidator()
    input_file = Path(__file__).parent / "list.txt"

    if input_file.exists():
        validator.validate_file(input_file)
    else:
        print(f"Error: {input_file} not found")
        sys.exit(1)
