import discord, os, db, spotify
from datetime import datetime
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_TO_SEND_DAILY = os.getenv("CHANNEL_ID")
TIME_ZONE = ZoneInfo("Europe/Paris")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents=intents)
time = { "h" : 10, "m" : 0 }
previous_roll_id = None


async def daily_track():
    """

    Retourne le titre aléatoire de la playlist d'un utilisateur aléatoire.

    Returns:
        string: Message contenant le titre et l'utilisateur choisi aléatoirement, dans le canal désigné, ou message "aucune playlist enregistrée".
    """

    global previous_roll_id

    channel = bot.get_channel(int(CHANNEL_TO_SEND_DAILY))

    if db.nb_with_playlist() > 1:
        random_user_id = db.select_random_w_playlist()
        while random_user_id == previous_roll_id:
            random_user_id = db.select_random_w_playlist()
        random_track = spotify.get_random_track(random_user_id)
        previous_roll_id = random_user_id
        await channel.send(f"Le son du jour vient de la playlist de <@{random_user_id}> ! Le son choisi est: \n {random_track}")

    elif db.nb_with_playlist() == 1:
        random_user_id = db.select_random_w_playlist()
        random_track = spotify.get_random_track(random_user_id)
        previous_roll_id = random_user_id
        await channel.send(f"Le son du jour vient de la playlist de <@{random_user_id}> ! Le son choisi est: \n {random_track}. (Seul utilisateur enregistré.)")
    
    else:
        await channel.send(f"Aucune playlist trouvée pour le son du jour.")


@tasks.loop(minutes=1)
async def check_scheduled_time():
    """

    Boucle en arrière plan pour vérifier l'heure actuelle et exécuter
    daily_track() si l'heure est égale a l'heure enregistrée.

    """
    now = datetime.now(TIME_ZONE)
    if now.hour == time["h"] and now.minute == time["m"]:
        await daily_track()


async def setup_hook():
    """

    Fonction de démarrage du bot

    """
    channel = await bot.fetch_channel(int(CHANNEL_TO_SEND_DAILY))

    check_scheduled_time.start()
    db.db_init()
    print(f'Bot en ligne: {bot.user}')
    if channel:
        await channel.send("Bot en ligne. Le message du jour s'enverra ici.")


@bot.command()
async def link(ctx):
    """

    Envoie un lien Spotify de liaison à l'utilisateur qui a exécuté la commande.
    Utilisation: !link

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.
    
    Returns:
        message(string): message dans le canal en fonction de la réponse.
    
    """
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
async def unlink(ctx):
    """
    
    Retire l'utilisateur et toutes ses informations(tokens et ID de playlist) de la base de données.

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.
    
    """
    user_id_str = str(ctx.author.id)
    access_token = db.get_access_token(user_id_str)
    if access_token:
        db.remove_user(user_id_str)
        await ctx.send("Tes informations ont bien été supprimées de la base de données. Si tu voudras à nouveau pouvoir sauvegarder ta playlist, tu devras refaire la commande !link.")
    else:
        await ctx.send("Aucune donnée n'a été trouvée pour ton compte.")

@bot.command()
async def register_playlist(ctx, playlist_id):
    """

    Enregistre la playlist spécifiée dans la base de données.
    Utilisation: !register_playlist PLAYLIST_ID

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.
        playlist_id (string): L'ID de la playlist
    
    """
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
    """

    Change notre playlist enregistrée dans la base de données.
    Utilisation: !change_playlist PLAYLIST_ID

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.
        playlist_id (string): L'ID de la playlist

    """
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
    """

    Obtenir les informations de la playlist qu'on a enregistrée.
    Utilisation: !my_playlist_info

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.

    """
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
    """

    Enlever sa playlist de la base de données.
    Utilisation: !remove_playlist

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.
    """
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
    """

    Obtenir un titre aléatoire de la playlist qu'on a enregistrée.
    Utilisation: !random_track

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.

    """
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
        
@bot.command()
@has_permissions(administrator=True)
async def change_time(ctx, hours, minutes):
    """

    Permet de changer l'heure et la minute à laquelle le bot va envoyer le message journalier.

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.
        hours (string): L'heure en nombres
        minutes (string): Les minutes en nombres

    """
    try:
        hours = int(hours)
        minutes = int(minutes)
    except ValueError:
        await ctx.send("Le format spécifié est incorrect.")
    
    if 0 <= hours <= 24 and 0 <= minutes < 60:
            time["h"] = hours
            time["m"] = minutes
            await ctx.send(f"L'heure du message journalier a été modifiée. Désormais, le message se génèrera à {time['h']} heure(s) et {time['m']} minute(s).")
    else:
        await ctx.send("Le format spécifié est incorrect.")

@bot.command()
async def get_time(ctx):
    """

    Obtenir le temps enregistré pour le message journalier.

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.
    """
    await ctx.send(f"Le message du jour s'envoie à {time['h']} heure(s) et {time['m']} minute(s) -> Fuseau horaire: {TIME_ZONE}.")
    
@bot.command()
@has_permissions(administrator=True)
async def force_daily(ctx):
    """

    Commande administrateur pour forcer le message quotidien.

    """
    global previous_roll_id
    
    await ctx.send(f"[DEBUG USAGE]\n \nPrevious user: {previous_roll_id} \n Total users registered with playlists: {db.nb_with_playlist()} \n Daily message try(in the channel specified) ")
    await daily_track()

@force_daily.error
async def force_daily_error(ctx, error):
    """

    Vérifications des permissions de l'utilisateur qui effectue la commande du message quotidien.

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.
        error (): erreur lorsque l'utilisateur n'est pas administrateur.
    """
    if isinstance(error, CheckFailure):  
        await ctx.send("Tu n'as pas les permissions pour faire cela")


@change_time.error
async def change_time_error(ctx, error):
    """

    Vérifications des permissions de l'utilisateur qui effectue la commande de changement d'heure.

    Args:
        ctx (contexte): informations pour indiquer quel utilisateur a exécuté la commande et dans quel canal.
        error (): erreur lorsque l'utilisateur n'est pas administrateur.
    """
    if isinstance(error, CheckFailure):  
        await ctx.send("Tu n'as pas les permissions pour faire cela")


bot.setup_hook = setup_hook
bot.run(BOT_TOKEN)