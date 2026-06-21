from datetime import datetime, timezone
from typing import Annotated, List, Optional

from pydantic import BaseModel, EmailStr, PlainSerializer


def _utc_iso(v):
    if v is None:
        return None
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.isoformat().replace("+00:00", "Z")


UtcDatetime = Annotated[datetime, PlainSerializer(_utc_iso, return_type=str)]


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CategoryOut(BaseModel):
    id: int
    name: str
    price_cents: int
    quota: int
    available: int

    class Config:
        from_attributes = True


class EventOut(BaseModel):
    id: int
    title: str
    description: str
    city: str
    venue: str
    starts_at: UtcDatetime
    capacity: int
    status: str
    cover_color: str

    class Config:
        from_attributes = True


class EventDetailOut(EventOut):
    categories: List[CategoryOut] = []
    available: int = 0


class OrderItemIn(BaseModel):
    category_id: int
    quantity: int


class OrderCreate(BaseModel):
    event_id: int
    items: List[OrderItemIn]
    promo_code: Optional[str] = None


class OrderItemOut(BaseModel):
    category_id: int
    quantity: int
    unit_price_cents: int

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    event_id: int
    status: str
    total_cents: int
    created_at: UtcDatetime
    expires_at: Optional[UtcDatetime]
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True


class PaymentIn(BaseModel):
    card_number: str
    exp_month: int
    exp_year: int
    cvc: str
    cardholder: str = ""


class OrderItemDetail(BaseModel):
    category_id: int
    category_name: str
    quantity: int
    unit_price_cents: int


class OrderDetailOut(BaseModel):
    id: int
    event_id: int
    event_title: str
    event_city: str
    event_starts_at: UtcDatetime
    status: str
    total_cents: int
    created_at: UtcDatetime
    expires_at: Optional[UtcDatetime]
    items: List[OrderItemDetail] = []


class CategoryIn(BaseModel):
    name: str
    price_cents: int
    quota: int


class AdminEventCreate(BaseModel):
    title: str
    description: str = ""
    city: str
    venue: str = ""
    starts_at: datetime
    capacity: int
    status: str = "published"
    cover_color: str = "#6C4DF6"
    categories: List[CategoryIn] = []


class AdminEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    venue: Optional[str] = None
    starts_at: Optional[datetime] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    cover_color: Optional[str] = None


class CategoryStat(BaseModel):
    id: int
    name: str
    price_cents: int
    quota: int
    sold: int
    available: int


class EventStats(BaseModel):
    id: int
    title: str
    city: str
    venue: str
    starts_at: UtcDatetime
    status: str
    cover_color: str
    capacity: int
    sold: int
    pending: int
    available: int
    revenue_cents: int
    fill_rate: float
    categories: List[CategoryStat] = []


class AdminEventRow(BaseModel):
    id: int
    title: str
    city: str
    starts_at: UtcDatetime
    status: str
    capacity: int
    sold: int
    revenue_cents: int
    fill_rate: float


class AdminSummary(BaseModel):
    events: int
    published: int
    total_sold: int
    total_revenue_cents: int


class OrderAdminOut(BaseModel):
    id: int
    buyer_email: str
    buyer_name: str
    status: str
    total_cents: int
    tickets: int
    created_at: UtcDatetime


class PromoOut(BaseModel):
    id: int
    code: str
    percent_off: int
    max_uses: int
    used_count: int
    expires_at: Optional[UtcDatetime]


class PromoCreate(BaseModel):
    code: str
    percent_off: int
    max_uses: int = 1
    expires_at: Optional[datetime] = None


class PromoUpdate(BaseModel):
    percent_off: Optional[int] = None
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class AvatarUpdate(BaseModel):
    avatar: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
