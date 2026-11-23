import re

import pytest
from playwright.sync_api import Page, expect

from utils import config

pytestmark = pytest.mark.ui


def add_tickets(page: Page, category_name, quantity):
    row = page.locator(".cat-row").filter(has_text=category_name)
    for _ in range(quantity):
        row.get_by_role("button", name="+").click()
    return row


def go_to_checkout(page: Page, event_id, category_name="Plein tarif", quantity=1):
    page.goto(f"/events/{event_id}")
    add_tickets(page, category_name, quantity)
    page.get_by_role("button", name="Continuer vers le paiement").click()
    expect(page).to_have_url(re.compile(r"/checkout/\d+$"))
    expect(page.get_by_text("Paiement securise simule")).to_be_visible()


def test_total_is_updated_when_adding_tickets(logged_in_page: Page, qa_event):
    logged_in_page.goto(f"/events/{qa_event['id']}")
    add_tickets(logged_in_page, "Plein tarif", 2)
    expect(logged_in_page.get_by_text("Total (2 billets)")).to_be_visible()
    expect(logged_in_page.locator(".price")).to_contain_text("70,00")


def test_cannot_select_more_than_six_tickets(logged_in_page: Page, qa_event):
    logged_in_page.goto(f"/events/{qa_event['id']}")
    row = add_tickets(logged_in_page, "Plein tarif", 6)
    expect(row.get_by_role("button", name="+")).to_be_disabled()
    expect(logged_in_page.get_by_text("Total (6 billets)")).to_be_visible()


def test_anonymous_user_is_sent_to_login_when_booking(page: Page, qa_event):
    page.goto(f"/events/{qa_event['id']}")
    add_tickets(page, "Plein tarif", 1)
    page.get_by_role("button", name="Continuer vers le paiement").click()
    expect(page).to_have_url(re.compile(r"/login$"))

@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_expired_promo_code_shows_error(logged_in_page: Page, qa_event):
    logged_in_page.goto(f"/events/{qa_event['id']}")
    add_tickets(logged_in_page, "Plein tarif", 1)
    logged_in_page.get_by_placeholder("WELCOME10").fill("EXPIRED")
    logged_in_page.get_by_role("button", name="Continuer vers le paiement").click()
    expect(logged_in_page.locator(".notice-err")).to_have_text("Promo code expired")


def test_declined_card_shows_error(logged_in_page: Page, qa_event):
    go_to_checkout(logged_in_page, qa_event["id"])
    logged_in_page.get_by_placeholder("4242 4242 4242 4242").fill(config.CARD_DECLINED)
    logged_in_page.get_by_placeholder("Camille Client").fill("QA Bot")
    logged_in_page.get_by_role("button", name=re.compile("^Payer")).click()
    expect(logged_in_page.locator(".notice-err")).to_have_text("Card declined")
