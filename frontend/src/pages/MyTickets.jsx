import { useEffect, useState } from "react";
import api, { euros, fmtDate, downloadTicket } from "../api";

const STATUS = {
  paid: { label: "Paye", cls: "b-mint", icon: "fa-circle-check" },
  pending: { label: "En attente", cls: "b-violet", icon: "fa-clock" },
  expired: { label: "Expire", cls: "b-coral", icon: "fa-circle-xmark" },
  cancelled: { label: "Annule", cls: "b-coral", icon: "fa-ban" },
};

export default function MyTickets() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/orders/me").then((r) => setOrders(r.data)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="container">
      <h1 className="page-title">Mes billets</h1>
      <p className="subtitle">Retrouvez l'ensemble de vos commandes.</p>
      {loading ? (
        <p className="muted">Chargement...</p>
      ) : orders.length === 0 ? (
        <p className="muted">Aucune commande pour le moment.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {orders.map((o) => {
            const s = STATUS[o.status] || STATUS.pending;
            const count = o.items.reduce((a, i) => a + i.quantity, 0);
            return (
              <div className="panel" key={o.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <div className="row" style={{ gap: 10 }}>
                    <span className="mono" style={{ fontSize: 13 }}>REF-{String(o.id).padStart(5, "0")}</span>
                    <span className={`badge ${s.cls}`}><i className={`fa-solid ${s.icon}`} /> {s.label}</span>
                  </div>
                  <div className="muted" style={{ fontSize: 14, marginTop: 6 }}>
                    {count} billet{count > 1 ? "s" : ""} &middot; {fmtDate(o.created_at)}
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <span className="price">{euros(o.total_cents)}</span>
                  {o.status === "paid" && (
                    <button className="btn btn-ghost btn-sm" onClick={() => downloadTicket(o.id)} aria-label="Telecharger le billet">
                      <i className="fa-solid fa-download" /> Billet
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
