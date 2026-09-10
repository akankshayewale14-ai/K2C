import { useEffect, useState } from "react";
import { collectorApi } from "../api/collectorApi";
import { priceApi } from "../api/priceApi";
import type { Collector, MapConfig, MarketRequest } from "../api/types";
import { Badge } from "../components/Badge";
import { CityMap } from "../components/CityMap";
import { useAuth } from "../lib/auth";
import { inr } from "../lib/format";

type Dash = {
  name: string;
  available_pickups: number;
  expected_earnings: number;
  completed_pickups: number;
  rating: number | null;
  verification: string;
  jobs: { id: string; status: string; area: string | null; eta_minutes: number | null }[];
};

export function CollectorsPage() {
  const { token, user } = useAuth();
  const [rows, setRows] = useState<Collector[]>([]);
  const [dash, setDash] = useState<Dash | null>(null);
  const [requests, setRequests] = useState<MarketRequest[]>([]);
  const [map, setMap] = useState<MapConfig | null>(null);
  const [routeNote, setRouteNote] = useState<string | null>(null);

  useEffect(() => {
    collectorApi.list().then(setRows).catch(() => undefined);
    priceApi.mapConfig().then(setMap).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (token && (user?.role === "COLLECTOR" || user?.role === "ADMIN")) {
      collectorApi.dashboard(token).then((d) => setDash(d as Dash)).catch(() => undefined);
      collectorApi.marketRequests(token).then(setRequests).catch(() => undefined);
    }
  }, [token, user]);

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Collector network</h1>
      {dash ? (
        <section className="rounded-2xl border border-line bg-forest p-5 text-cream">
          <h2 className="font-display text-2xl">{dash.name}</h2>
          <p className="text-sm text-emerald-light">{dash.verification}</p>
          <p className="mt-2">
            Open jobs {dash.available_pickups} · Expected {inr(dash.expected_earnings)} · Completed {dash.completed_pickups}
          </p>
          <button
            className="mt-3 rounded-full bg-cream px-4 py-2 text-sm font-semibold text-forest"
            onClick={async () => {
              if (!token) return;
              const r = await collectorApi.route(token);
              setRouteNote(`${r.method}: ${r.total_distance_km} km · ${r.data_note}`);
            }}
          >
            Optimize today&apos;s route
          </button>
          {routeNote ? <p className="mt-2 text-xs">{routeNote}</p> : null}
        </section>
      ) : null}

      {token && (user?.role === "COLLECTOR" || user?.role === "ADMIN") ? (
        <section className="rounded-3xl border border-line bg-white/70 p-5 shadow-sm">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-muted">Marketplace</p>
              <h2 className="font-display text-2xl font-bold">Seller pickup requests</h2>
            </div>
            <Badge>{String(requests.length)}</Badge>
          </div>
          {requests.length ? (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {requests.map((r) => (
                <article key={r.id} className="rounded-2xl border border-line bg-cream p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-display text-xl">{r.seller_name}</h3>
                      <p className="text-sm text-muted">{r.seller_type}</p>
                    </div>
                    <span className="rounded-full bg-emerald/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.15em] text-emerald">
                      {r.status}
                    </span>
                  </div>
                  <p className="mt-3 text-sm text-muted">{r.area}</p>
                  <p className="mt-2 text-lg font-semibold text-ink">
                    {r.material_name} · {r.quantity ?? 0} {r.unit}
                  </p>
                  <p className="mt-2 line-clamp-3 text-sm text-muted">{r.description}</p>
                  <div className="mt-3 rounded-xl bg-white p-3 text-sm text-muted">
                    <div className="flex items-center justify-between">
                      <span>Location</span>
                      <strong className="text-ink">{r.location || r.area}</strong>
                    </div>
                    <div className="mt-2 flex items-center justify-between">
                      <span>Photos</span>
                      <strong className="text-ink">{r.photo_count}</strong>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <p className="rounded-2xl border border-dashed border-line bg-cream p-4 text-sm text-muted">
              No active seller requests right now. New pickup requests will appear here when a seller lists scrap.
            </p>
          )}
        </section>
      ) : null}

      <CityMap
        config={map}
        points={rows.filter((r) => r.lat && r.lng).map((r) => ({ lat: r.lat as number, lng: r.lng as number }))}
      />
      <div className="grid gap-4 md:grid-cols-2">
        {rows.map((c) => (
          <article key={c.id} className="rounded-2xl border border-line p-5">
            <h2 className="font-display text-xl">{c.name}</h2>
            <p className="text-sm text-muted">
              {c.vehicle_type} · {c.service_areas.join(", ")}
            </p>
            <p className="mt-2 text-sm">Rating {c.rating ?? "—"} · {c.completed_pickups} pickups</p>
            <Badge>{c.verification}</Badge>
          </article>
        ))}
      </div>
    </div>
  );
}
