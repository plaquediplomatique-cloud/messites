import discord
from discord.ext import commands
from discord import Intents, app_commands
from dotenv import load_dotenv
import os
import config
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN", "")
if not TOKEN:
    raise ValueError("⚠️ DISCORD_TOKEN non trouvé! Ajoute-le dans le fichier .env")

intents = Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Variables globales
GUILD = None
RULES_CHANNEL = None
ROLES_CHANNEL = None
RULES_MESSAGE_ID = None

class Logger:
    """Système de logging professionnel"""

    @staticmethod
    def log(level: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")

        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "DEBUG": "🔍",
            "ACTION": "⚡",
        }

        icon = icons.get(level, "•")
        print(f"[{timestamp}] {icon} {message}")

@bot.event
async def on_ready():
    global GUILD, RULES_CHANNEL, ROLES_CHANNEL, RULES_MESSAGE_ID

    Logger.log("INFO", f"Bot connecté en tant que {bot.user}")

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        Logger.log("SUCCESS", f"{len(synced)} commandes slash synchronisées")
    except Exception as e:
        Logger.log("ERROR", f"Erreur sync commandes: {e}")

    # Récupérer le serveur
    GUILD = bot.guilds[0] if bot.guilds else None
    if not GUILD:
        Logger.log("ERROR", "Aucun serveur trouvé!")
        return

    Logger.log("INFO", f"Serveur: {GUILD.name} (ID: {GUILD.id})")

    # Analyser le serveur existant
    await analyze_existing_server()

    # Configurer le bot
    await configure_bot()

    Logger.log("SUCCESS", "Bot prêt à l'emploi! 🚀\n")

async def analyze_existing_server():
    """Analyse le serveur et récupère les salons/rôles existants"""
    global RULES_CHANNEL, ROLES_CHANNEL, RULES_MESSAGE_ID

    Logger.log("INFO", "\n📊 ANALYSE DU SERVEUR EXISTANT")
    Logger.log("INFO", "=" * 50)

    # Analyser les salons
    Logger.log("INFO", f"\n📂 Salons ({len(GUILD.text_channels)}):")
    for channel in GUILD.text_channels:
        perms = channel.permissions_synced
        print(f"   • #{channel.name} {'(catégorie)' if channel.permissions_synced else ''}")

        if "règlement" in channel.name.lower():
            RULES_CHANNEL = channel
            Logger.log("SUCCESS", f"   → Salon #règlement trouvé!")

        if "rôle" in channel.name.lower():
            ROLES_CHANNEL = channel
            Logger.log("SUCCESS", f"   → Salon #rôles trouvé!")

    # Chercher le message du règlement
    if RULES_CHANNEL:
        try:
            async for message in RULES_CHANNEL.history(limit=50):
                if message.author == GUILD.me or len(message.embeds) > 0:
                    RULES_MESSAGE_ID = message.id
                    Logger.log("SUCCESS", f"   → Message du règlement trouvé (ID: {RULES_MESSAGE_ID})")
                    break
        except Exception as e:
            Logger.log("WARNING", f"   → Erreur recherche message: {e}")

    # Analyser les rôles
    Logger.log("INFO", f"\n🎭 Rôles ({len(GUILD.roles) - 1}):")
    roles_found = []
    for role in GUILD.roles[1:]:
        roles_found.append(role.name)

    for role_name in roles_found[:10]:
        print(f"   • {role_name}")

    if len(roles_found) > 10:
        print(f"   • ... et {len(roles_found) - 10} autres")

    # Analyser les catégories
    Logger.log("INFO", f"\n📁 Catégories ({len(GUILD.categories)}):")
    for category in GUILD.categories:
        channels_count = len(category.channels)
        print(f"   • {category.name} ({channels_count} salons)")

    Logger.log("INFO", "=" * 50)

async def configure_bot():
    """Configure le bot en fonction de ce qui existe"""

    Logger.log("INFO", "\n⚙️  CONFIGURATION")
    Logger.log("INFO", "=" * 50)

    # Configurer les permissions
    await setup_permissions()

    # Configurer les réactions
    if RULES_MESSAGE_ID and RULES_CHANNEL:
        await setup_rules_reactions()

    Logger.log("INFO", "=" * 50)

async def setup_permissions():
    """Configure les permissions des salons admin"""

    Logger.log("ACTION", "\n🔒 Configuration des permissions admin...")

    staff_role = discord.utils.get(GUILD.roles, name=config.STAFF_ROLE)
    everyone_role = GUILD.default_role
    updated = 0

    if not staff_role:
        Logger.log("WARNING", f"   Rôle '{config.STAFF_ROLE}' non trouvé")
        return

    for channel in GUILD.channels:
        if isinstance(channel, discord.TextChannel):
            if any(admin_name in channel.name for admin_name in config.ADMIN_CHANNELS):
                try:
                    await channel.set_permissions(everyone_role, view_channel=False)
                    await channel.set_permissions(staff_role, view_channel=True)
                    updated += 1
                    Logger.log("SUCCESS", f"   ✓ #{channel.name}")
                except Exception as e:
                    Logger.log("ERROR", f"   ✗ #{channel.name}: {e}")

    Logger.log("SUCCESS", f"   {updated} salons configurés")

async def setup_rules_reactions():
    """Configure les réactions automatiques au message du règlement"""

    Logger.log("ACTION", "\n👁️  Configuration des réactions au règlement...")

    try:
        message = await RULES_CHANNEL.fetch_message(RULES_MESSAGE_ID)

        # Vérifier si la réaction ✅ existe déjà
        if not any(reaction.emoji == "✅" for reaction in message.reactions):
            await message.add_reaction("✅")
            Logger.log("SUCCESS", "   ✓ Réaction ✅ ajoutée")
        else:
            Logger.log("INFO", "   ✓ Réaction ✅ déjà présente")

    except Exception as e:
        Logger.log("ERROR", f"   ✗ Erreur: {e}")

