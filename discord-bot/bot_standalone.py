import discord
from discord.ext import commands
from discord import Intents, app_commands
from dotenv import load_dotenv
import os
import config

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN", "")
if not TOKEN:
    raise ValueError("⚠️ DISCORD_TOKEN non trouvé! Ajoute-le dans le fichier .env")

intents = Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = None
RULES_MESSAGE_ID = None
ROLES_CHANNEL_ID = None

@bot.event
async def on_ready():
    global GUILD_ID, RULES_MESSAGE_ID, ROLES_CHANNEL_ID

    print(f"\n{'='*50}")
    print(f"✅ Bot connecté en tant que {bot.user}")
    print(f"{'='*50}\n")

    try:
        synced = await bot.tree.sync()
        print(f"✨ {len(synced)} slash commandes synchronisées!\n")
    except Exception as e:
        print(f"❌ Erreur sync commandes: {e}\n")

    guild = bot.guilds[0] if bot.guilds else None
    if not guild:
        print("❌ Aucun serveur trouvé!")
        return

    GUILD_ID = guild.id
    print(f"📍 Serveur trouvé: {guild.name} (ID: {GUILD_ID})\n")

    await setup_roles(guild)
    await setup_permissions(guild)
    await create_rules_message(guild)
    await create_roles_message(guild)
    await analyze_server(guild)

    print(f"{'='*50}")
    print("✨ CONFIGURATION TERMINÉE!")
    print(f"{'='*50}\n")

async def setup_roles(guild):
    """Crée les rôles s'ils n'existent pas"""
    all_roles = {role.name for role in guild.roles}

    roles_to_create = [
        config.MEMBER_ROLE,
        config.STAFF_ROLE,
        "Booster",
        "Animation",
        "Live",
        "Annonce all",
        "Femme",
        "Homme",
        "Non binaire",
        "13/15 ans",
        "15/18 ans",
        "18+",
        "Violence district",
        "Minecraft",
        "LOL",
        "Valorant",
        "Call of",
        "Blade ball",
        "Dbd",
        "Téléphone",
        "Console",
        "PC",
        "Tablette",
    ]

    created_count = 0
    print("\n🎭 Création des rôles:")
    for role_name in roles_to_create:
        if role_name not in all_roles:
            try:
                await guild.create_role(name=role_name)
                created_count += 1
                print(f"  ✅ {role_name}")
            except Exception as e:
                print(f"  ❌ {role_name}: {e}")

    if created_count > 0:
        print(f"\n✨ {created_count} rôles créés!")
    else:
        print("✅ Tous les rôles existent déjà!")

async def setup_permissions(guild):
    """Configure les permissions de tous les salons"""
    staff_role = discord.utils.get(guild.roles, name=config.STAFF_ROLE)
    everyone_role = guild.default_role
    updated_count = 0

    print("\n🔒 Configuration des permissions:")
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            if any(admin_name in channel.name for admin_name in config.ADMIN_CHANNELS):
                if staff_role:
                    try:
                        await channel.set_permissions(everyone_role, view_channel=False)
                        await channel.set_permissions(staff_role, view_channel=True)
                        updated_count += 1
                        print(f"  🔒 #{channel.name}")
                    except Exception as e:
                        print(f"  ❌ #{channel.name}: {e}")

    print(f"✅ {updated_count} salons configurés!")

async def create_rules_message(guild):
    """Crée le message du règlement automatiquement"""
    global RULES_MESSAGE_ID

    print("\n📋 Création du message du règlement:")

    rules_channel = discord.utils.get(guild.channels, name="règlement")
    if not rules_channel:
        try:
            rules_channel = await guild.create_text_channel("règlement")
            print(f"  ✅ Salon #règlement créé")
        except Exception as e:
            print(f"  ❌ Erreur création salon: {e}")
            return

    embed = discord.Embed(
        title="✨ BIENVENUE SUR ZETSU LIVE! ✨",
        description="Un petit endroit tranquille pour discuter, rigoler, partager nos délires et passer un bon moment ensemble.\n\n**Réagis au message ci-dessous pour accepter le règlement et obtenir le rôle Membre!** ✅",
        color=discord.Color.from_rgb(200, 100, 255)
    )

    embed.add_field(
        name="📌 LES RÈGLES",
        value="""
💜 **• Le respect avant tout**
C'est la raison d'être de notre communauté. Les propos racistes, homophobes, sexistes, haineux ou insultants n'ont pas leur place ici.

🚫 **• Pas de NSFW / gore**
Le serveur doit rester confortable et accessible à tous.
Pas de contenu pornographique, sexuel ou particulièrement violent.

📢 **• Pas de spam**
Évite les messages à répétition, le spam de mentions, les copias-collés à outrance ou toute autre forme de spam.

📍 **• Un salon = un sujet**
Chaque salon possède son propre thème. Pense à utiliser le bon endroit pour envoyer les messages afin de garder le serveur organisé et agréable à parcourir.

😌 **• Les sujets sensibles, avec modération**
Les discussions autour de la politique ou de la religion peuvent avoir leur place tant que ça reste calme.
Si une discussion commence à dégénérer, le staff pourra intervenir et y mettre fin.

🛡️ **• Respecte le staff**
Les membres du staff sont là pour maintenir une bonne ambiance et régler les problèmes lorsqu'il y a.
Une remarque ou une demande de leur part doit être respectueuse, inutile de transformer ça en embrouille.

🎮 **• Et surtout... amuse-toi !**
Le but du serveur reste avant tout de passer un bon moment.
        """,
        inline=False
    )

    embed.set_footer(text="Merci d'avoir pris le temps de lire, et bienvenue chez Zetsu! 🎮✨")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1166726320340201541/1293502223819931679/zetsu.png")

    try:
        msg = await rules_channel.send(embed=embed)
        await msg.add_reaction("✅")
        RULES_MESSAGE_ID = msg.id
        print(f"  ✅ Message du règlement créé (ID: {msg.id})")
    except Exception as e:
        print(f"  ❌ Erreur création message: {e}")

