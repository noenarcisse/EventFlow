from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from sqlalchemy import inspect, text

from .database import Base, engine
from .routers import admin, auth, events, orders

Base.metadata.create_all(bind=engine)


def _ensure_columns():
    """Idempotent: ajoute les colonnes profil aux bases existantes (sans Alembic)."""
    insp = inspect(engine)
    existing = {c["name"] for c in insp.get_columns("users")}
    to_add = []
    if "phone" not in existing:
        to_add.append("ALTER TABLE users ADD COLUMN phone VARCHAR(40)")
    if "avatar" not in existing:
        to_add.append("ALTER TABLE users ADD COLUMN avatar TEXT")
    if to_add:
        with engine.begin() as conn:
            for stmt in to_add:
                conn.execute(text(stmt))


_ensure_columns()

app = FastAPI(title="EventFlow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(orders.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "eventflow-api"}
