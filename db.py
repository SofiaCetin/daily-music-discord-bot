import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def connect():
    return psycopg2.connect(DATABASE_URL)

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

def save_state(discord_id,state):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO linked_users (discord_id, state)
        VALUES (%s, %s)
        ON CONFLICT(discord_id) DO UPDATE SET state = excluded.state
    """, (discord_id, state))

    conn.commit()
    cur.close()
    conn.close()

def check_user_state(discord_id,state):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT state 
        FROM linked_users 
        WHERE discord_id = %s
    """, (discord_id,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    if res[0] == state:
        return True
    else:
        return False

def check_state_exists(state):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT discord_id
        FROM linked_users
        WHERE state = %s
    """, (state,))
    ligne = cur.fetchone()
    cur.close()
    conn.close()
    if ligne:
        discord_id = ligne[0]
        print(f"Le state existe pour l'ID discord {discord_id}")
        return discord_id
    else:
        print("Le state n'existe pas")
        return None

def get_state_expiration(state):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT state_expiration
        FROM linked_users
        WHERE state = %s
""", (state, ))
    cur.close()
    conn.close()
    
def get_refresh_token(discord_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT refresh_token 
        FROM linked_users 
        WHERE discord_id = %s
    """,(discord_id,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    if res:
        return res[0]
    else:
        return None

def get_access_token(discord_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT access_token
        FROM linked_users
        WHERE discord_id = %s
    """, (discord_id,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    if res:
        return res[0]
    else:
        return None
    
def add_new_refresh_token(discord_id, refresh_token):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        UPDATE linked_users
        SET refresh_token = %s
        WHERE state = %s
""",(refresh_token, discord_id))
    conn.commit()
    cur.close()
    conn.close()
    
    
def add_new_token(discord_id, access_token, expires_at):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        UPDATE linked_users
        SET access_token = %s, expires_at = %s
        WHERE state = %s          
    """, (access_token ,expires_at ,discord_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_state(discord_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        UPDATE linked_users
        SET state = NULL
        WHERE discord_id = %s
""", (discord_id, ))
    conn.commit()
    cur.close()
    conn.close()