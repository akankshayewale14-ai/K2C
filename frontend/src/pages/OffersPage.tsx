import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { offersApi } from "../api/offersApi";
import { scrapApi } from "../api/scrapApi";
import type { Offer, Scrap } from "../api/types";
import { Badge } from "../components/Badge";
import { useAuth } from "../lib/auth";
import { dataBadge, inr } from "../lib/format";

export function OffersPage() {
  const { token } = useAuth();
  const [params] = useSearchParams();
  const nav = useNavigate();
  const [listings, setListings] = useState<Scrap[]>([]);
  const [listingId, setListingId] = useState(params.get("listing") ?? "");
  const [offers, setOffers] = useState<Offer[]>([]);
  const [photoUrls, setPhotoUrls] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!token) return;
    scrapApi.list(token).then(setListings).catch((e) => setError(e.message));
  }, [token]);

  useEffect(() => {
    if (!token || !listingId) return;
    offersApi
      .list(token, listingId)
      .then(setOffers)
      .catch((e) => setError(e.message));

    try {
      const raw = localStorage.getItem(`scrap-photos-${listingId}`);
      setPhotoUrls(raw ? JSON.parse(raw) : []);
    } catch {
      setPhotoUrls([]);
    }
  }, [token, listingId]);

  const selectedListing = useMemo(
    () => listings.find((listing) => listing.id === listingId) ?? null,
    [listingId, listings],
  );

  async function accept(id: string) {
    if (!token) return;
    setBusy(true);
    try {
      await offersApi.accept(token, id);
      nav(`/pickup?listing=${listingId}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Accept failed");
    } finally {
      setBusy(false);
    }
  }

  if (!token) return <p>Sign in to compare offers.</p>;

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Collector offers</h1>
      <label className="block max-w-md text-sm">
        Listing
        <select className="mt-1 w-full rounded-xl border border-line bg-white px-3 py-2.5" value={listingId} onChange={(e) => setListingId(e.target.value)}>
          <option value="">Select a listing</option>
          {listings.map((l) => (
            <option key={l.id} value={l.id}>
              {l.area} · {l.status} · {l.id.slice(0, 8)}
            </option>
          ))}
        </select>
      </label>
      {error ? <p className="text-sm text-[#a0443a]">{error}</p> : null}

      {selectedListing ? (
        <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <aside className="rounded-3xl border border-line bg-forest p-5 text-cream">
            <p className="text-xs uppercase tracking-[0.2em] text-emerald-light">Seller request</p>
            <h2 className="mt-3 font-display text-2xl font-bold">{selectedListing.area ?? "Bengaluru"}</h2>
            {photoUrls.length ? (
              <div className="mt-4 grid grid-cols-3 gap-2">
                {photoUrls.map((src, index) => (
                  <img key={`${src}-${index}`} src={src} alt="Seller scrap preview" className="h-20 w-full rounded-xl object-cover" />
                ))}
              </div>
            ) : (
              <div className="mt-4 rounded-xl border border-dashed border-white/20 bg-white/5 p-3 text-sm text-cream/80">
                Seller photo not uploaded yet. Scrap details are ready for pickup coordination.
              </div>
            )}
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl bg-white/5 p-3">
                <p className="text-emerald-light">Material</p>
                <p className="mt-2 font-semibold">Scrap mix</p>
              </div>
              <div className="rounded-xl bg-white/5 p-3">
                <p className="text-emerald-light">Quantity</p>
                <p className="mt-2 font-semibold">{selectedListing.quantity ?? 0} kg</p>
              </div>
              <div className="rounded-xl bg-white/5 p-3">
                <p className="text-emerald-light">Pickup</p>
                <p className="mt-2 font-semibold">{selectedListing.area ?? "Local"}</p>
              </div>
              <div className="rounded-xl bg-white/5 p-3">
                <p className="text-emerald-light">Status</p>
                <p className="mt-2 font-semibold">{selectedListing.status}</p>
              </div>
            </div>
            <div className="mt-4 rounded-xl border border-emerald/40 bg-emerald/10 p-3 text-sm text-emerald-light">
              Seller type: {selectedListing.status === "PROCESSING" ? "Business or household pickup" : "Active seller"}
            </div>
          </aside>

          <div className="rounded-3xl border border-line bg-white/60 p-5">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-2xl font-bold">Collector pickup options</h2>
              <Badge>{`${offers.length} live`}</Badge>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {offers.map((o) => (
                <article key={o.id} className="rounded-2xl border border-line bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-display text-xl">{o.name}</h3>
                      <p className="text-sm text-muted">
                        {o.buyer_type} · {o.eta_label}
                        {o.distance_km != null ? ` · ${o.distance_km} km` : ""}
                      </p>
                    </div>
                    <Badge>{dataBadge(o.data_type)}</Badge>
                  </div>

                  <div className="mt-4 rounded-xl bg-[#f2efe9] p-3">
                    <div className="flex items-center justify-between text-sm text-muted">
                      <span>Pickup ETA</span>
                      <span className="font-semibold text-ink">{o.eta_label}</span>
                    </div>
                    <div className="mt-2 flex items-end justify-between">
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-muted">Offer</p>
                        <p className="text-2xl font-bold text-ink">{inr(o.price_per_unit)}</p>
                      </div>
                      <span className="rounded-full bg-emerald/10 px-2 py-1 text-xs font-semibold text-emerald">Score {o.score.toFixed(2)}</span>
                    </div>
                  </div>

                  <p className="mt-3 text-xs text-muted">{o.verification}</p>
                  <p className="mt-1 text-xs">Status {o.status}</p>
                  <button
                    disabled={busy || o.status !== "ACTIVE"}
                    onClick={() => accept(o.id)}
                    className="mt-4 w-full rounded-full bg-emerald px-4 py-2.5 text-sm font-semibold text-cream disabled:opacity-50"
                  >
                    Accept offer
                  </button>
                </article>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