async def create_roles_message(guild):
    """Crée le message de sélection de rôles automatiquement"""
    global ROLES_CHANNEL_ID

    print("\n🎭 Création du message des rôles:")

    roles_channel = discord.utils.get(guild.channels, name="rôles")
    if not roles_channel:
        try:
            roles_channel = await guild.create_text_channel("rôles")
            print(f"  ✅ Salon #rôles créé")
        except Exception as e:
            print(f"  ❌ Erreur création salon: {e}")
            return

    ROLES_CHANNEL_ID = roles_channel.id

    embed = discord.Embed(
        title="📋 Sélectionnez vos rôles",
        description="Réagissez aux emojis pour ajouter/retirer les rôles qui vous intéressent!",
        color=discord.Color.purple()
    )

    roles_text = ""
    for emoji, role_name in config.ROLE_EMOJIS.items():
        roles_text += f"{emoji} {role_name}\n"

    embed.add_field(name="Rôles disponibles", value=roles_text, inline=False)
    embed.set_footer(text="Clique sur les emojis pour activer/désactiver tes rôles!")

    try:
        msg = await roles_channel.send(embed=embed)
        for emoji in config.ROLE_EMOJIS.keys():
            await msg.add_reaction(emoji)
        print(f"  ✅ Message des rôles créé (ID: {msg.id})")
    except Exception as e:
        print(f"  ❌ Erreur création message: {e}")

async def analyze_server(guild):
    """Analyse complète du serveur"""
    print(f"\n{'='*50}")
    print("📊 ANALYSE DU SERVEUR")
    print(f"{'='*50}")

    print(f"\n📌 {guild.name}")
    print(f"👥 Membres: {guild.member_count}")
    print(f"🎭 Rôles: {len(guild.roles) - 1}")

    print(f"\n📂 Catégories ({len(guild.categories)}):")
    for category in guild.categories:
        channels = [ch.name for ch in category.channels if isinstance(ch, discord.TextChannel)]
        if channels:
            print(f"  📁 {category.name}")
            for ch in channels:
                print(f"    ├─ #{ch}")

    print(f"\n✅ Serveur prêt!")

@bot.event
async def on_raw_reaction_add(payload):
    """Ajoute le rôle Membre quand quelqu'un réagit au message du règlement"""
    global RULES_MESSAGE_ID

    if not RULES_MESSAGE_ID or payload.message_id != RULES_MESSAGE_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return

    member_role = discord.utils.get(guild.roles, name=config.MEMBER_ROLE)
    if member_role:
        try:
            await member.add_roles(member_role)
            print(f"✅ Rôle 'Membre' donné à {member.name}")
        except Exception as e:
            print(f"❌ Erreur: {e}")

@bot.event
async def on_raw_reaction_add_roles(payload):
    """Gère les réactions aux rôles"""
    global ROLES_CHANNEL_ID

    if not ROLES_CHANNEL_ID or payload.channel_id != ROLES_CHANNEL_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return

    emoji_str = str(payload.emoji)

    if emoji_str in config.ROLE_EMOJIS:
        role_name = config.ROLE_EMOJIS[emoji_str]
        role = discord.utils.get(guild.roles, name=role_name)

        if role:
            try:
                await member.add_roles(role)
                print(f"✅ Rôle '{role_name}' donné à {member.name}")
            except Exception as e:
                print(f"❌ Erreur: {e}")

@bot.event
async def on_raw_reaction_remove(payload):
    """Retire le rôle quand la réaction est enlevée"""
    global ROLES_CHANNEL_ID

    if not ROLES_CHANNEL_ID or payload.channel_id != ROLES_CHANNEL_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return

    emoji_str = str(payload.emoji)

    if emoji_str in config.ROLE_EMOJIS:
        role_name = config.ROLE_EMOJIS[emoji_str]
        role = discord.utils.get(guild.roles, name=role_name)

        if role:
            try:
                await member.remove_roles(role)
                print(f"➖ Rôle '{role_name}' retiré de {member.name}")
            except Exception as e:
                print(f"❌ Erreur: {e}")

@bot.tree.command(name="live", description="Annonce que tu es en live!")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(titre="Titre du live", message="Message personnalisé")
async def live_command(interaction: discord.Interaction, titre: str = None, message: str = None):
    """Annonce un live TikTok"""

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
        name="🎥 TikTok",
        value="[tiktok.com/zetsuhi](https://tiktok.com/@zetsuhi)",
        inline=False
    )

    embed.add_field(
        name="📌 Rejoins-moi!",
        value="Clique sur le lien pour regarder le live en direct! 🔴",
        inline=False
    )

    embed.set_footer(text="Zetsu Live • En direct maintenant!")

    await interaction.response.send_message(embed=embed)
    print(f"🔴 Live annoncé par {interaction.user.name}!")

print("\n🤖 Démarrage du bot Misa...")
bot.run(TOKEN)
