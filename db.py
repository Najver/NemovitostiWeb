import mysql.connector
import json
from flask import current_app

with open("config.json", "r") as f:
    config = json.load(f)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=config["db_host"],
            user=config["db_user"],
            password=config["db_password"],
            database=config["db_name"]
        )
        current_app.logger.info("[DB] Připojení k databázi úspěšné.")
        return conn
    except mysql.connector.Error as err:
        current_app.logger.exception(f"[DB] Chyba při připojení k databázi: {err}")
        raise
