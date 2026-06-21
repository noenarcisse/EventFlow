import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import api, { euros, fmtDate, errMessage, downloadTicket } from "../api";

export default function Confirmation() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [err, setErr] = useState("");
  const [dl, setDl] = useState(false);

  useEffect(() => {
    api.get(`/api/orders/${orderId}`)
      .then((r) => setOrder(r.data))
      .catch((e) => setErr(errMessage(e, "Commande introuvable.")));
  }, [orderId]);

  const handleDownload = async () => {
    setErr(""); setDl(true);
    try {
      await downloadTicket(orderId);
    } catch (e) {
      setErr(errMessage(e, "Telechargement impossible."));
    } finally {
      setDl(false);
    }
  };

  if (err && !order) return <div className="container"><div className="center-narrow"><div className="notice notice-err">{err}</div></div></div>;
  if (!order) return <div className="container"><p className="muted" style={{ marginTop: 30 }}>Chargement...</p></div>;

  return (
    <div className="container">
      <div className="center-narrow">
        <div className="panel" style={{ textAlign: "center" }}>
          <div className="conf-check"><i className="fa-solid fa-check" /></div>
          <h2 style={{ marginTop: 16 }}>Paiement confirme</h2>
          <p className="muted" style={{ marginBottom: 18 }}>
            Reference <span className="mono">REF-{String(order.id).padStart(5, "0")}</span>
          </p>

          <div style={{ textAlign: "left", borderTop: "1px solid var(--line)", paddingTop: 16 }}>
            <div style={{ fontWeight: 600 }}>{order.event_title}</div>
            <div className="meta"><i className="fa-solid fa-location-dot" /> {order.event_city}</div>
            <div className="meta" style={{ marginBottom: 10 }}><i className="fa-regular fa-calendar" /> {fmtDate(order.event_starts_at)}</div>
            {order.items.map((it) => (
              <div className="cat-row" key={it.category_id}>
                <span>{it.quantity} &times; {it.category_name}</span>
                <span className="mono">{euros(it.unit_price_cents * it.quantity)}</span>
              </div>
            ))}
            <div className="row" style={{ justifyContent: "space-between", marginTop: 14 }}>
              <span className="muted">Total paye</span>
              <span className="price">{euros(order.total_cents)}</span>
            </div>
          </div>

          {err && <div className="notice notice-err" style={{ marginTop: 14 }}>{err}</div>}

          <button className="btn btn-primary" style={{ width: "100%", marginTop: 20 }} onClick={handleDownload} disabled={dl}>
            <i className="fa-solid fa-download" /> {dl ? "Generation..." : "Telecharger mon billet (PDF)"}
          </button>
          <div className="row" style={{ gap: 10, marginTop: 12, justifyContent: "center" }}>
            <Link to="/tickets" className="btn btn-ghost btn-sm"><i className="fa-solid fa-ticket" /> Mes billets</Link>
            <Link to="/" className="btn btn-ghost btn-sm">Retour au catalogue</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
