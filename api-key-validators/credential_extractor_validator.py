#!/usr/bin/env python3
"""
Credential Extractor & Validator - Professional
Scans folders for ALL credential formats, extracts tokens, validates with all 19 validators
"""
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import argparse

sys.path.insert(0, str(Path(__file__).parent))

from validate_keys import SERVICE_VALIDATORS
from base_validator import ValidationResult

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


class CredentialExtractor:
    """Extract credentials from various file formats"""

    def __init__(self):
        self.extracted = defaultdict(list)
        self.patterns = {
            "aws": [
                r'AKIA[0-9A-Z]{16}:[A-Za-z0-9/+=]{40,}',
                r'AIDA[0-9A-Z]{16}:[A-Za-z0-9/+=]{40,}',
            ],
            "sendgrid": [
                r'SG\.[a-zA-Z0-9_-]{60,}',
            ],
            "stripe": [
                r'sk_(live|test)_[a-zA-Z0-9]{20,}',
            ],
            "brevo": [
                r'xkeysib_[a-zA-Z0-9]{50,}',
            ],
            "mailchimp": [
                r'[a-f0-9]{32}-[a-z]{2}\d{1,2}',
            ],
            "twilio": [
                r'AC[a-z0-9]{32}:[a-zA-Z0-9]{32,}',
            ],
            "github": [
                r'ghp_[a-zA-Z0-9_]{36,}',
                r'ghu_[a-zA-Z0-9_]{36,}',
                r'ghs_[a-zA-Z0-9_]{36,}',
            ],
            "gitlab": [
                r'glpat-[a-zA-Z0-9_-]{20,}',
                r'[a-zA-Z0-9_-]{20,}',  # Generic token
            ],
            "slack": [
                r'xoxb-[a-zA-Z0-9_-]{100,}',
                r'xoxp-[a-zA-Z0-9_-]{100,}',
            ],
            "mongodb": [
                r'[a-zA-Z0-9]+:[a-zA-Z0-9]{32,}@',
            ],
            "huggingface": [
                r'hf_[a-zA-Z0-9_]{30,}',
            ],
            "digitalocean": [
                r'dop_v1_[a-zA-Z0-9]{64,}',
            ],
            "heroku": [
                r'[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}',
            ],
            "npm": [
                r'npm_[a-zA-Z0-9]{36,}',
            ],
            "pypi": [
                r'pypi-[a-zA-Z0-9_]{30,}',
            ],
            "azure": [
                r'[a-zA-Z0-9\._-]{80,}',  # Long bearer token
            ],
        }

    def extract_from_file(self, filepath: Path) -> Dict[str, List[str]]:
        """Extract credentials from a file"""
        extracted = defaultdict(list)

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Try to parse format: URL/PATH/TOKEN
                    # Extract just the credential part
                    parts = line.split(':')

                    # Try pattern matching for each service
                    for service, patterns in self.patterns.items():
                        for pattern in patterns:
                            matches = re.findall(pattern, line)
                            for match in matches:
                                if match and len(match) > 15:
                                    extracted[service].append(match)

                    # Also check last part if it looks like a token
                    if len(parts) > 0:
                        last_part = parts[-1].strip()
                        if len(last_part) > 20 and last_part.isalnum() or '_' in last_part or '-' in last_part:
                            # Might be a token, try to identify service
                            if last_part.startswith('SG.'):
                                extracted['sendgrid'].append(last_part)
                            elif last_part.startswith('sk_'):
                                extracted['stripe'].append(last_part)
                            elif last_part.startswith('xkeysib_'):
                                extracted['brevo'].append(last_part)
                            elif last_part.startswith('ghp_'):
                                extracted['github'].append(last_part)
                            elif last_part.startswith('xoxb-') or last_part.startswith('xoxp-'):
                                extracted['slack'].append(last_part)
                            elif last_part.startswith('pypi-'):
                                extracted['pypi'].append(last_part)
                            elif last_part.startswith('hf_'):
                                extracted['huggingface'].append(last_part)

        except Exception as e:
            print(f"Error reading {filepath}: {e}")

        return extracted

    def scan_directory(self, directory: Path) -> Dict[str, List[str]]:
        """Scan directory for all text files and extract credentials"""
        all_extracted = defaultdict(list)

        for filepath in directory.rglob('*.txt'):
            extracted = self.extract_from_file(filepath)
            for service, credentials in extracted.items():
                all_extracted[service].extend(credentials)

        # Remove duplicates
        for service in all_extracted:
            all_extracted[service] = list(set(all_extracted[service]))

        return all_extracted


