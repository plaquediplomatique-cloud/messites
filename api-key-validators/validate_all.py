#!/usr/bin/env python3
"""
API Key Validators - Master Script
Validates API keys for multiple services
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SERVICES = ["sendgrid", "twilio", "brevo", "mailchimp", "stripe", "aws"]


def validate_service(service_name):
    """Run validator for a specific service"""
    service_path = Path(__file__).parent / service_name
    validator_file = service_path / "validator.py"
    list_file = service_path / "list.txt"

    if not validator_file.exists():
        print(f"❌ {service_name}: validator.py not found")
        return False

    if not list_file.exists():
        print(f"⏭️  {service_name}: Skipping (list.txt not found)")
        return None

    print(f"\n{'='*50}")
    print(f"🔍 Validating {service_name.upper()}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            [sys.executable, str(validator_file)],
            capture_output=False,
            timeout=300,
            cwd=str(service_path)
        )

        if result.returncode == 0:
            print(f"✅ {service_name}: Validation completed")
            return True
        else:
            print(f"❌ {service_name}: Validation failed")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️  {service_name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {service_name}: Error - {str(e)}")
        return False


def main():
    print(f"""
╔══════════════════════════════════════════════════╗
║     API Key Validators - Master Controller       ║
║     Starting validation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}      ║
╚══════════════════════════════════════════════════╝
    """)

    results = {}
    for service in SERVICES:
        results[service] = validate_service(service)

    print(f"\n{'='*50}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*50}")

    completed = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    failed = sum(1 for v in results.values() if v is False)

    for service, result in results.items():
        if result is True:
            status = "✅ COMPLETED"
        elif result is None:
            status = "⏭️  SKIPPED"
        else:
            status = "❌ FAILED"
        print(f"  {service:15} {status}")

    print(f"\n  Total Completed: {completed}")
    print(f"  Total Skipped: {skipped}")
    print(f"  Total Failed: {failed}")

    print(f"\n📁 Results Location: {Path(__file__).parent}/{'{service}'}/results.txt")
    print(f"\n✨ Validation finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
