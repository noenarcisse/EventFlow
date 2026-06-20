from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import require_staff
from ..database import get_db
from ..models import Event, Order, OrderItem, PromoCode, TicketCategory, User
from ..schemas import (
    AdminEventCreate,
    AdminEventRow,
    AdminEventUpdate,
    AdminSummary,
    CategoryIn,
    CategoryStat,
    EventStats,
    OrderAdminOut,
    PromoCreate,
    PromoOut,
    PromoUpdate,
)
from ..services import category_available, category_sold

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_staff)])


def _paid_qty(db: Session, event_id: int) -> int:
    q = (
        db.query(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.event_id == event_id, Order.status == "paid")
    )
    return int(q.scalar() or 0)


def _revenue(db: Session, event_id: int) -> int:
    q = db.query(func.coalesce(func.sum(Order.total_cents), 0)).filter(
        Order.event_id == event_id, Order.status == "paid"
    )
    return int(q.scalar() or 0)


# ---------- summary ----------
@router.get("/summary", response_model=AdminSummary)
def summary(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    total_sold = sum(_paid_qty(db, e.id) for e in events)
    total_rev = sum(_revenue(db, e.id) for e in events)
    return AdminSummary(
        events=len(events),
        published=len([e for e in events if e.status == "published"]),
        total_sold=total_sold,
        total_revenue_cents=total_rev,
    )


# ---------- events ----------
@router.get("/events", response_model=list[AdminEventRow])
def list_events(db: Session = Depends(get_db)):
    rows = []
    for e in db.query(Event).order_by(Event.starts_at).all():
        sold = _paid_qty(db, e.id)
        rows.append(
            AdminEventRow(
                id=e.id, title=e.title, city=e.city, starts_at=e.starts_at,
                status=e.status, capacity=e.capacity, sold=sold,
                revenue_cents=_revenue(db, e.id),
                fill_rate=round(sold / e.capacity, 3) if e.capacity else 0.0,
            )
        )
    return rows


@router.post("/events", response_model=EventStats, status_code=201)
def create_event(payload: AdminEventCreate, db: Session = Depends(get_db)):
    event = Event(
        title=payload.title, description=payload.description, city=payload.city,
        venue=payload.venue, starts_at=payload.starts_at, capacity=payload.capacity,
        status=payload.status, cover_color=payload.cover_color,
    )
    for c in payload.categories:
        event.categories.append(
            TicketCategory(name=c.name, price_cents=c.price_cents, quota=c.quota)
        )
    db.add(event)
    db.commit()
    db.refresh(event)
    return _stats(db, event)


@router.get("/events/{event_id}", response_model=EventStats)
def event_stats(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return _stats(db, event)


@router.put("/events/{event_id}", response_model=EventStats)
def update_event(event_id: int, payload: AdminEventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return _stats(db, event)


@router.post("/events/{event_id}/categories", response_model=EventStats, status_code=201)
def add_category(event_id: int, payload: CategoryIn, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.add(TicketCategory(event_id=event_id, name=payload.name,
                          price_cents=payload.price_cents, quota=payload.quota))
    db.commit()
    db.refresh(event)
    return _stats(db, event)


def _stats(db: Session, event: Event) -> EventStats:
    cats = []
    for c in event.categories:
        sold = category_sold(db, c.id)
        cats.append(CategoryStat(
            id=c.id, name=c.name, price_cents=c.price_cents, quota=c.quota,
            sold=sold, available=category_available(db, c),
        ))
    paid = _paid_qty(db, event.id)
    total_quota = sum(c.quota for c in event.categories)
    return EventStats(
        id=event.id, title=event.title, city=event.city, venue=event.venue,
        starts_at=event.starts_at, status=event.status, cover_color=event.cover_color,
        capacity=event.capacity, sold=paid,
        pending=sum(c.sold for c in cats) - paid,
        available=max(0, event.capacity - paid),
        revenue_cents=_revenue(db, event.id),
        fill_rate=round(paid / event.capacity, 3) if event.capacity else 0.0,
        categories=cats,
    )


# ---------- orders ----------
@router.get("/events/{event_id}/orders", response_model=list[OrderAdminOut])
def event_orders(event_id: int, db: Session = Depends(get_db)):
    orders = (
        db.query(Order).filter(Order.event_id == event_id)
        .order_by(Order.created_at.desc()).all()
    )
    out = []
    for o in orders:
        buyer = db.query(User).filter(User.id == o.user_id).first()
        out.append(OrderAdminOut(
            id=o.id,
            buyer_email=buyer.email if buyer else "?",
            buyer_name=buyer.full_name if buyer else "",
            status=o.status, total_cents=o.total_cents,
            tickets=sum(i.quantity for i in o.items),
            created_at=o.created_at,
        ))
    return out


# ---------- promo codes ----------
@router.get("/promo", response_model=list[PromoOut])
def list_promo(db: Session = Depends(get_db)):
    return db.query(PromoCode).order_by(PromoCode.id).all()


@router.post("/promo", response_model=PromoOut, status_code=201)
def create_promo(payload: PromoCreate, db: Session = Depends(get_db)):
    if db.query(PromoCode).filter(PromoCode.code == payload.code).first():
        raise HTTPException(status_code=409, detail="Code already exists")
    promo = PromoCode(code=payload.code.upper(), percent_off=payload.percent_off,
                      max_uses=payload.max_uses, expires_at=payload.expires_at)
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo


@router.put("/promo/{promo_id}", response_model=PromoOut)
def update_promo(promo_id: int, payload: PromoUpdate, db: Session = Depends(get_db)):
    promo = db.query(PromoCode).filter(PromoCode.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promo not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(promo, field, value)
    db.commit()
    db.refresh(promo)
    return promo


@router.post("/promo/{promo_id}/disable", response_model=PromoOut)
def disable_promo(promo_id: int, db: Session = Depends(get_db)):
    promo = db.query(PromoCode).filter(PromoCode.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promo not found")
    promo.expires_at = datetime.utcnow()
    db.commit()
    db.refresh(promo)
    return promo
