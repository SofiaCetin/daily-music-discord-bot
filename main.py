import discord, app, uuid, os, db, json
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command()
async def link(ctx):
    user_id = await bot.fetch_user(ctx.author.id)
    user_id_str = str(user_id)
    try:
        access_token = db.get_access_token(user_id_str)
        if access_token:
            await ctx.send("Ton compte Spotify est déjà lié au bot.")
        else:
            state = str(uuid.uuid4())
            scope = 'user-read-private user-library-read playlist-read-private playlist-read-collaborative'
            params = {
                "client_id" : app.CLIENT_ID,
                "response_type" : "code",
                "scope" : scope,
                "redirect_uri" : app.REDIRECT_URI,
                "state" : state
            }
            auth_URL = f"{app.AUTH_URL}?{app.urllib.parse.urlencode(params)}"
            db.save_state(user_id_str,state)
            await user_id.send(f"Voici ton lien, ne le partage à personne: {auth_URL}")
            await ctx.send("Je t'ai envoyé en message privé le lien pour lier ton compte Spotify ! Le lien expire au bout de 2 minutes. Ne le partage à personne.")
    except discord.Forbidden:
        await ctx.send("Je ne peux pas t'envoyer de messages en privé. Vérifie tes paramètres de confidentialité")

@bot.command()
async def register_playlist(ctx, playlist_id):
    user_id = await bot.fetch_user(ctx.author.id)
    user_id_str = str(user_id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        playlist = app.get_random_track(user_id_str, playlist_id)
        if "error" in playlist.keys():
            await ctx.send(playlist)
        else:
            playlist_length = int(playlist["total"])
            indice = playlist_length
            if playlist_length > 20:
                indice = 20
            random_item = app.random.randint(0,indice - 1)
            await ctx.send(playlist["items"][random_item]["item"]["name"])
    else:
        await ctx.send("Ton compte Spotify n'est pas lié au bot. Tape la commande !link pour le lier.")

@bot.command()
async def send_json(ctx, playlist_id):
    user_id = await bot.fetch_user(ctx.author.id)
    user_id_str = str(user_id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        json_data = app.get_random_track(user_id_str, playlist_id)
        with open("data.json", 'w',encoding="utf-8") as file:
            json.dump(json_data, file, ensure_ascii=False, indent=4)
        await ctx.send(file=discord.File("data.json"))

@bot.command()
async def playlist_length(ctx, playlist_id):
    user_id = await bot.fetch_user(ctx.author.id)
    user_id_str = str(user_id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        total = app.get_random_track(user_id_str, playlist_id)
        await ctx.send(total["total"])
                  
app.keep_alive()
bot.run(BOT_TOKEN)