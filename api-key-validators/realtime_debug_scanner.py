#!/usr/bin/env python3
"""
Real-Time Debug Scanner - LOGS WRITTEN IMMEDIATELY
Creates folder and logs EVERYTHING as it happens
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


class RealtimeDebugScanner:
    """Real-time logging to file"""

    def __init__(self, output_folder: Path):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

        self.log_file = self.output_folder / "REALTIME_DEBUG.log"
        self.log_f = open(self.log_file, "w", encoding='utf-8')

        self.creds_log = self.output_folder / "FOUND_CREDENTIALS.txt"
        self.creds_f = open(self.creds_log, "w", encoding='utf-8')

        self.log(f"🔐 REALTIME DEBUG SCANNER STARTED\n")

        self.patterns = {
            "aws": [
                (r'AKIA[0-9A-Z]{16}:[A-Za-z0-9/+=]{40,}', 'aws_full'),
                (r'AIDA[0-9A-Z]{16}:[A-Za-z0-9/+=]{40,}', 'aws_full'),
            ],
            "sendgrid": [(r'SG\.[a-zA-Z0-9_-]{60,}', 'sendgrid')],
            "stripe": [(r'sk_(live|test)_[a-zA-Z0-9]{20,}', 'stripe')],
            "brevo": [(r'xkeysib_[a-zA-Z0-9]{50,}', 'brevo')],
            "mailchimp": [(r'[a-f0-9]{32}-[a-z]{2}\d{1,2}', 'mailchimp')],
            "twilio": [(r'AC[a-z0-9]{32}:[a-zA-Z0-9]{32,}', 'twilio')],
            "github": [
                (r'ghp_[a-zA-Z0-9_]{36,}', 'github'),
                (r'ghu_[a-zA-Z0-9_]{36,}', 'github'),
                (r'ghs_[a-zA-Z0-9_]{36,}', 'github'),
            ],
            "gitlab": [(r'glpat-[a-zA-Z0-9_-]{20,}', 'gitlab')],
            "slack": [
                (r'xoxb-[a-zA-Z0-9_-]{100,}', 'slack'),
                (r'xoxp-[a-zA-Z0-9_-]{100,}', 'slack'),
            ],
            "mongodb": [(r'mongodb\+srv://[a-zA-Z0-9:@./?=-]{50,}', 'mongodb')],
            "huggingface": [(r'hf_[a-zA-Z0-9_]{30,}', 'huggingface')],
            "digitalocean": [(r'dop_v1_[a-zA-Z0-9]{64,}', 'digitalocean')],
            "heroku": [(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'heroku')],
            "npm": [(r'npm_[a-zA-Z0-9]{36,}', 'npm')],
            "pypi": [(r'pypi-[a-zA-Z0-9_]{30,}', 'pypi')],
            "gcp": [(r'ya29\.[a-zA-Z0-9_-]{100,}', 'gcp')],
        }

    def log(self, msg, color=""):
        """Log to file AND stdout IMMEDIATELY"""
        print(f"{color}{msg}{COLORS['RESET']}", flush=True)
        self.log_f.write(f"{msg}\n")
        self.log_f.flush()

    def log_cred(self, msg):
        """Log found credential"""
        print(msg, flush=True)
        self.creds_f.write(f"{msg}\n")
        self.creds_f.flush()

    def scan_files(self, directory: Path) -> Dict[str, Set[str]]:
        """Scan files with REAL-TIME logging"""
        all_found = defaultdict(set)

        files = list(directory.rglob('*'))
        file_list = [f for f in files if f.is_file()]
        file_count = len(file_list)

        self.log(f"\n{'='*80}")
        self.log(f"SCAN PARAMETERS")
        self.log(f"{'='*80}")
        self.log(f"  Source folder: {directory}")
        self.log(f"  Output folder: {self.output_folder}")
        self.log(f"  Total files to scan: {file_count}")
        self.log(f"  Patterns to match: {len(self.patterns)} services")
        self.log(f"\n{'='*80}")
        self.log(f"SCANNING STARTED")
        self.log(f"{'='*80}\n")

        scanned = 0
        errors = 0
        skipped = 0

        for i, filepath in enumerate(file_list, 1):
            try:
                scanned += 1

                # REAL-TIME progress (every 5 files)
                if scanned % 5 == 0:
                    msg = f"[PROGRESS {scanned}/{file_count}] Errors: {errors} | Skipped: {skipped} | Creds found: {sum(len(c) for c in all_found.values())}"
                    self.log(msg, COLORS['CYAN'])

                try:
                    file_size = filepath.stat().st_size

                    # Try UTF-8
                    content = None
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        self.log(f"[{scanned}] ✓ {filepath.name} ({file_size} bytes)", COLORS['GREEN'])
                    except Exception as e:
                        try:
                            with open(filepath, 'r', encoding='latin-1', errors='ignore') as f:
                                content = f.read()
                            self.log(f"[{scanned}] ⚠ {filepath.name} (recovered with Latin-1)", COLORS['YELLOW'])
                        except Exception as e2:
                            self.log(f"[{scanned}] ✗ {filepath.name} - FAILED: {type(e).__name__}", COLORS['RED'])
                            errors += 1
                            continue

                    if content is None or len(content) == 0:
                        self.log(f"      → Empty file, skipping")
                        skipped += 1
                        continue

                    # Limit size
                    original_size = len(content)
                    if len(content) > 5_000_000:
                        self.log(f"      ⚠ Too large ({original_size} bytes), truncating to 5MB")
                        content = content[:5_000_000]

                    # Scan patterns
                    for service, patterns in self.patterns.items():
                        for pattern, ptype in patterns:
                            try:
                                matches = re.findall(pattern, content, re.IGNORECASE)

                                if matches:
                                    self.log(f"      🔑 [{service}] Found {len(matches)}", COLORS['CYAN'])

                                for match in matches:
                                    try:
                                        if isinstance(match, tuple):
                                            for m in match:
                                                if m and len(str(m)) > 15:
                                                    all_found[service].add(str(m))
                                                    self.log_cred(f"  ✅ {service}: {str(m)[:80]}")
                                        else:
                                            if match and len(str(match)) > 15:
                                                all_found[service].add(str(match))
                                                self.log_cred(f"  ✅ {service}: {str(match)[:80]}")
                                    except Exception:
                                        pass
                            except re.error as e:
                                self.log(f"      ✗ Regex error: {str(e)[:50]}", COLORS['RED'])
                            except Exception as e:
                                self.log(f"      ✗ Pattern error: {type(e).__name__}: {str(e)[:50]}", COLORS['RED'])

                except PermissionError:
                    self.log(f"[{scanned}] ✗ {filepath.name} - Permission denied", COLORS['RED'])
                    errors += 1
                except IsADirectoryError:
                    self.log(f"[{scanned}] ⊘ {filepath.name} - Is directory", COLORS['YELLOW'])
                    skipped += 1
                except Exception as e:
                    self.log(f"[{scanned}] ✗ {filepath.name} - {type(e).__name__}: {str(e)[:50]}", COLORS['RED'])
                    errors += 1

            except KeyboardInterrupt:
                self.log("\n\n⚠️  INTERRUPTED BY USER", COLORS['RED'])
                break
            except Exception as e:
                self.log(f"[{scanned}] ✗ CRITICAL: {type(e).__name__}: {str(e)}", COLORS['RED'])
                self.log(f"  {traceback.format_exc()}", COLORS['RED'])
                errors += 1

        self.log(f"\n{'='*80}")
        self.log(f"SCAN COMPLETE")
        self.log(f"{'='*80}")
        self.log(f"  Total scanned: {scanned}/{file_count}")
        self.log(f"  Total errors: {errors}")
        self.log(f"  Total skipped: {skipped}")
        self.log(f"  Total credentials found: {sum(len(c) for c in all_found.values())}\n")

        result = {}
        for service, creds in all_found.items():
            if creds:
                result[service] = list(creds)

        return result

    def validate(self, creds_by_service: Dict[str, List[str]]):
        """Validate with REAL-TIME logging"""
        self.log(f"\n{'='*80}")
        self.log(f"VALIDATION STARTED")
        self.log(f"{'='*80}\n")

        results = defaultdict(list)
        total_valid = 0
        total_tested = 0

        for service in sorted(creds_by_service.keys()):
            creds = creds_by_service[service]

            if service not in SERVICE_VALIDATORS:
                self.log(f"[{service.upper()}] ⚠ Unknown service - skipping {len(creds)}", COLORS['YELLOW'])
                continue

            self.log(f"\n[{service.upper()}] Validating {len(creds)} credentials", COLORS['MAGENTA'])

            try:
                validator = SERVICE_VALIDATORS[service]()
            except Exception as e:
                self.log(f"  ✗ Failed to create validator: {type(e).__name__}", COLORS['RED'])
                continue

            valid = 0

            for i, cred in enumerate(creds, 1):
                total_tested += 1
                try:
                    result = validator.validate(cred)

                    if result.is_valid:
                        valid += 1
                        total_valid += 1
                        results[service].append(result.to_dict())
                        self.log(f"    ✅ [{i}] VALID - {result.key_sample}", COLORS['GREEN'])
                    else:
                        self.log(f"    ❌ [{i}] Invalid - {result.error}", COLORS['RED'])

                except Exception as e:
                    self.log(f"    ✗ [{i}] Error: {type(e).__name__}: {str(e)[:40]}", COLORS['RED'])

            self.log(f"  Result: {valid} VALID / {len(creds)} tested\n")

        self.log(f"\n{'='*80}")
        self.log(f"VALIDATION COMPLETE")
        self.log(f"{'='*80}")
        self.log(f"  Total tested: {total_tested}")
        self.log(f"  Total VALID: {total_valid}")
        self.log(f"  Success rate: {(total_valid/total_tested*100):.2f}%\n")

        # Save JSON
        self._save_json(results, total_tested, total_valid)

        return results

    def _save_json(self, results: Dict, total_tested: int, total_valid: int):
        """Save JSON report"""
        try:
            json_path = self.output_folder / "VALID_CREDENTIALS.json"
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
            self.log(f"✗ Failed to save JSON: {type(e).__name__}", COLORS['RED'])


def main():
    parser = argparse.ArgumentParser(description="Real-Time Debug Scanner")
    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument("-o", "--output", default="./results_realtime", help="Output folder")

    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"{COLORS['RED']}Error: Folder not found{COLORS['RESET']}")
        sys.exit(1)

    print(f"\n{COLORS['BOLD']}🔐 REAL-TIME DEBUG SCANNER{COLORS['RESET']}")
    print(f"📁 Source: {folder}")
    print(f"📁 Output: {args.output}")
    print(f"📝 Real-time logs will appear below and be saved\n")

    scanner = RealtimeDebugScanner(Path(args.output))

    try:
        print(f"{COLORS['CYAN']}Step 1: Scanning...{COLORS['RESET']}\n")
        creds = scanner.scan_files(folder)

        total = sum(len(c) for c in creds.values())
        print(f"\n{COLORS['BOLD']}Found {total} credentials:{COLORS['RESET']}")
        for service in sorted(creds.keys()):
            print(f"  • {service}: {len(creds[service])}")

        print(f"\n{COLORS['CYAN']}Step 2: Validating...{COLORS['RESET']}\n")
        results = scanner.validate(creds)

        total_valid = sum(len(r) for r in results.values())
        print(f"\n{COLORS['BOLD']}🎉 COMPLETE!{COLORS['RESET']}")
        print(f"  Total VALID: {total_valid}")
        print(f"  Files in: {args.output}/\n")

    except Exception as e:
        scanner.log(f"\n✗ CRITICAL: {type(e).__name__}: {str(e)}", COLORS['RED'])
        scanner.log(traceback.format_exc(), COLORS['RED'])

    finally:
        scanner.log_f.close()
        scanner.creds_f.close()


if __name__ == "__main__":
    main()
