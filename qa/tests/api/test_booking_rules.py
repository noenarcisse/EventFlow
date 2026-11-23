"""Regles metier du tunnel de reservation (RM1, RM3, RM4) - tests pilotes par les donnees."""
import pytest

from utils.config import CARD_DECLINED, CARD_OK
from utils.data_loader import load_csv, load_json
from utils.factories import category
from utils.schema import schema_errors

pytestmark = pytest.mark.api

RM3_CASES = load_csv("rm3_quantites.csv")
PROMO_CASES = load_json("codes_promo.json")


@pytest.mark.parametrize("case", RM3_CASES, ids=[c["cas"] for c in RM3_CASES])
def test_rm3_max_six_tickets_per_order(new_client_api, qa_event, case):
    plein = category(qa_event, "Plein tarif")
    r = new_client_api.create_order(qa_event["id"], [{"category_id": plein["id"], "quantity": int(case["quantite"])}])
    assert r.status_code == int(case["statut_attendu"]), f"{case['commentaire']} -> {r.status_code} {r.text}"


@pytest.mark.parametrize("promo", PROMO_CASES, ids=[p["code"] for p in PROMO_CASES])
def test_rm4_promo_codes(new_client_api, qa_event, promo):
    plein = category(qa_event, "Plein tarif")
    r = new_client_api.create_order(qa_event["id"], [{"category_id": plein["id"], "quantity": 2}], promo_code=promo["code"])
    assert r.status_code == promo["statut_attendu"], r.text
    if promo["remise_pct"] is not None:
        expected = round(2 * plein["price_cents"] * (100 - promo["remise_pct"]) / 100)
        assert r.json()["total_cents"] == expected


def test_rm1_cannot_order_more_than_available_stock(new_client_api, anonymous_api, qa_event):
    detail = anonymous_api.get(f"/api/events/{qa_event['id']}").json()
    vip = category(detail, "VIP")
    # breakpoint()
    ret = new_client_api.create_order(qa_event["id"], [{"category_id": vip["id"], "quantity": vip["available"] + 1}])
    # breakpoint()
    assert ret.status_code == 409, f"Sur-reservation acceptee (B1) : {ret.text}"


def test_pending_order_reserves_stock(new_client_api, anonymous_api, qa_event):
    early = category(qa_event, "Early bird")
    before = category(anonymous_api.get(f"/api/events/{qa_event['id']}").json(), "Early bird")["available"]
    r = new_client_api.create_order(qa_event["id"], [{"category_id": early["id"], "quantity": 2}])
    assert r.status_code == 201
    after = category(anonymous_api.get(f"/api/events/{qa_event['id']}").json(), "Early bird")["available"]
    assert after == before - 2


def test_order_response_matches_schema(new_client_api, qa_event):
    plein = category(qa_event, "Plein tarif")
    r = new_client_api.create_order(qa_event["id"], [{"category_id": plein["id"], "quantity": 1}])
    assert r.status_code == 201
    assert schema_errors(r.json(), "order.schema.json") == []
    assert r.json()["status"] == "pending"


def test_category_from_another_event_is_rejected(new_client_api, anonymous_api, qa_event):
    other_event = anonymous_api.get("/api/events").json()[0]
    other_cat = anonymous_api.get(f"/api/events/{other_event['id']}").json()["categories"][0]
    r = new_client_api.create_order(qa_event["id"], [{"category_id": other_cat["id"], "quantity": 1}])
    assert r.status_code == 400


def test_full_booking_flow_pays_order(new_client_api, qa_event):
    plein = category(qa_event, "Plein tarif")
    order = new_client_api.create_order(qa_event["id"], [{"category_id": plein["id"], "quantity": 2}]).json()

    paid = new_client_api.pay(order["id"], CARD_OK)
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"

    mine = new_client_api.get("/api/orders/me").json()
    assert [o["status"] for o in mine if o["id"] == order["id"]] == ["paid"]


def test_declined_card_keeps_order_pending(new_client_api, qa_event):
    plein = category(qa_event, "Plein tarif")
    order = new_client_api.create_order(qa_event["id"], [{"category_id": plein["id"], "quantity": 1}]).json()

    r = new_client_api.pay(order["id"], CARD_DECLINED)
    assert r.status_code == 402
    assert new_client_api.get(f"/api/orders/{order['id']}").json()["status"] == "pending"


def test_order_cannot_be_paid_twice(new_client_api, qa_event):
    plein = category(qa_event, "Plein tarif")
    order = new_client_api.create_order(qa_event["id"], [{"category_id": plein["id"], "quantity": 1}]).json()
    assert new_client_api.pay(order["id"], CARD_OK).status_code == 200
    assert new_client_api.pay(order["id"], CARD_OK).status_code == 400


def test_ticket_pdf_only_available_once_paid(new_client_api, qa_event):
    plein = category(qa_event, "Plein tarif")
    order = new_client_api.create_order(qa_event["id"], [{"category_id": plein["id"], "quantity": 1}]).json()
    assert new_client_api.get(f"/api/orders/{order['id']}/ticket").status_code == 400

    new_client_api.pay(order["id"], CARD_OK)
    r = new_client_api.get(f"/api/orders/{order['id']}/ticket")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF-")
