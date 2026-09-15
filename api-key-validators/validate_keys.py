#!/usr/bin/env python3
"""
Professional API Key Validation Suite - Master Script
Scans folders, validates all keys, generates comprehensive reports
Usage: python validate_keys.py /path/to/keys/folder
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

# Import all validators
from validators.sendgrid_validator import SendGridValidator
from validators.twilio_validator import TwilioValidator
from validators.stripe_validator import StripeValidator
from validators.brevo_validator import BrevoValidator
from validators.mailchimp_validator import MailchimpValidator
from validators.aws_validator import AWSValidator
from validators.other_validators import (
    GitHubValidator,
    GitLabValidator,
    MongoDBValidator,
    SlackValidator
)
from validators.additional_validators import (
    HuggingFaceValidator,
    AzureValidator,
    GCPValidator,
    DigitalOceanValidator,
    HerokuValidator,
    GiteaValidator,
    BitbucketValidator,
    NpmValidator,
    PyPiValidator
)


SERVICE_VALIDATORS = {
    "sendgrid": SendGridValidator,
    "twilio": TwilioValidator,
    "stripe": StripeValidator,
    "brevo": BrevoValidator,
    "mailchimp": MailchimpValidator,
    "aws": AWSValidator,
    "github": GitHubValidator,
    "gitlab": GitLabValidator,
    "mongodb": MongoDBValidator,
    "slack": SlackValidator,
    "huggingface": HuggingFaceValidator,
    "azure": AzureValidator,
    "gcp": GCPValidator,
    "digitalocean": DigitalOceanValidator,
    "heroku": HerokuValidator,
    "gitea": GiteaValidator,
    "bitbucket": BitbucketValidator,
    "npm": NpmValidator,
    "pypi": PyPiValidator,
}

COLORS = {
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
}


class KeyValidator:
    """Master validator that orchestrates all service validators"""

    def __init__(self, keys_folder: str, output_folder: str = None):
        self.keys_folder = Path(keys_folder)
        self.output_folder = Path(output_folder) if output_folder else Path("validation_results")
        self.output_folder.mkdir(exist_ok=True)
        self.results = defaultdict(list)
        self.summary = defaultdict(lambda: {"valid": 0, "invalid": 0, "error": 0})

    def scan_keys(self) -> Dict[str, List[str]]:
        """Scan folder for service key files"""
        keys = defaultdict(list)

        if not self.keys_folder.exists():
            print(f"{COLORS['RED']}Error: Folder not found: {self.keys_folder}{COLORS['RESET']}")
            sys.exit(1)

        # Scan for service-specific txt files
        for service in SERVICE_VALIDATORS.keys():
            file_path = self.keys_folder / f"{service}.txt"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            keys[service].append(line)

        return keys

    def validate_service_keys(self, service: str, keys: List[str]):
        """Validate all keys for a service"""
        if service not in SERVICE_VALIDATORS:
            print(f"{COLORS['YELLOW']}⚠ Unknown service: {service}{COLORS['RESET']}")
            return

        validator_class = SERVICE_VALIDATORS[service]
        validator = validator_class()

        print(f"\n{COLORS['CYAN']}{'='*60}{COLORS['RESET']}")
        print(f"{COLORS['BLUE']}🔍 Validating {service.upper()}{COLORS['RESET']}")
        print(f"{COLORS['CYAN']}{'='*60}{COLORS['RESET']}")
        print(f"Found {len(keys)} key(s) to validate\n")

        for i, key in enumerate(keys, 1):
            print(f"[{i}/{len(keys)}] Validating...", end="\r")
            result = validator.validate(key)

            self.results[service].append(result.to_dict())

            if result.is_valid:
                self.summary[service]["valid"] += 1
            elif result.error:
                self.summary[service]["invalid"] += 1
            else:
                self.summary[service]["error"] += 1

        print(" " * 40 + "\r", end="")  # Clear line

    def format_report_text(self) -> str:
        """Generate formatted text report"""
        report = []
        report.append(f"\n{'='*80}")
        report.append(f"API KEY VALIDATION REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"{'='*80}\n")

        for service, results in self.results.items():
            report.append(f"\n{'─'*80}")
            report.append(f"SERVICE: {service.upper()}")
            report.append(f"{'─'*80}")

            valid_keys = [r for r in results if r.get("is_valid")]
            invalid_keys = [r for r in results if not r.get("is_valid")]

            report.append(f"Total: {len(results)} | Valid: {len(valid_keys)} | Invalid: {len(invalid_keys)}\n")

            # Valid keys section
            if valid_keys:
                report.append(f"{COLORS['GREEN']}✓ VALID KEYS ({len(valid_keys)}):{COLORS['RESET']}")
                for result in valid_keys:
                    report.append(f"\n  Key: {result['key_sample']}")
                    report.append(f"  Status: {'LIVE' if result['is_live'] else 'TEST'}")

                    details = result.get("details", {})
                    for key, value in details.items():
                        if key not in ["is_valid", "is_live", "error"] and value:
                            if isinstance(value, dict):
                                report.append(f"  {key}:")
                                for k, v in value.items():
                                    if v and not isinstance(v, (dict, list)):
                                        report.append(f"    • {k}: {v}")
                            elif isinstance(value, list):
                                if value:
                                    report.append(f"  {key}: {', '.join(map(str, value[:5]))}")
                            else:
                                report.append(f"  {key}: {value}")

            # Invalid keys section
            if invalid_keys:
                report.append(f"\n{COLORS['RED']}✗ INVALID KEYS ({len(invalid_keys)}):{COLORS['RESET']}")
                for result in invalid_keys:
                    report.append(f"  Key: {result['key_sample']}")
                    if result.get("error"):
                        report.append(f"  Reason: {result['error']}")

        # Summary
        report.append(f"\n{'='*80}")
        report.append(f"SUMMARY")
        report.append(f"{'='*80}\n")

        total_valid = sum(s["valid"] for s in self.summary.values())
        total_invalid = sum(s["invalid"] for s in self.summary.values())
        total_error = sum(s["error"] for s in self.summary.values())

        for service, counts in self.summary.items():
            status = "✓" if counts["invalid"] == 0 else "✗"
            report.append(f"  {status} {service:15} Valid: {counts['valid']:2} | Invalid: {counts['invalid']:2}")

        report.append(f"\n{'─'*80}")
        report.append(f"  Total Valid:   {total_valid}")
        report.append(f"  Total Invalid: {total_invalid}")
        report.append(f"  Success Rate:  {(total_valid/(total_valid+total_invalid)*100):.1f}%" if (total_valid+total_invalid) > 0 else "  N/A")

        report.append(f"\n{'='*80}\n")

        return "\n".join(report)

    def save_reports(self):
        """Save JSON and text reports"""
        # JSON report
        json_path = self.output_folder / "validation_report.json"
        with open(json_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": dict(self.results),
                "summary": dict(self.summary)
            }, f, indent=2, default=str)

        # Text report
        text_path = self.output_folder / "validation_report.txt"
        report_text = self.format_report_text()
        with open(text_path, 'w') as f:
            f.write(report_text)

        print(f"\n{COLORS['GREEN']}✓ Reports saved:{COLORS['RESET']}")
        print(f"  JSON: {json_path}")
        print(f"  TXT:  {text_path}")

    def run(self):
        """Execute validation for all services"""
        print(f"\n{COLORS['BOLD']}🔐 API Key Validation Suite{COLORS['RESET']}")
        print(f"Scanning: {self.keys_folder}")

        keys = self.scan_keys()

        if not keys:
            print(f"{COLORS['YELLOW']}⚠ No key files found. Expected format: service.txt (e.g., sendgrid.txt, github.txt){COLORS['RESET']}")
            return

        for service in sorted(keys.keys()):
            self.validate_service_keys(service, keys[service])

        # Display and save reports
        report_text = self.format_report_text()
        print(report_text)
        self.save_reports()


def main():
    parser = argparse.ArgumentParser(
        description="Professional API Key Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_keys.py ./keys
  python validate_keys.py ./keys -o ./reports

Supported services:
  sendgrid, twilio, stripe, brevo, mailchimp, aws,
  github, gitlab, mongodb, slack,
  huggingface, azure, gcp, digitalocean, heroku,
  gitea, bitbucket, npm, pypi
        """
    )

    parser.add_argument(
        "folder",
        help="Folder containing key files (service.txt format)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output folder for reports (default: validation_results)",
        default=None
    )

    args = parser.parse_args()

    validator = KeyValidator(args.folder, args.output)
    validator.run()


if __name__ == "__main__":
    main()
