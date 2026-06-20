import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { errMessage } from "../api";
import Logo from "../components/Logo";

export default function Login() {
  const { login, register } = useAuth();
  const nav = useNavigate();
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("client@eventflow.test");
  const [password, setPassword] = useState("client1234");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password, fullName);
      nav("/");
    } catch (err) {
      setError(errMessage(err, "Echec de l'authentification."));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container">
      <div className="center-narrow">
        <div className="panel">
          <div className="row" style={{ justifyContent: "center", marginBottom: 18 }}>
            <Logo size={44} />
          </div>
          <h2 style={{ textAlign: "center", marginBottom: 4 }}>
            {mode === "login" ? "Connexion" : "Creer un compte"}
          </h2>
          <p className="muted" style={{ textAlign: "center", marginBottom: 20, fontSize: 14 }}>
            Compte de demo pre-rempli ci-dessous.
          </p>
          <form onSubmit={submit}>
            {mode === "register" && (
              <div className="field">
                <label>Nom complet</label>
                <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
              </div>
            )}
            <div className="field">
              <label>Email</label>
              <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="field">
              <label>Mot de passe</label>
              <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            {error && <div className="notice notice-err" style={{ marginBottom: 12 }}>{error}</div>}
            <button className="btn btn-primary" style={{ width: "100%" }} disabled={busy}>
              {busy ? "..." : mode === "login" ? "Se connecter" : "Creer le compte"}
            </button>
          </form>
          <p className="muted" style={{ textAlign: "center", marginTop: 16, fontSize: 14 }}>
            {mode === "login" ? "Pas de compte ?" : "Deja inscrit ?"}{" "}
            <a style={{ color: "var(--violet)", cursor: "pointer", fontWeight: 600 }}
              onClick={() => setMode(mode === "login" ? "register" : "login")}>
              {mode === "login" ? "Creer un compte" : "Se connecter"}
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
