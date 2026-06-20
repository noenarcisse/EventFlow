"""Seed demo data: users, events, ticket categories, promo codes."""
from datetime import datetime, timedelta

from .auth import hash_password
from .database import Base, SessionLocal, engine
from .models import Event, PromoCode, TicketCategory, User


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Seed skipped: data already present.")
            return

        db.add_all([
            User(email="admin@eventflow.test", password_hash=hash_password("admin1234"),
                 full_name="Admin EventFlow", role="admin"),
            User(email="orga@eventflow.test", password_hash=hash_password("orga1234"),
                 full_name="Olivia Organisatrice", role="organizer"),
            User(email="client@eventflow.test", password_hash=hash_password("client1234"),
                 full_name="Camille Client", role="client"),
        ])

        now = datetime.utcnow()
        events = [
            Event(title="Nuit electro - Halles Saint-Gery", city="Bruxelles",
                  venue="Halles Saint-Gery", starts_at=now + timedelta(days=21),
                  capacity=300, cover_color="#6C4DF6",
                  description="Une nuit electro au coeur de Bruxelles."),
            Event(title="Conference DevOps & Cloud 2026", city="Gand",
                  venue="ICC Gent", starts_at=now + timedelta(days=40),
                  capacity=500, cover_color="#1FD6A6",
                  description="Keynotes et ateliers autour du cloud et de l'automatisation."),
            Event(title="Festival Jazz au Parc", city="Liege",
                  venue="Parc de la Boverie", starts_at=now + timedelta(days=60),
                  capacity=800, cover_color="#FF5B4A",
                  description="Trois scenes, vingt artistes, un week-end de jazz."),
            Event(title="Atelier QA & Test automatise", city="Bruxelles",
                  venue="BeCentral", starts_at=now + timedelta(days=12),
                  capacity=40, cover_color="#15131E",
                  description="Atelier pratique d'automatisation de tests."),
        ]
        db.add_all(events)
        db.flush()

        cats = []
        for ev in events:
            cats.append(TicketCategory(event_id=ev.id, name="Early bird",
                        price_cents=int(ev.capacity and 2500), quota=max(10, ev.capacity // 5)))
            cats.append(TicketCategory(event_id=ev.id, name="Plein tarif",
                        price_cents=3500, quota=max(20, ev.capacity // 2)))
            cats.append(TicketCategory(event_id=ev.id, name="VIP",
                        price_cents=7500, quota=max(5, ev.capacity // 10)))
        db.add_all(cats)

        db.add_all([
            PromoCode(code="WELCOME10", percent_off=10, max_uses=1000,
                      expires_at=now + timedelta(days=90)),
            PromoCode(code="VIP25", percent_off=25, max_uses=50,
                      expires_at=now + timedelta(days=30)),
            PromoCode(code="EXPIRED", percent_off=15, max_uses=100,
                      expires_at=now - timedelta(days=1)),
        ])

        db.commit()
        print("Seed complete: users, events, categories, promo codes created.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
