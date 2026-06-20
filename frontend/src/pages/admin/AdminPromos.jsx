import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { fmtDate, errMessage } from "../../api";

export default function AdminPromos() {
  const [promos, setPromos] = useState([]);
  const [form, setForm] = useState({ code: "", percent_off: 10, max_uses: 100 });
  const [error, setError] = useState("");

  const load = () => api.get("/api/admin/promo").then((r) => setPromos(r.data));
  useEffect(() => { load(); }, []);

  const isExpired = (p) => p.expires_at && new Date(p.expires_at) < new Date();

  const create = async (e) => {
    e.preventDefault(); setError("");
    try {
      await api.post("/api/admin/promo", {
        code: form.code, percent_off: parseInt(form.percent_off, 10), max_uses: parseInt(form.max_uses, 10),
      });
      setForm({ code: "", percent_off: 10, max_uses: 100 });
      load();
    } catch (err) { setError(errMessage(err)); }
  };

  const disable = async (id) => {
    try { await api.post(`/api/admin/promo/${id}/disable`); load(); }
    catch (err) { setError(errMessage(err)); }
  };

  return (
    <div className="container">
      <Link to="/admin" className="muted" style={{ fontSize: 14, display: "inline-block", marginTop: 28 }}><i className="fa-solid fa-arrow-left-long" /> Back-office</Link>
      <h1 className="page-title" style={{ marginTop: 6 }}>Codes promo</h1>

      <form onSubmit={create} className="panel">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 130px 130px auto", gap: 12, alignItems: "end" }}>
          <div className="field" style={{ margin: 0 }}><label>Code</label><input className="input mono" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })} placeholder="SUMMER20" required /></div>
          <div className="field" style={{ margin: 0 }}><label>Reduction (%)</label><input className="input" type="number" min="0" max="100" value={form.percent_off} onChange={(e) => setForm({ ...form, percent_off: e.target.value })} required /></div>
          <div className="field" style={{ margin: 0 }}><label>Usages max</label><input className="input" type="number" min="1" value={form.max_uses} onChange={(e) => setForm({ ...form, max_uses: e.target.value })} required /></div>
          <button className="btn btn-primary"><i className="fa-solid fa-plus" /> Creer</button>
        </div>
        {error && <div className="notice notice-err" style={{ marginTop: 12 }}>{error}</div>}
      </form>

      <div className="panel" style={{ marginTop: 16, padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead><tr><th>Code</th><th>Reduction</th><th>Utilisation</th><th>Expiration</th><th>Statut</th><th></th></tr></thead>
          <tbody>
            {promos.map((p) => {
              const expired = isExpired(p);
              return (
                <tr key={p.id}>
                  <td className="mono" style={{ fontWeight: 600 }}>{p.code}</td>
                  <td>-{p.percent_off}%</td>
                  <td>{p.used_count}/{p.max_uses}</td>
                  <td className="muted" style={{ fontSize: 13 }}>{p.expires_at ? fmtDate(p.expires_at) : "—"}</td>
                  <td><span className={`badge ${expired ? "b-coral" : "b-mint"}`}>{expired ? "inactif" : "actif"}</span></td>
                  <td style={{ textAlign: "right" }}>
                    {!expired && <button className="btn btn-ghost btn-sm" onClick={() => disable(p.id)}>Desactiver</button>}
                  </td>
                </tr>
              );
            })}
            {promos.length === 0 && <tr><td colSpan={6} className="muted" style={{ padding: 16 }}>Aucun code promo.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
