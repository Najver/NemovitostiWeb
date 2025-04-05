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

def test_successful_register_and_login(client):
    username = "testuser_success"
    password = "securepassword"

    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        conn.close()

    response = client.post("/register", data={
        "username": username,
        "password": password,
        "confirm_password": password
    }, follow_redirects=True)

    html = response.data.decode("utf-8")
    assert "úspěšně zaregistrován" in html.lower() or "přihlásit" in html.lower()

    response = client.post("/login", data={
        "username": username,
        "password": password
    }, follow_redirects=True)

    html = response.data.decode("utf-8")
    assert f"Přihlášen jako {username}" in html or "odhlásit" in html.lower()

def test_logout(client):
    username = "logoutuser"
    password = "logoutpass"

    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed = generate_password_hash(password)
        cursor.execute("INSERT IGNORE INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        conn.close()

    client.post("/login", data={
        "username": username,
        "password": password
    }, follow_redirects=True)

    response = client.get("/logout", follow_redirects=True)
    html = response.data.decode("utf-8")

    assert "přihlásit" in html.lower() or "registrovat" in html.lower()
