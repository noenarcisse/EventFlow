import { Link, useNavigate } from "react-router-dom";
import Logo from "./Logo";
import { useAuth } from "../auth";

export default function NavBar() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  return (
    <nav className="nav">
      <div className="container nav-inner">
        <Link to="/" className="brand">
          <Logo />
          <span>event<span className="v">flow</span></span>
        </Link>
        <div className="nav-spacer" />
        <Link to="/" className="link">Evenements</Link>
        {user && <Link to="/tickets" className="link">Mes billets</Link>}
        {user && ["organizer", "admin"].includes(user.role) && (
          <Link to="/admin" className="link"><i className="fa-solid fa-gauge-high" /> Back-office</Link>
        )}
        {user ? (
          <>
            <span className="muted" style={{ fontSize: 14 }}>
              <i className="fa-regular fa-circle-user" /> {user.full_name || user.email}
            </span>
            <button className="btn btn-ghost btn-sm" onClick={() => { logout(); nav("/"); }}>
              Deconnexion
            </button>
          </>
        ) : (
          <Link to="/login" className="btn btn-primary btn-sm">Connexion</Link>
        )}
      </div>
    </nav>
  );
}
