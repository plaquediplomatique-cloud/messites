#!/usr/bin/env python3
"""
AWS Validator - Complete and Optimized
Validates credentials and extracts: account, regions, quotas, permissions, services
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any


class AWSValidator(BaseValidator):
    """Professional AWS validator - production ready"""

    def __init__(self):
        super().__init__("AWS", timeout=15, max_retries=3)

    def validate(self, credentials: str) -> ValidationResult:
        """Validate AWS credentials (ACCESS_KEY:SECRET_KEY)"""
        # Format validation
        if not self._validate_format(credentials):
            return self.create_result(
                credentials,
                is_valid=False,
                is_live=False,
                details={"error": "Invalid format - use ACCESS_KEY:SECRET_KEY"},
                error="Format validation failed"
            )

        access_key, secret_key = credentials.split(':', 1)
        details = self.get_detailed_info(access_key, secret_key)
        is_valid = details.get("is_valid", False)

        return self.create_result(
            credentials,
            is_valid=is_valid,
            is_live=True,  # AWS doesn't have test/live
            details=details,
            error=details.get("error")
        )

    def _validate_format(self, credentials: str) -> bool:
        """Validate basic AWS credentials format"""
        if not isinstance(credentials, str) or ':' not in credentials:
            return False

        parts = credentials.split(':', 1)
        if len(parts) != 2:
            return False

        access_key, secret_key = parts

        # AWS Access Key: AKIA or AIDA prefix, 20 chars total
        if not (access_key.startswith(("AKIA", "AIDA")) and len(access_key) == 20):
            return False

        # Secret Key: 40 chars
        if len(secret_key) < 40:
            return False

        return True

    def get_detailed_info(self, access_key: str, secret_key: str) -> Dict[str, Any]:
        """Extract complete AWS account information"""
        info = {
            "is_valid": False,
            "error": None,
            "account": {},
            "permissions": [],
            "regions": [],
            "quotas": {},
            "services": [],
            "security": {}
        }

        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError, ParamValidationError
        except ImportError:
            info["error"] = "boto3 not installed - pip install boto3"
            return info

        try:
            # Initialize STS client to verify credentials
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name='us-east-1'
            )

            # Get caller identity - this verifies the credentials
            identity = sts_client.get_caller_identity()
            info["is_valid"] = True

            # Extract account information
            account_id = identity.get("Account")
            arn = identity.get("Arn", "")
            user_id = identity.get("UserId", "")

            info["account"]["account_id"] = account_id
            info["account"]["arn"] = arn
            info["account"]["user_id"] = user_id
            info["account"]["access_key_sample"] = f"{access_key[:6]}...{access_key[-4:]}"
            info["account"]["secret_key_sample"] = f"{secret_key[:6]}...{secret_key[-4:]}"

            # Determine credential type
            if "/user/" in arn:
                info["account"]["type"] = "IAM User"
                info["account"]["username"] = arn.split("/")[-1]
            elif ":assumed-role/" in arn:
                info["account"]["type"] = "Assumed Role"
                role_info = arn.split(":")[-1].split("/")
                info["account"]["role_name"] = role_info[1] if len(role_info) > 1 else "Unknown"
                info["account"]["session_name"] = role_info[2] if len(role_info) > 2 else "Unknown"
            elif arn.endswith(f":root"):
                info["account"]["type"] = "Root Account"
            else:
                info["account"]["type"] = "Unknown"

            # Step 1: Get IAM user details (if applicable)
            try:
                iam_client = boto3.client(
                    'iam',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )

                # Get user info
                if info["account"]["type"] == "IAM User":
                    user = iam_client.get_user(UserName=info["account"]["username"])
                    user_info = user["User"]

                    info["account"]["create_date"] = str(user_info.get("CreateDate", "N/A"))
                    info["account"]["password_last_used"] = str(user_info.get("PasswordLastUsed", "Never"))

                    # Check MFA
                    mfa_devices = iam_client.list_mfa_devices(UserName=info["account"]["username"])
                    mfa_count = len(mfa_devices.get("MFADevices", []))
                    info["security"]["mfa_enabled"] = mfa_count > 0
                    info["security"]["mfa_device_count"] = mfa_count

                # Get attached policies for user/role
                if info["account"]["type"] == "IAM User":
                    policies_response = iam_client.list_attached_user_policies(
                        UserName=info["account"]["username"]
                    )
                    for policy in policies_response.get("AttachedPolicies", []):
                        info["permissions"].append(policy.get("PolicyName"))

                elif info["account"]["type"] == "Assumed Role":
                    try:
                        policies_response = iam_client.list_attached_role_policies(
                            RoleName=info["account"]["role_name"]
                        )
                        for policy in policies_response.get("AttachedPolicies", []):
                            info["permissions"].append(policy.get("PolicyName"))
                    except ClientError:
                        pass

                # Get access keys for the user (to check key age)
                if info["account"]["type"] == "IAM User":
                    try:
                        keys_response = iam_client.list_access_keys(
                            UserName=info["account"]["username"]
                        )
                        access_keys = keys_response.get("AccessKeyMetadata", [])
                        info["quotas"]["total_access_keys"] = len(access_keys)

                        # Check if current key is active
                        for key in access_keys:
                            if key.get("AccessKeyId") == access_key:
                                info["account"]["key_status"] = key.get("Status", "Unknown")
                                info["account"]["key_create_date"] = str(key.get("CreateDate", "N/A"))
                                break
                    except ClientError:
                        pass

            except (ClientError, ParamValidationError):
                # If IAM access fails, that's ok - still valid credentials
                pass

            # Step 2: Get available regions
            try:
                ec2_client = boto3.client(
                    'ec2',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )

                regions_response = ec2_client.describe_regions()
                regions = [r["RegionName"] for r in regions_response.get("Regions", [])]
                info["regions"] = sorted(regions)
                info["quotas"]["total_regions_available"] = len(regions)
            except ClientError:
                pass

            # Step 3: Check EC2 resources
            try:
                ec2_client = boto3.client(
                    'ec2',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )

                # Get instances
                instances_response = ec2_client.describe_instances()
                running_instances = 0
                total_instances = 0

                for reservation in instances_response.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        total_instances += 1
                        if instance.get("State", {}).get("Name") == "running":
                            running_instances += 1

                info["quotas"]["ec2_running_instances"] = running_instances
                info["quotas"]["ec2_total_instances"] = total_instances
                info["services"].append("EC2")
            except ClientError:
                pass

            # Step 4: Check S3 access
            try:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )

                buckets_response = s3_client.list_buckets()
                bucket_count = len(buckets_response.get("Buckets", []))
                info["quotas"]["s3_buckets"] = bucket_count
                info["services"].append("S3")
            except ClientError:
                pass

            # Step 5: Check RDS access
            try:
                rds_client = boto3.client(
                    'rds',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )

                databases_response = rds_client.describe_db_instances()
                db_count = len(databases_response.get("DBInstances", []))
                info["quotas"]["rds_databases"] = db_count
                info["services"].append("RDS")
            except ClientError:
                pass

            # Step 6: Check Lambda functions
            try:
                lambda_client = boto3.client(
                    'lambda',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )

                functions_response = lambda_client.list_functions()
                function_count = len(functions_response.get("Functions", []))
                info["quotas"]["lambda_functions"] = function_count
                info["services"].append("Lambda")
            except ClientError:
                pass

            # Step 7: Check DynamoDB tables
            try:
                dynamodb_client = boto3.client(
                    'dynamodb',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )

                tables_response = dynamodb_client.list_tables()
                table_count = len(tables_response.get("TableNames", []))
                info["quotas"]["dynamodb_tables"] = table_count
                info["services"].append("DynamoDB")
            except ClientError:
                pass

            # Step 8: Check CloudFormation stacks
            try:
                cf_client = boto3.client(
                    'cloudformation',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )

                stacks_response = cf_client.list_stacks(
                    StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE']
                )
                stack_count = len(stacks_response.get("StackSummaries", []))
                info["quotas"]["cloudformation_stacks"] = stack_count
                info["services"].append("CloudFormation")
            except ClientError:
                pass

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            if error_code == "InvalidClientTokenId":
                info["error"] = "Invalid access key or secret key"
            elif error_code == "AccessDenied":
                info["error"] = f"Access denied: {error_message[:100]}"
            else:
                info["error"] = f"AWS Error ({error_code}): {error_message[:100]}"

        except Exception as e:
            info["error"] = f"Unexpected error: {str(e)[:100]}"

        return info
