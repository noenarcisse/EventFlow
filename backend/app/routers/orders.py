import re
from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..config import settings
from ..database import get_db
from ..models import Event, Order, OrderItem, Payment, PromoCode, TicketCategory, User
from ..schemas import (
    OrderCreate,
    OrderDetailOut,
    OrderItemDetail,
    OrderOut,
    PaymentIn,
)
from ..services import MAX_TICKETS_PER_ORDER, category_available, expire_stale_orders
from ..ticket_pdf import build_tickets_pdf

router = APIRouter(prefix="/api/orders", tags=["orders"])

# Test cards for the simulated payment gateway (Stripe-style).
# Any other valid-looking number succeeds.
DECLINE_CARDS = {"4000000000000002"}


def _validate_promo(db: Session, code: str) -> PromoCode:
    promo = db.query(PromoCode).filter(PromoCode.code == code).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Unknown promo code")
    # RM4: a promo has a max number of uses and an expiry date.
    if promo.expires_at and promo.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Promo code expired")
    if promo.used_count >= promo.max_uses:
        raise HTTPException(status_code=400, detail="Promo code fully used")
    return promo


def _order_detail(db: Session, order: Order) -> OrderDetailOut:
    event = db.query(Event).filter(Event.id == order.event_id).first()
    items = []
    for it in order.items:
        cat = db.query(TicketCategory).filter(TicketCategory.id == it.category_id).first()
        items.append(
            OrderItemDetail(
                category_id=it.category_id,
                category_name=cat.name if cat else "?",
                quantity=it.quantity,
                unit_price_cents=it.unit_price_cents,
            )
        )
    return OrderDetailOut(
        id=order.id,
        event_id=order.event_id,
        event_title=event.title if event else "?",
        event_city=event.city if event else "",
        event_starts_at=event.starts_at if event else order.created_at,
        status=order.status,
        total_cents=order.total_cents,
        created_at=order.created_at,
        expires_at=order.expires_at,
        items=items,
    )


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    expire_stale_orders(db)

    total_qty = sum(item.quantity for item in payload.items)
    if total_qty <= 0:
        raise HTTPException(status_code=400, detail="Order must contain at least one ticket")
    # RM3: maximum 6 tickets per order.
    if total_qty > MAX_TICKETS_PER_ORDER:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_TICKETS_PER_ORDER} tickets per order")

    order = Order(
        user_id=current.id,
        event_id=payload.event_id,
        status="pending",
        expires_at=datetime.utcnow() + timedelta(minutes=settings.reservation_minutes),
    )

    total = 0
    for item in payload.items:
        category = db.query(TicketCategory).filter(TicketCategory.id == item.category_id).first()
        if not category or category.event_id != payload.event_id:
            raise HTTPException(status_code=400, detail="Invalid ticket category")
        # RM1: never sell more than the available stock.
        if item.quantity > category_available(db, category):
            raise HTTPException(status_code=409, detail=f"Not enough stock for {category.name}")
        total += category.price_cents * item.quantity
        order.items.append(
            OrderItem(
                category_id=category.id,
                quantity=item.quantity,
                unit_price_cents=category.price_cents,
            )
        )

    if payload.promo_code:
        promo = _validate_promo(db, payload.promo_code)
        total = int(round(total * (100 - promo.percent_off) / 100))
        order.promo_code_id = promo.id

    order.total_cents = total
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/me", response_model=list[OrderOut])
def my_orders(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    expire_stale_orders(db)
    return (
        db.query(Order)
        .filter(Order.user_id == current.id)
        .order_by(Order.created_at.desc())
        .all()
    )


@router.get("/{order_id}", response_model=OrderDetailOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    expire_stale_orders(db)
    order = db.query(Order).filter(Order.id == order_id).first()
    # RM7: a user can only access their own orders.
    if not order or order.user_id != current.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return _order_detail(db, order)


@router.post("/{order_id}/pay", response_model=OrderDetailOut)
def pay_order(
    order_id: int,
    payment: PaymentIn | None = Body(default=None),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order or order.user_id != current.id:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")
    if order.status != "pending" or (order.expires_at and order.expires_at < datetime.utcnow()):
        raise HTTPException(status_code=400, detail="Reservation expired")

    # Simulated payment gateway: validate the (fake) card and play test scenarios.
    if payment is not None:
        digits = re.sub(r"\D", "", payment.card_number)
        if len(digits) < 13 or len(digits) > 19:
            raise HTTPException(status_code=400, detail="Invalid card number")
        if digits in DECLINE_CARDS:
            raise HTTPException(status_code=402, detail="Card declined")

    order.status = "paid"
    db.add(Payment(order_id=order.id, amount_cents=order.total_cents, status="succeeded"))
    if order.promo_code_id:
        promo = db.query(PromoCode).filter(PromoCode.id == order.promo_code_id).first()
        if promo:
            promo.used_count += 1
    db.commit()
    db.refresh(order)
    return _order_detail(db, order)


@router.get("/{order_id}/ticket")
def download_ticket(
    order_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order or order.user_id != current.id:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "paid":
        raise HTTPException(status_code=400, detail="Order is not paid")

    event = db.query(Event).filter(Event.id == order.event_id).first()
    units = []
    for it in order.items:
        cat = db.query(TicketCategory).filter(TicketCategory.id == it.category_id).first()
        name = cat.name if cat else "Billet"
        units.extend([name] * it.quantity)

    ref_base = f"REF-{order.id:05d}"
    pdf = build_tickets_pdf(
        ref_base=ref_base,
        event_title=event.title if event else "Evenement",
        city=event.city if event else "",
        date_str=event.starts_at.strftime("%d/%m/%Y") if event else "",
        holder=current.full_name or current.email,
        units=units or ["Billet"],
        secret=settings.jwt_secret,
    )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="eventflow-{ref_base}.pdf"'},
    )