class CredentialValidator:
    """Validate extracted credentials"""

    def __init__(self):
        self.results = defaultdict(list)

    def validate_credentials(self, credentials_by_service: Dict[str, List[str]]) -> Dict:
        """Validate all extracted credentials"""
        total = 0
        valid_count = 0

        for service, credentials in credentials_by_service.items():
            if service not in SERVICE_VALIDATORS:
                print(f"{COLORS['YELLOW']}⚠ Unknown service: {service}{COLORS['RESET']}")
                continue

            print(f"\n{COLORS['CYAN']}Validating {service.upper()}{COLORS['RESET']}")
            print(f"Found {len(credentials)} credential(s)")

            validator_class = SERVICE_VALIDATORS[service]
            validator = validator_class()

            for cred in credentials:
                total += 1
                try:
                    result = validator.validate(cred)

                    if result.is_valid:
                        valid_count += 1
                        self.results[service].append(result.to_dict())
                        print(f"  {COLORS['GREEN']}✓{COLORS['RESET']} Valid credential found!")
                        print(f"    Key: {result.key_sample}")
                        if result.details:
                            for key, val in list(result.details.items())[:3]:
                                if val and key != 'error' and key != 'is_valid':
                                    print(f"    {key}: {str(val)[:100]}")
                    else:
                        print(f"  {COLORS['RED']}✗{COLORS['RESET']} Invalid: {result.error}")

                except Exception as e:
                    print(f"  {COLORS['RED']}✗{COLORS['RESET']} Error validating: {str(e)[:50]}")

        return {
            "total_credentials": total,
            "valid_credentials": valid_count,
            "results": dict(self.results)
        }

    def generate_report(self, output_folder: Path) -> None:
        """Generate JSON and text reports"""
        output_folder.mkdir(exist_ok=True)

        # JSON report
        json_path = output_folder / "extracted_credentials_report.json"
        with open(json_path, 'w') as f:
            json.dump({
                "timestamp": __import__('datetime').datetime.now().isoformat(),
                "results": dict(self.results)
            }, f, indent=2)

        # Text report
        text_path = output_folder / "extracted_credentials_report.txt"
        with open(text_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("EXTRACTED & VALIDATED CREDENTIALS REPORT\n")
            f.write("="*80 + "\n\n")

            total_valid = 0
            for service, results in self.results.items():
                if results:
                    f.write(f"\n{service.upper()}\n")
                    f.write("-"*40 + "\n")
                    for result in results:
                        f.write(f"✓ Key: {result['key_sample']}\n")
                        f.write(f"  Valid: {result['is_valid']}\n")
                        f.write(f"  Live: {result['is_live']}\n")
                        details = result.get('details', {})
                        for key, val in details.items():
                            if val and key not in ['is_valid', 'is_live', 'error']:
                                f.write(f"  {key}: {str(val)[:100]}\n")
                        f.write("\n")
                        total_valid += 1

            f.write("\n" + "="*80 + "\n")
            f.write(f"SUMMARY: {total_valid} valid credentials found\n")
            f.write("="*80 + "\n")

        print(f"\n{COLORS['GREEN']}✓ Reports saved:{COLORS['RESET']}")
        print(f"  JSON: {json_path}")
        print(f"  TXT:  {text_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract and validate credentials from files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python credential_extractor_validator.py ./my_folder
  python credential_extractor_validator.py ./my_folder -o ./reports
        """
    )

    parser.add_argument(
        "folder",
        help="Folder to scan for credential files"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output folder for reports (default: extracted_results)",
        default="extracted_results"
    )

    args = parser.parse_args()

    source_folder = Path(args.folder)
    output_folder = Path(args.output)

    if not source_folder.exists():
        print(f"{COLORS['RED']}Error: Folder not found: {source_folder}{COLORS['RESET']}")
        sys.exit(1)

    print(f"\n{COLORS['BOLD']}🔐 Credential Extractor & Validator{COLORS['RESET']}")
    print(f"Scanning: {source_folder}\n")

    # Extract
    print(f"{COLORS['CYAN']}Extracting credentials...{COLORS['RESET']}")
    extractor = CredentialExtractor()
    credentials = extractor.scan_directory(source_folder)

    print(f"\n{COLORS['CYAN']}Found {sum(len(c) for c in credentials.values())} potential credentials{COLORS['RESET']}")

    # Validate
    print(f"\n{COLORS['CYAN']}Validating credentials...{COLORS['RESET']}")
    validator = CredentialValidator()
    summary = validator.validate_credentials(credentials)

    # Report
    validator.generate_report(output_folder)

    print(f"\n{COLORS['BOLD']}Summary:{COLORS['RESET']}")
    print(f"  Total scanned: {summary['total_credentials']}")
    print(f"  Valid found: {summary['valid_credentials']}")
    if summary['total_credentials'] > 0:
        success_rate = (summary['valid_credentials'] / summary['total_credentials']) * 100
        print(f"  Success rate: {success_rate:.1f}%")


if __name__ == "__main__":
    main()
