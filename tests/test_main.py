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


def login_user(client, username="predikceuser", password="test1234"):
    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed = generate_password_hash(password)
        cursor.execute("INSERT IGNORE INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]
        conn.close()

    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["username"] = username

    return user_id


def test_invalid_dispozice(client):
    response = client.post("/", data={
        "metraz": 60,
        "rozloha": "6+kk",
        "energeticka": "C",
        "stav": "Po rekonstrukci",
        "lokalita": "Praha",
        "action": "predikce"
    }, follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "neplatná dispozice" in html.lower()


def test_invalid_energeticka(client):
    response = client.post("/", data={
        "metraz": 60,
        "rozloha": "2+kk",
        "energeticka": "Z",
        "stav": "Po rekonstrukci",
        "lokalita": "Praha",
        "action": "predikce"
    }, follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "neplatná energetická" in html.lower()


def test_ulozit_predikci(client):
    user_id = login_user(client)
    response = client.post("/ulozit-predikci", data={
        "metraz": 75,
        "rozloha": "3+kk",
        "energeticka": "B",
        "stav": "V dobrém stavu",
        "lokalita": "Praha",
        "cena": 7200000
    }, follow_redirects=True)
    assert response.status_code == 200

    # Ověření v DB
    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM prediction_history WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        data = cursor.fetchone()
        conn.close()

        assert data is not None
        assert data["lokalita"] == "Praha"
        assert data["rozloha"] == "3+kk"


def test_moje_predikce(client):
    user_id = login_user(client)

    # Vložíme jednu predikci napřímo
    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prediction_history (user_id, metraz, rozloha, energeticka, stav, lokalita, cena)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, 60, "2+kk", "C", "Po rekonstrukci", "Praha", 6000000))
        conn.commit()
        conn.close()

    response = client.get("/moje-predikce", follow_redirects=True)
    html = response.data.decode("utf-8")
    assert "praha" in html.lower()
    assert "2+kk" in html


def test_smazat_predikci(client):
    user_id = login_user(client)

    # Uložíme testovací predikci
    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prediction_history (user_id, metraz, rozloha, energeticka, stav, lokalita, cena)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, 80, "4+kk", "D", "Novostavba", "Praha", 8500000))
        pred_id = cursor.lastrowid
        conn.commit()
        conn.close()

    # Odešleme žádost o smazání
    response = client.get(f"/smazat-predikci/{pred_id}", follow_redirects=True)
    assert response.status_code == 200

    # Ověříme, že záznam zmizel
    with flask_app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prediction_history WHERE id = %s", (pred_id,))
        assert cursor.fetchone() is None
        conn.close()
