"""Petit client HTTP pour l'API EventFlow."""
import requests
from constants import TIMEOUT

from utils.config import API_URL


class ApiClient:
    def __init__(self, base_url=API_URL, token=None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = False  # certificat auto-signe sur l'env de recette
        if token:
            self.set_token(token)

    def set_token(self, token):
        self.session.headers["Authorization"] = f"Bearer {token}"

    def login(self, email, password):
        r = requests.post(
            f"{self.base_url}/api/auth/token",
            data={"username": email, "password": password},
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            self.set_token(r.json()["access_token"])
        return r

    def get(self, path, **kwargs):
        return self.session.get(self.base_url + path, **kwargs)

    def post(self, path, **kwargs):
        return self.session.post(self.base_url + path, **kwargs)

    def put(self, path, **kwargs):
        return self.session.put(self.base_url + path, **kwargs)

    def patch(self, path, **kwargs):
        return self.session.patch(self.base_url + path, **kwargs)

    # --- raccourcis metier -------------------------------------------------
    def create_order(self, event_id, items, promo_code=None):
        payload = {"event_id": event_id, "items": items}
        if promo_code:
            payload["promo_code"] = promo_code
        return self.post("/api/orders", json=payload)

    def pay(self, order_id, card_number):
        return self.post(f"/api/orders/{order_id}/pay", json={
            "card_number": card_number,
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "cardholder": "QA Bot",
        })
