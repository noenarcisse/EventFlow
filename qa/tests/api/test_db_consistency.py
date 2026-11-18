"""Controles de coherence directement en base (necessite le PostgreSQL du docker compose)."""
from datetime import datetime, timedelta, timezone

import pytest

from utils import config, db
from utils.factories import category

pytestmark = [pytest.mark.api, pytest.mark.db]


def test_paid_amount_equals_order_total(new_client_api, qa_event):
    """B7 : Early bird (24,95 EUR) + WELCOME10 -> 22,455 EUR, l'arrondi doit etre le meme partout."""
    early = category(qa_event, "Early bird")
    order = new_client_api.create_order(
        qa_event["id"], [{"category_id": early["id"], "quantity": 1}], promo_code="WELCOME10"
    ).json()
    new_client_api.pay(order["id"], config.CARD_OK)

    row = db.order_payment(order["id"])
    assert row is not None, "Aucun paiement enregistre"
    assert row["amount_cents"] == row["total_cents"], f"Ecart d'arrondi (B7) : {row}"


def test_expired_reservation_releases_stock(new_client_api, anonymous_api, qa_event):
    """RM2 / B5 : une reservation expiree ne bloque plus le stock.

    Plutot que d'attendre 10 minutes, on fait vieillir la commande directement en base.
    """
    early = category(qa_event, "Early bird")

    def available():
        return category(anonymous_api.get(f"/api/events/{qa_event['id']}").json(), "Early bird")["available"]

    initial = available()
    order = new_client_api.create_order(qa_event["id"], [{"category_id": early["id"], "quantity": 3}]).json()
    assert available() == initial - 3

    db.execute(
        "UPDATE orders SET expires_at = :past WHERE id = :id",
        past=datetime.now(tz=timezone.utc) - timedelta(minutes=1), id=order["id"],
    )

    assert available() == initial, "Le stock n'est pas libere apres expiration (B5)"
    assert new_client_api.get(f"/api/orders/{order['id']}").json()["status"] == "expired"


def test_no_category_is_oversold():
    """RM1 : aucune categorie ne doit avoir plus de billets payes que son quota."""
    oversold = db.fetch_all("""
        SELECT c.id, c.name, c.quota, SUM(i.quantity) AS sold
        FROM ticket_categories c
        JOIN order_items i ON i.category_id = c.id
        JOIN orders o ON o.id = i.order_id AND o.status = 'paid'
        GROUP BY c.id, c.name, c.quota
        HAVING SUM(i.quantity) > c.quota
    """)
    assert oversold == []


def test_no_paid_order_without_payment():
    orphans = db.fetch_all("""
        SELECT o.id FROM orders o
        LEFT JOIN payments p ON p.order_id = o.id
        WHERE o.status = 'paid' AND p.id IS NULL
    """)
    assert orphans == []
