import { useEffect, useState } from "react";
import { adminApi } from "../api/adminApi";
import { useAuth } from "../lib/auth";

export function AdminPage() {
  const { token, user } = useAuth();
  const [users, setUsers] = useState<{ email: string; full_name: string; role: string }[]>([]);
  const [verifications, setVerifications] = useState<{ id: string; status: string; authority_name: string | null }[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || user?.role !== "ADMIN") return;
    Promise.all([adminApi.users(token), adminApi.verifications(token)])
      .then(([u, v]) => {
        setUsers(u);
        setVerifications(v);
      })
      .catch((e) => setError(e.message));
  }, [token, user]);

  if (user?.role !== "ADMIN") return <p>Admin only.</p>;

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Admin</h1>
      {error ? <p className="text-sm text-[#a0443a]">{error}</p> : null}
      <section>
        <h2 className="font-semibold">Users</h2>
        <ul className="mt-2 text-sm">
          {users.map((u) => (
            <li key={u.email}>
              {u.full_name} · {u.email} · {u.role}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2 className="font-semibold">Verifications</h2>
        <ul className="mt-2 space-y-2 text-sm">
          {verifications.map((v) => (
            <li key={v.id} className="flex items-center justify-between gap-3 rounded-lg border border-line px-3 py-2">
              <span>
                {v.authority_name ?? "Record"} · {v.status}
              </span>
              {token ? (
                <button
                  className="text-xs underline"
                  onClick={() => adminApi.review(token, v.id, "VERIFIED").then(() => adminApi.verifications(token).then(setVerifications))}
                >
                  Mark verified
                </button>
              ) : null}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
