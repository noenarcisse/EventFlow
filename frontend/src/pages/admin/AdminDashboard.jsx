import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { euros, fmtDate } from "../../api";

const STATUS_BADGE = {
  published: "b-mint",
  draft: "b-violet",
  archived: "b-coral",
};

export default function AdminDashboard() {
  const [summary, setSummary] = useState(null);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    api.get("/api/admin/summary").then((r) => setSummary(r.data));
    api.get("/api/admin/events").then((r) => setEvents(r.data));
  }, []);

  return (
    <div className="container">
      <div className="row" style={{ justifyContent: "space-between", marginTop: 28 }}>
        <h1 className="page-title" style={{ margin: 0 }}>Back-office</h1>
        <div className="row" style={{ gap: 10 }}>
          <Link to="/admin/promos" className="btn btn-ghost"><i className="fa-solid fa-tag" /> Codes promo</Link>
          <Link to="/admin/events/new" className="btn btn-primary"><i className="fa-solid fa-plus" /> Nouvel evenement</Link>
        </div>
      </div>
      <p className="subtitle">Gestion des evenements, ventes et participants.</p>

      <div className="metrics">
        <div className="metric"><div className="m-label">Evenements</div><div className="m-value">{summary?.events ?? "-"}</div></div>
        <div className="metric"><div className="m-label">Publies</div><div className="m-value">{summary?.published ?? "-"}</div></div>
        <div className="metric"><div className="m-label">Billets vendus</div><div className="m-value">{summary?.total_sold ?? "-"}</div></div>
        <div className="metric"><div className="m-label">Chiffre d'affaires</div><div className="m-value">{summary ? euros(summary.total_revenue_cents) : "-"}</div></div>
      </div>

      <div className="panel" style={{ marginTop: 22, padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr><th>Evenement</th><th>Date</th><th>Statut</th><th>Remplissage</th><th style={{ textAlign: "right" }}>CA</th><th></th></tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.id}>
                <td><div style={{ fontWeight: 600 }}>{e.title}</div><div className="muted" style={{ fontSize: 13 }}>{e.city}</div></td>
                <td>{fmtDate(e.starts_at)}</td>
                <td><span className={`badge ${STATUS_BADGE[e.status] || "b-violet"}`}>{e.status}</span></td>
                <td>
                  <div className="bar"><div className="bar-fill" style={{ width: `${Math.min(100, Math.round(e.fill_rate * 100))}%` }} /></div>
                  <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>{e.sold}/{e.capacity} ({Math.round(e.fill_rate * 100)}%)</div>
                </td>
                <td style={{ textAlign: "right" }} className="mono">{euros(e.revenue_cents)}</td>
                <td style={{ textAlign: "right" }}><Link to={`/admin/events/${e.id}`} className="btn btn-ghost btn-sm">Gerer</Link></td>
              </tr>
            ))}
            {events.length === 0 && <tr><td colSpan={6} className="muted" style={{ padding: 18 }}>Aucun evenement.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
