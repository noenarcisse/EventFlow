import { createContext, useContext, useEffect, useState } from "react";
import api from "./api";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("ef_token");
    if (!token) { setReady(true); return; }
    api.get("/api/auth/me")
      .then((r) => setUser(r.data))
      .catch(() => localStorage.removeItem("ef_token"))
      .finally(() => setReady(true));
  }, []);

  const login = async (email, password) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    const r = await api.post("/api/auth/token", form);
    localStorage.setItem("ef_token", r.data.access_token);
    const me = await api.get("/api/auth/me");
    setUser(me.data);
  };

  const register = async (email, password, full_name) => {
    await api.post("/api/auth/register", { email, password, full_name });
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem("ef_token");
    setUser(null);
  };

  return (
    <AuthCtx.Provider value={{ user, ready, login, register, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
