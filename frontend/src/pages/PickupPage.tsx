import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { pickupApi } from "../api/pickupApi";
import { priceApi } from "../api/priceApi";
import { scrapApi } from "../api/scrapApi";
import type { MapConfig, Pickup, Scrap } from "../api/types";
import { Badge } from "../components/Badge";
import { CityMap } from "../components/CityMap";
import { useAuth } from "../lib/auth";

export function PickupPage() {
  const { token, user } = useAuth();
  const [params] = useSearchParams();
  const [listings, setListings] = useState<Scrap[]>([]);
  const [listingId, setListingId] = useState(params.get("listing") ?? "");
  const [area, setArea] = useState("Whitefield");
  const [pickup, setPickup] = useState<Pickup | null>(null);
  const [map, setMap] = useState<MapConfig | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    priceApi.mapConfig().then(setMap).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!token) return;
    scrapApi.list(token).then(setListings).catch((e) => setError(e.message));
    const id = params.get("id");
    if (id) pickupApi.get(token, id).then(setPickup).catch((e) => setError(e.message));
  }, [token, params]);

  async function create(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    try {
      const row = await pickupApi.create(token, { listing_id: listingId, area, address: area });
      setPickup(row);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Pickup failed");
    }
  }

  async function advance(status: string) {
    if (!token || !pickup) return;
    try {
      setPickup(await pickupApi.status(token, pickup.id, status));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Status update failed");
    }
  }

  if (!token) return <p>Sign in to book pickup.</p>;

  const points =
    pickup?.lat && pickup.lng
      ? [{ lat: pickup.lat, lng: pickup.lng }]
      : [{ lat: 12.9698, lng: 77.75 }];

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="space-y-4">
        <h1 className="font-display text-3xl font-bold">Smart pickup</h1>
        <form onSubmit={create} className="space-y-3 rounded-2xl border border-line bg-white/50 p-5">
          <label className="block text-sm">
            Listing
            <select className="mt-1 w-full rounded-xl border border-[#2a2e2c] bg-[#f3f0ea] px-3 py-3 text-lg text-[#111827] shadow-none outline-none" value={listingId} onChange={(e) => setListingId(e.target.value)} required>
              <option value="">Select</option>
              {listings.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.area} · {l.status}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm">
            Area
            <input className="mt-1 w-full rounded-xl border border-line bg-[#f3f0ea] px-3 py-3 text-lg text-[#111827] placeholder:text-[#6b6864]" value={area} onChange={(e) => setArea(e.target.value)} />
          </label>
          {error ? <p className="text-sm text-[#a0443a]">{error}</p> : null}
          <button className="rounded-full bg-emerald px-4 py-2 text-sm font-semibold text-cream">Request pickup</button>
        </form>
        {pickup ? (
          <div className="rounded-2xl border border-line p-5">
            <p className="text-sm text-muted">Pickup {pickup.id}</p>
            <p className="mt-1 text-xl font-semibold">{pickup.status.replaceAll("_", " ")}</p>
            <p className="text-sm">
              {pickup.collector_name ?? "Unassigned"} · {pickup.vehicle_type ?? "vehicle TBD"}
            </p>
            {pickup.eta_minutes != null ? <p className="text-sm">ETA {pickup.eta_minutes} min</p> : null}
            <p className="mt-2 text-xs text-muted">{pickup.data_note}</p>
            {user?.role === "COLLECTOR" || user?.role === "ADMIN" ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {["CONFIRMED", "ON_THE_WAY", "ARRIVED", "COLLECTED", "COMPLETED"].map((s) => (
                  <button key={s} className="rounded-full border border-line px-3 py-1 text-xs" onClick={() => advance(s)}>
                    {s}
                  </button>
                ))}
              </div>
            ) : null}
            <Badge>{pickup.status}</Badge>
          </div>
        ) : null}
      </div>
      <div>
        <CityMap config={map} points={points} route={pickup?.route} />
        {map && !map.provider_configured ? <p className="mt-2 text-xs text-muted">{map.note}</p> : null}
      </div>
    </div>
  );
}
