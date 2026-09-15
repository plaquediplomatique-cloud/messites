# API Key Validators Suite 🔐

Suite complète et sécurisée pour valider vos clés API pour les principaux services cloud et SaaS.

## Services Supportés

- ✅ **SendGrid** - Email delivery service
- ✅ **Twilio** - SMS/Voice messaging
- ✅ **Brevo** - Marketing automation & email
- ✅ **Mailchimp** - Email marketing
- ✅ **Stripe** - Payment processing
- ✅ **AWS** - Cloud infrastructure

## Installation

### 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

Pour AWS, vous aurez également besoin de boto3:
```bash
pip install boto3
```

### 2. Structure des fichiers

Chaque service a sa propre structure:

```
sendgrid/
├── list.txt          # Clés API à valider (1 par ligne)
├── validator.py      # Script de validation
└── results.txt       # Résultats (généré automatiquement)
```

## Utilisation

### Mode Rapide - Valider Un Service

```bash
# SendGrid
python sendgrid/validator.py

# Twilio
python twilio/validator.py

# Brevo
python brevo/validator.py

# Mailchimp
python mailchimp/validator.py

# Stripe
python stripe/validator.py

# AWS
python aws/validator.py
```

### Mode Complet - Valider Tous les Services

```bash
python validate_all.py
```

Cela validera tous les services qui ont un fichier `list.txt`.

## Format des Clés

### SendGrid
```
SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
**Fichier:** `sendgrid/list.txt` (1 clé par ligne)

### Twilio
```
account_sid:auth_token
```
**Fichier:** `twilio/list.txt` (format: `account_sid:auth_token`)

### Brevo
```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
**Fichier:** `brevo/list.txt` (1 clé par ligne)

### Mailchimp
```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xx
```
**Fichier:** `mailchimp/list.txt` (1 clé par ligne, le format inclut le datacenter)

### Stripe
```
sk_live_[YOUR_KEY_HERE]
sk_test_[YOUR_KEY_HERE]
```
**Fichier:** `stripe/list.txt` (1 clé par ligne)

### AWS
```
AKIAXXXXXXXXXXXXXXXX:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
**Fichier:** `aws/list.txt` (format: `access_key:secret_key`)

## Exemple d'Utilisation

### 1. Ajouter vos clés SendGrid

```bash
cat > sendgrid/list.txt << EOF
SG.key1xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SG.key2xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF
```

### 2. Valider

```bash
python sendgrid/validator.py
```

### 3. Consulter les résultats

```bash
cat sendgrid/results.txt
```

## Fonctionnalités de Sécurité

✅ **Aucune clé complète n'est loggée**
- Les clés sont tronquées: `xxxx...xxxx`
- Les logs ne contiennent jamais les secrets

✅ **Fichiers locaux uniquement**
- Aucun envoi de données externes
- Tous les résultats restent sur votre machine

✅ **Protection .gitignore**
- `list.txt` ignoré (ne sera jamais committée)
- `results.txt` ignoré
- Fichiers `.env` ignorés

✅ **Validation sécurisée**
- Timeouts configurés (5 secondes par défaut)
- Gestion des erreurs complète
- Pas de stockage de mots de passe

## Résultats de Validation

Chaque validation produit un rapport détaillé:

```
=== SendGrid API Key Validation Results ===
Timestamp: 2024-01-15T14:30:45.123456
Total Keys Checked: 2

✓ VALID - SG.xxxx...xxxx
  Account: your-email@example.com
  Reputation: 8.5

✗ INVALID - SG.yyyy...yyyy
  Reason: Authentication failed (401)

=== SUMMARY ===
Valid: 1
Invalid: 1
Success Rate: 50.0%
```

## Informations Récupérées

### SendGrid
- Email du compte
- Nom du compte
- Réputation
- Nom et ID de la clé API
- Scopes autorisés

### Twilio
- Nom du compte
- Statut
- Nombre de numéros téléphoniques
- Exemples de numéros

### Brevo
- Email du compte
- Nom de l'entreprise
- Plan d'abonnement
- Crédits disponibles

### Mailchimp
- Email du compte
- Nom du compte
- Nombre de listes
- Exemples de listes

### Stripe
- ID du compte
- Environnement (LIVE ou TEST)
- Nom de l'entreprise
- Pays
- Type de clé

### AWS
- ID du compte
- ARN de l'utilisateur
- Nom de l'utilisateur
- Date de création

## Erreurs Courants et Solutions

### "list.txt not found"
```bash
# Créer le fichier vide d'abord
touch sendgrid/list.txt
```

### "Request timeout"
- Vérifier votre connexion internet
- La clé API peut être bloquée

### "Authentication failed (401)"
- Clé API invalide ou expirée
- Vérifier le format exact

### AWS: "boto3 not installed"
```bash
pip install boto3
```

## Bonnes Pratiques

1. ✅ **Stockez les clés localement** dans les fichiers `list.txt`
2. ✅ **Ne committez jamais** les `list.txt` (protégé par .gitignore)
3. ✅ **Vérifiez régulièrement** les clés API actives
4. ✅ **Archivez les résultats** pour auditer les changements
5. ✅ **Utilisez des clés avec permissions limitées** quand possible

## Contribution

Des validateurs supplémentaires peuvent être ajoutés facilement. Consultez `sendgrid/validator.py` pour un exemple.

## License

MIT - Libre d'utilisation

---

**⚠️ SÉCURITÉ:** Ne partagez jamais vos fichiers `list.txt` ou `results.txt`. Ils contiennent des informations sensibles sur vos comptes.
