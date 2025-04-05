import pytest
from app import app as flask_app
from db import get_db_connection
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.secret_key = "testsecret"
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

def login_test_user(client):
    username = "hypotest"
    password = "securetest123"

    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO users (username, password_hash) VALUES (%s, %s)",
                       (username, generate_password_hash(password)))
        conn.commit()
        conn.close()

    client.post("/login", data={"username": username, "password": password}, follow_redirects=True)

def test_negative_uver(client):
    login_test_user(client)
    response = client.post("/hypoteka", data={
        "uver": -500000,
        "urok": 5.5,
        "mesice": 120,
        "fixace": "5"
    }, follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "výše úvěru nemůže být záporná" in html.lower()

def test_negative_urok(client):
    login_test_user(client)
    response = client.post("/hypoteka", data={
        "uver": 1000000,
        "urok": -2,
        "mesice": 120,
        "fixace": "5"
    }, follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "úroková sazba" in html.lower()

def test_negative_mesice(client):
    login_test_user(client)
    response = client.post("/hypoteka", data={
        "uver": 1000000,
        "urok": 5,
        "mesice": -20,
        "fixace": "5"
    }, follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "doba splácení" in html.lower()

def test_fixace_vs_mesice(client):
    login_test_user(client)
    response = client.post("/hypoteka", data={
        "uver": 1000000,
        "urok": 5,
        "mesice": 60,  # 5 let
        "fixace": "10"  # 10 let
    }, follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "fixaci" in html.lower() or "musí být doba splácení" in html.lower()

def test_vlastni_vice_nez_cena(client):
    login_test_user(client)
    response = client.post("/hypoteka?cena=2000000", data={
        "vlastni": 2500000,
        "urok": 5,
        "mesice": 120,
        "fixace": "5"
    }, follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "nemusíte si brát hypotéku" in html.lower()
