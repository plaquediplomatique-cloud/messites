#!/usr/bin/env python3
"""
Simple Credential Scanner - ULTRA ROBUST
No threading, no complications, just scan and validate
"""
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import argparse

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


class SimpleCredentialScanner:
    """Ultra simple, no threading"""

    def __init__(self):
        self.patterns = {
            "aws": [
                (r'AKIA[0-9A-Z]{16}:[A-Za-z0-9/+=]{40,}', 'aws_full'),
                (r'AIDA[0-9A-Z]{16}:[A-Za-z0-9/+=]{40,}', 'aws_full'),
            ],
            "sendgrid": [
                (r'SG\.[a-zA-Z0-9_-]{60,}', 'sendgrid'),
            ],
            "stripe": [
                (r'sk_(live|test)_[a-zA-Z0-9]{20,}', 'stripe'),
            ],
            "brevo": [
                (r'xkeysib_[a-zA-Z0-9]{50,}', 'brevo'),
            ],
            "mailchimp": [
                (r'[a-f0-9]{32}-[a-z]{2}\d{1,2}', 'mailchimp'),
            ],
            "twilio": [
                (r'AC[a-z0-9]{32}:[a-zA-Z0-9]{32,}', 'twilio'),
            ],
            "github": [
                (r'ghp_[a-zA-Z0-9_]{36,}', 'github'),
                (r'ghu_[a-zA-Z0-9_]{36,}', 'github'),
                (r'ghs_[a-zA-Z0-9_]{36,}', 'github'),
            ],
            "gitlab": [
                (r'glpat-[a-zA-Z0-9_-]{20,}', 'gitlab'),
            ],
            "slack": [
                (r'xoxb-[a-zA-Z0-9_-]{100,}', 'slack'),
                (r'xoxp-[a-zA-Z0-9_-]{100,}', 'slack'),
            ],
            "mongodb": [
                (r'mongodb\+srv://[a-zA-Z0-9:@./?=-]{50,}', 'mongodb'),
            ],
            "huggingface": [
                (r'hf_[a-zA-Z0-9_]{30,}', 'huggingface'),
            ],
            "digitalocean": [
                (r'dop_v1_[a-zA-Z0-9]{64,}', 'digitalocean'),
            ],
            "heroku": [
                (r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'heroku'),
            ],
            "npm": [
                (r'npm_[a-zA-Z0-9]{36,}', 'npm'),
            ],
            "pypi": [
                (r'pypi-[a-zA-Z0-9_]{30,}', 'pypi'),
            ],
            "gcp": [
                (r'ya29\.[a-zA-Z0-9_-]{100,}', 'gcp'),
            ],
        }

    def scan_files(self, directory: Path) -> Dict[str, Set[str]]:
        """Scan all files - SIMPLE VERSION"""
        all_found = defaultdict(set)

        files = list(directory.rglob('*'))
        file_count = sum(1 for f in files if f.is_file())

        print(f"\n🔍 Found {file_count} files\n")

        scanned = 0
        errors = 0

        for filepath in files:
            if not filepath.is_file():
                continue

            scanned += 1

            if scanned % 100 == 0:
                print(f"  Scanned: {scanned}/{file_count} | Errors: {errors} | Found: {sum(len(c) for c in all_found.values())}")

            try:
                # Read file with error handling
                content = ""
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except:
                    try:
                        with open(filepath, 'r', encoding='latin-1', errors='ignore') as f:
                            content = f.read()
                    except:
                        errors += 1
                        continue

                # Limit size
                if len(content) > 5_000_000:
                    content = content[:5_000_000]

                # Find patterns
                for service, patterns in self.patterns.items():
                    for pattern, ptype in patterns:
                        try:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if isinstance(match, tuple):
                                    for m in match:
                                        if m and len(str(m)) > 15:
                                            all_found[service].add(str(m))
                                else:
                                    if match and len(str(match)) > 15:
                                        all_found[service].add(str(match))
                        except:
                            pass

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                break
            except Exception as e:
                errors += 1

        print(f"\n✅ Scanning complete!")
        print(f"  Total scanned: {scanned}")
        print(f"  Total errors: {errors}")

        # Convert to lists
        result = {}
        for service, creds in all_found.items():
            if creds:
                result[service] = list(creds)

        return result

    def validate(self, creds_by_service: Dict[str, List[str]], output_folder: Path):
        """Validate found credentials"""
        output_folder.mkdir(exist_ok=True)

        results = defaultdict(list)
        total_valid = 0
        total_tested = 0

        print(f"\n{COLORS['BOLD']}📋 VALIDATING CREDENTIALS{COLORS['RESET']}\n")

        for service in sorted(creds_by_service.keys()):
            creds = creds_by_service[service]

            if service not in SERVICE_VALIDATORS:
                continue

            print(f"{COLORS['CYAN']}[{service.upper()}]{COLORS['RESET']} {len(creds)} credentials")

            validator = SERVICE_VALIDATORS[service]()
            valid = 0

            for cred in creds:
                total_tested += 1
                try:
                    result = validator.validate(cred)
                    if result.is_valid:
                        valid += 1
                        total_valid += 1
                        results[service].append(result.to_dict())
                        print(f"  ✅ {result.key_sample}")
                except:
                    pass

            if valid > 0:
                print(f"  → {COLORS['GREEN']}{valid} VALID{COLORS['RESET']}\n")
            else:
                print(f"  → 0 valid\n")

        # Save reports
        self._save_reports(output_folder, results, total_tested, total_valid)

        return results

    def _save_reports(self, folder: Path, results: Dict, total_tested: int, total_valid: int):
        """Save JSON and text reports"""

        # JSON
        json_path = folder / "VALID_CREDENTIALS.json"
        report = {
            "summary": {
                "total_tested": total_tested,
                "total_valid": total_valid,
                "success_rate": f"{(total_valid/total_tested*100):.2f}%" if total_tested > 0 else "0%"
            },
            "credentials": dict(results)
        }

        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✅ JSON: {json_path}")

        # TEXT
        txt_path = folder / "VALID_CREDENTIALS.txt"
        with open(txt_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("VALID CREDENTIALS FOUND\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total Tested: {total_tested}\n")
            f.write(f"Total Valid: {total_valid}\n")
            f.write(f"Success Rate: {(total_valid/total_tested*100):.2f}%\n\n")
            f.write("=" * 80 + "\n\n")

            for service in sorted(results.keys()):
                creds = results[service]
                if creds:
                    f.write(f"\n{service.upper()} - {len(creds)} credentials\n")
                    f.write("-" * 40 + "\n\n")

                    for cred in creds:
                        f.write(f"✓ {cred['key_sample']}\n")
                        f.write(f"  Live: {cred['is_live']}\n")
                        details = cred.get('details', {})
                        for k, v in list(details.items())[:3]:
                            if v and k not in ['is_valid', 'is_live', 'error']:
                                f.write(f"  {k}: {str(v)[:100]}\n")
                        f.write("\n")

        print(f"✅ TEXT: {txt_path}")


def main():
    parser = argparse.ArgumentParser(description="Simple Credential Scanner")
    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument("-o", "--output", default="./results", help="Output folder")

    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"{COLORS['RED']}Error: Folder not found{COLORS['RESET']}")
        sys.exit(1)

    print(f"\n{COLORS['BOLD']}🔐 SIMPLE CREDENTIAL SCANNER{COLORS['RESET']}")
    print(f"📁 Source: {folder}\n")

    scanner = SimpleCredentialScanner()

    # Scan
    print(f"{COLORS['CYAN']}Step 1: Scanning files...{COLORS['RESET']}")
    creds = scanner.scan_files(folder)

    total_creds = sum(len(c) for c in creds.values())
    print(f"\n{COLORS['BOLD']}Found {total_creds} potential credentials:{COLORS['RESET']}")
    for service in sorted(creds.keys()):
        print(f"  • {service}: {len(creds[service])}")

    # Validate
    print(f"\n{COLORS['CYAN']}Step 2: Validating credentials...{COLORS['RESET']}")
    results = scanner.validate(creds, Path(args.output))

    # Summary
    total_valid = sum(len(r) for r in results.values())
    print(f"\n{COLORS['BOLD']}🎉 DONE!{COLORS['RESET']}")
    print(f"  Total VALID credentials: {total_valid}")
    print(f"  Output: {args.output}/\n")


if __name__ == "__main__":
    main()
