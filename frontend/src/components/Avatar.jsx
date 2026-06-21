export default function Avatar({ user, size = 36 }) {
  const label = user?.full_name || user?.email || "?";
  const initials = label.trim().split(/\s+/).map((w) => w[0]).slice(0, 2).join("").toUpperCase();
  if (user?.avatar) {
    return (
      <img src={user.avatar} alt={label}
        style={{ width: size, height: size, borderRadius: "50%", objectFit: "cover", flex: "none" }} />
    );
  }
  return (
    <div className="avatar-fallback" style={{ width: size, height: size, fontSize: Math.round(size * 0.4) }}>
      {initials}
    </div>
  );
}
