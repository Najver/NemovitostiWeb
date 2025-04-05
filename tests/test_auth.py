import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

def test_login_nonexistent_user(client):
    response = client.post("/login", data={
        "username": "neexistuje",
        "password": "neco"
    }, follow_redirects=True)
    text = response.data.decode("utf-8")
    assert "nesprávné" in text.lower() or "uživatel" in text.lower()

def test_register_short_password(client):
    response = client.post("/register", data={
        "username": "testshort",
        "password": "krátké",
        "confirm_password": "krátké"
    }, follow_redirects=True)
    text = response.data.decode("utf-8")
    assert "8 znaků" in text or "heslo" in text.lower()

def test_register_passwords_not_matching(client):
    response = client.post("/register", data={
        "username": "neshoda",
        "password": "dlouheheslo",
        "confirm_password": "jinene"
    }, follow_redirects=True)
    text = response.data.decode("utf-8")
    assert "neshodují" in text.lower()
