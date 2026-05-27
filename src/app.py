import os, db, spotify
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Initialisation des variables d'environnement

load_dotenv()

APP_SECRET = os.getenv("APP_SECRET")
PORT = os.getenv("PORT")

# Liens

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
    if not state or not discord_id:
        return "State error: state expired or invalid"
        
    if "code" in request.args:
        return spotify.request_token(request.args["code"], discord_id)
    
    return "No body"