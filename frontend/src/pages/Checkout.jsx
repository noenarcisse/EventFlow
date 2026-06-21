import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import api, { euros, errMessage, toDate } from "../api";

const TEST_OK = "4242 4242 4242 4242";
const TEST_KO = "4000 0000 0000 0002";

function useCountdown(expiresAt) {
  const [left, setLeft] = useState(0);
  useEffect(() => {
    if (!expiresAt) return;
    const tick = () => setLeft(Math.max(0, Math.floor((toDate(expiresAt) - new Date()) / 1000)));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [expiresAt]);
  return left;
}

const formatCard = (v) => v.replace(/\D/g, "").slice(0, 19).replace(/(.{4})/g, "$1 ").trim();
const formatExp = (v) => {
  const d = v.replace(/\D/g, "").slice(0, 4);
  return d.length >= 3 ? `${d.slice(0, 2)}/${d.slice(2)}` : d;
};

export default function Checkout() {
  const { orderId } = useParams();
  const nav = useNavigate();
  const [order, setOrder] = useState(null);
  const [loadErr, setLoadErr] = useState("");
  const [card, setCard] = useState(TEST_OK);
  const [exp, setExp] = useState("12/30");
  const [cvc, setCvc] = useState("123");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [bugMode, setBugMode] = useState(false);
  const loaded = useRef(false);

  useEffect(() => {
    api.get(`/api/orders/${orderId}`)
      .then((r) => { setOrder(r.data); loaded.current = true; })
      .catch((e) => setLoadErr(errMessage(e, "Commande introuvable.")));
    api.get("/api/config").then((r) => setBugMode(Boolean(r.data?.seed_bugs))).catch(() => {});
  }, [orderId]);

  const left = useCountdown(order?.expires_at);
  const mmss = useMemo(() => {
    const m = String(Math.floor(left / 60)).padStart(2, "0");
    const s = String(left % 60).padStart(2, "0");
    return `${m}:${s}`;
  }, [left]);

  if (loadErr) return <div className="container"><div className="center-narrow"><div className="notice notice-err">{loadErr}</div></div></div>;
  if (!order) return <div className="container"><p className="muted" style={{ marginTop: 30 }}>Chargement...</p></div>;

  if (order.status === "paid") {
    nav(`/confirmation/${order.id}`, { replace: true });
    return null;
  }
  const expired = order.status !== "pending" || left <= 0;

  const pay = async (e) => {
    e.preventDefault();
    // BUG B12 (fil rouge): quand le mode bug est actif, le clic de paiement est
    // parfois ignore (bouton "parfois inactif") -> cible ideale pour tester le flaky.
    if (bugMode && Math.random() < 0.35) return;
    setError("");
    const [mm, yy] = exp.split("/");
    if (!mm || !yy) { setError("Date d'expiration invalide."); return; }
    setBusy(true);
    try {
      await api.post(`/api/orders/${order.id}/pay`, {
        card_number: card,
        exp_month: parseInt(mm, 10),
        exp_year: 2000 + parseInt(yy, 10),
        cvc,
        cardholder: name,
      });
      nav(`/confirmation/${order.id}`, { replace: true });
    } catch (err) {
      setError(errMessage(err, "Paiement refuse."));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container" style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 28, alignItems: "start", marginTop: 28 }}>
      <div>
        <h1 className="page-title" style={{ marginTop: 0 }}>Paiement</h1>
        <p className="subtitle">Paiement securise simule &mdash; aucune vraie transaction.</p>

        <div className="panel">
          <div className="cc">
            <div className="cc-top">
              <i className="fa-solid fa-wifi" style={{ transform: "rotate(90deg)" }} aria-hidden="true" />
              <span className="cc-brand">eventpay</span>
            </div>
            <div className="cc-number mono">{card || "•••• •••• •••• ••••"}</div>
            <div className="cc-bottom">
              <span>{name || "NOM DU TITULAIRE"}</span>
              <span className="mono">{exp || "MM/AA"}</span>
            </div>
          </div>

          <form onSubmit={pay} style={{ marginTop: 20 }}>
            <div className="field">
              <label>Numero de carte</label>
              <input className="input mono" inputMode="numeric" value={card}
                onChange={(e) => setCard(formatCard(e.target.value))} placeholder="4242 4242 4242 4242" required />
            </div>
            <div className="field">
              <label>Titulaire</label>
              <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Camille Client" required />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div className="field">
                <label>Expiration</label>
                <input className="input mono" value={exp} onChange={(e) => setExp(formatExp(e.target.value))} placeholder="MM/AA" required />
              </div>
              <div className="field">
                <label>CVC</label>
                <input className="input mono" inputMode="numeric" value={cvc}
                  onChange={(e) => setCvc(e.target.value.replace(/\D/g, "").slice(0, 4))} placeholder="123" required />
              </div>
            </div>

            {error && <div className="notice notice-err" style={{ marginBottom: 12 }}>{error}</div>}

            <button className="btn btn-primary" style={{ width: "100%" }} disabled={busy || expired}>
              <i className="fa-solid fa-lock" /> {busy ? "Traitement..." : `Payer ${euros(order.total_cents)}`}
            </button>
          </form>

          <div className="notice" style={{ background: "#ECE7FE", color: "#4A32C0", marginTop: 14, fontSize: 13 }}>
            <strong>Cartes de test</strong> &mdash; succes : {TEST_OK} &middot; refus : {TEST_KO}. Date future et CVC libres.
          </div>
        </div>
      </div>

      <div className="panel">
        <h3 style={{ marginBottom: 10 }}>Votre commande</h3>
        <div style={{ fontWeight: 600 }}>{order.event_title}</div>
        <div className="meta" style={{ marginBottom: 12 }}><i className="fa-solid fa-location-dot" /> {order.event_city}</div>
        {order.items.map((it) => (
          <div className="cat-row" key={it.category_id}>
            <span>{it.quantity} &times; {it.category_name}</span>
            <span className="mono">{euros(it.unit_price_cents * it.quantity)}</span>
          </div>
        ))}
        <div className="row" style={{ justifyContent: "space-between", marginTop: 14 }}>
          <span className="muted">Total</span>
          <span className="price">{euros(order.total_cents)}</span>
        </div>
        <div className={`notice ${expired ? "notice-err" : ""}`} style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 8, background: expired ? undefined : "#DDF7EF", color: expired ? undefined : "#0E6B53" }}>
          <i className={`fa-regular ${expired ? "fa-circle-xmark" : "fa-clock"}`} />
          {expired ? "Reservation expiree" : `Reservation tenue encore ${mmss}`}
        </div>
        {expired && (
          <button className="btn btn-ghost" style={{ width: "100%", marginTop: 12 }} onClick={() => nav(`/events/${order.event_id}`)}>
            Retour a l'evenement
          </button>
        )}
      </div>
    </div>
  );
}
