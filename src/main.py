import discord, os, db, spotify
from datetime import time
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_TO_SEND_DAILY = os.getenv("CHANNEL_ID")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents=intents)


async def daily_track():
    channel = bot.get_channel(CHANNEL_TO_SEND_DAILY)
    random_user = db.select_random_w_playlist()
    if random_user:
        random_user_id = random_user[0]
        random_track = spotify.get_random_track(random_user_id)
        await channel.send(f"Le son du jour vient de la playlist de <@{random_user_id}> ! Le son choisi est: \n {random_track}")
    return None


@tasks.loop(time=time(hour=5, minute=25))
async def check_scheduled_time():
    await daily_track()


@bot.event
async def on_ready():
    check_scheduled_time.start()
    db.db_init()
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
async def register_playlist(ctx, playlist_id):
    user_id_str = str(ctx.author.id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        if db.check_if_playlist(user_id_str):
            await ctx.send("Tu as déjà enregistré une playlist. Si tu veux la changer, fais la commande !change_playlist <PLAYLIST_ID>")
        else:
            if spotify.check_playlist(user_id_str, playlist_id):
                db.save_playlist(user_id_str, playlist_id)
                await ctx.send("Ta playlist a bien été enregistrée")
            else:
                await ctx.send("Requête API invalide. Tu dois mettre une playlist qui t'appartient.")
    else:
        await ctx.send("Token inaccessible. Assure-toi que tu as bien lié ton compte Spotify au bot avec la commande !link")


@bot.command()
async def change_playlist(ctx, playlist_id):
    user_id_str = str(ctx.author.id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        if spotify.check_playlist(user_id_str, playlist_id):
            db.replace_playlist(user_id_str, playlist_id)
            await ctx.send("Le changement de playlist a bien été pris en compte.")
        else:
            await ctx.send("Requête API invalide. Tu dois mettre une playlist qui t'appartient.")
    else:
        await ctx.send("Token inaccessible. Assure-toi que tu as bien lié ton compte Spotify au bot avec la commande !link")


@bot.command()
async def my_playlist_info(ctx):
    user_id_str = str(ctx.author.id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        playlist = db.check_if_playlist(user_id_str)
        if playlist:
            await ctx.send(f"L'ID de ta playlist enregistrée est {playlist}")
        else:
            await ctx.send("Aucune playlist enregistrée.")


@bot.command()
async def remove_playlist(ctx):
    user_id_str = str(ctx.author.id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        if db.check_if_playlist(user_id_str):
            db.clear_playlist(user_id_str)
            await ctx.send("Ta playlist a bien été supprimée.")
        else:
            await ctx.send("Aucune playlist enregistrée.")

 
@bot.command()
async def random_track(ctx):
    user_id_str = str(ctx.author.id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        track = spotify.get_random_track(user_id_str)
        if not track:
            await ctx.send("Aucune playlist enregistrée.")
        else:
            await ctx.send(track)
    else:
        await ctx.send("Token inaccessible. Assure-toi que tu as bien lié ton compte Spotify au bot avec la commande !link")


bot.run(BOT_TOKEN)