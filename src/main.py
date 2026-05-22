import discord, app, uuid, os, db, spotify
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot en ligne: {bot.user}')


@bot.command()
async def link(ctx):
    user_id_str = str(ctx.author.id)
    try:
        access_token = db.get_access_token(user_id_str)
        if access_token:
            await ctx.send("Ton compte Spotify est déjà lié au bot.")
        else:
            auth_URL = spotify.link_user(user_id_str)
            await ctx.author.send(f"Voici ton lien, ne le partage à personne: {auth_URL}")
            await ctx.send("Je t'ai envoyé en message privé le lien pour lier ton compte Spotify ! Le lien expire au bout de 2 minutes. Ne le partage à personne.")
    except discord.Forbidden:
        await ctx.send("Je ne peux pas t'envoyer de messages en privé. Vérifie tes paramètres de confidentialité")

@bot.command()
async def random_track(ctx, playlist_id):
    user_id_str = str(ctx.author.id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        total = spotify.get_random_track(user_id_str, playlist_id)
        await ctx.send(total)

db.db_init()
bot.run(BOT_TOKEN)