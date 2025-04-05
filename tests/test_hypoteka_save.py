import pytest
from app import app as flask_app
from db import get_db_connection
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

def create_test_user(username="hypotekauser", password="hypoteka123"):
    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed = generate_password_hash(password)
        cursor.execute("INSERT IGNORE INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]
        conn.close()
        return user_id

def test_hypoteka_saved(client):
    username = "hypotekauser"
    password = "hypoteka123"
    user_id = create_test_user(username, password)

    client.post("/login", data={
        "username": username,
        "password": password
    }, follow_redirects=True)

    response = client.post("/hypoteka", data={
        "uver": 1500000,
        "urok": 5.5,
        "mesice": 120,
        "fixace": "5"
    }, follow_redirects=True)

    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM hypoteka_history WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        zaznam = cursor.fetchone()
        conn.close()

        assert zaznam is not None
        assert zaznam["mesice"] == 120
        assert round(float(zaznam["sazba"]), 1) == 5.5
