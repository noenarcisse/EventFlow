from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False, default="")
    role = Column(String(20), nullable=False, default="client")  # client|organizer|admin
    phone = Column(String(40), nullable=True)
    avatar = Column(Text, nullable=True)  # data URL (image)
    created_at = Column(DateTime, server_default=func.now())

    orders = relationship("Order", back_populates="user")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    city = Column(String(120), nullable=False, index=True)
    venue = Column(String(255), default="")
    starts_at = Column(DateTime, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="published")  # draft|published|archived
    cover_color = Column(String(7), default="#6C4DF6")

    categories = relationship("TicketCategory", back_populates="event", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="event")


class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    name = Column(String(120), nullable=False)
    price_cents = Column(Integer, nullable=False)
    quota = Column(Integer, nullable=False)

    event = relationship("Event", back_populates="categories")
    items = relationship("OrderItem", back_populates="category")


class PromoCode(Base):
    __tablename__ = "promo_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String(40), unique=True, nullable=False, index=True)
    percent_off = Column(Integer, nullable=False)
    max_uses = Column(Integer, nullable=False, default=1)
    used_count = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime, nullable=True)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending|paid|expired|cancelled
    total_cents = Column(Integer, nullable=False, default=0)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="orders")
    event = relationship("Event", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    category = relationship("TicketCategory", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    amount_cents = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="succeeded")
    paid_at = Column(DateTime, server_default=func.now())

    order = relationship("Order", back_populates="payment")


class Refund(Base):
    __tablename__ = "refunds"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="processed")
    created_at = Column(DateTime, server_default=func.now())
