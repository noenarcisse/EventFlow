import { Link } from "react-router-dom";
import { dayMonth } from "../api";
import Logo from "./Logo";

export default function EventCard({ ev }) {
  const dm = dayMonth(ev.starts_at);
  return (
    <Link to={`/events/${ev.id}`} className="card">
      <div className="cover" style={{ background: ev.cover_color }}>
        <div className="date"><div className="d">{dm.d}</div><div className="m">{dm.m}</div></div>
        <div className="mark"><Logo size={34} /></div>
      </div>
      <div className="card-body">
        <h3>{ev.title}</h3>
        <div className="meta"><i className="fa-solid fa-location-dot" /> {ev.city}</div>
        <div className="meta"><i className="fa-regular fa-calendar" /> {ev.venue}</div>
        <div className="card-foot">
          <span className="badge b-violet"><i className="fa-solid fa-ticket" /> Billets</span>
          <span className="muted" style={{ fontSize: 14 }}>Voir <i className="fa-solid fa-arrow-right-long" /></span>
        </div>
      </div>
    </Link>
  );
}
