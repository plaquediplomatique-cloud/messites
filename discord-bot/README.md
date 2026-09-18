# 🤖 Bot Discord - Zetsu Live

Bot complet pour gérer le serveur Discord Zetsu Live avec système de rôles et règlement.

## 🎯 Fonctionnalités

✅ **Système de Règlement**
- Les membres qui réagissent au message du règlement reçoivent automatiquement le rôle "Membre"

✅ **Sélection de Rôles**
- Système de réactions pour choisir des rôles (jeux, genres, âge, etc.)
- Réagir pour ajouter, enlever pour retirer

✅ **Permissions Admin**
- Salons admin accessibles SEULEMENT aux staff
- Configuration automatique des permissions

## 📦 Installation

### 1. Créer une application Discord
1. Va sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique sur "New Application"
3. Donne-lui un nom (ex: "Zetsu Bot")
4. Va dans "Bot" → "Add Bot"
5. Sous TOKEN, clique "Copy" et sauvegarde-le

### 2. Configurer les permissions
1. Va dans "OAuth2" → "URL Generator"
2. Sélectionne les scopes:
   - `bot`
3. Sélectionne les permissions:
   - `Send Messages`
   - `Manage Roles`
   - `Manage Channels`
   - `Read Message History`
   - `Add Reactions`
4. Copie l'URL générée et ouvre-la pour ajouter le bot à ton serveur

### 3. Configuration locale

```bash
cd discord-bot
pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` et ajoute:
- `DISCORD_TOKEN`: Le token du bot (étape 1)
- `GUILD_ID`: L'ID de ton serveur (clic droit sur le serveur → Copier l'ID)
- `RULES_MESSAGE_ID`: L'ID du message du règlement
- `ROLES_CHANNEL_ID`: L'ID du salon #rôles

### 4. Lancer le bot

```bash
python bot.py
```

## 🎮 Utilisation

### Message du Règlement
Les utilisateurs cliquent sur une réaction → reçoivent le rôle "Membre" automatiquement

### Sélection de Rôles
Dans le salon #rôles, utilise la commande:
```
!setup_roles_message
```

Le bot affichera tous les rôles disponibles avec emojis.

## 🔧 Configuration Personnalisée

Edite `config.py` pour modifier:
- Les noms des rôles
- Les emojis des rôles
- Les salons admin
- Les noms des rôles staff

## 📝 Notes

- Le bot a besoin de permissions d'administrateur pour fonctionner correctement
- Assure-toi que le rôle du bot est au-dessus des autres rôles dans les paramètres
- Remplace les emojis dans `config.py` si tu veux d'autres symboles

## ❌ Troubleshooting

**Le bot ne répond pas**
- Vérifie que le token est correct dans `.env`
- Assure-toi que le bot est dans le serveur

**Les rôles ne s'ajoutent pas**
- Le rôle du bot doit être au-dessus des autres rôles
- Vérifie les permissions du bot

**Les permissions ne fonctionnent pas**
- Assure-toi que les noms des salons contiennent "admin" ou "staff"
- Crée un rôle nommé "Modérateur" ou change le nom dans `config.py`
