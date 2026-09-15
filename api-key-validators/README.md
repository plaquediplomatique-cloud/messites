# 🔐 Professional API Key Validators Suite

**Production-Grade API Key Validation Framework**  
Comprehensive, secure, and professional validation for all your API keys and credentials.

## 🎯 Supported Services (19 Validators)

### Email & Marketing
| Service | Type | Format | Features |
|---------|------|--------|----------|
| **SendGrid** | Email | `SG.xxxxx` | Quota, reputation, scopes |
| **Brevo** | Email Marketing | `xkeysib_xxxxx` | Credits, lists, IP restrictions |
| **Mailchimp** | Email Marketing | `key-dc` | Lists, members, campaigns, datacenter |

### Cloud & Infrastructure
| Service | Type | Format | Features |
|---------|------|--------|----------|
| **AWS** | Cloud | `ACCESS_KEY:SECRET_KEY` | Regions, quotas, permissions, services |
| **Azure** | Cloud | Bearer Token | Subscriptions, access tokens |
| **GCP** | Cloud | Service Account JSON / Bearer Token | Project info, user details |
| **DigitalOcean** | Hosting | Bearer Token | Account, droplets, billing |
| **Heroku** | Hosting | Bearer Token | Apps, dynos, account info |

### Version Control & Collaboration
| Service | Type | Format | Features |
|---------|------|--------|----------|
| **GitHub** | Repository | `ghp_xxxxx` | User, scopes, rate limit |
| **GitLab** | Repository | `glpat_xxxxx` | User, projects, groups |
| **Gitea** | Repository | `URL:TOKEN` | User, repositories, instance |
| **Bitbucket** | Repository | `USERNAME:PASSWORD` | User, repositories, workspace |

### Communication & Services
| Service | Type | Format | Features |
|---------|------|--------|----------|
| **Twilio** | SMS/Voice | `SID:TOKEN` | SMS countries, balance, phone numbers |
| **Slack** | Messaging | `xoxb/xoxp_token` | Workspace info, users, channels |
| **MongoDB** | Database | `PUBLIC:PRIVATE` | Organizations, clusters |

### Package Registries & ML
| Service | Type | Format | Features |
|---------|------|--------|----------|
| **NPM** | Package Registry | Token | User, email |
| **PyPI** | Package Registry | `pypi-xxxxx` | Token verification |
| **HuggingFace** | ML Models | Bearer Token | User info, models count |

### Payments
| Service | Type | Format | Features |
|---------|------|--------|----------|
| **Stripe** | Payments | `sk_live/test_xxxxx` | EUR balance, charges, business info |

## 📋 Installation

### 1. Install Python 3.8+

```bash
python --version  # Should be 3.8 or higher
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

# For AWS validation specifically
pip install boto3
```

### 3. Verify Installation

```bash
python validate_keys.py --help
```

## 🚀 Quick Start

### Step 1: Create Key Files

Create a folder with service-specific `.txt` files:

```
keys/
├── sendgrid.txt
├── twilio.txt
├── stripe.txt
├── brevo.txt
├── mailchimp.txt
├── aws.txt
├── github.txt
├── gitlab.txt
├── mongodb.txt
├── slack.txt
├── huggingface.txt
├── azure.txt
├── gcp.txt
├── digitalocean.txt
├── heroku.txt
├── gitea.txt
├── bitbucket.txt
├── npm.txt
└── pypi.txt
```

### Step 2: Add Your Keys

**SendGrid** (`keys/sendgrid.txt`):
```
SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SG.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

**Twilio** (`keys/twilio.txt`):
```
AC[your_account_sid]:[your_auth_token]
AC[another_account_sid]:[another_auth_token]
```

**Stripe** (`keys/stripe.txt`):
```
sk_live_[your_stripe_key]
sk_test_[your_stripe_key]
```

**AWS** (`keys/aws.txt`):
```
AKIA[your_access_key]:[your_secret_key]
AKIA[another_access_key]:[another_secret_key]
```

**GitHub** (`keys/github.txt`):
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ghp_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

### Step 3: Run Validation

```bash
# Validate all keys
python validate_keys.py ./keys

# With custom output folder
python validate_keys.py ./keys -o ./my_reports
```

### Step 4: Check Reports

Reports are generated in `validation_results/`:

```bash
cat validation_results/validation_report.txt
cat validation_results/validation_report.json
```

## 📊 Example Output

```
════════════════════════════════════════════════════════════════════════════════
API KEY VALIDATION REPORT
Generated: 2024-01-15 14:30:45
════════════════════════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────────────────────────
SERVICE: SENDGRID
────────────────────────────────────────────────────────────────────────────────
Total: 2 | Valid: 2 | Invalid: 0

✓ VALID KEYS (2):

  Key: SG.1234...wxyz
  Status: LIVE
  account:
    • email: admin@mycompany.com
    • reputation: 8.5
    • plan: Pro

  Key: SG.abcd...7890
  Status: LIVE
  account:
    • email: noreply@mycompany.com
    • reputation: 9.2
    • plan: Pro


