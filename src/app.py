import requests, os, datetime, db
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Initialisation des variables d'environnement

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
APP_SECRET = os.getenv("APP_SECRET")
PORT = os.getenv("PORT")

# Liens

REDIRECT_URL = os.getenv("REDIRECT_URL")
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

app = Flask(__name__)
app.secret_key = APP_SECRET

db.db_init()

# Routes
    
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
            "redirect_uri" : REDIRECT_URL,
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