@bot.event
async def on_raw_reaction_add(payload):
    """Gère l'ajout de réactions (règlement et rôles)"""

    # Règlement
    if RULES_MESSAGE_ID and payload.message_id == RULES_MESSAGE_ID:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member and not member.bot:
            member_role = discord.utils.get(guild.roles, name=config.MEMBER_ROLE)
            if member_role and member_role not in member.roles:
                try:
                    await member.add_roles(member_role)
                    Logger.log("ACTION", f"✅ Rôle '{config.MEMBER_ROLE}' donné à {member.name}")
                except Exception as e:
                    Logger.log("ERROR", f"Erreur: {e}")

    # Rôles
    if ROLES_CHANNEL and payload.channel_id == ROLES_CHANNEL.id:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji_str = str(payload.emoji)

        if member and not member.bot and emoji_str in config.ROLE_EMOJIS:
            role_name = config.ROLE_EMOJIS[emoji_str]
            role = discord.utils.get(guild.roles, name=role_name)

            if role and role not in member.roles:
                try:
                    await member.add_roles(role)
                    Logger.log("ACTION", f"✅ Rôle '{role_name}' donné à {member.name}")
                except Exception as e:
                    Logger.log("ERROR", f"Erreur: {e}")

@bot.event
async def on_raw_reaction_remove(payload):
    """Gère le retrait de réactions"""

    if ROLES_CHANNEL and payload.channel_id == ROLES_CHANNEL.id:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji_str = str(payload.emoji)

        if member and not member.bot and emoji_str in config.ROLE_EMOJIS:
            role_name = config.ROLE_EMOJIS[emoji_str]
            role = discord.utils.get(guild.roles, name=role_name)

            if role and role in member.roles:
                try:
                    await member.remove_roles(role)
                    Logger.log("ACTION", f"➖ Rôle '{role_name}' retiré de {member.name}")
                except Exception as e:
                    Logger.log("ERROR", f"Erreur: {e}")

@bot.tree.command(name="live", description="📺 Annonce un live TikTok!")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    titre="Titre du live",
    message="Message personnalisé"
)
async def live_command(interaction: discord.Interaction, titre: str = None, message: str = None):
    """Commande pour annoncer un live"""

    if titre is None:
        titre = "📺 JE SUIS EN LIVE!"
    if message is None:
        message = "Viens me rejoindre maintenant!"

    embed = discord.Embed(
        title=titre,
        description=message,
        color=discord.Color.from_rgb(255, 0, 127)
    )

    embed.add_field(
        name="🎥 Rejoins-moi sur TikTok",
        value="[→ tiktok.com/zetsuhi ←](https://tiktok.com/@zetsuhi)",
        inline=False
    )

    embed.add_field(
        name="🔴 EN DIRECT MAINTENANT",
        value="Clique sur le lien pour regarder le live!",
        inline=False
    )

    embed.set_footer(text="Zetsu Live • En direct")

    await interaction.response.send_message(embed=embed)
    Logger.log("ACTION", f"📺 Live annoncé par {interaction.user.name}")

@bot.tree.command(name="status", description="📊 Voir l'état du serveur")
@app_commands.checks.has_permissions(administrator=True)
async def status_command(interaction: discord.Interaction):
    """Affiche l'état du serveur"""

    await interaction.response.defer()

    embed = discord.Embed(
        title="📊 État du serveur Zetsu Live",
        color=discord.Color.green()
    )

    embed.add_field(
        name="👥 Membres",
        value=f"{GUILD.member_count} membres",
        inline=True
    )

    embed.add_field(
        name="🎭 Rôles",
        value=f"{len(GUILD.roles) - 1} rôles",
        inline=True
    )

    embed.add_field(
        name="📂 Salons",
        value=f"{len(GUILD.text_channels)} salons",
        inline=True
    )

    embed.add_field(
        name="🔌 Statut du bot",
        value="✅ En ligne et fonctionnel",
        inline=False
    )

    if RULES_CHANNEL:
        embed.add_field(
            name="📋 Salon du règlement",
            value=f"#{RULES_CHANNEL.name}",
            inline=True
        )

    if ROLES_CHANNEL:
        embed.add_field(
            name="🎭 Salon des rôles",
            value=f"#{ROLES_CHANNEL.name}",
            inline=True
        )

    embed.set_footer(text="Misa Bot • Prêt à l'emploi")

    await interaction.followup.send(embed=embed)
    Logger.log("ACTION", f"Status demandé par {interaction.user.name}")

@bot.tree.command(name="reanalyze", description="🔍 Ré-analyser le serveur")
@app_commands.checks.has_permissions(administrator=True)
async def reanalyze_command(interaction: discord.Interaction):
    """Ré-analyse le serveur"""

    await interaction.response.defer()

    await analyze_existing_server()
    await configure_bot()

    embed = discord.Embed(
        title="✅ Analyse complète terminée!",
        description="Le serveur a été ré-analysé et reconfiguré.",
        color=discord.Color.green()
    )

    embed.add_field(name="🔍 Détails", value="Vérifie la console pour les détails complets!", inline=False)

    await interaction.followup.send(embed=embed)
    Logger.log("ACTION", f"Ré-analyse effectuée par {interaction.user.name}")

Logger.log("INFO", "\n🤖 Démarrage du bot Misa...")
Logger.log("INFO", "=" * 50 + "\n")

bot.run(TOKEN)
