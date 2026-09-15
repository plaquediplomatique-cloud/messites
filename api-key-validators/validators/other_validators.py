#!/usr/bin/env python3
"""
Additional Service Validators - GitHub, GitLab, MongoDB, Slack, Firebase, etc.
Comprehensive validators for popular APIs
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any


class GitHubValidator(BaseValidator):
    """GitHub Token Validator"""

    def __init__(self):
        super().__init__("GitHub", timeout=10)
        self.api_url = "https://api.github.com"

    def validate(self, token: str) -> ValidationResult:
        """Validate GitHub token"""
        if not token or len(token) < 20:
            return self.create_result(
                token, False, False,
                {"error": "Invalid token format"},
                "Token too short"
            )

        details = self.get_detailed_info(token)
        return self.create_result(
            token,
            details.get("is_valid", False),
            details.get("is_live", False),
            details,
            details.get("error")
        )

    def get_detailed_info(self, token: str) -> Dict[str, Any]:
        """Get GitHub user and token info"""
        info = {
            "is_valid": False,
            "is_live": False,
            "error": None,
            "user": {},
            "scopes": [],
            "quotas": {}
        }

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/user",
            headers=headers
        )

        if error or not response:
            info["error"] = error
            return info

        if response.status_code == 401:
            info["error"] = "Invalid token"
            return info

        if response.status_code != 200:
            info["error"] = f"API error ({response.status_code})"
            return info

        try:
            user = response.json()
            info["is_valid"] = True
            info["is_live"] = True

            info["user"]["login"] = user.get("login")
            info["user"]["name"] = user.get("name")
            info["user"]["email"] = user.get("email")
            info["user"]["company"] = user.get("company")
            info["user"]["location"] = user.get("location")
            info["user"]["public_repos"] = user.get("public_repos")

            # Get token scopes from headers
            if "X-OAuth-Scopes" in response.headers:
                scopes = response.headers["X-OAuth-Scopes"].split(", ")
                info["scopes"] = [s.strip() for s in scopes if s.strip()]

            # Get rate limit
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/rate_limit",
                headers=headers
            )

            if response and response.status_code == 200:
                rl = response.json()["rate"]["limit"]
                info["quotas"]["api_calls_limit"] = rl
                info["quotas"]["api_calls_remaining"] = response.json()["rate"]["remaining"]

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info


class GitLabValidator(BaseValidator):
    """GitLab Token Validator"""

    def __init__(self):
        super().__init__("GitLab", timeout=10)
        self.api_url = "https://gitlab.com/api/v4"

    def validate(self, token: str) -> ValidationResult:
        """Validate GitLab token"""
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
        """Get GitLab user and project info"""
        info = {
            "is_valid": False,
            "error": None,
            "user": {},
            "quotas": {}
        }

        headers = {"PRIVATE-TOKEN": token}

        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/user",
            headers=headers
        )

        if error or not response:
            info["error"] = error
            return info

        if response.status_code == 401:
            info["error"] = "Invalid token"
            return info

        if response.status_code != 200:
            info["error"] = f"API error ({response.status_code})"
            return info

        try:
            user = response.json()
            info["is_valid"] = True

            info["user"]["username"] = user.get("username")
            info["user"]["name"] = user.get("name")
            info["user"]["email"] = user.get("email")
            info["user"]["state"] = user.get("state")

            # Get projects
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/projects?simple=true",
                headers=headers
            )

            if response and response.status_code == 200:
                projects = response.json()
                info["quotas"]["projects_count"] = len(projects)

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info


class MongoDBValidator(BaseValidator):
    """MongoDB Atlas API Validator"""

    def __init__(self):
        super().__init__("MongoDB", timeout=10)
        self.api_url = "https://cloud.mongodb.com/api/atlas/v1.0"

    def validate(self, credentials: str) -> ValidationResult:
        """Validate MongoDB API credentials (PUBLIC_KEY:PRIVATE_KEY)"""
        if ':' not in credentials:
            return self.create_result(
                credentials, False, False,
                {"error": "Invalid format"},
                "Use PUBLIC_KEY:PRIVATE_KEY"
            )

        public, private = credentials.split(':', 1)
        details = self.get_detailed_info(public, private)
        return self.create_result(
            credentials,
            details.get("is_valid", False),
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, public_key: str, private_key: str) -> Dict[str, Any]:
        """Get MongoDB organization and clusters info"""
        info = {
            "is_valid": False,
            "error": None,
            "organization": {},
            "quotas": {}
        }

        from base64 import b64encode
        credentials = f"{public_key}:{private_key}"
        encoded = b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {encoded}"}

        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/orgs",
            headers=headers
        )

        if error or not response:
            info["error"] = error
            return info

        if response.status_code == 401:
            info["error"] = "Invalid credentials"
            return info

        try:
            orgs = response.json().get("results", [])
            if orgs:
                info["is_valid"] = True
                org = orgs[0]
                info["organization"]["name"] = org.get("name")
                info["organization"]["id"] = org.get("id")
                info["quotas"]["organizations"] = len(orgs)

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info


class SlackValidator(BaseValidator):
    """Slack Bot Token Validator"""

    def __init__(self):
        super().__init__("Slack", timeout=10)
        self.api_url = "https://slack.com/api"

    def validate(self, token: str) -> ValidationResult:
        """Validate Slack token"""
        if not token or not token.startswith(("xoxb-", "xoxp-")):
            return self.create_result(
                token, False, False,
                {"error": "Invalid token"},
                "Must start with xoxb- or xoxp-"
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
        """Get Slack workspace info"""
        info = {
            "is_valid": False,
            "error": None,
            "workspace": {},
            "quotas": {}
        }

        headers = {"Authorization": f"Bearer {token}"}

        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/auth.test",
            headers=headers
        )

        if error or not response:
            info["error"] = error
            return info

        if response.status_code != 200:
            info["error"] = f"Invalid token"
            return info

        try:
            data = response.json()
            if data.get("ok"):
                info["is_valid"] = True
                info["workspace"]["team"] = data.get("team")
                info["workspace"]["user_id"] = data.get("user_id")
                info["workspace"]["team_id"] = data.get("team_id")

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info
