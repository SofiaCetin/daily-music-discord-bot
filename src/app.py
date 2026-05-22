import requests, os, datetime, db, urllib, base64, random
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Initialisation des variables d'environnement

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
APP_SECRET = os.getenv("APP_SECRET")
PORT = os.getenv("PORT")
PLAYLIST_ID = "6hLPlHPMv2H2KzK7lTYySD"

# Liens

REDIRECT_URI = "https://daily-music-discord-bot.up.railway.app/callback"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

# App

def create_app():
    
    app = Flask(__name__)
    app.secret_key = APP_SECRET

    db.db_init()

    @app.route('/')
    def index():
        return "Bot is online"

    @app.route("/callback")
    def callback():
        if "error" in request.args:
            return jsonify({"error": request.args["error"]})
        
        if not "state" in request.args:
            return "State error: No state found"
        
        state = request.args["state"]
        discord_id = db.check_state_exists(state)
        if not discord_id:
            return "State error: state expired or invalid"
        
        if "code" in request.args:
            req_body = {
                "code" : request.args["code"],
                "grant_type" : "authorization_code",
                "redirect_uri" : REDIRECT_URI,
                "client_id" : CLIENT_ID,
                "client_secret" : CLIENT_SECRET
            }

            response = requests.post(TOKEN_URL,data=req_body)
            token_info = response.json()
            db.add_new_refresh_token(discord_id, token_info["refresh_token"])
            db.add_new_token(discord_id, token_info["access_token"], datetime.datetime.now().timestamp() + token_info["expires_in"])
            db.delete_state(discord_id)

            return "State valid"
        else:
            return "No body"
    
    return app
        
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
    new_token_info = response.json()
    if "error" in new_token_info:
        return new_token_info
    else:
        expires_at = datetime.datetime.now().timestamp() + new_token_info["expires_in"]
        access_token = new_token_info["access_token"]
        db.add_new_token(user_id,access_token,expires_at)

def get_random_track(user_id, playlist_id):
    expiration = db.get_token_expiration(user_id)
    if expiration < datetime.datetime.now().timestamp():
        refresh_token(user_id)
    access_token = db.get_access_token(user_id)
    headers = {
        "Authorization" : f"Bearer {access_token}"
    }
    response = requests.get(API_BASE_URL + f"playlists/{playlist_id}/items", headers=headers)
    data = response.json()
    if "error" in data.keys():
        return data
    else:
        playlist_length = data["total"]
        rand_i = random.randint(0,playlist_length)
        track_link = data["items"][rand_i]["item"]["external_urls"]["spotify"]
        return track_link