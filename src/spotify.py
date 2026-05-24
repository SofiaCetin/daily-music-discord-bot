import random, requests, db, datetime, os, base64, urllib, uuid

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

REDIRECT_URL = os.getenv("REDIRECT_URL")
API_BASE_URL = "https://api.spotify.com/v1/"
TOKEN_URL = "https://accounts.spotify.com/api/token"
AUTH_URL = "https://accounts.spotify.com/authorize"

def link_user(user_id):
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

def check_playlist(user_id, playlist_id):
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

    data = response.json()

    if len(data) == 0 or "error" in data:
        return False
    else:
        return True

def get_random_track(user_id):
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

    data = response.json()

    total = data["total"]

    rand_i = random.randint(0, total - 1)

    response = requests.get(
        API_BASE_URL + f"playlists/{playlist}/items?limit=1&offset={rand_i}",
        headers=headers
    )

    data = response.json()

    track = data["items"][0]["item"]["external_urls"]["spotify"]

    return track

def refresh_token(user_id):
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
        return {"error": f"Spotify API error: {response.status_code}"}
    else:
        new_token_info = response.json()
        expires_at = datetime.datetime.now().timestamp() + new_token_info["expires_in"]
        access_token = new_token_info["access_token"]
        db.add_new_token(user_id,access_token,expires_at)