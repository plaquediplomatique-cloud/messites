# 📋 Examples - API Key Validators

Complete examples for each service validation.

## SendGrid Example

### Step 1: Get your API Key

Go to [SendGrid Settings](https://app.sendgrid.com/settings/api_keys) and copy a key.

### Step 2: Add to list.txt

```bash
cat > sendgrid/list.txt << EOF
SG.1234567890abcdefghijklmnopqrstuvwxyz
SG.abcdefghijklmnopqrstuvwxyz1234567890
EOF
```

### Step 3: Validate

```bash
python sendgrid/validator.py
```

### Step 4: Check Results

```bash
cat sendgrid/results.txt
```

**Output Example:**
```
=== SendGrid API Key Validation Results ===
Timestamp: 2024-01-15T14:30:45.123456
Total Keys Checked: 2

✓ VALID - SG.1234...wxyz
  Account: admin@mycompany.com
  Reputation: 8.5

✓ VALID - SG.abcd...7890
  Account: support@mycompany.com
  Reputation: 9.2

=== SUMMARY ===
Valid: 2
Invalid: 0
Success Rate: 100.0%
```

---

## Twilio Example

### Step 1: Get your Credentials

Go to [Twilio Console](https://www.twilio.com/console) and copy:
- Account SID: Your account SID (starts with `AC`)
- Auth Token: Your authentication token (long hexadecimal string)

### Step 2: Add to list.txt

```bash
cat > twilio/list.txt << EOF
AC[YOUR_ACCOUNT_SID]:[YOUR_AUTH_TOKEN]
AC[ANOTHER_ACCOUNT_SID]:[ANOTHER_AUTH_TOKEN]
EOF
```

Example format: `AC[alphanumeric]:[alphanumeric]`

### Step 3: Validate

```bash
python twilio/validator.py
```

### Step 4: Check Results

```bash
cat twilio/results.txt
```

**Output Example:**
```
=== Twilio Credentials Validation Results ===
Timestamp: 2024-01-15T14:30:45.123456
Total Credentials Checked: 2

✓ VALID - AC1234...abcdef
  Account: My Company Production
  Status: active
  Phone Numbers: 5

✓ VALID - ACABCD...QRSTUV
  Account: My Company Testing
  Status: active
  Phone Numbers: 2

=== SUMMARY ===
Valid: 2
Invalid: 0
Success Rate: 100.0%
```

---

## Brevo Example

### Step 1: Get your API Key

Go to [Brevo Settings](https://app.brevo.com/settings/account) and copy API key.

### Step 2: Add to list.txt

```bash
cat > brevo/list.txt << EOF
xkeysib_1234567890abcdefghijklmnopqrst
xkeysib_abcdefghijklmnopqrst1234567890
EOF
```

### Step 3: Validate

```bash
python brevo/validator.py
```

### Step 4: Check Results

```bash
cat brevo/results.txt
```

**Output Example:**
```
=== Brevo API Key Validation Results ===
Timestamp: 2024-01-15T14:30:45.123456
Total Keys Checked: 2

✓ VALID - xkey...opqrst
  Email: hello@mycompany.com
  Company: My Company Inc
  Plan: Professional

✓ VALID - xkey...1234567890
  Email: marketing@mycompany.com
  Company: My Company Inc
  Plan: Essentials

=== SUMMARY ===
Valid: 2
Invalid: 0
Success Rate: 100.0%
```

---

## Mailchimp Example

### Step 1: Get your API Key

Go to [Mailchimp Account Settings](https://us1.admin.mailchimp.com/account/api-keys/) 
and copy API key (format includes datacenter: `key-dc`).

### Step 2: Add to list.txt

```bash
cat > mailchimp/list.txt << EOF
[YOUR_API_KEY]-us1
[YOUR_API_KEY]-eu1
EOF
```

Example format: `[alphanumeric_key]-dc` (where dc is datacenter like us1, eu1, etc)

### Step 3: Validate

```bash
python mailchimp/validator.py
```

### Step 4: Check Results

```bash
cat mailchimp/results.txt
```

**Output Example:**
```
=== Mailchimp API Key Validation Results ===
Timestamp: 2024-01-15T14:30:45.123456
Total Keys Checked: 2

✓ VALID - 1234...abcdef-us1
  Datacenter: us1
  Email: admin@mycompany.com
  Lists: 8

✓ VALID - abcd...7890-eu1
  Datacenter: eu1
  Email: eu-admin@mycompany.com
  Lists: 3

=== SUMMARY ===
Valid: 2
Invalid: 0
Success Rate: 100.0%
```

---

## Stripe Example

### Step 1: Get your Secret Key

Go to [Stripe Dashboard API Keys](https://dashboard.stripe.com/apikeys) 
and copy the Secret Key.

### Step 2: Add to list.txt

```bash
cat > stripe/list.txt << EOF
sk_live_[YOUR_STRIPE_KEY]
sk_test_[YOUR_STRIPE_KEY]
EOF
```

Example format: `sk_live_[alphanumeric_string]` or `sk_test_[alphanumeric_string]`

### Step 3: Validate

```bash
python stripe/validator.py
```

### Step 4: Check Results

```bash
cat stripe/results.txt
```

**Output Example:**
```
=== Stripe API Key Validation Results ===
Timestamp: 2024-01-15T14:30:45.123456
Total Keys Checked: 2

✓ VALID - sk_live...mnopqrst
  Environment: LIVE
  Type: SECRET_KEY
  Business: My Company Inc
  Country: US

✓ VALID - sk_test...1234567890
  Environment: TEST
  Type: SECRET_KEY
  Business: My Company Inc
  Country: US

=== SUMMARY ===
Valid: 2
Invalid: 0
Success Rate: 100.0%
```

---

## AWS Example

### Step 1: Get your Credentials

Go to [AWS IAM Users](https://console.aws.amazon.com/iam/home#/users) 
and create/copy Access Key ID and Secret Access Key.

### Step 2: Install boto3

```bash
pip install boto3
```

### Step 3: Add to list.txt

```bash
cat > aws/list.txt << EOF
AKIA[YOUR_ACCESS_KEY_ID]:[YOUR_SECRET_ACCESS_KEY]
AKIA[ANOTHER_ACCESS_KEY_ID]:[ANOTHER_SECRET_ACCESS_KEY]
EOF
```

Example format: `AKIA[alphanumeric]:[alphanumeric]`

### Step 4: Validate

```bash
python aws/validator.py
```

### Step 5: Check Results

```bash
cat aws/results.txt
```

**Output Example:**
```
=== AWS Credentials Validation Results ===
Timestamp: 2024-01-15T14:30:45.123456
Total Credentials Checked: 2

✓ VALID - AKIA[XXXX]...
  Account ID: 123456789012
  ARN: arn:aws:iam::123456789012:user/deployer
  User: deployer

✓ VALID - AKIA[YYYY]...
  Account ID: 987654321098
  ARN: arn:aws:iam::987654321098:user/ci-user
  User: ci-user

=== SUMMARY ===
Valid: 2
Invalid: 0
Success Rate: 100.0%
```

---

## Batch Validation (All Services)

### Validate Everything at Once

```bash
python validate_all.py
```

**Output:**
```
══════════════════════════════════════════════════
     API Key Validators - Master Controller
     Starting validation at 2024-01-15 14:30:45
══════════════════════════════════════════════════

==================================================
🔍 Validating SENDGRID
==================================================
[SendGrid] Found 2 keys to validate...
✓ Results saved to /home/user/messites/api-key-validators/sendgrid/results.txt
  Valid: 2 | Invalid: 0

==================================================
🔍 Validating TWILIO
==================================================
[Twilio] Found 2 credentials to validate...
✓ Results saved to /home/user/messites/api-key-validators/twilio/results.txt
  Valid: 2 | Invalid: 0

... (continues for all services)

==================================================
📊 VALIDATION SUMMARY
==================================================
  sendgrid        ✅ COMPLETED
  twilio          ✅ COMPLETED
  brevo           ✅ COMPLETED
  mailchimp       ✅ COMPLETED
  stripe          ✅ COMPLETED
  aws             ✅ COMPLETED

  Total Completed: 6
  Total Skipped: 0
  Total Failed: 0

📁 Results Location: /home/user/messites/api-key-validators/{service}/results.txt

✨ Validation finished at 2024-01-15 14:30:55
```

---

## Common Errors

### "Authentication failed (401)"

**Cause:** Invalid or expired API key  
**Solution:** 
1. Verify the key in your service's console
2. Check it's not expired
3. Ensure correct format

### "Request timeout"

**Cause:** Network issues or API unavailability  
**Solution:**
1. Check your internet connection
2. Verify the service is available
3. Try again in a few moments

### "Access denied (403)"

**Cause:** Key doesn't have required permissions  
**Solution:**
1. Create a new API key with broader permissions
2. Or use API key with explicit permissions for validation

### "boto3 not installed" (AWS)

**Solution:**
```bash
pip install boto3
```

---

## Tips & Tricks

### Export Results as CSV

```bash
# Extract valid keys to CSV
grep "VALID" sendgrid/results.txt | awk '{print $3}' > valid_keys.csv
```

### Monitor Key Expiration

```bash
# Keep validation history
cp sendgrid/results.txt sendgrid/results_$(date +%Y%m%d).txt

# Compare with previous run
diff sendgrid/results_20240115.txt sendgrid/results_20240116.txt
```

### Schedule Regular Validation

```bash
# Add to crontab for weekly validation
0 9 * * 0 cd /home/user/messites/api-key-validators && python validate_all.py
```

### Encrypt Results

```bash
# Encrypt results for backup
gpg --symmetric sendgrid/results.txt

# Decrypt when needed
gpg --decrypt sendgrid/results.txt.gpg
```

---

For more help, see [README.md](README.md) and [SECURITY.md](SECURITY.md)