────────────────────────────────────────────────────────────────────────────────
SERVICE: STRIPE
────────────────────────────────────────────────────────────────────────────────
Total: 1 | Valid: 1 | Invalid: 0

✓ VALID KEYS (1):

  Key: sk_live_abc...xyz
  Status: LIVE
  environment: LIVE
  account:
    • id: acct_1234567890ABC
    • email: billing@mycompany.com
    • business_name: My Company Inc
    • country: FR
  balance:
    • available_eur: €2,500.50
    • pending_eur: €150.00
  quotas:
    • total_charges: 1247


════════════════════════════════════════════════════════════════════════════════
SUMMARY
════════════════════════════════════════════════════════════════════════════════

  ✓ sendgrid          Valid:  2 | Invalid:  0
  ✓ stripe            Valid:  1 | Invalid:  0
  ✗ twilio            Valid:  1 | Invalid:  1
  
────────────────────────────────────────────────────────────────────────────────
  Total Valid:   4
  Total Invalid: 1
  Success Rate:  80.0%

════════════════════════════════════════════════════════════════════════════════
```

## 🔑 Key Format Guide

### SendGrid
- **Format**: `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Length**: ~70+ characters
- **Prefix**: Must start with `SG.`

### Twilio
- **Format**: `ACCOUNT_SID:AUTH_TOKEN`
- **Account SID**: Starts with `AC`, 34 characters
- **Auth Token**: 32+ characters
- **Example**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy`

### Stripe
- **Format**: `sk_live_xxxxxx` or `sk_test_xxxxxx`
- **Type**: Secret key (starts with `sk_`)
- **Length**: 50+ characters
- **Live vs Test**: Indicated by prefix

### Brevo
- **Format**: `xkeysib_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Length**: 40+ characters
- **Prefix**: Must start with `xkeysib_`

### Mailchimp
- **Format**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-dc`
- **Datacenter**: The suffix (us1, us2, eu1, etc.)
- **Length**: 32 char key + 3-4 char datacenter

### AWS
- **Format**: `ACCESS_KEY_ID:SECRET_ACCESS_KEY`
- **Access Key ID**: Starts with `AKIA` or `AIDA`, 20 characters
- **Secret Key**: 40 characters
- **Example**: `AKIAIOSFODNN7EXAMPLE:wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

### GitHub
- **Format**: Personal access token or OAuth token
- **Length**: 30+ characters
- **Prefix**: `ghp_` for personal, `ghu_` for user-to-server, `ghs_` for server-to-server

### GitLab
- **Format**: Personal access token, project access token, or OAuth token
- **Length**: 20+ characters

### MongoDB
- **Format**: `PUBLIC_KEY:PRIVATE_KEY`
- **Keys**: Both 32+ characters

### Slack
- **Format**: `xoxb_xxxxxxxxxxxxx` or `xoxp_xxxxxxxxxxxxx`
- **xoxb**: Bot token
- **xoxp**: User token
- **Length**: 100+ characters

### HuggingFace
- **Format**: Bearer token
- **Length**: 20+ characters
- **Access**: API tokens from huggingface.co/settings/tokens

### Azure
- **Format**: Bearer token or subscription key
- **Length**: 30+ characters

### GCP
- **Format**: Service account JSON or Bearer token (ya29.*)
- **Service Account**: JSON file with project_id and email

### DigitalOcean
- **Format**: Bearer token (API token)
- **Length**: 30+ characters
- **Access**: https://cloud.digitalocean.com/account/api/tokens

### Heroku
- **Format**: Bearer token (API key)
- **Length**: 20+ characters
- **Access**: heroku.com/account/settings/applications

### Gitea
- **Format**: `URL:TOKEN`
- **Example**: `https://git.mycompany.com:token_value`
- **Token Length**: 20+ characters

### Bitbucket
- **Format**: `USERNAME:PASSWORD` or app password
- **Username**: Bitbucket username
- **Password**: App password or personal password

### NPM
- **Format**: Bearer token or `npm_xxxxx`
- **Length**: 20+ characters
- **Access**: https://www.npmjs.com/settings/~/tokens

### PyPI
- **Format**: `pypi-xxxxxxxxxxxxxxxxxxxxx`
- **Length**: 20+ characters
- **Prefix**: Must start with `pypi-`

## 📖 Detailed Information Collected

### Per Service

#### SendGrid
- ✓ Email address & account name
- ✓ API key name & scopes
- ✓ Account reputation
- ✓ Email sending statistics
- ✓ Bounce & click rates

#### Twilio
- ✓ Account SID & friendly name
- ✓ Account status (active/suspended)
- ✓ Phone numbers with countries
- ✓ SMS capabilities by country
- ✓ Account balance & currency
- ✓ Date created

