import { useRef, useState } from "react";
import api, { errMessage } from "../api";
import { useAuth } from "../auth";
import Avatar from "../components/Avatar";

function resizeImage(file, size = 256) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext("2d");
        const min = Math.min(img.width, img.height);
        const sx = (img.width - min) / 2;
        const sy = (img.height - min) / 2;
        ctx.drawImage(img, sx, sy, min, min, 0, 0, size, size);
        resolve(canvas.toDataURL("image/jpeg", 0.85));
      };
      img.onerror = reject;
      img.src = reader.result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export default function Profile() {
  const { user, updateUser } = useAuth();
  const fileRef = useRef(null);

  const [info, setInfo] = useState({ full_name: user.full_name || "", phone: user.phone || "" });
  const [infoMsg, setInfoMsg] = useState(null);
  const [avatarMsg, setAvatarMsg] = useState(null);
  const [pwd, setPwd] = useState({ current: "", next: "", confirm: "" });
  const [pwdMsg, setPwdMsg] = useState(null);
  const [busy, setBusy] = useState(false);

  const saveInfo = async (e) => {
    e.preventDefault(); setInfoMsg(null); setBusy(true);
    try {
      const r = await api.patch("/api/auth/me", { full_name: info.full_name, phone: info.phone });
      updateUser(r.data);
      setInfoMsg({ ok: true, text: "Informations mises a jour." });
    } catch (err) {
      setInfoMsg({ ok: false, text: errMessage(err) });
    } finally { setBusy(false); }
  };

  const onAvatar = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarMsg(null);
    try {
      const dataUrl = await resizeImage(file);
      const r = await api.post("/api/auth/me/avatar", { avatar: dataUrl });
      updateUser(r.data);
      setAvatarMsg({ ok: true, text: "Photo mise a jour." });
    } catch (err) {
      setAvatarMsg({ ok: false, text: errMessage(err) });
    } finally {
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const removeAvatar = async () => {
    setAvatarMsg(null);
    try {
      const r = await api.delete("/api/auth/me/avatar");
      updateUser(r.data);
    } catch (err) { setAvatarMsg({ ok: false, text: errMessage(err) }); }
  };

  const changePwd = async (e) => {
    e.preventDefault(); setPwdMsg(null);
    if (pwd.next !== pwd.confirm) { setPwdMsg({ ok: false, text: "La confirmation ne correspond pas." }); return; }
    if (pwd.next.length < 8) { setPwdMsg({ ok: false, text: "8 caracteres minimum." }); return; }
    setBusy(true);
    try {
      await api.post("/api/auth/change-password", { current_password: pwd.current, new_password: pwd.next });
      setPwd({ current: "", next: "", confirm: "" });
      setPwdMsg({ ok: true, text: "Mot de passe modifie." });
    } catch (err) {
      setPwdMsg({ ok: false, text: errMessage(err) });
    } finally { setBusy(false); }
  };

  const Note = ({ msg }) => msg ? <div className={`notice ${msg.ok ? "notice-ok" : "notice-err"}`} style={{ marginTop: 12 }}>{msg.text}</div> : null;

  return (
    <div className="container">
      <h1 className="page-title">Mon profil</h1>
      <p className="subtitle">Gerez votre photo, vos informations et votre mot de passe.</p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, alignItems: "start" }}>
        <div className="panel">
          <h3 style={{ marginBottom: 14 }}>Photo de profil</h3>
          <div className="row" style={{ gap: 16 }}>
            <Avatar user={user} size={84} />
            <div className="row" style={{ gap: 10 }}>
              <button className="btn btn-ghost btn-sm" onClick={() => fileRef.current?.click()}><i className="fa-solid fa-upload" /> Changer</button>
              {user.avatar && <button className="btn btn-ghost btn-sm" onClick={removeAvatar}><i className="fa-solid fa-trash" /> Retirer</button>}
            </div>
            <input ref={fileRef} type="file" accept="image/*" hidden onChange={onAvatar} />
          </div>
          <p className="muted" style={{ fontSize: 12, marginTop: 12 }}>JPG ou PNG, recadree automatiquement en carre.</p>
          <Note msg={avatarMsg} />
        </div>

        <form className="panel" onSubmit={saveInfo}>
          <h3 style={{ marginBottom: 14 }}>Informations</h3>
          <div className="field"><label>Adresse email</label>
            <input className="input" value={user.email} disabled style={{ opacity: .7 }} />
            <span className="muted" style={{ fontSize: 12 }}>L'adresse email ne peut pas etre modifiee.</span>
          </div>
          <div className="field"><label>Nom complet</label>
            <input className="input" value={info.full_name} onChange={(e) => setInfo({ ...info, full_name: e.target.value })} required />
          </div>
          <div className="field"><label>Telephone</label>
            <input className="input" value={info.phone} onChange={(e) => setInfo({ ...info, phone: e.target.value })} placeholder="+32 ..." />
          </div>
          <button className="btn btn-primary" disabled={busy}><i className="fa-solid fa-floppy-disk" /> Enregistrer</button>
          <Note msg={infoMsg} />
        </form>

        <form className="panel" onSubmit={changePwd}>
          <h3 style={{ marginBottom: 14 }}>Mot de passe</h3>
          <div className="field"><label>Mot de passe actuel</label>
            <input className="input" type="password" value={pwd.current} onChange={(e) => setPwd({ ...pwd, current: e.target.value })} required />
          </div>
          <div className="field"><label>Nouveau mot de passe</label>
            <input className="input" type="password" value={pwd.next} onChange={(e) => setPwd({ ...pwd, next: e.target.value })} required />
          </div>
          <div className="field"><label>Confirmer</label>
            <input className="input" type="password" value={pwd.confirm} onChange={(e) => setPwd({ ...pwd, confirm: e.target.value })} required />
          </div>
          <button className="btn btn-primary" disabled={busy}><i className="fa-solid fa-key" /> Modifier le mot de passe</button>
          <Note msg={pwdMsg} />
        </form>
      </div>
    </div>
  );
}
