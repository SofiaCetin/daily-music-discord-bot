import requests, os, datetime, db, urllib
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from threading import Thread

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
APP_SECRET = os.getenv("APP_SECRET")
PLAYLIST_ID = "6hLPlHPMv2H2KzK7lTYySD"
PORT = os.getenv("PORT")

REDIRECT_URI = "http://127.0.0.1:5000/callback"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

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
        db.add_new_refresh_token(state, token_info["refresh_token"])
        db.add_new_token(state, token_info["access_token"], datetime.now().timestamp() + token_info["expires_in"])
        db.delete_state(state)

        db.conn.commit()

        return "State valid"

def run():
    app.run(host="0.0.0.0", port=PORT)

def keep_alive():
    t = Thread(target=run)
    t.start