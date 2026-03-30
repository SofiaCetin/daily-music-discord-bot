import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def connect():
    return psycopg.connect(DATABASE_URL)

def db_init():

    conn = connect()

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS linked_users(
        discord_id TEXT PRIMARY KEY,
        state TEXT,
        access_token TEXT,
        refresh_token TEXT,
        expires_at BIGINT
        )     
    """)

    conn.commit()
    cur.close()
    conn.close()

conn = connect()

cur = conn.cursor()

def save_state(discord_id,state):
    cur.execute("""
        INSERT INTO linked_users (discord_id, state)
        VALUES (%s, %s)
        ON CONFLICT(discord_id) DO UPDATE SET state = excluded.state
    """, (discord_id, state))

def check_user_state(discord_id,state):
    cur.execute("""
        SELECT state 
        FROM linked_users 
        WHERE discord_id = %s
    """, (discord_id,))
    res = cur.fetchone()
    if res[0] == state:
        return True
    else:
        return False

def check_state_exists(state):
    cur.execute("""
        SELECT discord_id
        FROM linked_users
        WHERE state = %s
    """, (state,))
    ligne = cur.fetchone()
    if ligne:
        discord_id = ligne[0]
        print(f"Le state existe pour l'ID discord {discord_id}")
        return discord_id
    else:
        print("Le state n'existe pas")
        return None

def get_state_expiration(state):
    cur.execute("""
        SELECT state_expiration
        FROM linked_users
        WHERE state = %s
""", (state, ))
    
def get_refresh_token(discord_id):
    cur.execute("""
        SELECT refresh_token 
        FROM linked_users 
        WHERE discord_id = %s
    """,(discord_id,))
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        return None

def get_access_token(discord_id):
    cur.execute("""
        SELECT access_token
        FROM linked_users
        WHERE discord_id = %s
    """, (discord_id,))
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        return None
    
def add_new_refresh_token(state, refresh_token):
    cur.execute("""
        UPDATE linked_users
        SET refresh_token = %s
        WHERE state = %s
""",(refresh_token, state))
    
def add_new_token(state, access_token, expires_at):
    cur.execute("""
        UPDATE linked_users
        SET access_token = %s, expires_at = %s
        WHERE state = %s          
    """, (access_token ,expires_at ,state))

def delete_state(state):
    cur.execute("""
        UPDATE linked_users
        SET state = NULL
        WHERE state = %s
""", (state, ))