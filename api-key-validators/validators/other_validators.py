#!/usr/bin/env python3
"""
Additional Service Validators - GitHub, GitLab, MongoDB, Slack
Complete and optimized validators for popular APIs
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_validator import BaseValidator, ValidationResult
from typing import Dict, Any
from base64 import b64encode
import json


class GitHubValidator(BaseValidator):
    """GitHub Token Validator - comprehensive"""

    def __init__(self):
        super().__init__("GitHub", timeout=10, max_retries=3)
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
            True,
            details,
            details.get("error")
        )

    def get_detailed_info(self, token: str) -> Dict[str, Any]:
        """Get GitHub user and token info"""
        info = {
            "is_valid": False,
            "error": None,
            "user": {},
            "scopes": [],
            "rate_limit": {},
            "quotas": {}
        }

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Get user info
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

            # User info
            info["user"]["login"] = user.get("login")
            info["user"]["name"] = user.get("name")
            info["user"]["email"] = user.get("email")
            info["user"]["company"] = user.get("company")
            info["user"]["location"] = user.get("location")
            info["user"]["bio"] = user.get("bio")
            info["user"]["public_repos"] = user.get("public_repos")
            info["user"]["public_gists"] = user.get("public_gists")
            info["user"]["followers"] = user.get("followers")
            info["user"]["following"] = user.get("following")
            info["user"]["created_at"] = str(user.get("created_at"))
            info["user"]["updated_at"] = str(user.get("updated_at"))

            # Get scopes
            if "X-OAuth-Scopes" in response.headers:
                scopes_str = response.headers.get("X-OAuth-Scopes", "")
                info["scopes"] = [s.strip() for s in scopes_str.split(",") if s.strip()]

            # Get rate limits
            if "X-RateLimit-Limit" in response.headers:
                info["rate_limit"]["limit"] = int(response.headers.get("X-RateLimit-Limit", 0))
                info["rate_limit"]["remaining"] = int(response.headers.get("X-RateLimit-Remaining", 0))
                info["rate_limit"]["reset"] = int(response.headers.get("X-RateLimit-Reset", 0))

            # Get repos count
            info["quotas"]["public_repositories"] = user.get("public_repos", 0)
            info["quotas"]["total_repos"] = user.get("public_repos", 0) + user.get("owned_private_repos", 0)

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info


class GitLabValidator(BaseValidator):
    """GitLab Token Validator - comprehensive"""

    def __init__(self):
        super().__init__("GitLab", timeout=10, max_retries=3)
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
            info["user"]["web_url"] = user.get("web_url")
            info["user"]["created_at"] = str(user.get("created_at"))

            # Get projects
            response, _ = self._safe_request(
                "GET",
                f"{self.api_url}/projects?simple=true&per_page=1",
                headers=headers
            )

            if response and response.status_code == 200:
                try:
                    projects = response.json()
                    # Get total from headers if available
                    total = response.headers.get("X-Total", 0)
                    info["quotas"]["projects_count"] = int(total) if total else len(projects)
                except:
                    pass

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info


class MongoDBValidator(BaseValidator):
    """MongoDB Atlas API Validator"""

    def __init__(self):
        super().__init__("MongoDB", timeout=10, max_retries=3)
        self.api_url = "https://cloud.mongodb.com/api/atlas/v1.0"

    def validate(self, credentials: str) -> ValidationResult:
        """Validate MongoDB API credentials"""
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

        credentials = f"{public_key}:{private_key}"
        try:
            encoded = b64encode(credentials.encode()).decode('ascii')
        except:
            info["error"] = "Failed to encode credentials"
            return info

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
                info["organization"]["created"] = str(org.get("created"))
                info["quotas"]["organizations_count"] = len(orgs)

                # Get projects/clusters
                org_id = org.get("id")
                response, _ = self._safe_request(
                    "GET",
                    f"{self.api_url}/groups",
                    headers=headers
                )

                if response and response.status_code == 200:
                    try:
                        groups = response.json().get("results", [])
                        info["quotas"]["projects_count"] = len(groups)
                    except:
                        pass

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info


class SlackValidator(BaseValidator):
    """Slack Bot Token Validator"""

    def __init__(self):
        super().__init__("Slack", timeout=10, max_retries=3)
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
            "user": {},
            "quotas": {}
        }

        headers = {"Authorization": f"Bearer {token}"}

        # Test auth
        response, error = self._safe_request(
            "GET",
            f"{self.api_url}/auth.test",
            headers=headers
        )

        if error or not response:
            info["error"] = error
            return info

        if response.status_code != 200:
            info["error"] = "Invalid token"
            return info

        try:
            data = response.json()
            if data.get("ok"):
                info["is_valid"] = True

                info["workspace"]["name"] = data.get("team")
                info["workspace"]["team_id"] = data.get("team_id")
                info["workspace"]["url"] = data.get("url")

                info["user"]["user_id"] = data.get("user_id")
                info["user"]["username"] = data.get("user")

                token_type = "Bot" if token.startswith("xoxb-") else "User"
                info["user"]["token_type"] = token_type

                # Get team info
                response, _ = self._safe_request(
                    "GET",
                    f"{self.api_url}/team.info",
                    headers=headers
                )

                if response and response.status_code == 200:
                    try:
                        team = response.json()
                        if team.get("ok"):
                            team_data = team.get("team", {})
                            info["workspace"]["domain"] = team_data.get("domain")
                            info["workspace"]["icon"] = team_data.get("icon", {}).get("image_192")
                    except:
                        pass

                # Get users count
                response, _ = self._safe_request(
                    "GET",
                    f"{self.api_url}/users.list",
                    headers=headers
                )

                if response and response.status_code == 200:
                    try:
                        users = response.json()
                        if users.get("ok"):
                            info["quotas"]["users_count"] = len(users.get("members", []))
                    except:
                        pass

                # Get channels
                response, _ = self._safe_request(
                    "GET",
                    f"{self.api_url}/conversations.list",
                    headers=headers
                )

                if response and response.status_code == 200:
                    try:
                        channels = response.json()
                        if channels.get("ok"):
                            info["quotas"]["channels_count"] = len(channels.get("channels", []))
                    except:
                        pass

        except Exception as e:
            info["error"] = f"Parse error: {str(e)[:50]}"

        return info
