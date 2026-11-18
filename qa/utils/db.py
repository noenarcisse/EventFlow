"""Acces direct a la base PostgreSQL d'EventFlow pour les controles de coherence."""
from sqlalchemy import create_engine, text

from utils.config import DB_URL

_engine = None


def engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DB_URL)
    return _engine


def fetch_all(sql, **params):
    with engine().connect() as conn:
        return [dict(row._mapping) for row in conn.execute(text(sql), params)]


def execute(sql, **params):
    with engine().begin() as conn:
        conn.execute(text(sql), params)


def order_payment(order_id):
    """Montant de la commande vs montant reellement preleve."""
    rows = fetch_all(
        """--sql 
            SELECT o.total_cents, p.amount_cents FROM orders o
            JOIN payments p ON p.order_id = o.id WHERE o.id = :nom
        """, 
        nom=order_id
    )
    return rows[0] if rows else None
