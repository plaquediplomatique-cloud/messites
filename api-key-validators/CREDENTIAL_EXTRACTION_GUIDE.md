# 🔐 Credential Extraction & Validation Guide

## Overview

Two powerful tools for extracting and validating credentials from files:

1. **credential_extractor_validator.py** - Basic extraction with format parsing
2. **advanced_credential_scanner.py** - Advanced scanning with aggressive regex patterns

## Tool 1: Credential Extractor & Validator

### Usage

```bash
# Basic usage
python credential_extractor_validator.py ./my_folder

# Custom output folder
python credential_extractor_validator.py ./my_folder -o ./my_reports

# Scan raw directory
python credential_extractor_validator.py ./raw_files
```

### What it does

1. Scans all `.txt` files in the folder
2. Extracts credentials using pattern matching
3. Parses URL/PATH/TOKEN format (extracts just the TOKEN)
4. Validates each credential with all 19 validators
5. Generates JSON and text reports with ONLY valid credentials

### Output

```
extracted_results/
├── extracted_credentials_report.json  # Machine-readable results
└── extracted_credentials_report.txt   # Human-readable report
```

### JSON Report Structure

```json
{
  "timestamp": "2026-09-15T16:57:53",
  "results": {
    "aws": [
      {
        "status": "✓ VALID",
        "service": "AWS",
        "key_sample": "AKIA...XYZ",
        "is_valid": true,
        "is_live": true,
        "details": {
          "account_id": "123456789",
          "permissions": ["s3:*", "ec2:*"],
          "regions": ["us-east-1", "eu-west-1"]
        }
      }
    ],
    "sendgrid": [...],
    "stripe": [...]
  }
}
```

---

## Tool 2: Advanced Credential Scanner (RECOMMENDED)

### Usage

```bash
# Scan entire directory tree (recommended)
python advanced_credential_scanner.py ./my_folder

# Scan raw files with custom threads
python advanced_credential_scanner.py ./raw -t 8 -o ./found_creds

# Single thread for slow systems
python advanced_credential_scanner.py ./files -t 1

# Scan everything in current directory
python advanced_credential_scanner.py .
```

### What it does

1. Scans **ALL** files (not just .txt)
2. Uses aggressive regex patterns for maximum detection
3. Multi-threaded scanning for speed
4. Detects formats:
   - AWS: `AKIA*`, `AIDA*`, `KEY:SECRET`
   - SendGrid: `SG.*`
   - Stripe: `sk_live_*`, `sk_test_*`
   - Twilio: `AC*:TOKEN`
   - GitHub: `ghp_*`, `ghu_*`, `ghs_*`
   - Slack: `xoxb-*`, `xoxp-*`
   - Brevo: `xkeysib_*`
   - Mailchimp: `*-us1/us2/eu1`
   - MongoDB: `mongodb+srv://`, `USER:PASS@`
   - HuggingFace: `hf_*`
   - Digital Ocean: `dop_v1_*`
   - Heroku: UUID format
   - NPM: `npm_*`, `_authToken`
   - PyPI: `pypi-*`
   - GCP: `ya29.*`, service account JSON
   - Azure: Long bearer tokens
   - Generic API keys with labeled patterns

5. **Validates EVERY credential found** with proper validators
6. Generates comprehensive reports with only **VALID** credentials

### Output

```
extracted_credentials/
├── VALID_CREDENTIALS.json  # All valid credentials with details
└── VALID_CREDENTIALS.txt   # Formatted report
```

### Reports

#### JSON Format (VALID_CREDENTIALS.json)
```json
{
  "timestamp": "2026-09-15T17:00:00",
  "summary": {
    "total_credentials_tested": 1250,
    "total_valid_credentials": 47,
    "success_rate_percent": 3.76
  },
  "valid_credentials_by_service": {
    "aws": {
      "count": 5,
      "credentials": [...]
    },
    "sendgrid": {
      "count": 3,
      "credentials": [...]
    }
  }
}
```

#### Text Format (VALID_CREDENTIALS.txt)
- Human-readable with clear sections per service
- Shows account details, quotas, and capabilities
- Organized for easy review

---

## Advanced Credential Formats Detected

### AWS
```
AKIA[YOUR_20_CHAR_KEY]:wJalrXUtnFEMI[YOUR_40_CHAR_SECRET]
AIDA[YOUR_20_CHAR_KEY]
```

### SendGrid
```
SG.[YOUR_70_CHAR_TOKEN]
```

### Stripe
```
sk_live_[YOUR_STRIPE_LIVE_KEY]
sk_test_[YOUR_STRIPE_TEST_KEY]
```

### Twilio
```
AC[YOUR_32_CHAR_SID]:[YOUR_32_CHAR_TOKEN]
```

### GitHub
```
ghp_[YOUR_36_CHAR_TOKEN]
ghu_[YOUR_36_CHAR_TOKEN]
ghs_[YOUR_36_CHAR_TOKEN]
github_token=[YOUR_TOKEN]
```

### Slack
```
xoxb-[YOUR_TOKEN_PARTS]
xoxp-[YOUR_TOKEN_PARTS]
```

### Brevo
```
xkeysib_[YOUR_KEY]
```

### Mailchimp
```
[YOUR_32_CHAR_KEY]-us1
[YOUR_32_CHAR_KEY]-eu1
```

### MongoDB
```
mongodb+srv://[USERNAME]:[PASSWORD]@cluster0.[YOUR_CLUSTER].mongodb.net/
```

