import pytest

from utils import config
from utils.factories import unique

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_health(anonymous_api):
    r = anonymous_api.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.smoke
def test_login_with_valid_credentials_returns_bearer_token(anonymous_api):
    r = anonymous_api.login(config.CLIENT_EMAIL, config.CLIENT_PASSWORD)
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2  # format JWT header.payload.signature


@pytest.mark.parametrize("email, password", [
    (config.CLIENT_EMAIL, "mauvais-mot-de-passe"),
    ("inconnu@eventflow.test", "client1234"),
    (config.CLIENT_EMAIL, ""),
])
def test_login_with_invalid_credentials_is_rejected(anonymous_api, email, password):
    r = anonymous_api.login(email, password)
    assert r.status_code in (401, 422)


def test_register_then_duplicate_email_is_rejected(anonymous_api):
    email = f"{unique('reg')}@example.com"
    first = anonymous_api.post("/api/auth/register", json={"email": email, "password": "Passw0rd!"})
    assert first.status_code == 201
    assert first.json()["role"] == "client"

    second = anonymous_api.post("/api/auth/register", json={"email": email, "password": "Passw0rd!"})
    assert second.status_code == 409


def test_me_requires_authentication(anonymous_api):
    assert anonymous_api.get("/api/auth/me").status_code == 401


def test_me_returns_current_user(client_api):
    r = client_api.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == config.CLIENT_EMAIL


def test_profile_update_cannot_change_email_or_role(new_client_api):
    before = new_client_api.get("/api/auth/me").json()
    r = new_client_api.patch("/api/auth/me", json={"full_name": "Nouveau Nom", "email": "pirate@x.test", "role": "admin"})
    assert r.status_code == 200
    after = r.json()
    assert after["full_name"] == "Nouveau Nom"
    assert after["email"] == before["email"]
    assert after["role"] == "client"
