#!/usr/bin/env python3
"""AWS Validator - Account ID, region, quotas, permissions"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any


class AWSValidator(BaseValidator):
    """Professional AWS validator with permissions and quotas"""

    def __init__(self):
        super().__init__("AWS", timeout=10)

    def validate(self, credentials: str) -> ValidationResult:
        """Validate AWS credentials (ACCESS_KEY:SECRET_KEY)"""
        if ':' not in credentials:
            return self.create_result(
                credentials,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid format - use ACCESS_KEY:SECRET_KEY"},
                error="Missing colon separator"
            )

        access_key, secret_key = credentials.split(':', 1)

        if not (access_key.startswith(("AKIA", "AIDA")) and len(access_key) >= 16):
            return self.create_result(
                credentials,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid access key format"},
                error="Access key must start with AKIA or AIDA"
            )

        details = self.get_detailed_info(access_key, secret_key)
        is_valid = details.get("is_valid", False)
        is_live = True  # AWS doesn't have test/live distinction

        return self.create_result(
            credentials,
            is_valid=is_valid,
            is_live=is_live,
            details=details,
            error=details.get("error")
        )

    def get_detailed_info(self, access_key: str, secret_key: str) -> Dict[str, Any]:
        """Get comprehensive AWS account info"""
        info = {
            "is_valid": False,
            "is_live": True,
            "error": None,
            "account": {},
            "permissions": [],
            "quotas": {},
            "services": []
        }

        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
        except ImportError:
            info["error"] = "boto3 not installed - pip install boto3"
            return info

        try:
            # Initialize STS client for identity check
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name='us-east-1'
            )

            # Get caller identity
            identity = sts_client.get_caller_identity()
            info["is_valid"] = True
            info["account"]["account_id"] = identity.get("Account")
            info["account"]["arn"] = identity.get("Arn")
            info["account"]["user_id"] = identity.get("UserId")

            # Extract user info if available
            arn = identity.get("Arn", "")
            if "/user/" in arn:
                info["account"]["type"] = "IAM User"
                info["account"]["username"] = arn.split("/")[-1]
            elif ":assumed-role/" in arn:
                info["account"]["type"] = "Assumed Role"
                parts = arn.split(":")[-1].split("/")
                info["account"]["role"] = parts[1] if len(parts) > 1 else "Unknown"
            else:
                info["account"]["type"] = "Root"

            # Try to get user details
            try:
                iam_client = boto3.client(
                    'iam',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
                user = iam_client.get_user()
                info["account"]["user_name"] = user["User"]["UserName"]
                info["account"]["create_date"] = str(user["User"]["CreateDate"])
                info["account"]["mfa_enabled"] = user["User"].get("MFADevices", [])

                # Get attached policies
                policies_response = iam_client.list_attached_user_policies(
                    UserName=info["account"]["user_name"]
                )
                info["permissions"] = [p["PolicyName"] for p in policies_response.get("AttachedPolicies", [])]

            except ClientError:
                pass

            # Check available regions
            try:
                ec2_client = boto3.client(
                    'ec2',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )
                regions_response = ec2_client.describe_regions()
                regions = [r["RegionName"] for r in regions_response.get("Regions", [])]
                info["quotas"]["available_regions"] = len(regions)
                info["quotas"]["regions"] = regions[:5] + (["..."] if len(regions) > 5 else [])
            except:
                pass

            # Check EC2 quotas
            try:
                ec2_client = boto3.client(
                    'ec2',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )
                instances = ec2_client.describe_instances()
                running_count = sum(
                    len(r["Instances"])
                    for r in instances["Reservations"]
                )
                info["quotas"]["ec2_instances_running"] = running_count
                info["services"].append("EC2")
            except:
                pass

            # Check S3 access
            try:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
                buckets = s3_client.list_buckets()
                info["quotas"]["s3_buckets"] = len(buckets.get("Buckets", []))
                info["services"].append("S3")
            except:
                pass

            # Check RDS access
            try:
                rds_client = boto3.client(
                    'rds',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )
                databases = rds_client.describe_db_instances()
                info["quotas"]["rds_databases"] = len(databases.get("DBInstances", []))
                info["services"].append("RDS")
            except:
                pass

        except Exception as e:
            info["error"] = f"AWS Error: {str(e)[:100]}"

        return info