### HuggingFace
```
hf_[YOUR_TOKEN]
```

### GCP
```
ya29.[YOUR_BEARER_TOKEN]
{
  "type": "service_account",
  "project_id": "[YOUR_PROJECT]",
  ...
}
```

---

## Usage Examples

### Scenario 1: Scan the "raw" directory

```bash
python advanced_credential_scanner.py ./raw -o ./found_credentials
```

This will:
- Scan every file in `./raw`
- Extract ALL credentials found
- Validate each one
- Output `./found_credentials/VALID_CREDENTIALS.json` with results

### Scenario 2: Find credentials in a specific service folder

```bash
python advanced_credential_scanner.py ./aws_results -o ./aws_valid
```

### Scenario 3: Scan multiple locations and merge results

```bash
python advanced_credential_scanner.py ./raw -o ./final_results
python advanced_credential_scanner.py ./results -o ./final_results  # Appends
```

### Scenario 4: Quick scan with many threads

```bash
# Use 16 threads for maximum speed on large datasets
python advanced_credential_scanner.py ./huge_folder -t 16 -o ./fast_results
```

---

## Performance Tips

1. **Use Threading**: `-t 8` or higher for large directories
2. **Exclude Large Files**: Scanner auto-handles them, but consider pre-filtering
3. **Raw Scanning**: Best performance on `./raw` folder (many small files)
4. **Parallel Runs**: Can run multiple scanners on different folders simultaneously

---

## Important Notes

### Security

✅ All credentials are **truncated** in output (e.g., `AKIA...XYZ`)
✅ Full credentials are stored **encrypted in memory only**
✅ Validation uses proper API calls for accuracy
✅ Reports are **JSON for easy programmatic access**

### Accuracy

- ✅ AWS: Validates with boto3 (most accurate)
- ✅ Stripe: Validates with Stripe API
- ✅ SendGrid: Real API validation
- ✅ All major services: Verified through actual API calls
- ⚠️ Format-only checks for smaller services

### File Support

- ✅ `.txt` files
- ✅ `.log` files  
- ✅ `.json` files
- ✅ `.env` files
- ✅ All plain text formats
- ✅ Binary files (skipped gracefully)

---

## Advanced Features

### Credential Parsing

The scanner automatically extracts credentials from:

```
URL:PATH:TOKEN          → Extracts TOKEN
URL/api/key/TOKEN       → Extracts TOKEN
LABEL=TOKEN             → Extracts TOKEN
TOKEN standalone        → Uses directly
```

### Service Auto-Detection

Uses prefix patterns for accurate detection:

- `SG.` → SendGrid
- `sk_` → Stripe
- `ghp_` → GitHub
- `xoxb-` → Slack Bot
- `xoxp-` → Slack User
- `AKIA` → AWS
- etc.

### Multi-Format Support

Handles various file structures:

```
# YAML format
aws_key: AKIA123...
aws_secret: wJalr...

# JSON format
{"credentials": {"aws": "AKIA123..."}}

# Raw text
AKIA123456789:wJalrXUtnFEMI

# Labeled
API Key: SG.xxxxx
Token: ghp_xxxxx
```

---

## Troubleshooting

### "No credentials found"

- Check folder path exists
- Ensure files are readable
- Try with `-t 1` to see error messages
- Check file encoding (UTF-8 recommended)

### "Permission denied"

```bash
chmod -R 755 ./your_folder
python advanced_credential_scanner.py ./your_folder
```

### "Memory issues with large directories"

```bash
# Process in smaller batches
python advanced_credential_scanner.py ./raw/part1 -o ./results1
python advanced_credential_scanner.py ./raw/part2 -o ./results2
```

---

## Integration with Validation Suite

The scanners use the same 19 validators as the main suite:

- ✓ SendGrid, Twilio, Stripe, Brevo, Mailchimp
- ✓ AWS, Azure, GCP, DigitalOcean, Heroku
- ✓ GitHub, GitLab, Gitea, Bitbucket
- ✓ Slack, MongoDB, HuggingFace
- ✓ NPM, PyPI

Each validated credential includes:
- Account information
- Quotas and limits
- Permissions and capabilities
- Security information (MFA, key age, etc.)
- Service-specific details

---

## Example Workflow

```bash
# 1. Scan all raw files
python advanced_credential_scanner.py ./raw -t 8 -o ./findings

# 2. Check results
cat ./findings/VALID_CREDENTIALS.txt

# 3. Review JSON for detailed info
python -m json.tool ./findings/VALID_CREDENTIALS.json | less

# 4. Extract just AWS credentials
grep -A5 '"aws"' ./findings/VALID_CREDENTIALS.json

# 5. Generate report with filtering
python -c "
import json
with open('./findings/VALID_CREDENTIALS.json') as f:
    data = json.load(f)
    for service, info in data['valid_credentials_by_service'].items():
        if info['count'] > 0:
            print(f'{service}: {info[\"count\"]} valid credentials')
"
```

---

## Next Steps

For comprehensive credential management:

1. **Run Scanner**: Extract all credentials
2. **Review Results**: Check VALID_CREDENTIALS.json
3. **Categorize**: Group by service and environment
4. **Rotate**: Update compromised credentials
5. **Monitor**: Set up periodic scanning
6. **Archive**: Keep audit trail of findings

---

**Version**: 1.0  
**Last Updated**: 2026-09-15  
**Compatibility**: Python 3.8+