#### Stripe
- ✓ Account ID & type
- ✓ Business information
- ✓ **Balance in EUR** (€ format, not cents)
- ✓ Balance in USD
- ✓ Charges enabled / Payouts enabled
- ✓ Total charges count
- ✓ Environment (LIVE/TEST)

#### Brevo
- ✓ Account email & company
- ✓ Plan type & status
- ✓ SMS & email credits
- ✓ Contact lists count & member count
- ✓ Email templates count
- ✓ IP whitelist (if configured)
- ✓ SMTP relay status

#### Mailchimp
- ✓ Username & email
- ✓ Datacenter location
- ✓ Contact lists with member counts
- ✓ Total campaigns
- ✓ Account role

#### AWS
- ✓ Account ID & ARN
- ✓ User name & type
- ✓ IAM policies attached
- ✓ Available regions
- ✓ EC2 instances running count
- ✓ S3 buckets count
- ✓ RDS databases count
- ✓ MFA enabled status

#### GitHub
- ✓ Username & real name
- ✓ Email & company
- ✓ Public repositories count
- ✓ Token scopes
- ✓ API rate limit & remaining

#### GitLab
- ✓ Username & email
- ✓ User state
- ✓ Projects count
- ✓ Instance URL

#### MongoDB
- ✓ Organization name & ID
- ✓ Organization count
- ✓ Cluster information

#### Slack
- ✓ Team name & ID
- ✓ User ID
- ✓ Token type (bot/user)

#### HuggingFace
- ✓ Username
- ✓ Full name
- ✓ Email address
- ✓ Avatar URL
- ✓ Models count

#### Azure
- ✓ Subscriptions count
- ✓ Subscription IDs
- ✓ Resource groups

#### GCP
- ✓ Project ID
- ✓ Service account email (if applicable)
- ✓ User email (if user token)
- ✓ Cloud resources info

#### DigitalOcean
- ✓ Account email
- ✓ Account status
- ✓ Droplet limit & count
- ✓ Floating IP limit
- ✓ Resource usage

#### Heroku
- ✓ Account email & ID
- ✓ Apps count
- ✓ Dyno usage
- ✓ Organization info (if applicable)

#### Gitea
- ✓ Username & full name
- ✓ Email address
- ✓ Instance URL
- ✓ Repositories count
- ✓ Organization access

#### Bitbucket
- ✓ Username & display name
- ✓ Email address
- ✓ Workspace info
- ✓ Repositories count
- ✓ Team access

#### NPM
- ✓ Username
- ✓ Email address
- ✓ Access level
- ✓ Package count

#### PyPI
- ✓ Token type verification
- ✓ Token validity
- ✓ Package access

## 🔒 Security Best Practices

### 1. **Never Commit Keys**
```bash
# Keys folder is ignored
echo "keys/" >> .gitignore
```

### 2. **Use Environment Variables**
```bash
export SENDGRID_KEY="SG.xxxxx"
export STRIPE_KEY="sk_live_xxxxx"
```

### 3. **Encrypt Results**
```bash
gpg --symmetric validation_results/validation_report.json
```

### 4. **Restrict File Permissions**
```bash
chmod 600 keys/*.txt
chmod 700 validation_results/
```

### 5. **Schedule Validation**
```bash
# Weekly cron job
0 9 * * 0 cd /path/to/validators && python validate_keys.py ./keys
```

### 6. **Rotate Keys Regularly**
- Update keys in rotation schedule
- Remove expired keys
- Use dedicated keys per environment

## ⚙️ Advanced Usage

### Custom Output Folder
```bash
python validate_keys.py ./keys -o ./custom_reports
```

### Validate Specific Service
```bash
# Only create sendgrid.txt and stripe.txt
python validate_keys.py ./keys
```

### Parse JSON Report
```python
import json

with open('validation_results/validation_report.json') as f:
    data = json.load(f)
    
for service, results in data['results'].items():
    for result in results:
        if result['is_valid']:
            print(f"{service}: {result['key_sample']}")
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'validators'"
```bash
# Make sure you're in the right directory
cd api-key-validators
python validate_keys.py ./keys
```

### "No key files found"
```bash
# Create the keys folder and files first
mkdir keys
echo "SG.xxxxx" > keys/sendgrid.txt
python validate_keys.py ./keys
```

### "Connection timeout"
- Check internet connection
- Service might be down
- Try again later

### AWS Validation Fails
```bash
pip install boto3
# Then retry
```

## 📈 Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["python", "validate_keys.py"]
```

### CI/CD Integration
```yaml
# GitHub Actions
- name: Validate API Keys
  run: |
    pip install -r api-key-validators/requirements.txt
    python api-key-validators/validate_keys.py ./keys -o ./reports
```

## 📝 License

Professional & Secure - For authorized use only

## Support

For issues or questions, refer to the comprehensive error messages provided by the validators.

---

**Last Updated**: 2024  
**Version**: 2.0 (Professional Grade)  
**Reliability**: Production Ready
