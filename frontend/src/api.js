import axios from "axios";

const api = axios.create({ baseURL: "/" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("ef_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;

export const toDate = (s) => {
  if (!s) return new Date(NaN);
  const hasTz = /[zZ]$|[+-]\d{2}:?\d{2}$/.test(s);
  return new Date(hasTz ? s : s + "Z");
};

export const euros = (cents) =>
  (cents / 100).toLocaleString("fr-BE", { style: "currency", currency: "EUR" });

export const fmtDate = (iso) =>
  toDate(iso).toLocaleDateString("fr-BE", { day: "2-digit", month: "short", year: "numeric" });

export const dayMonth = (iso) => {
  const d = toDate(iso);
  return {
    d: d.toLocaleDateString("fr-BE", { day: "2-digit" }),
    m: d.toLocaleDateString("fr-BE", { month: "short" }),
  };
};

export function errMessage(err, fallback = "Une erreur est survenue.") {
  const d = err?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((e) => e?.msg || JSON.stringify(e)).join(" - ");
  if (d && typeof d === "object") return d.msg || JSON.stringify(d);
  if (err?.message) return err.message;
  return fallback;
}

export async function downloadTicket(orderId) {
  const r = await api.get(`/api/orders/${orderId}/ticket`, { responseType: "blob" });
  const url = URL.createObjectURL(r.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = `eventflow-REF-${String(orderId).padStart(5, "0")}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
