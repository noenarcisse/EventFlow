import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api, { errMessage } from "../../api";

const empty = { title: "", city: "", venue: "", starts_at: "", capacity: 100, status: "published", cover_color: "#6C4DF6" };

// API sends UTC "...Z"; <input type=datetime-local> wants "YYYY-MM-DDTHH:MM"
const toLocalInput = (iso) => (iso ? iso.slice(0, 16) : "");

export default function AdminEventForm() {
  const { id } = useParams();
  const editing = Boolean(id);
  const nav = useNavigate();
  const [form, setForm] = useState(empty);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (editing) {
      api.get(`/api/admin/events/${id}`).then((r) => {
        const e = r.data;
        setForm({
          title: e.title, city: e.city, venue: e.venue, starts_at: toLocalInput(e.starts_at),
          capacity: e.capacity, status: e.status, cover_color: e.cover_color,
        });
      });
    }
  }, [id]);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setBusy(true);
    const payload = { ...form, capacity: parseInt(form.capacity, 10) };
    try {
      if (editing) {
        await api.put(`/api/admin/events/${id}`, payload);
        nav(`/admin/events/${id}`);
      } else {
        const r = await api.post("/api/admin/events", payload);
        nav(`/admin/events/${r.data.id}`);
      }
    } catch (err) {
      setError(errMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container">
      <div className="center-narrow" style={{ maxWidth: 560 }}>
        <h1 className="page-title">{editing ? "Modifier l'evenement" : "Nouvel evenement"}</h1>
        <form onSubmit={submit} className="panel">
          <div className="field"><label>Titre</label><input className="input" value={form.title} onChange={set("title")} required /></div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div className="field"><label>Ville</label><input className="input" value={form.city} onChange={set("city")} required /></div>
            <div className="field"><label>Lieu</label><input className="input" value={form.venue} onChange={set("venue")} /></div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div className="field"><label>Date et heure</label><input className="input" type="datetime-local" value={form.starts_at} onChange={set("starts_at")} required /></div>
            <div className="field"><label>Capacite</label><input className="input" type="number" min="0" value={form.capacity} onChange={set("capacity")} required /></div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 120px", gap: 12 }}>
            <div className="field"><label>Statut</label>
              <select className="input" value={form.status} onChange={set("status")}>
                <option value="published">Publie</option>
                <option value="draft">Brouillon</option>
                <option value="archived">Archive</option>
              </select>
            </div>
            <div className="field"><label>Couleur</label><input className="input" type="color" style={{ padding: 4, height: 42 }} value={form.cover_color} onChange={set("cover_color")} /></div>
          </div>
          {error && <div className="notice notice-err" style={{ marginBottom: 12 }}>{error}</div>}
          <div className="row" style={{ gap: 10 }}>
            <button className="btn btn-primary" disabled={busy}>{busy ? "..." : editing ? "Enregistrer" : "Creer"}</button>
            <button type="button" className="btn btn-ghost" onClick={() => nav(editing ? `/admin/events/${id}` : "/admin")}>Annuler</button>
          </div>
        </form>
      </div>
    </div>
  );
}
