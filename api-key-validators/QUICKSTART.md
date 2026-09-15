# ⚡ Quick Start - API Key Validators

Get up and running in 2 minutes.

## 1️⃣ Installation

```bash
cd api-key-validators
pip install -r requirements.txt
```

## 2️⃣ Add Your Keys

### SendGrid
```bash
echo "SG.your_sendgrid_key_here" > sendgrid/list.txt
```

### Twilio
```bash
echo "account_sid:auth_token" > twilio/list.txt
```

### Brevo
```bash
echo "your_brevo_key_here" > brevo/list.txt
```

### Mailchimp
```bash
echo "your_mailchimp_key-dc" > mailchimp/list.txt
```

### Stripe
```bash
echo "sk_live_your_stripe_key_here" > stripe/list.txt
```

### AWS
```bash
echo "AKIA...:secret_key" > aws/list.txt
pip install boto3
```

## 3️⃣ Run Validation

**Single Service:**
```bash
python sendgrid/validator.py
```

**All Services:**
```bash
python validate_all.py
```

## 4️⃣ Check Results

```bash
cat sendgrid/results.txt
```

---

## 📊 Output Example

```
=== SendGrid API Key Validation Results ===
Timestamp: 2024-01-15T14:30:45.123456
Total Keys Checked: 1

✓ VALID - SG.xxxx...xxxx
  Account: your-email@example.com
  Reputation: 8.5

=== SUMMARY ===
Valid: 1
Invalid: 0
Success Rate: 100.0%
```

---

## 🔐 Security Checklist

- ✅ `list.txt` is in `.gitignore` (protected)
- ✅ `results.txt` is in `.gitignore` (protected)
- ✅ Keys are never logged in full
- ✅ All validation runs locally
- ✅ No data sent to external services

---

## 🆘 Need Help?

- **Examples:** See [EXAMPLES.md](EXAMPLES.md)
- **Security:** See [SECURITY.md](SECURITY.md)
- **Full Docs:** See [README.md](README.md)

---

## Key Format Reference

| Service    | Format | Example |
|-----------|--------|---------|
| SendGrid  | Single key | `SG.xxxxxx` |
| Twilio    | `sid:token` | `ACxxxxxx:xxxxxx` |
| Brevo     | Single key | `xkeysib_xxxxxx` |
| Mailchimp | `key-dc` | `xxxxxx-us1` |
| Stripe    | Single key | `sk_live_xxxxxx` |
| AWS       | `id:secret` | `AKIA...:secret` |

---

⏱️ **Takes less than 1 minute per service!**
