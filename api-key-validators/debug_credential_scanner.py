#!/usr/bin/env python3
"""
Debug Credential Scanner - FULL LOGGING
Shows EVERYTHING that happens - every error, every exception
"""
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import argparse
import traceback

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


class DebugCredentialScanner:
    """With FULL debug logging"""

    def __init__(self, verbose=True):
        self.verbose = verbose
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
        self.log_file = open("debug_scan.log", "w", encoding='utf-8')

    def log(self, msg, color=""):
        """Log to file and stdout"""
        print(f"{color}{msg}{COLORS['RESET']}")
        self.log_file.write(f"{msg}\n")
        self.log_file.flush()

    def scan_files(self, directory: Path) -> Dict[str, Set[str]]:
        """Scan all files with FULL logging"""
        all_found = defaultdict(set)

        files = list(directory.rglob('*'))
        file_list = [f for f in files if f.is_file()]
        file_count = len(file_list)

        self.log(f"\n{'='*80}")
        self.log(f"SCAN STARTED - Found {file_count} files")
        self.log(f"{'='*80}\n")

        scanned = 0
        errors = 0
        skipped = 0

        for filepath in file_list:
            try:
                scanned += 1

                # Show progress
                if scanned % 10 == 0:
                    msg = f"[{scanned}/{file_count}] Scanned | Errors: {errors} | Skipped: {skipped} | Found creds: {sum(len(c) for c in all_found.values())}"
                    self.log(msg, COLORS['CYAN'])

                # Read file
                try:
                    content = None
                    file_size = 0

                    try:
                        file_size = filepath.stat().st_size

                        # Try UTF-8
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            self.log(f"  ✓ [{scanned}] {filepath.name} ({file_size} bytes) - UTF-8 OK", COLORS['GREEN'])
                        except Exception as e:
                            self.log(f"  ⚠ [{scanned}] {filepath.name} - UTF-8 failed: {str(e)[:50]}", COLORS['YELLOW'])

                            # Try Latin-1
                            try:
                                with open(filepath, 'r', encoding='latin-1', errors='ignore') as f:
                                    content = f.read()
                                self.log(f"    ✓ Recovered with Latin-1", COLORS['GREEN'])
                            except Exception as e2:
                                self.log(f"    ✗ Latin-1 also failed: {str(e2)[:50]}", COLORS['RED'])
                                errors += 1
                                continue

                    except PermissionError:
                        self.log(f"  ✗ [{scanned}] {filepath.name} - Permission denied", COLORS['RED'])
                        errors += 1
                        continue
                    except IsADirectoryError:
                        self.log(f"  ⊘ [{scanned}] {filepath.name} - Is directory, skipping", COLORS['YELLOW'])
                        skipped += 1
                        continue
                    except Exception as e:
                        self.log(f"  ✗ [{scanned}] {filepath.name} - Read error: {type(e).__name__}: {str(e)[:50]}", COLORS['RED'])
                        errors += 1
                        continue

                    if content is None or len(content) == 0:
                        self.log(f"    ⊘ Empty file, skipping", COLORS['YELLOW'])
                        skipped += 1
                        continue

                    # Limit size
                    if len(content) > 5_000_000:
                        self.log(f"    ⚠ File too large ({len(content)} bytes), truncating to 5MB")
                        content = content[:5_000_000]

                    # Scan for patterns
                    file_creds_found = defaultdict(int)

                    for service, patterns in self.patterns.items():
                        for pattern, ptype in patterns:
                            try:
                                matches = re.findall(pattern, content, re.IGNORECASE)

                                if matches:
                                    self.log(f"    🔑 [{service}] Found {len(matches)} matches", COLORS['CYAN'])

                                for match in matches:
                                    try:
                                        if isinstance(match, tuple):
                                            for m in match:
                                                if m and len(str(m)) > 15:
                                                    all_found[service].add(str(m))
                                                    file_creds_found[service] += 1
                                        else:
                                            if match and len(str(match)) > 15:
                                                all_found[service].add(str(match))
                                                file_creds_found[service] += 1
                                    except Exception as e:
                                        self.log(f"      ✗ Error processing match: {type(e).__name__}: {str(e)[:30]}", COLORS['RED'])

                            except re.error as e:
                                self.log(f"    ✗ Regex error on {service}: {str(e)[:50]}", COLORS['RED'])
                            except Exception as e:
                                self.log(f"    ✗ Pattern error: {type(e).__name__}: {str(e)[:50]}", COLORS['RED'])

                except KeyboardInterrupt:
                    self.log("\n\n⚠️  Interrupted by user", COLORS['RED'])
                    break
                except Exception as e:
                    self.log(f"  ✗ Unexpected error: {type(e).__name__}: {str(e)}", COLORS['RED'])
                    self.log(f"    {traceback.format_exc()}", COLORS['RED'])
                    errors += 1

            except Exception as main_error:
                self.log(f"  ✗ CRITICAL ERROR: {type(main_error).__name__}: {str(main_error)}", COLORS['RED'])
                self.log(f"    {traceback.format_exc()}", COLORS['RED'])
                errors += 1

        self.log(f"\n{'='*80}")
        self.log(f"SCAN COMPLETE")
        self.log(f"{'='*80}")
        self.log(f"  Total scanned: {scanned}")
        self.log(f"  Total errors: {errors}")
        self.log(f"  Total skipped: {skipped}")
        self.log(f"  Total credentials found: {sum(len(c) for c in all_found.values())}\n")

        # Convert to lists
        result = {}
        for service, creds in all_found.items():
            if creds:
                result[service] = list(creds)

        return result

    def validate(self, creds_by_service: Dict[str, List[str]], output_folder: Path):
        """Validate with full logging"""
        output_folder.mkdir(exist_ok=True)

        self.log(f"\n{'='*80}")
        self.log(f"VALIDATION STARTED")
        self.log(f"{'='*80}\n")

        results = defaultdict(list)
        total_valid = 0
        total_tested = 0
        validation_errors = 0

        for service in sorted(creds_by_service.keys()):
            creds = creds_by_service[service]

            if service not in SERVICE_VALIDATORS:
                self.log(f"  ⚠ [{service.upper()}] Unknown service - skipping {len(creds)} credentials", COLORS['YELLOW'])
                continue

            self.log(f"\n[{service.upper()}] Validating {len(creds)} credentials", COLORS['MAGENTA'])

            try:
                validator = SERVICE_VALIDATORS[service]()
                self.log(f"  ✓ Validator instantiated", COLORS['GREEN'])
            except Exception as e:
                self.log(f"  ✗ Failed to instantiate validator: {type(e).__name__}: {str(e)}", COLORS['RED'])
                continue

            valid = 0

            for i, cred in enumerate(creds):
                total_tested += 1
                try:
                    result = validator.validate(cred)

                    if result.is_valid:
                        valid += 1
                        total_valid += 1
                        results[service].append(result.to_dict())
                        self.log(f"    ✅ [{i+1}] VALID - {result.key_sample}", COLORS['GREEN'])
                    else:
                        self.log(f"    ❌ [{i+1}] Invalid - {result.error}", COLORS['RED'])

                except Exception as e:
                    validation_errors += 1
                    self.log(f"    ✗ [{i+1}] Validation error: {type(e).__name__}: {str(e)[:50]}", COLORS['RED'])

            if valid > 0:
                self.log(f"  → {COLORS['GREEN']}{valid} VALID out of {len(creds)}{COLORS['RESET']}\n")
            else:
                self.log(f"  → 0 valid out of {len(creds)}\n")

        self.log(f"\n{'='*80}")
        self.log(f"VALIDATION COMPLETE")
        self.log(f"{'='*80}")
        self.log(f"  Total tested: {total_tested}")
        self.log(f"  Total valid: {total_valid}")
        self.log(f"  Validation errors: {validation_errors}\n")

        # Save reports
        self._save_reports(output_folder, results, total_tested, total_valid)

        return results

    def _save_reports(self, folder: Path, results: Dict, total_tested: int, total_valid: int):
        """Save JSON and text reports"""

        try:
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

            self.log(f"✅ JSON saved: {json_path}", COLORS['GREEN'])
        except Exception as e:
            self.log(f"✗ Failed to save JSON: {type(e).__name__}: {str(e)}", COLORS['RED'])

        try:
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

            self.log(f"✅ TEXT saved: {txt_path}", COLORS['GREEN'])
        except Exception as e:
            self.log(f"✗ Failed to save TEXT: {type(e).__name__}: {str(e)}", COLORS['RED'])


def main():
    parser = argparse.ArgumentParser(description="Debug Credential Scanner - FULL LOGGING")
    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument("-o", "--output", default="./results", help="Output folder")

    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"{COLORS['RED']}Error: Folder not found{COLORS['RESET']}")
        sys.exit(1)

    print(f"\n{COLORS['BOLD']}🔐 DEBUG CREDENTIAL SCANNER - FULL LOGGING{COLORS['RESET']}")
    print(f"📁 Source: {folder}")
    print(f"📝 Log file: debug_scan.log\n")

    scanner = DebugCredentialScanner()

    try:
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
        print(f"  Output: {args.output}/")
        print(f"  Debug log: debug_scan.log\n")

    except Exception as e:
        scanner.log(f"\n✗ CRITICAL ERROR: {type(e).__name__}: {str(e)}", COLORS['RED'])
        scanner.log(traceback.format_exc(), COLORS['RED'])
        print(f"{COLORS['RED']}CRITICAL ERROR - Check debug_scan.log{COLORS['RESET']}")

    finally:
        scanner.log_file.close()


if __name__ == "__main__":
    main()
