"""Fabriques de donnees de test : evenements et utilisateurs isoles par execution."""
import uuid
from datetime import datetime, timedelta, timezone

from utils.api_client import ApiClient


def unique(prefix="qa"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def create_event(admin: ApiClient, status="published", early_quota=50, full_quota=200, vip_quota=3, title=None):
    """Cree un evenement dedie aux tests via l'API back-office et retourne son detail."""
    payload = {
        "title": title or f"QA Event {unique()}",
        "description": "Evenement cree par la suite de tests automatisee",
        "city": "Bruxelles",
        "venue": "Salle QA",
        "starts_at": (datetime.now(tz=datetime.utc) + timedelta(days=45)).isoformat(),
        "capacity": early_quota + full_quota + vip_quota,
        "status": status,
        "categories": [
            {"name": "Early bird", "price_cents": 2495, "quota": early_quota},
            {"name": "Plein tarif", "price_cents": 3500, "quota": full_quota},
            {"name": "VIP", "price_cents": 7500, "quota": vip_quota},
        ],
    }
    r = admin.post("/api/admin/events", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def register_user(api: ApiClient, password="Passw0rd!"):
    email = f"{unique('user')}@example.com"
    r = api.post("/api/auth/register", json={"email": email, "password": password, "full_name": "QA User"})
    assert r.status_code == 201, r.text
    return email, password


def category(event, name):
    return next(c for c in event["categories"] if c["name"] == name)
