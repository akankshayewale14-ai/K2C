import { FormEvent, useState } from "react";
import { businessApi } from "../api/businessApi";
import type { Bulk } from "../api/types";
import { Badge } from "../components/Badge";
import { useAuth } from "../lib/auth";
import { dataBadge, inr } from "../lib/format";

export function BusinessPage() {
  const { token, user } = useAuth();
  const [orgType, setOrgType] = useState("IT company");
  const [location, setLocation] = useState("Whitefield IT Park");
  const [slug, setSlug] = useState("cardboard");
  const [qty, setQty] = useState("400");
  const [row, setRow] = useState<Bulk | null>(null);
  const [bids, setBids] = useState<{ id: string; amount: number; notes: string | null }[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    try {
      const created = await businessApi.create(token, {
        organization_type: orgType,
        pickup_location: location,
        materials: [{ slug, quantity: Number(qty) }],
      });
      setRow(created);
      setBids(await businessApi.offers(token, created.id));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create request");
    }
  }

  if (!token) return <p>Sign in as the business demo account (itpark@kabadiwala.local) to create bulk requests.</p>;
  if (user && user.role !== "BUSINESS" && user.role !== "ADMIN") {
    return <p>This workflow is for business accounts.</p>;
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="font-display text-3xl font-bold">Institutional bulk pickup</h1>
      <form onSubmit={submit} className="space-y-3 rounded-2xl border border-line p-5">
        <label className="block text-sm">
          Organization type
          <input className="mt-1 w-full rounded-lg border border-line px-3 py-2" value={orgType} onChange={(e) => setOrgType(e.target.value)} />
        </label>
        <label className="block text-sm">
          Pickup location
          <input className="mt-1 w-full rounded-lg border border-line px-3 py-2" value={location} onChange={(e) => setLocation(e.target.value)} />
        </label>
        <label className="block text-sm">
          Material slug
          <input className="mt-1 w-full rounded-lg border border-line px-3 py-2" value={slug} onChange={(e) => setSlug(e.target.value)} />
        </label>
        <label className="block text-sm">
          Quantity
          <input className="mt-1 w-full rounded-lg border border-line px-3 py-2" value={qty} onChange={(e) => setQty(e.target.value)} />
        </label>
        {error ? <p className="text-sm text-[#a0443a]">{error}</p> : null}
        <button className="rounded-full bg-emerald px-4 py-2 font-semibold text-cream">Submit request</button>
      </form>
      {row ? (
        <div className="rounded-2xl border border-line p-5">
          <p>
            Status {row.status} <Badge>{dataBadge(row.data_type)}</Badge>
          </p>
          <p className="mt-1">
            Estimate {inr(row.estimated_low)} – {inr(row.estimated_high)}
          </p>
          <p className="mt-2 text-sm text-muted">{bids.length ? `${bids.length} bids received` : "No bids received yet."}</p>
        </div>
      ) : null}
    </div>
  );
}
