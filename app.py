from flask import Flask
import json
import logging
from logging.handlers import RotatingFileHandler
from tensorflow.keras.models import load_model
import pickle

from routes.main import main_routes
from routes.hypoteka import hypoteka_routes
from routes.auth import auth_routes

# nacteni konfigu
with open("config.json", "r") as f:
    config = json.load(f)

# inicializce applikace
app = Flask(__name__)
app.secret_key = config.get("secret_key", "tajny_klic")

# inicializace loggeru
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
log_file = config.get("logger_file_path")

file_handler = RotatingFileHandler(
    log_file,
    maxBytes=1_000_000,
    backupCount=3,
    encoding='utf-8'
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# nacteni modelu
try:
    app.model = load_model(config["model_path"])
    with open(config["scaler_path"], "rb") as f:
        app.scaler = pickle.load(f)
    with open(config["location_mapping_path"], "rb") as f:
        app.location_mapping = pickle.load(f)
    with open(config["energy_mapping_path"], "rb") as f:
        app.energy_mapping = pickle.load(f)
    with open(config["condition_mapping_path"], "rb") as f:
        app.condition_mapping = pickle.load(f)

    app.logger.info("Model a konfigurace úspěšně načteny.")
except Exception as e:
    app.logger.exception("Chyba při načítání modelu nebo konfigurace:")
    raise

# routy
app.register_blueprint(main_routes)
app.register_blueprint(hypoteka_routes)
app.register_blueprint(auth_routes)

if __name__ == "__main__":
    app.run(
        host=config.get("host", "127.0.0.1"),
        port=config.get("port", 5000),
        debug=config.get("debug", False)
    )
