import random, requests, datetime, os, base64, urllib, uuid, db

# Variables d'environnement

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")

# Liens Spotify

API_BASE_URL = "https://api.spotify.com/v1/"
TOKEN_URL = "https://accounts.spotify.com/api/token"
AUTH_URL = "https://accounts.spotify.com/authorize"

def link_user(user_id):
    """

    Retourne un lien Spotify pour permettre à l'utilisateur de donner les permissions au bot.

    Args:
        user_id (string): L'ID Discord de l'utilisateur

    Returns:
        auth_URL(string): L'URL de liaison encodée avec sa propre id(state) et les paramètres que Spotify demande(params).
    """

    state = str(uuid.uuid4())
    scope = 'user-read-private user-library-read playlist-read-private playlist-read-collaborative'
    params = {
        "client_id" : CLIENT_ID,
        "response_type" : "code",
        "scope" : scope,
        "redirect_uri" : REDIRECT_URL,
        "state" : state
        }
    auth_URL = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    db.save_state(user_id,state)
    return auth_URL

# Requêtes

def request_token(code, discord_id):
    req_body = {
        "code" : code,
        "grant_type" : "authorization_code",
        "redirect_uri" : REDIRECT_URL,
        "client_id" : CLIENT_ID,
        "client_secret" : CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL,data=req_body)
    
    if response.status_code != 200:
        print(f"ERREUR\nStatus code: {response.status_code}\nDescription: {response.text}")
        return None
    
    token_info = response.json()
    if len(token_info) == 0 or "error" in token_info:
        return "Connection error"
    
    db.add_new_refresh_token(discord_id, token_info["refresh_token"])
    db.add_new_token(discord_id, token_info["access_token"], datetime.datetime.now().timestamp() + token_info["expires_in"])
    db.delete_state(discord_id)
    
    return "State Valid"

def check_playlist(user_id, playlist_id):
    """

    Vérifie si l'utilisateur possède bien les droits sur cette playlist(créateur ou collaborateur).


    Args:
        user_id (string): ID discord
        playlist_id (string): ID de la playlist

    Returns:
        True(bool): si il n'y a pas d'erreur dans le JSON obtenu(l'utilisateur a les droits)
        False(bool): si le JSON est vide ou contient des erreurs(l'utilisateur n'a pas les droits/l'API est inaccessible)
    """

    expiration = db.get_token_expiration(user_id)
    if expiration < datetime.datetime.now().timestamp():
        refresh_token(user_id)
    
    access_token = db.get_access_token(user_id)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        API_BASE_URL + f"playlists/{playlist_id}/items?limit=1",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"ERREUR\nStatus code: {response.status_code}\nDescription: {response.text}")
        return None

    data = response.json()

    if len(data) == 0 or "error" in data:
        return False
    else:
        return True

def get_random_track(user_id):
    """

    Permet d'obtenir un titre aléatoire de la playlist enregistrée par l'utilisateur spécifié.

    Args:
        user_id (string): L'ID Discord

    Returns:
        None(null): si aucune playlist n'a été enregistrée ou que l'API est inaccessible
        track(string): le lien Spotify du titre choisi aléatoirement
    """

    playlist = db.check_if_playlist(user_id)
    if not playlist:
        return None
    
    expiration = db.get_token_expiration(user_id)
    if expiration < datetime.datetime.now().timestamp():
        refresh_token(user_id)
    
    access_token = db.get_access_token(user_id)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        API_BASE_URL + f"playlists/{playlist}/items?limit=1",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"ERREUR\nStatus code: {response.status_code}\nDescription: {response.text}")
        return None

    data = response.json()
    if len(data) == 0 or "error" in data:
        return None

    total = data["total"]
    rand_i = random.randint(0, total - 1)

    response = requests.get(
        API_BASE_URL + f"playlists/{playlist}/items?limit=1&offset={rand_i}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"ERREUR\nStatus code: {response.status_code}\nDescription: {response.text}")
        return None

    data = response.json()
    
    if len(data) == 0 or "error" in data:
        return None

    track = data["items"][0]["item"]["external_urls"]["spotify"]

    return track

def refresh_token(user_id):
    """

    Permet d'actualiser le token de l'utilisateur, surtout dans le cas où le token actuel a expiré.

    Args:
        user_id (string): L'ID Discord.

    Returns:
        json: JSON contenant le code d'erreur, si la réponse n'est pas correcte.
        -: Modifie directement la base de données si tout va bien.
    """

    refresh_token = db.get_refresh_token(user_id)
    req_body = {
        "grant_type" : "refresh_token",
        "refresh_token" : refresh_token,

    }

    encoded_client_id = CLIENT_ID.encode()
    encoded_client_secret = CLIENT_SECRET.encode()
    data = base64.b64encode(encoded_client_id + b':' + encoded_client_secret)
    headers = {
        "Content-Type" : "application/x-www-form-urlencoded",
        "Authorization" : "Basic " + data.decode()
    }

    response = requests.post(TOKEN_URL, data=req_body, headers=headers)
    
    if response.status_code != 200:
        print(f"ERREUR\nStatus code: {response.status_code}\nDescription: {response.text}")
        return None
    
    new_token_info = response.json()
    expires_at = datetime.datetime.now().timestamp() + new_token_info["expires_in"]
    access_token = new_token_info["access_token"]
    db.add_new_token(user_id,access_token,expires_at)