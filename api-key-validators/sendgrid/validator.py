#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
from pathlib import Path

class SendGridValidator:
    def __init__(self):
        self.api_url = "https://api.sendgrid.com/v3"
        self.results = []

    def validate_key(self, api_key):
        """Validate a SendGrid API key"""
        if not api_key or len(api_key) < 10:
            return {
                "status": "INVALID",
                "reason": "Key format invalid (too short)",
                "key_sample": f"{api_key[:4]}...***",
                "details": None
            }

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Test 1: Check API access
            response = requests.get(
                f"{self.api_url}/user/account",
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

            if response.status_code != 200:
                return {
                    "status": "ERROR",
                    "reason": f"API error ({response.status_code})",
                    "key_sample": f"{api_key[:4]}...***",
                    "details": response.text[:100]
                }

            account_data = response.json()

            # Test 2: Get API key details
            response = requests.get(
                f"{self.api_url}/api_keys",
                headers=headers,
                timeout=5
            )

            key_info = {
                "account_email": account_data.get("email", "N/A"),
                "account_name": account_data.get("name", "N/A"),
                "reputation": account_data.get("reputation", "N/A"),
            }

            if response.status_code == 200:
                try:
                    keys = response.json().get("result", [])
                    for key in keys:
                        if api_key in str(key):
                            key_info["key_name"] = key.get("name", "Unknown")
                            key_info["key_id"] = key.get("id", "Unknown")
                            key_info["scopes"] = key.get("scopes", [])
                            break
                except:
                    pass

            return {
                "status": "VALID",
                "reason": "API key is active",
                "key_sample": f"{api_key[:4]}...{api_key[-4:]}",
                "details": key_info,
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

        print(f"[SendGrid] Found {len(keys)} keys to validate...")

        with open(output_file, 'w') as out:
            out.write(f"=== SendGrid API Key Validation Results ===\n")
            out.write(f"Timestamp: {datetime.now().isoformat()}\n")
            out.write(f"Total Keys Checked: {len(keys)}\n\n")

            for i, key in enumerate(keys, 1):
                print(f"[{i}/{len(keys)}] Validating...", end='\r')
                result = self.validate_key(key)
                self.results.append(result)

                status = result['status']
                if status == "VALID":
                    valid_count += 1
                    out.write(f"✓ VALID - {result['key_sample']}\n")
                    out.write(f"  Account: {result['details'].get('account_email')}\n")
                    out.write(f"  Reputation: {result['details'].get('reputation')}\n")
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
    validator = SendGridValidator()
    input_file = Path(__file__).parent / "list.txt"

    if input_file.exists():
        validator.validate_file(input_file)
    else:
        print(f"Error: {input_file} not found")
        sys.exit(1)
