"""Business logic shared across routers (availability, pricing, expiry)."""
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Order, OrderItem, TicketCategory

MAX_TICKETS_PER_ORDER = 6  # RM3


def expire_stale_orders(db: Session) -> None:
    """RM2: a pending order older than its expiry releases the stock."""
    now = datetime.utcnow()
    stale = (
        db.query(Order)
        .filter(Order.status == "pending", Order.expires_at < now)
        .all()
    )
    for order in stale:
        order.status = "expired"
    if stale:
        db.commit()


def category_sold(db: Session, category_id: int) -> int:
    """Tickets that count against the quota: paid orders + live pending orders."""
    now = datetime.utcnow()
    q = (
        db.query(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(OrderItem.category_id == category_id)
        .filter(
            (Order.status == "paid")
            | ((Order.status == "pending") & (Order.expires_at > now))
        )
    )
    return int(q.scalar() or 0)


def category_available(db: Session, category: TicketCategory) -> int:
    return max(0, category.quota - category_sold(db, category.id))


def event_available(db: Session, categories) -> int:
    return sum(category_available(db, c) for c in categories)
