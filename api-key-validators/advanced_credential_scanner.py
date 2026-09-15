#!/usr/bin/env python3
"""
Advanced Credential Scanner - Ultimate Extractor
Scans ALL files (including raw), extracts every possible credential format
Uses aggressive regex patterns for maximum detection
"""
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))

from validate_keys import SERVICE_VALIDATORS

COLORS = {
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "MAGENTA": "\033[95m",
    "BOLD": "\033[1m",
    "RESET": "\033[0m",
}


class AdvancedCredentialScanner:
    """Advanced credential detection with comprehensive regex patterns"""

    def __init__(self):
        # Aggressive regex patterns for each service
        self.patterns = {
            "aws": [
                (r'(?:^|\s)([A-Z0-9]{20}):([A-Za-z0-9/+=]{40,})', 'colon_separated'),
                (r'AKIA[0-9A-Z]{16}', 'akia_prefix'),
                (r'AIDA[0-9A-Z]{16}', 'aida_prefix'),
            ],
            "sendgrid": [
                (r'SG\.[a-zA-Z0-9_-]{60,}', 'sendgrid_prefix'),
            ],
            "stripe": [
                (r'sk_(live|test)_[a-zA-Z0-9]{20,}', 'stripe_live_test'),
                (r'rk_(live|test)_[a-zA-Z0-9]{20,}', 'stripe_restricted'),
            ],
            "brevo": [
                (r'xkeysib_[a-zA-Z0-9]{50,}', 'brevo_prefix'),
            ],
            "mailchimp": [
                (r'[a-f0-9]{32}-[a-z]{2}\d{1,2}', 'mailchimp_format'),
            ],
            "twilio": [
                (r'AC[a-z0-9]{32}:[a-zA-Z0-9]{32,}', 'twilio_format'),
                (r'AC[a-z0-9]{32}', 'twilio_sid_only'),
            ],
            "github": [
                (r'ghp_[a-zA-Z0-9_]{36,}', 'github_personal'),
                (r'ghu_[a-zA-Z0-9_]{36,}', 'github_user_to_server'),
                (r'ghs_[a-zA-Z0-9_]{36,}', 'github_server'),
                (r'github[_\.]?token[_:=][\s]*([a-zA-Z0-9_-]{30,})', 'github_labeled'),
            ],
            "gitlab": [
                (r'glpat-[a-zA-Z0-9_-]{20,}', 'gitlab_personal'),
                (r'gitlab[_\.]?token[_:=][\s]*([a-zA-Z0-9_-]{20,})', 'gitlab_labeled'),
            ],
            "slack": [
                (r'xoxb-[a-zA-Z0-9_-]{100,}', 'slack_bot'),
                (r'xoxp-[a-zA-Z0-9_-]{100,}', 'slack_user'),
            ],
            "mongodb": [
                (r'mongodb\+srv://[a-zA-Z0-9:@./?=-]{50,}', 'mongodb_atlas_url'),
                (r'[a-zA-Z0-9]+:[a-zA-Z0-9]+@', 'mongodb_credentials'),
            ],
            "huggingface": [
                (r'hf_[a-zA-Z0-9_]{30,}', 'huggingface_token'),
            ],
            "digitalocean": [
                (r'dop_v1_[a-zA-Z0-9]{64,}', 'digitalocean_token'),
            ],
            "heroku": [
                (r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'heroku_uuid'),
            ],
            "npm": [
                (r'npm_[a-zA-Z0-9]{36,}', 'npm_token'),
                (r'//registry\.npmjs\.org/:_authToken=([a-zA-Z0-9]{36,})', 'npm_auth_token'),
            ],
            "pypi": [
                (r'pypi-[a-zA-Z0-9_]{30,}', 'pypi_token'),
            ],
            "azure": [
                (r'[a-zA-Z0-9\._-]{80,}', 'azure_bearer'),  # Very generic, use with care
            ],
            "gcp": [
                (r'"type":\s*"service_account"', 'gcp_service_account'),
                (r'ya29\.[a-zA-Z0-9_-]{100,}', 'gcp_bearer_token'),
            ],
            "api_key_generic": [
                (r'api[_-]?key[_:=][\s]*([a-zA-Z0-9\._-]{30,})', 'api_key_labeled'),
                (r'key[_:=][\s]*([a-zA-Z0-9\._-]{30,})', 'key_labeled'),
                (r'token[_:=][\s]*([a-zA-Z0-9\._-]{30,})', 'token_labeled'),
            ],
        }

    def scan_file(self, filepath: Path) -> Dict[str, Set[str]]:
        """Scan a single file for credentials"""
        found = defaultdict(set)

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Scan with all patterns
                for service, patterns in self.patterns.items():
                    for pattern, pattern_type in patterns:
                        try:
                            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                            for match in matches:
                                if isinstance(match, tuple):
                                    # Extract credential from groups
                                    for group in match:
                                        if group and len(str(group)) > 15:
                                            found[service].add(str(group))
                                else:
                                    if match and len(str(match)) > 15:
                                        found[service].add(str(match))
                        except Exception:
                            pass

        except Exception as e:
            print(f"{COLORS['YELLOW']}Warning: Could not read {filepath}: {e}{COLORS['RESET']}")

        return dict(found)

    def scan_directory(self, directory: Path, num_threads: int = 4) -> Dict[str, Set[str]]:
        """Scan directory with multiple threads"""
        all_found = defaultdict(set)

        print(f"{COLORS['CYAN']}Scanning files...{COLORS['RESET']}")

        files_to_scan = []
        for filepath in directory.rglob('*'):
            if filepath.is_file():
                # Include all files, not just .txt
                files_to_scan.append(filepath)

        print(f"Found {len(files_to_scan)} files to scan")

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {executor.submit(self.scan_file, f): f for f in files_to_scan}

            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 10 == 0:
                    print(f"  Scanned: {completed}/{len(files_to_scan)}", end='\r')

                found = future.result()
                for service, credentials in found.items():
                    all_found[service].update(credentials)

        print(f"  Scanned: {completed}/{len(files_to_scan)} ✓")

        # Convert sets to lists and filter
        final_result = {}
        for service, creds in all_found.items():
            # Remove duplicates and empty strings
            cleaned = [c for c in creds if c and len(str(c)) > 15]
            if cleaned:
                final_result[service] = cleaned

        return final_result

    def validate_and_report(self, credentials_by_service: Dict[str, List[str]], output_folder: Path):
        """Validate all credentials and generate comprehensive reports"""
        output_folder.mkdir(exist_ok=True)

        all_results = defaultdict(list)
        total_valid = 0
        total_tested = 0

        print(f"\n{COLORS['BOLD']}Validating {sum(len(c) for c in credentials_by_service.values())} credentials...{COLORS['RESET']}\n")

        for service, credentials in credentials_by_service.items():
            if service not in SERVICE_VALIDATORS:
                print(f"{COLORS['YELLOW']}⚠ Skipping unknown service: {service}{COLORS['RESET']}")
                continue

            print(f"{COLORS['MAGENTA']}[{service.upper()}]{COLORS['RESET']} Testing {len(credentials)} credential(s)")

            validator_class = SERVICE_VALIDATORS[service]
            validator = validator_class()

            valid_count = 0
            for cred in credentials:
                total_tested += 1
                try:
                    result = validator.validate(cred)

                    if result.is_valid:
                        valid_count += 1
                        total_valid += 1
                        all_results[service].append(result.to_dict())
                        print(f"  {COLORS['GREEN']}✓ VALID{COLORS['RESET']} {result.key_sample}")

                except Exception as e:
                    pass  # Silent fail

            if valid_count > 0:
                print(f"  → {COLORS['GREEN']}{valid_count} valid{COLORS['RESET']}\n")

        # Generate reports
        self._write_json_report(output_folder, all_results, total_tested, total_valid)
        self._write_text_report(output_folder, all_results, total_tested, total_valid)

        return all_results

    def _write_json_report(self, output_folder: Path, results: Dict, total_tested: int, total_valid: int):
        """Write comprehensive JSON report"""
        json_path = output_folder / "VALID_CREDENTIALS.json"

        report = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "summary": {
                "total_credentials_tested": total_tested,
                "total_valid_credentials": total_valid,
                "success_rate_percent": (total_valid / total_tested * 100) if total_tested > 0 else 0,
            },
            "valid_credentials_by_service": {}
        }

        for service, creds in results.items():
            report["valid_credentials_by_service"][service] = {
                "count": len(creds),
                "credentials": creds
            }

        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"{COLORS['GREEN']}✓ JSON report:{COLORS['RESET']} {json_path}")

    def _write_text_report(self, output_folder: Path, results: Dict, total_tested: int, total_valid: int):
        """Write comprehensive text report"""
        text_path = output_folder / "VALID_CREDENTIALS.txt"

        with open(text_path, 'w') as f:
            f.write("╔" + "═"*78 + "╗\n")
            f.write("║" + " "*20 + "VALID CREDENTIALS REPORT" + " "*35 + "║\n")
            f.write("╚" + "═"*78 + "╝\n\n")

            f.write(f"Total Credentials Tested: {total_tested}\n")
            f.write(f"Total Valid Found: {total_valid}\n")
            if total_tested > 0:
                f.write(f"Success Rate: {(total_valid / total_tested * 100):.2f}%\n\n")

            f.write("="*80 + "\n\n")

            for service in sorted(results.keys()):
                creds = results[service]
                if creds:
                    f.write(f"\n{service.upper()}\n")
                    f.write("-"*40 + "\n")
                    f.write(f"Found: {len(creds)} valid credential(s)\n\n")

                    for result in creds:
                        f.write(f"✓ Key Sample: {result['key_sample']}\n")
                        f.write(f"  Status: {'LIVE' if result['is_live'] else 'TEST'}\n")

                        details = result.get('details', {})
                        if details:
                            f.write("  Details:\n")
                            for key, val in details.items():
                                if val and key not in ['is_valid', 'is_live', 'error']:
                                    val_str = str(val)[:150]
                                    if len(val_str) > 100:
                                        val_str = val_str[:100] + "..."
                                    f.write(f"    • {key}: {val_str}\n")

                        f.write("\n")

            f.write("="*80 + "\n")
            f.write(f"Report generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"{COLORS['GREEN']}✓ Text report:{COLORS['RESET']} {text_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Advanced Credential Scanner - Maximum Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python advanced_credential_scanner.py ./my_folder
  python advanced_credential_scanner.py /path/to/raw -o ./reports
  python advanced_credential_scanner.py . -t 8  # Use 8 threads
        """
    )

    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument("-o", "--output", default="extracted_credentials", help="Output folder")
    parser.add_argument("-t", "--threads", type=int, default=4, help="Number of threads")

    args = parser.parse_args()

    source_folder = Path(args.folder)
    if not source_folder.exists():
        print(f"{COLORS['RED']}Error: Folder not found{COLORS['RESET']}")
        sys.exit(1)

    print(f"\n{COLORS['BOLD']}🔐 ADVANCED CREDENTIAL SCANNER{COLORS['RESET']}")
    print(f"Source: {source_folder}\n")

    scanner = AdvancedCredentialScanner()
    credentials = scanner.scan_directory(source_folder, num_threads=args.threads)

    print(f"\n{COLORS['CYAN']}Found {sum(len(c) for c in credentials.values())} potential credentials{COLORS['RESET']}")
    for service in sorted(credentials.keys()):
        print(f"  • {service:20} : {len(credentials[service]):3} found")

    results = scanner.validate_and_report(credentials, Path(args.output))

    print(f"\n{COLORS['BOLD']}Summary:{COLORS['RESET']}")
    total = sum(len(r) for r in results.values())
    print(f"  Total VALID credentials found: {total}\n")


if __name__ == "__main__":
    main()
