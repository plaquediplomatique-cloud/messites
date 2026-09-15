#!/bin/bash
# Example usage of the API Key Validators Suite

set -e

echo "🔐 API Key Validators - Example Usage"
echo "======================================"

# Create example keys folder
mkdir -p example_keys

# Create sample key files (with PLACEHOLDER values - replace with real keys)
echo "Creating example key files..."

cat > example_keys/sendgrid.txt << 'EOF'
# SendGrid API keys
# SG.your_real_key_here_1
# SG.your_real_key_here_2
EOF

cat > example_keys/twilio.txt << 'EOF'
# Twilio credentials (SID:TOKEN format)
# ACxxxxxxxxxxxxxxxxxxxxxxxx:your_auth_token_here
EOF

cat > example_keys/stripe.txt << 'EOF'
# Stripe Secret Keys
# sk_live_your_real_stripe_key_here
# sk_test_your_test_stripe_key_here
EOF

cat > example_keys/brevo.txt << 'EOF'
# Brevo API keys
# xkeysib_your_real_brevo_key_here
EOF

cat > example_keys/mailchimp.txt << 'EOF'
# Mailchimp API keys (format: key-datacenter)
# your_key_here-us1
# another_key_here-eu1
EOF

cat > example_keys/aws.txt << 'EOF'
# AWS IAM credentials (ACCESS_KEY:SECRET_KEY)
# AKIAIOSFODNN7EXAMPLE:your_secret_key_here
EOF

cat > example_keys/github.txt << 'EOF'
# GitHub Personal Access Tokens
# ghp_your_real_token_here
EOF

cat > example_keys/slack.txt << 'EOF'
# Slack Bot Tokens
# xoxb_your_real_token_here
EOF

echo "✓ Example key files created in ./example_keys/"
echo ""
echo "📝 Next steps:"
echo "  1. Edit the files in example_keys/ and add real API keys"
echo "  2. Run: python validate_keys.py ./example_keys"
echo "  3. Check results in: validation_results/"
echo ""
echo "⚠️  Remember:"
echo "  - Never commit real keys to git"
echo "  - Always use .gitignore to protect key files"
echo "  - Rotate and revoke compromised keys immediately"
