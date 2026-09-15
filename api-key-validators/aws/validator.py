#!/usr/bin/env python3
import sys
from datetime import datetime
from pathlib import Path
import json

class AWSValidator:
    def __init__(self):
        pass

    def validate_credentials(self, access_key, secret_key):
        """Validate AWS credentials using boto3"""
        if not access_key or not secret_key:
            return {
                "status": "INVALID",
                "reason": "Missing Access Key or Secret Key",
                "sample": "***",
                "details": None
            }

        # Basic format check
        if not access_key.startswith("AKIA") and not access_key.startswith("AIDA"):
            return {
                "status": "INVALID",
                "reason": "Access Key format invalid (should start with AKIA or AIDA)",
                "sample": f"{access_key[:8]}...***",
                "details": None
            }

        if len(secret_key) < 20:
            return {
                "status": "INVALID",
                "reason": "Secret Key format invalid (too short)",
                "sample": f"{access_key[:8]}...***",
                "details": None
            }

        try:
            # Try to import boto3
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError

            # Create STS client
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name='us-east-1'
            )

            # Get current identity
            response = sts_client.get_caller_identity(timeout=5)

            account_info = {
                "account_id": response.get("Account", "N/A"),
                "user_arn": response.get("Arn", "N/A"),
                "access_key_sample": f"{access_key[:8]}...{access_key[-4:]}",
            }

            # Try to get user info
            try:
                iam_client = boto3.client(
                    'iam',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                )
                user = iam_client.get_user()
                account_info["user_name"] = user.get("User", {}).get("UserName", "N/A")
                account_info["user_create_date"] = str(user.get("User", {}).get("CreateDate", "N/A"))
            except:
                pass

            return {
                "status": "VALID",
                "reason": "Credentials are valid",
                "sample": f"{access_key}",
                "details": account_info,
                "timestamp": datetime.now().isoformat()
            }

        except ImportError:
            return {
                "status": "ERROR",
                "reason": "boto3 not installed. Install with: pip install boto3",
                "sample": f"{access_key[:8]}...***",
                "details": None
            }
        except Exception as e:
            error_str = str(e).lower()
            if "invalidclienttokensupplied" in error_str or "invalid" in error_str:
                return {
                    "status": "INVALID",
                    "reason": "Invalid credentials",
                    "sample": f"{access_key[:8]}...***",
                    "details": None
                }
            elif "unauthorized" in error_str or "denied" in error_str:
                return {
                    "status": "INVALID",
                    "reason": "Access denied / Unauthorized",
                    "sample": f"{access_key[:8]}...***",
                    "details": None
                }
            else:
                return {
                    "status": "ERROR",
                    "reason": str(type(e).__name__),
                    "sample": f"{access_key[:8]}...***",
                    "details": str(e)[:100]
                }

    def validate_file(self, input_file):
        """
        Validate AWS credentials from file
        Format: access_key:secret_key (one per line)
        """
        output_file = Path(__file__).parent / "results.txt"
        valid_count = 0
        invalid_count = 0

        with open(input_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and ':' in line]

        print(f"[AWS] Found {len(lines)} credentials to validate...")
        print(f"[AWS] Make sure boto3 is installed: pip install boto3")

        with open(output_file, 'w') as out:
            out.write(f"=== AWS Credentials Validation Results ===\n")
            out.write(f"Timestamp: {datetime.now().isoformat()}\n")
            out.write(f"Total Credentials Checked: {len(lines)}\n\n")

            for i, line in enumerate(lines, 1):
                parts = line.split(':', 1)
                if len(parts) != 2:
                    continue

                access_key, secret_key = parts
                print(f"[{i}/{len(lines)}] Validating...", end='\r')

                result = self.validate_credentials(access_key, secret_key)
                status = result['status']

                if status == "VALID":
                    valid_count += 1
                    out.write(f"✓ VALID - {result['sample'][:15]}...\n")
                    out.write(f"  Account ID: {result['details'].get('account_id')}\n")
                    out.write(f"  ARN: {result['details'].get('user_arn')}\n")
                    out.write(f"  User: {result['details'].get('user_name', 'N/A')}\n")
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
    validator = AWSValidator()
    input_file = Path(__file__).parent / "list.txt"

    if input_file.exists():
        validator.validate_file(input_file)
    else:
        print(f"Error: {input_file} not found")
        sys.exit(1)
