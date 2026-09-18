import discord
from discord.ext import commands
from discord import Intents, app_commands
import os
from dotenv import load_dotenv
import config

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
RULES_MESSAGE_ID = int(os.getenv("RULES_MESSAGE_ID"))
ROLES_CHANNEL_ID = int(os.getenv("ROLES_CHANNEL_ID"))

intents = Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    print(f"✨ Serveur: {GUILD_ID}")

    try:
        synced = await bot.tree.sync()
        print(f"✨ {len(synced)} slash commandes synchronisées!")
    except Exception as e:
        print(f"❌ Erreur sync commandes: {e}")

    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"📍 Serveur trouvé: {guild.name}")

        setup_roles(guild)
        setup_permissions(guild)

        print("✨ Configuration terminée!")

def setup_roles(guild):
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

    for role_name in roles_to_create:
        if role_name not in all_roles:
            print(f"📝 Création du rôle: {role_name}")

@bot.event
async def on_raw_reaction_add(payload):
    """Ajoute le rôle Membre quand quelqu'un réagit au message du règlement"""
    if payload.message_id != RULES_MESSAGE_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if member.bot:
        return

    member_role = discord.utils.get(guild.roles, name=config.MEMBER_ROLE)
    if member_role:
        try:
            await member.add_roles(member_role)
            print(f"✅ Rôle 'Membre' donné à {member.name}")
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout du rôle: {e}")

@bot.event
async def on_raw_reaction_add_roles(payload):
    """Gère les réactions aux rôles dans le salon #rôles"""
    if payload.channel_id != ROLES_CHANNEL_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    emoji_str = str(payload.emoji)

    if emoji_str in config.ROLE_EMOJIS:
        role_name = config.ROLE_EMOJIS[emoji_str]
        role = discord.utils.get(guild.roles, name=role_name)

        if role and not member.bot:
            try:
                await member.add_roles(role)
                print(f"✅ Rôle '{role_name}' donné à {member.name}")
            except Exception as e:
                print(f"❌ Erreur: {e}")

@bot.event
async def on_raw_reaction_remove(payload):
    """Retire le rôle quand la réaction est enlevée"""
    if payload.channel_id != ROLES_CHANNEL_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    emoji_str = str(payload.emoji)

    if emoji_str in config.ROLE_EMOJIS:
        role_name = config.ROLE_EMOJIS[emoji_str]
        role = discord.utils.get(guild.roles, name=role_name)

        if role and not member.bot:
            try:
                await member.remove_roles(role)
                print(f"➖ Rôle '{role_name}' retiré de {member.name}")
            except Exception as e:
                print(f"❌ Erreur: {e}")

def setup_permissions(guild):
    """Configure les permissions des salons admin"""
    for channel in guild.channels:
        if any(admin_name in channel.name for admin_name in config.ADMIN_CHANNELS):
            staff_role = discord.utils.get(guild.roles, name=config.STAFF_ROLE)
            everyone_role = guild.default_role

            if staff_role:
                try:
                    channel.set_permissions(everyone_role, view_channel=False)
                    channel.set_permissions(staff_role, view_channel=True)
                    print(f"🔒 Permission mise à jour pour #{channel.name}")
                except Exception as e:
                    print(f"❌ Erreur permission {channel.name}: {e}")

@bot.command(name="setup_roles_message")
@commands.has_permissions(administrator=True)
async def setup_roles_message(ctx):
    """Crée le message de sélection de rôles"""
    embed = discord.Embed(
        title="📋 Sélectionnez vos rôles",
        description="Réagissez aux emojis pour ajouter/retirer les rôles!",
        color=discord.Color.purple()
    )

    roles_text = ""
    for emoji, role_name in config.ROLE_EMOJIS.items():
        roles_text += f"{emoji} {role_name}\n"

    embed.add_field(name="Rôles disponibles", value=roles_text, inline=False)

    msg = await ctx.send(embed=embed)

    for emoji in config.ROLE_EMOJIS.keys():
        await msg.add_reaction(emoji)

    await ctx.send(f"✅ Message de rôles créé! ID: {msg.id}")

@bot.tree.command(name="live", description="Annonce que tu es en live sur TikTok!")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(titre="Titre du live (défaut: 📺 JE SUIS EN LIVE!)", message="Message personnalisé")
async def live_command(interaction: discord.Interaction, titre: str = None, message: str = None):
    """Commande slash pour annoncer un live TikTok"""

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
    embed.set_thumbnail(url="https://p16-sign.tiktokcdn.com/aweme/100x100/tos-useast2a-avt-0068-gltf-v2.jpeg?x-expires=1695998400&x-signature=test")

    await interaction.response.send_message(embed=embed)
    print(f"🔴 Live annoncé par {interaction.user.name}!")

bot.run(TOKEN)
