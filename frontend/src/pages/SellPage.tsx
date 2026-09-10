import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { priceApi } from "../api/priceApi";
import { scrapApi } from "../api/scrapApi";
import type { Scrap } from "../api/types";
import { Badge } from "../components/Badge";
import { useAuth } from "../lib/auth";
import { inr } from "../lib/format";

export function SellPage() {
  const { token, user } = useAuth();
  const nav = useNavigate();
  const [sellerType, setSellerType] = useState<"individual" | "business">(
    user?.role === "BUSINESS" ? "business" : "individual",
  );
  const [area, setArea] = useState("Whitefield");
  const [description, setDescription] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [materials, setMaterials] = useState<{ slug: string; name: string }[]>([]);
  const [slug, setSlug] = useState("copper");
  const [qty, setQty] = useState("10");
  const [listing, setListing] = useState<Scrap | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    priceApi.materials().then((m) => setMaterials(m)).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!files.length) {
      setPreviews([]);
      return;
    }
    const urls = files.map((file) => URL.createObjectURL(file));
    setPreviews(urls);
    localStorage.setItem(`scrap-photos-draft`, JSON.stringify(urls));
    return () => urls.forEach((url) => URL.revokeObjectURL(url));
  }, [files]);

  useEffect(() => {
    if (!listing) return;
    if (previews.length) {
      localStorage.setItem(`scrap-photos-${listing.id}`, JSON.stringify(previews));
    }
  }, [listing, previews]);

  const sellerLabel = useMemo(
    () => (sellerType === "business" ? "Business seller" : "Individual seller"),
    [sellerType],
  );

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    if (!token) {
      nav("/login");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      let current = listing ?? (await scrapApi.create(token, { location: "Bengaluru", area, description }));
      if (files.length) await scrapApi.upload(token, current.id, files);
      let identMsg: string | null = null;
      let identOk: boolean | null = null;
      try {
        const identified = await scrapApi.identify(token, current.id);
        identMsg = identified.identification_message;
        identOk = identified.identification_available;
      } catch {
        identMsg = "Automatic identification is currently unavailable. Select the material manually.";
      }
      current = await scrapApi.quantity(token, current.id, { quantity: Number(qty), unit: "kg", material_slug: slug });
      setListing({ ...current, identification_message: identMsg, identification_available: identOk });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save listing");
    } finally {
      setBusy(false);
    }
  }

  function onFileChange(e: ChangeEvent<HTMLInputElement>) {
    setFiles(Array.from(e.target.files ?? []));
  }

  if (user && user.role !== "CONSUMER" && user.role !== "BUSINESS" && user.role !== "ADMIN") {
    return <p>Sign in as a consumer or business account to list scrap.</p>;
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-end justify-between gap-4">
        <h1 className="font-display text-3xl font-bold">Sell scrap</h1>
        <div className="inline-flex rounded-full border border-line bg-white/60 p-1 text-sm">
          <button
            type="button"
            onClick={() => setSellerType("individual")}
            className={`rounded-full px-4 py-2 ${sellerType === "individual" ? "bg-emerald text-cream" : "text-muted"}`}
          >
            Individual seller
          </button>
          <button
            type="button"
            onClick={() => setSellerType("business")}
            className={`rounded-full px-4 py-2 ${sellerType === "business" ? "bg-emerald text-cream" : "text-muted"}`}
          >
            Business seller
          </button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <form onSubmit={onCreate} className="space-y-4 rounded-3xl border border-line bg-white/60 p-6 shadow-sm">
          <div className="rounded-2xl bg-forest px-4 py-3 text-sm text-cream">
            <p className="font-semibold">{sellerLabel}</p>
            <p className="mt-1 text-emerald-light">Quick pickup for homes and institutions.</p>
          </div>

          <label className="block text-sm">
            Area
            <input className="mt-1 w-full rounded-xl border border-line bg-cream px-3 py-2.5" value={area} onChange={(e) => setArea(e.target.value)} />
          </label>
          <label className="block text-sm">
            Description
            <textarea className="mt-1 w-full rounded-xl border border-line bg-cream px-3 py-2.5" value={description} onChange={(e) => setDescription(e.target.value)} />
          </label>
          <label className="block text-sm">
            Photos (optional)
            <input className="mt-1 w-full rounded-xl border border-dashed border-line bg-cream px-3 py-2 text-sm" type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={onFileChange} />
          </label>
          {previews.length ? (
            <div className="grid grid-cols-3 gap-2">
              {previews.map((src, index) => (
                <img key={`${src}-${index}`} src={src} alt={`Scrap upload ${index + 1}`} className="h-20 w-full rounded-xl object-cover" />
              ))}
            </div>
          ) : null}
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm">
              Material
              <select className="mt-1 w-full rounded-xl border border-line bg-cream px-3 py-2.5" value={slug} onChange={(e) => setSlug(e.target.value)}>
                {materials.map((m) => (
                  <option key={m.slug} value={m.slug}>
                    {m.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm">
              Quantity (kg)
              <input className="mt-1 w-full rounded-xl border border-line bg-cream px-3 py-2.5" type="number" min="0.1" step="0.1" value={qty} onChange={(e) => setQty(e.target.value)} />
            </label>
          </div>
          {error ? <p className="text-sm text-[#a0443a]">{error}</p> : null}
          <button disabled={busy} className="w-full rounded-full bg-emerald px-5 py-3 font-semibold text-cream">
            {busy ? "Saving…" : "Estimate and list"}
          </button>
        </form>

        <div className="space-y-4">
          <div className="rounded-3xl border border-line bg-forest p-5 text-cream shadow-sm">
            <p className="text-xs uppercase tracking-[0.2em] text-emerald-light">Pickup request</p>
            <h2 className="mt-3 font-display text-2xl font-bold">
              {sellerType === "business" ? "Institutional scrap pickup" : "Household scrap pickup"}
            </h2>
            <div className="mt-4 space-y-3 text-sm text-cream/80">
              <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
                <span>Location</span>
                <strong>{area}</strong>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
                <span>Material</span>
                <strong>{materials.find((m) => m.slug === slug)?.name ?? slug}</strong>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2">
                <span>Weight</span>
                <strong>{qty} kg</strong>
              </div>
            </div>
            <div className="mt-4 rounded-xl border border-emerald/40 bg-emerald/10 p-3 text-sm text-emerald-light">
              {sellerType === "business" ? "8 collectors nearby are ready for bulk pickup." : "3 trusted local collectors are nearby for quick pickup."}
            </div>
          </div>

          {listing ? (
            <div className="rounded-3xl border border-line bg-white/60 p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted">Listing {listing.id.slice(0, 8)}</p>
                <Badge>{listing.status}</Badge>
              </div>
              <p className="mt-3 text-2xl font-semibold">
                Estimate {inr(listing.estimated_low)} – {inr(listing.estimated_high)}
              </p>
              {listing.identification_message ? (
                <p className="mt-3 text-sm">
                  <Badge tone="warn">AI</Badge> {listing.identification_message}
                </p>
              ) : null}
              <button className="mt-4 w-full rounded-full bg-forest px-4 py-2.5 text-sm font-semibold text-cream" onClick={() => nav(`/offers?listing=${listing.id}`)}>
                View collector offers
              </button>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
