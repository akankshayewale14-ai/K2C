import { useEffect, useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { authApi } from "../api/authApi";
import type { Notification } from "../api/types";
import { useAuth } from "../lib/auth";

const links = [
  { to: "/prices", label: "Prices" },
  { to: "/sell", label: "Sell" },
  { to: "/offers", label: "Offers" },
  { to: "/pickup", label: "Pickup" },
  { to: "/track", label: "Track" },
  { to: "/collectors", label: "Collectors" },
  { to: "/traceability", label: "Trace" },
];

export function Layout() {
  const { user, token, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    if (!token) {
      setNotifications([]);
      return;
    }
    authApi
      .notifications(token)
      .then(setNotifications)
      .catch(() => setNotifications([]));
  }, [token]);

  return (
    <div className="min-h-screen bg-cream text-ink">
      <header className="sticky top-0 z-20 border-b border-line/60 bg-cream/90 backdrop-blur">
        <div className="mx-auto flex max-w-page items-center justify-between gap-4 px-4 py-3">
          <Link to="/" className="font-display text-lg font-extrabold tracking-tight">
            KABADIWALA2CONNECT
          </Link>
          <nav className="hidden items-center gap-4 lg:flex">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) => `text-sm ${isActive ? "text-emerald" : "text-muted hover:text-ink"}`}
              >
                {l.label}
              </NavLink>
            ))}
            {user?.role === "ADMIN" ? (
              <NavLink to="/admin" className={({ isActive }) => `text-sm ${isActive ? "text-emerald" : "text-muted"}`}>
                Admin
              </NavLink>
            ) : null}
          </nav>
          <div className="flex items-center gap-3">
            {user ? (
              <>
                {notifications.length ? (
                  <span className="hidden rounded-full bg-forest px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-cream sm:inline-flex">
                    {notifications[0].title}
                  </span>
                ) : null}
                <span className="hidden text-xs text-muted sm:inline">{user.full_name}</span>
                <button type="button" onClick={logout} className="text-sm text-forest underline">
                  Sign out
                </button>
              </>
            ) : (
              <Link to="/login" className="rounded-full bg-emerald px-4 py-2 text-sm font-semibold text-cream">
                Sign in
              </Link>
            )}
            <button type="button" className="lg:hidden" aria-label="Menu" onClick={() => setOpen((v) => !v)}>
              ☰
            </button>
          </div>
        </div>
        {open ? (
          <div className="flex flex-col gap-2 border-t border-line px-4 py-3 lg:hidden">
            {links.map((l) => (
              <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)} className="text-sm">
                {l.label}
              </NavLink>
            ))}
          </div>
        ) : null}
      </header>
      <main className="mx-auto w-full max-w-page px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-line px-4 py-8 text-sm text-muted">
        <div className="mx-auto max-w-page">
          Bengaluru recycling marketplace. Seeded prices are labeled DEMO until a live provider is configured.
        </div>
      </footer>
    </div>
  );
}
