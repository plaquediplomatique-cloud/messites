# 🔒 Security Guide - API Key Validators

## Safety Principles

### Never Commit Credentials
```bash
# ✅ GOOD - Files are in .gitignore
list.txt
results.txt

# ❌ BAD - Don't do this
git add api-key-validators/sendgrid/list.txt
```

### Credential Format Best Practices

1. **Access Keys Only**
   - Use dedicated API keys for each validator
   - Don't use personal account credentials

2. **Limited Scope**
   - Create keys with minimal required permissions
   - Example: SendGrid key with "Mail Send" scope only

3. **Key Rotation**
   - Regularly rotate expired keys
   - Remove unused keys from validation lists

### Local Storage Security

```bash
# Protect your validation results
chmod 600 sendgrid/results.txt
chmod 600 twilio/results.txt

# Back up securely (encrypted)
# Don't store results in cloud storage without encryption
```

### Environment Variable Alternative

For **AWS**, you can use environment variables instead of storing in files:

```bash
export AWS_ACCESS_KEY_ID="AKIAXXXXXXXX"
export AWS_SECRET_ACCESS_KEY="xxxxx"
python aws/validator.py
```

## Threat Model

### What These Tools Protect Against

✅ **Accidental key loss** - Verify existing keys are still valid  
✅ **Key expiration** - Catch expired credentials before they break services  
✅ **Configuration drift** - Validate keys match your current setup  
✅ **Account auditing** - Get info about which accounts keys belong to  

### What These Tools DON'T Protect Against

❌ **Compromised keys** - If a key is leaked, immediately revoke it  
❌ **Unauthorized access** - Don't share validation results  
❌ **Network attacks** - Use VPN/corporate network when possible  

## Secure Workflow

### Example: Safe Validation Process

```bash
# 1. Create a dedicated API key in your service
#    (minimal permissions, 90-day expiry)

# 2. Add to list.txt on secure machine
echo "your-new-key-here" >> sendgrid/list.txt

# 3. Run validation (air-gapped if possible)
python sendgrid/validator.py

# 4. Review results
cat sendgrid/results.txt

# 5. Delete from list.txt if temporary
sed -i '/your-new-key-here/d' sendgrid/list.txt

# 6. Verify it's removed
git status  # Should show no changes if in .gitignore
```

## AWS-Specific Security

### Recommended IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sts:GetCallerIdentity",
        "iam:GetUser"
      ],
      "Resource": "*"
    }
  ]
}
```

This policy allows validation without giving full AWS access.

### AWS Key Types

```
AKIA...  - Standard AWS Access Key (User or Temp credentials)
AIDA...  - Service-linked role credentials
```

Never use root credentials for validation!

## Incident Response

### If a Key is Compromised

```bash
# 1. IMMEDIATELY revoke the key in the service's console
# 2. Check CloudTrail / Activity logs for suspicious use
# 3. Remove from list.txt
# 4. Generate and test new credentials
# 5. Run validation with new key
```

### If Results are Leaked

```bash
# 1. Assume all keys in that results.txt are compromised
# 2. Revoke all listed keys
# 3. Delete the results.txt file
# 4. Generate new keys for each service
# 5. Update list.txt with new keys
# 6. Re-validate
```

## Compliance Notes

### PCI DSS (Payment Card Industry)
- Don't log full credit card numbers
- Use Stripe restricted keys when possible
- Store results securely

### GDPR (General Data Protection)
- Customer email addresses in results
- Store securely
- Delete when no longer needed

### SOC 2 / ISO 27001
- Use dedicated credentials for tools
- Monitor credential usage
- Implement key rotation

## Monitoring Commands

```bash
# Check when keys were last validated
ls -lt */results.txt | head -5

# Find uncommitted changes (should be empty)
git status api-key-validators/

# Verify .gitignore is working
git check-ignore -v sendgrid/list.txt

# Find any accidental key commits (in history)
git log -p --all -- "*list.txt" | grep -i "^+.*[a-z0-9]{32,}"
```

## Questions?

For security concerns or vulnerabilities found in this tool:
1. Do NOT create public issues
2. Email: plaquediplomatique@gmail.com
3. Include: severity, impact, reproducible steps

---

**Last Updated**: 2024  
**Validator Version**: 1.0  
**Recommended Review**: Quarterly
