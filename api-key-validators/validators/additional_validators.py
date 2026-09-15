#!/usr/bin/env python3
"""
Additional API Validators - Complete Coverage
HuggingFace, Azure, GCP, DigitalOcean, Heroku, Gitea, Bitbucket, etc.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any
from base64 import b64encode
import json


class HuggingFaceValidator(BaseValidator):
    """HuggingFace API Token Validator"""

    def __init__(self):
        super().__init__("HuggingFace", timeout=10, max_retries=3)
        self.api_url = "https://huggingface.co/api"

    def validate(self, token: str) -> ValidationResult:
        if not token or len(token) < 20:
            return self.create_result(
                token, False, False,
                {"error": "Invalid token"},
                "Token too short"
            )

        details = self.get_detailed_info(token)
        return self.create_result(
            token,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, token: str) -> Dict[str, Any]:
        info = {
            "is_valid": False,
            "error": None,
            "user": {},
            "quotas": {}
        }

        headers = {"Authorization": f"Bearer {token}"}

        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/user",
            headers=headers
        )

        if error or not response or response.status_code != 200:
            info["error"] = error or "Invalid token"
            return info

        try:
            user = response.json()
            info["is_valid"] = True

            info["user"]["username"] = user.get("user", "N/A")
            info["user"]["full_name"] = user.get("fullname", "N/A")
            info["user"]["email"] = user.get("email", "N/A")
            info["user"]["avatar_url"] = user.get("avatarUrl", "N/A")

            # Get models
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/user/models",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    models = response.json()
                    info["quotas"]["models_count"] = len(models)
                except:
                    pass

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info


class AzureValidator(BaseValidator):
    """Azure Subscription Key / Access Token Validator"""

    def __init__(self):
        super().__init__("Azure", timeout=10, max_retries=3)

    def validate(self, token: str) -> ValidationResult:
        if not token or len(token) < 30:
            return self.create_result(
                token, False, False,
                {"error": "Invalid token"},
                "Token too short"
            )

        details = self.get_detailed_info(token)
        return self.create_result(
            token,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, token: str) -> Dict[str, Any]:
        info = {
            "is_valid": False,
            "error": None,
            "subscription": {},
            "quotas": {}
        }

        # Azure tokens are often in JWT format, just validate structure
        if len(token) < 100:
            info["error"] = "Token format invalid"
            return info

        try:
            # Try multiple Azure endpoints
            headers = {"Authorization": f"Bearer {token}"}

            response, error = self._safe_request(
                "GET",
                "https://management.azure.com/subscriptions?api-version=2020-01-01",
                headers=headers
            )

            if response and response.status_code == 200:
                info["is_valid"] = True
                try:
                    subs = response.json()
                    subscription_list = subs.get("value", [])
                    info["quotas"]["subscriptions_count"] = len(subscription_list)

                    if subscription_list:
                        sub = subscription_list[0]
                        info["subscription"]["id"] = sub.get("subscriptionId", "N/A")
                        info["subscription"]["display_name"] = sub.get("displayName", "N/A")
                        info["subscription"]["state"] = sub.get("state", "N/A")
                except:
                    pass
            else:
                info["error"] = "Invalid token or insufficient permissions"

        except Exception as e:
            info["error"] = f"Error: {str(e)[:50]}"

        return info


class GCPValidator(BaseValidator):
    """Google Cloud Platform Service Account / Access Token Validator"""

    def __init__(self):
        super().__init__("GCP", timeout=10, max_retries=3)

    def validate(self, credentials: str) -> ValidationResult:
        if not credentials or len(credentials) < 50:
            return self.create_result(
                credentials, False, False,
                {"error": "Invalid credentials"},
                "Too short"
            )

        details = self.get_detailed_info(credentials)
        return self.create_result(
            credentials,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, credentials: str) -> Dict[str, Any]:
        info = {
            "is_valid": False,
            "error": None,
            "project": {},
            "quotas": {}
        }

        # Try to parse as JSON (service account key)
        try:
            if credentials.startswith("{"):
                creds = json.loads(credentials)
                info["is_valid"] = True

                info["project"]["project_id"] = creds.get("project_id", "N/A")
                info["project"]["service_account"] = creds.get("client_email", "N/A")
                info["project"]["key_id"] = creds.get("private_key_id", "N/A")
                info["project"]["type"] = creds.get("type", "N/A")

                return info
        except:
            pass

        # Try Bearer token
        if credentials.startswith("ya29.") or len(credentials) > 100:
            try:
                headers = {"Authorization": f"Bearer {credentials}"}
                response, _ = self._safe_request(
                    "GET",
                    "https://www.googleapis.com/oauth2/v1/userinfo",
                    headers=headers
                )

                if response and response.status_code == 200:
                    info["is_valid"] = True
                    try:
                        user = response.json()
                        info["project"]["email"] = user.get("email", "N/A")
                        info["project"]["name"] = user.get("name", "N/A")
                    except:
                        pass
                else:
                    info["error"] = "Invalid token"
            except Exception as e:
                info["error"] = str(e)[:50]

        return info


class DigitalOceanValidator(BaseValidator):
    """DigitalOcean API Token Validator"""

    def __init__(self):
        super().__init__("DigitalOcean", timeout=10, max_retries=3)
        self.api_url = "https://api.digitalocean.com/v2"

    def validate(self, token: str) -> ValidationResult:
        if not token or len(token) < 30:
            return self.create_result(
                token, False, False,
                {"error": "Invalid token"},
                "Token too short"
            )

        details = self.get_detailed_info(token)
        return self.create_result(
            token,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, token: str) -> Dict[str, Any]:
        info = {
            "is_valid": False,
            "error": None,
            "account": {},
            "quotas": {}
        }

        headers = {"Authorization": f"Bearer {token}"}

        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/account",
            headers=headers
        )

        if error or not response or response.status_code != 200:
            info["error"] = error or "Invalid token"
            return info

        try:
            account = response.json()
            account_data = account.get("account", {})
            info["is_valid"] = True

            info["account"]["email"] = account_data.get("email", "N/A")
            info["account"]["status"] = account_data.get("status", "N/A")
            info["account"]["floating_ip_limit"] = account_data.get("floating_ip_limit")
            info["account"]["droplet_limit"] = account_data.get("droplet_limit")

            # Get droplets
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/droplets",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    droplets = response.json()
                    info["quotas"]["droplets_count"] = len(droplets.get("droplets", []))
                except:
                    pass

        except Exception as e:
            info["error"] = str(e)[:50]

        return info


class HerokuValidator(BaseValidator):
    """Heroku API Token Validator"""

    def __init__(self):
        super().__init__("Heroku", timeout=10, max_retries=3)
        self.api_url = "https://api.heroku.com"

    def validate(self, token: str) -> ValidationResult:
        if not token or len(token) < 20:
            return self.create_result(
                token, False, False,
                {"error": "Invalid token"},
                "Token too short"
            )

        details = self.get_detailed_info(token)
        return self.create_result(
            token,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, token: str) -> Dict[str, Any]:
        info = {
            "is_valid": False,
            "error": None,
            "account": {},
            "quotas": {}
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.heroku+json;version=3"
        }

        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/user",
            headers=headers
        )

        if error or not response or response.status_code != 200:
            info["error"] = error or "Invalid token"
            return info

        try:
            user = response.json()
            info["is_valid"] = True

            info["account"]["email"] = user.get("email", "N/A")
            info["account"]["id"] = user.get("id", "N/A")

            # Get apps
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/apps",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    apps = response.json()
                    info["quotas"]["apps_count"] = len(apps)
                except:
                    pass

        except Exception as e:
            info["error"] = str(e)[:50]

        return info


class GiteaValidator(BaseValidator):
    """Gitea Instance Token Validator"""

    def __init__(self):
        super().__init__("Gitea", timeout=10, max_retries=3)

    def validate(self, credentials: str) -> ValidationResult:
        """Validate Gitea with URL:TOKEN format"""
        if ':' not in credentials or not credentials.startswith("http"):
            return self.create_result(
                credentials, False, False,
                {"error": "Invalid format - use URL:TOKEN"},
                "Expected URL:TOKEN"
            )

        parts = credentials.rsplit(':', 1)
        if len(parts) != 2:
            return self.create_result(
                credentials, False, False,
                {"error": "Invalid format"},
                "Failed to parse"
            )

        url, token = parts
        details = self.get_detailed_info(url, token)
        return self.create_result(
            credentials,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, base_url: str, token: str) -> Dict[str, Any]:
        info = {
            "is_valid": False,
            "error": None,
            "user": {},
            "instance": {},
            "quotas": {}
        }

        # Clean up URL
        if not base_url.endswith("/"):
            base_url += "/"

        headers = {"Authorization": f"token {token}"}

        response, error = self._safe_request(
            "GET",
            f"{base_url}api/v1/user",
            headers=headers
        )

        if error or not response or response.status_code != 200:
            info["error"] = error or "Invalid credentials"
            return info

        try:
            user = response.json()
            info["is_valid"] = True

            info["user"]["username"] = user.get("login", "N/A")
            info["user"]["full_name"] = user.get("full_name", "N/A")
            info["user"]["email"] = user.get("email", "N/A")
            info["instance"]["url"] = base_url

            # Get repos
            response, _ = self._safe_request(
                "GET",
                f"{base_url}api/v1/user/repos",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    repos = response.json()
                    info["quotas"]["repositories"] = len(repos)
                except:
                    pass

        except Exception as e:
            info["error"] = str(e)[:50]

        return info


class BitbucketValidator(BaseValidator):
    """Bitbucket Cloud API Token Validator"""

    def __init__(self):
        super().__init__("Bitbucket", timeout=10, max_retries=3)
        self.api_url = "https://api.bitbucket.org/2.0"

    def validate(self, credentials: str) -> ValidationResult:
        """Validate Bitbucket with USERNAME:PASSWORD format"""
        if ':' not in credentials:
            return self.create_result(
                credentials, False, False,
                {"error": "Invalid format"},
                "Use USERNAME:PASSWORD"
            )

        username, password = credentials.split(':', 1)
        details = self.get_detailed_info(username, password)
        return self.create_result(
            credentials,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, username: str, password: str) -> Dict[str, Any]:
        info = {
            "is_valid": False,
            "error": None,
            "user": {},
            "quotas": {}
        }

        credentials = f"{username}:{password}"
        try:
            encoded = b64encode(credentials.encode()).decode('ascii')
        except:
            info["error"] = "Failed to encode credentials"
            return info

        headers = {"Authorization": f"Basic {encoded}"}

        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/user",
            headers=headers
        )

        if error or not response or response.status_code != 200:
            info["error"] = error or "Invalid credentials"
            return info

        try:
            user = response.json()
            info["is_valid"] = True

            info["user"]["username"] = user.get("username", "N/A")
            info["user"]["display_name"] = user.get("display_name", "N/A")
            info["user"]["email"] = user.get("email", "N/A")

            # Get repos
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/repositories/{username}",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    data = response.json()
                    info["quotas"]["repositories"] = data.get("pagelen", 0)
                except:
                    pass

        except Exception as e:
            info["error"] = str(e)[:50]

        return info


class NpmValidator(BaseValidator):
    """NPM Registry Token Validator"""

    def __init__(self):
        super().__init__("NPM", timeout=10, max_retries=3)
        self.api_url = "https://registry.npmjs.org"

    def validate(self, token: str) -> ValidationResult:
        if not token or len(token) < 20:
            return self.create_result(
                token, False, False,
                {"error": "Invalid token"},
                "Token too short"
            )

        details = self.get_detailed_info(token)
        return self.create_result(
            token,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, token: str) -> Dict[str, Any]:
        info = {
            "is_valid": False,
            "error": None,
            "user": {},
            "quotas": {}
        }

        headers = {"Authorization": f"Bearer {token}"}

        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/-/user/org.couchdb.user:whoami",
            headers=headers
        )

        if error or not response or response.status_code != 200:
            info["error"] = error or "Invalid token"
            return info

        try:
            user = response.json()
            info["is_valid"] = True

            info["user"]["username"] = user.get("name", "N/A")
            info["user"]["email"] = user.get("email", "N/A")

        except Exception as e:
            info["error"] = str(e)[:50]

        return info


class PyPiValidator(BaseValidator):
    """PyPI API Token Validator"""

    def __init__(self):
        super().__init__("PyPI", timeout=10, max_retries=3)
        self.api_url = "https://pypi.org/pypi"

    def validate(self, token: str) -> ValidationResult:
        if not token or len(token) < 20:
            return self.create_result(
                token, False, False,
                {"error": "Invalid token"},
                "Token too short"
            )

        details = self.get_detailed_info(token)
        return self.create_result(
            token,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, token: str) -> Dict[str, Any]:
        info = {
            "is_valid": False,
            "error": None,
            "user": {},
        }

        # PyPI tokens are usually __token__ username with token as password
        if token.startswith("pypi-"):
            info["is_valid"] = True
            info["user"]["token_type"] = "API Token (pypi-*)"
            return info

        info["error"] = "Unable to validate PyPI token (offline verification only)"
        return info
