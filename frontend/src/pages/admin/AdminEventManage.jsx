import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { euros, fmtDate, errMessage } from "../../api";

const ORDER_BADGE = { paid: "b-mint", pending: "b-violet", expired: "b-coral", cancelled: "b-coral" };

export default function AdminEventManage() {
  const { id } = useParams();
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [cat, setCat] = useState({ name: "", price: "", quota: "" });
  const [error, setError] = useState("");

  const load = () => {
    api.get(`/api/admin/events/${id}`).then((r) => setStats(r.data));
    api.get(`/api/admin/events/${id}/orders`).then((r) => setOrders(r.data));
  };
  useEffect(() => { load(); }, [id]);

  const addCat = async (e) => {
    e.preventDefault(); setError("");
    try {
      await api.post(`/api/admin/events/${id}/categories`, {
        name: cat.name, price_cents: Math.round(parseFloat(cat.price) * 100), quota: parseInt(cat.quota, 10),
      });
      setCat({ name: "", price: "", quota: "" });
      load();
    } catch (err) { setError(errMessage(err)); }
  };

  if (!stats) return <div className="container"><p className="muted" style={{ marginTop: 30 }}>Chargement...</p></div>;

  return (
    <div className="container">
      <div className="row" style={{ justifyContent: "space-between", marginTop: 28 }}>
        <div>
          <Link to="/admin" className="muted" style={{ fontSize: 14 }}><i className="fa-solid fa-arrow-left-long" /> Back-office</Link>
          <h1 className="page-title" style={{ margin: "6px 0 0" }}>{stats.title}</h1>
          <div className="meta"><i className="fa-solid fa-location-dot" /> {stats.city} &middot; {fmtDate(stats.starts_at)} &middot; <span className={`badge ${stats.status === "published" ? "b-mint" : "b-violet"}`}>{stats.status}</span></div>
        </div>
        <Link to={`/admin/events/${id}/edit`} className="btn btn-ghost"><i className="fa-solid fa-pen" /> Modifier</Link>
      </div>

      <div className="metrics" style={{ marginTop: 20 }}>
        <div className="metric"><div className="m-label">Vendus</div><div className="m-value">{stats.sold}/{stats.capacity}</div></div>
        <div className="metric"><div className="m-label">Remplissage</div><div className="m-value">{Math.round(stats.fill_rate * 100)}%</div></div>
        <div className="metric"><div className="m-label">Disponibles</div><div className="m-value">{stats.available}</div></div>
        <div className="metric"><div className="m-label">Chiffre d'affaires</div><div className="m-value">{euros(stats.revenue_cents)}</div></div>
      </div>

      <h3 style={{ marginTop: 26 }}>Categories de billets</h3>
      <div className="panel" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead><tr><th>Categorie</th><th>Prix</th><th>Quota</th><th>Vendus</th><th>Dispo</th></tr></thead>
          <tbody>
            {stats.categories.map((c) => (
              <tr key={c.id}>
                <td style={{ fontWeight: 600 }}>{c.name}</td>
                <td className="mono">{euros(c.price_cents)}</td>
                <td>{c.quota}</td><td>{c.sold}</td><td>{c.available}</td>
              </tr>
            ))}
            {stats.categories.length === 0 && <tr><td colSpan={5} className="muted" style={{ padding: 16 }}>Aucune categorie.</td></tr>}
          </tbody>
        </table>
      </div>

      <form onSubmit={addCat} className="panel" style={{ marginTop: 14 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 120px 120px auto", gap: 12, alignItems: "end" }}>
          <div className="field" style={{ margin: 0 }}><label>Nouvelle categorie</label><input className="input" placeholder="Nom" value={cat.name} onChange={(e) => setCat({ ...cat, name: e.target.value })} required /></div>
          <div className="field" style={{ margin: 0 }}><label>Prix (EUR)</label><input className="input" type="number" step="0.01" min="0" value={cat.price} onChange={(e) => setCat({ ...cat, price: e.target.value })} required /></div>
          <div className="field" style={{ margin: 0 }}><label>Quota</label><input className="input" type="number" min="0" value={cat.quota} onChange={(e) => setCat({ ...cat, quota: e.target.value })} required /></div>
          <button className="btn btn-primary"><i className="fa-solid fa-plus" /> Ajouter</button>
        </div>
        {error && <div className="notice notice-err" style={{ marginTop: 12 }}>{error}</div>}
      </form>

      <h3 style={{ marginTop: 26 }}>Commandes ({orders.length})</h3>
      <div className="panel" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead><tr><th>Ref</th><th>Acheteur</th><th>Billets</th><th>Statut</th><th style={{ textAlign: "right" }}>Montant</th><th>Date</th></tr></thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td className="mono">REF-{String(o.id).padStart(5, "0")}</td>
                <td><div style={{ fontWeight: 600 }}>{o.buyer_name || "-"}</div><div className="muted" style={{ fontSize: 12 }}>{o.buyer_email}</div></td>
                <td>{o.tickets}</td>
                <td><span className={`badge ${ORDER_BADGE[o.status] || "b-violet"}`}>{o.status}</span></td>
                <td style={{ textAlign: "right" }} className="mono">{euros(o.total_cents)}</td>
                <td className="muted" style={{ fontSize: 13 }}>{fmtDate(o.created_at)}</td>
              </tr>
            ))}
            {orders.length === 0 && <tr><td colSpan={6} className="muted" style={{ padding: 16 }}>Aucune commande.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
