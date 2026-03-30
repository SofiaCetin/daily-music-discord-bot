import discord
import app
import uuid
from discord.ext import commands
from threading import Thread

BOT_TOKEN = app.os.environ.get("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command()
async def link(ctx):
    user_id = await bot.fetch_user(ctx.author.id)
    try:
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
        app.db.save_state(ctx.author.id,state)
        await user_id.send(f"Voici ton lien, ne le partage à personne: {auth_URL}")
        await ctx.send("Je t'ai envoyé en message privé le lien pour lier ton compte Spotify ! Le lien expire au bout de 2 minutes. Ne le partage à personne.")
    except discord.Forbidden:
        await ctx.send("Je ne peux pas t'envoyer de messages en privé. Vérifie tes paramètres de confidentialité")


bot.run(BOT_TOKEN)