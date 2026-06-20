from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Event
from ..schemas import CategoryOut, EventDetailOut, EventOut
from ..services import category_available, event_available, expire_stale_orders

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=list[EventOut])
def list_events(
    q: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Event).filter(Event.status == "published")
    if city:
        query = query.filter(Event.city == city)
    if q:
        query = query.filter(Event.title.ilike(f"%{q}%"))
    return query.order_by(Event.starts_at).all()


@router.get("/{event_id}", response_model=EventDetailOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    expire_stale_orders(db)
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    categories = [
        CategoryOut(
            id=c.id,
            name=c.name,
            price_cents=c.price_cents,
            quota=c.quota,
            available=category_available(db, c),
        )
        for c in event.categories
    ]
    return EventDetailOut(
        id=event.id,
        title=event.title,
        description=event.description or "",
        city=event.city,
        venue=event.venue or "",
        starts_at=event.starts_at,
        capacity=event.capacity,
        status=event.status,
        cover_color=event.cover_color,
        categories=categories,
        available=sum(c.available for c in categories),
    )
