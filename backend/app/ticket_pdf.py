"""Generate a branded EventFlow ticket PDF (one page per ticket) with a QR code."""
import hashlib
import hmac
import io

import qrcode
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

VIOLET = HexColor("#6C4DF6")
CORAL = HexColor("#FF5B4A")
INK = HexColor("#15131E")
MUTED = HexColor("#6B6878")
LINE = HexColor("#E7E5DF")

PAGE_W = 180 * mm
PAGE_H = 75 * mm


def signature(secret: str, ref: str) -> str:
    return hmac.new(secret.encode(), ref.encode(), hashlib.sha256).hexdigest()[:10]


def _qr_image(payload: str) -> ImageReader:
    qr = qrcode.QRCode(border=1, box_size=10)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#15131E", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def _draw_logo(c: canvas.Canvas, tx: float, ty: float, s: float) -> None:
    """Draw the eventflow symbol with bottom-left corner at (tx, ty), size s."""
    k = s / 96.0

    def rect(xs, ys, w, h, color, r=None):
        c.setFillColor(color)
        rr = (h / 2.0) * k if r is None else r
        c.roundRect(tx + xs * k, ty + (96 - ys - h) * k, w * k, h * k, rr, stroke=0, fill=1)

    c.setFillColor(VIOLET)
    c.roundRect(tx, ty, s, s, s * 0.25, stroke=0, fill=1)
    rect(27, 25, 11, 46, white)
    rect(38, 25, 34, 11, white)
    rect(38, 41, 23, 11, white)
    # coral forward chevron
    c.setStrokeColor(CORAL)
    c.setLineWidth(11 * k)
    c.setLineCap(1)
    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(tx + 44 * k, ty + (96 - 57) * k)
    p.lineTo(tx + 58 * k, ty + (96 - 63.5) * k)
    p.lineTo(tx + 44 * k, ty + (96 - 70) * k)
    c.drawPath(p, stroke=1, fill=0)


def _draw_ticket(c, *, ref, event_title, city, date_str, category, holder, index, total, secret):
    m = 5 * mm
    card_w = PAGE_W - 2 * m
    card_h = PAGE_H - 2 * m
    # card
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.roundRect(m, m, card_w, card_h, 5 * mm, stroke=1, fill=1)

    stub_x = m + 122 * mm  # perforation position
    # perforation (dashed) + notches
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.setDash(2, 3)
    c.line(stub_x, m + 5 * mm, stub_x, m + card_h - 5 * mm)
    c.setDash()

    # header: logo + wordmark
    _draw_logo(c, m + 7 * mm, m + card_h - 17 * mm, 12 * mm)
    wx = m + 22 * mm
    wy = m + card_h - 14 * mm
    c.setFont("Helvetica-Bold", 17)
    c.setFillColor(INK)
    c.drawString(wx, wy, "event")
    ev_w = c.stringWidth("event", "Helvetica-Bold", 17)
    c.setFillColor(VIOLET)
    c.drawString(wx + ev_w, wy, "flow")

    # divider under header
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(m + 7 * mm, m + card_h - 21 * mm, stub_x - 6 * mm, m + card_h - 21 * mm)

    # event title
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    title = event_title if len(event_title) <= 42 else event_title[:41] + "…"
    c.drawString(m + 7 * mm, m + card_h - 30 * mm, title)

    # info grid (label/value)
    def field(x, y, label, value):
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(x, y, label.upper())
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x, y - 5 * mm, value)

    col1 = m + 7 * mm
    col2 = m + 64 * mm
    field(col1, m + card_h - 40 * mm, "Quand", date_str)
    field(col2, m + card_h - 40 * mm, "Ou", city)
    field(col1, m + card_h - 50 * mm, "Categorie", category)
    field(col2, m + card_h - 50 * mm, "Titulaire", holder or "-")

    # footer note
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawString(m + 7 * mm, m + 3.5 * mm, "Billet simule - eventflow")

    # stub: QR + ref
    payload = f"EVENTFLOW:{ref}:{signature(secret, ref)}"
    qr_size = 34 * mm
    qr_x = stub_x + (PAGE_W - m - stub_x - qr_size) / 2
    qr_y = m + card_h - 46 * mm
    c.drawImage(_qr_image(payload), qr_x, qr_y, qr_size, qr_size)

    cx = stub_x + (PAGE_W - m - stub_x) / 2
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(cx, m + card_h - 9 * mm, f"BILLET {index}/{total}")
    c.setFillColor(INK)
    c.setFont("Courier-Bold", 11)
    c.drawCentredString(cx, qr_y - 6 * mm, ref)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(cx, qr_y - 11 * mm, "Scan a l'entree")


def build_tickets_pdf(*, ref_base, event_title, city, date_str, holder, units, secret):
    """units: list of category names, one per physical ticket."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    total = len(units)
    for i, category in enumerate(units, start=1):
        _draw_ticket(
            c,
            ref=f"{ref_base}-{i}",
            event_title=event_title,
            city=city,
            date_str=date_str,
            category=category,
            holder=holder,
            index=i,
            total=total,
            secret=secret,
        )
        c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()
