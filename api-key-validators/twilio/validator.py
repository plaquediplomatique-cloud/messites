#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
from pathlib import Path
from base64 import b64encode

class TwilioValidator:
    def __init__(self):
        self.api_url = "https://api.twilio.com/2010-04-01"

    def validate_credentials(self, account_sid, auth_token):
        """Validate Twilio credentials (Account SID + Auth Token)"""
        if not account_sid or not auth_token:
            return {
                "status": "INVALID",
                "reason": "Missing Account SID or Auth Token",
                "sample": "***",
                "details": None
            }

        try:
            # Create Basic Auth header
            credentials = f"{account_sid}:{auth_token}"
            encoded = b64encode(credentials.encode()).decode()
            headers = {
                "Authorization": f"Basic {encoded}"
            }

            # Test API access
            response = requests.get(
                f"{self.api_url}/Accounts/{account_sid}",
                headers=headers,
                timeout=5
            )

            if response.status_code == 401:
                return {
                    "status": "INVALID",
                    "reason": "Authentication failed (401)",
                    "sample": f"{account_sid[:6]}...{account_sid[-4:]}",
                    "details": None
                }

            if response.status_code != 200:
                return {
                    "status": "ERROR",
                    "reason": f"API error ({response.status_code})",
                    "sample": f"{account_sid[:6]}...***",
                    "details": response.text[:100]
                }

            account = response.json()

            # Get account details
            account_info = {
                "friendly_name": account.get("friendly_name", "N/A"),
                "type": account.get("type", "N/A"),
                "status": account.get("status", "N/A"),
                "date_created": account.get("date_created", "N/A"),
                "auth_token_sample": f"{auth_token[:6]}...{auth_token[-4:]}",
            }

            # Get phone numbers
            try:
                response = requests.get(
                    f"{self.api_url}/Accounts/{account_sid}/IncomingPhoneNumbers",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    numbers = response.json().get("incoming_phone_numbers", [])
                    account_info["phone_numbers_count"] = len(numbers)
                    if numbers:
                        account_info["sample_numbers"] = [n["phone_number"] for n in numbers[:3]]
            except:
                pass

            return {
                "status": "VALID",
                "reason": "Credentials are active",
                "sample": f"{account_sid}",
                "details": account_info,
                "timestamp": datetime.now().isoformat()
            }

        except requests.exceptions.Timeout:
            return {
                "status": "ERROR",
                "reason": "Request timeout",
                "sample": f"{account_sid[:6]}...***",
                "details": None
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "reason": str(type(e).__name__),
                "sample": f"{account_sid[:6]}...***",
                "details": str(e)[:100]
            }

    def validate_file(self, input_file):
        """Validate credentials from file (format: account_sid:auth_token)"""
        output_file = Path(__file__).parent / "results.txt"
        valid_count = 0
        invalid_count = 0

        with open(input_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and ':' in line]

        print(f"[Twilio] Found {len(lines)} credentials to validate...")

        with open(output_file, 'w') as out:
            out.write(f"=== Twilio Credentials Validation Results ===\n")
            out.write(f"Timestamp: {datetime.now().isoformat()}\n")
            out.write(f"Total Credentials Checked: {len(lines)}\n\n")

            for i, line in enumerate(lines, 1):
                parts = line.split(':', 1)
                if len(parts) != 2:
                    continue

                account_sid, auth_token = parts
                print(f"[{i}/{len(lines)}] Validating...", end='\r')

                result = self.validate_credentials(account_sid, auth_token)
                status = result['status']

                if status == "VALID":
                    valid_count += 1
                    out.write(f"✓ VALID - {result['sample']}\n")
                    out.write(f"  Account: {result['details'].get('friendly_name')}\n")
                    out.write(f"  Status: {result['details'].get('status')}\n")
                    out.write(f"  Phone Numbers: {result['details'].get('phone_numbers_count', 'N/A')}\n")
                elif status == "INVALID":
                    invalid_count += 1
                    out.write(f"✗ INVALID - {result['sample']}\n")
                    out.write(f"  Reason: {result['reason']}\n")
                else:
                    out.write(f"⚠ ERROR - {result['sample']}\n")
                    out.write(f"  Reason: {result['reason']}\n")
                out.write("\n")

            out.write(f"\n=== SUMMARY ===\n")
            out.write(f"Valid: {valid_count}\n")
            out.write(f"Invalid: {invalid_count}\n")
            if len(lines) > 0:
                out.write(f"Success Rate: {(valid_count/len(lines)*100):.1f}%\n")

        print(f"\n✓ Results saved to {output_file}")
        print(f"  Valid: {valid_count} | Invalid: {invalid_count}")


if __name__ == "__main__":
    validator = TwilioValidator()
    input_file = Path(__file__).parent / "list.txt"

    if input_file.exists():
        validator.validate_file(input_file)
    else:
        print(f"Error: {input_file} not found")
        sys.exit(1)
