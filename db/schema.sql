-- EventFlow - schema relationnel de reference (PostgreSQL)
-- Utilise pour le module SQL du fil rouge. Le backend cree aussi ces tables
-- automatiquement via SQLAlchemy ; ce fichier sert de reference pedagogique.

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL DEFAULT '',
    role            VARCHAR(20)  NOT NULL DEFAULT 'client',
    created_at      TIMESTAMP DEFAULT now()
);

CREATE TABLE events (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT DEFAULT '',
    city            VARCHAR(120) NOT NULL,
    venue           VARCHAR(255) DEFAULT '',
    starts_at       TIMESTAMP NOT NULL,
    capacity        INTEGER NOT NULL CHECK (capacity >= 0),
    status          VARCHAR(20) NOT NULL DEFAULT 'published',
    cover_color     VARCHAR(7) DEFAULT '#6C4DF6'
);

CREATE TABLE ticket_categories (
    id              SERIAL PRIMARY KEY,
    event_id        INTEGER NOT NULL REFERENCES events(id),
    name            VARCHAR(120) NOT NULL,
    price_cents     INTEGER NOT NULL CHECK (price_cents >= 0),
    quota           INTEGER NOT NULL CHECK (quota >= 0)
);

CREATE TABLE promo_codes (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(40) UNIQUE NOT NULL,
    percent_off     INTEGER NOT NULL CHECK (percent_off BETWEEN 0 AND 100),
    max_uses        INTEGER NOT NULL DEFAULT 1,
    used_count      INTEGER NOT NULL DEFAULT 0,
    expires_at      TIMESTAMP
);

CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    event_id        INTEGER NOT NULL REFERENCES events(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_cents     INTEGER NOT NULL DEFAULT 0,
    promo_code_id   INTEGER REFERENCES promo_codes(id),
    created_at      TIMESTAMP DEFAULT now(),
    expires_at      TIMESTAMP
);

CREATE TABLE order_items (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    category_id     INTEGER NOT NULL REFERENCES ticket_categories(id),
    quantity        INTEGER NOT NULL CHECK (quantity > 0 AND quantity <= 6),
    unit_price_cents INTEGER NOT NULL
);

CREATE TABLE payments (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL UNIQUE REFERENCES orders(id),
    amount_cents    INTEGER NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'succeeded',
    paid_at         TIMESTAMP DEFAULT now()
);

CREATE TABLE refunds (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    amount_cents    INTEGER NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'processed',
    created_at      TIMESTAMP DEFAULT now()
);

-- Exemple : RM1 - detecter une sur-reservation
-- SELECT e.id, e.title, e.capacity, SUM(oi.quantity) AS vendus
-- FROM events e
-- JOIN orders o       ON o.event_id = e.id AND o.status = 'paid'
-- JOIN order_items oi ON oi.order_id = o.id
-- GROUP BY e.id, e.title, e.capacity
-- HAVING SUM(oi.quantity) > e.capacity;
