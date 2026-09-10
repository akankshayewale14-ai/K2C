import { useEffect, useState } from "react";
import { recyclerApi } from "../api/recyclerApi";
import type { Recycler } from "../api/types";
import { Badge } from "../components/Badge";
import { useAuth } from "../lib/auth";

export function RecyclersPage() {
  const { token, user } = useAuth();
  const [rows, setRows] = useState<Recycler[]>([]);
  const [lots, setLots] = useState<{ lot_id: string; status: string; weight: number | null; id: string }[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    recyclerApi.list().then(setRows).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (token && (user?.role === "RECYCLER" || user?.role === "ADMIN")) {
      recyclerApi.lots(token).then(setLots).catch(() => undefined);
    }
  }, [token, user]);

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Recyclers</h1>
      {error ? <p className="text-sm text-[#a0443a]">{error}</p> : null}
      {lots.length ? (
        <section className="rounded-2xl border border-line p-4">
          <h2 className="font-semibold">Your lots</h2>
          <ul className="mt-2 text-sm">
            {lots.map((l) => (
              <li key={l.id}>
                {l.lot_id} · {l.status} · {l.weight ?? "—"} kg
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      <div className="grid gap-4 md:grid-cols-2">
        {rows.map((r) => (
          <article key={r.id} className="rounded-2xl border border-line bg-white/50 p-5">
            <h2 className="font-display text-xl">{r.organization_name}</h2>
            <p className="text-sm text-muted">{r.location}</p>
            <p className="mt-2 text-xs">{r.verification}</p>
            <p className="mt-1 text-xs text-muted">{r.verification_source}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {r.materials.map((m) => (
                <Badge key={m} tone="muted">
                  {m}
                </Badge>
              ))}
            </div>
            <p className="mt-3 text-sm">{r.pickup_available ? "Pickup available" : "Drop-off only"}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
