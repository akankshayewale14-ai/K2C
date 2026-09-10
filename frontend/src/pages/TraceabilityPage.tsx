import { FormEvent, useState } from "react";
import { traceabilityApi } from "../api/traceabilityApi";
import type { Trace } from "../api/types";
import { Badge } from "../components/Badge";
import { dataBadge } from "../lib/format";

export function TraceabilityPage() {
  const [lotId, setLotId] = useState("BLR-EW-2026-00827");
  const [trace, setTrace] = useState<Trace | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load(e: FormEvent) {
    e.preventDefault();
    try {
      setTrace(await traceabilityApi.get(lotId.trim()));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lot not found");
      setTrace(null);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Traceability</h1>
      <form onSubmit={load} className="flex max-w-xl gap-2">
        <input className="flex-1 rounded-lg border border-line px-3 py-2" value={lotId} onChange={(e) => setLotId(e.target.value)} />
        <button className="rounded-full bg-emerald px-4 py-2 text-sm font-semibold text-cream">Look up</button>
      </form>
      {error ? <p className="text-sm text-[#a0443a]">{error}</p> : null}
      {trace ? (
        <div>
          <p className="text-lg font-semibold">
            {trace.lot_id} · {trace.current_status} <Badge>{dataBadge(trace.data_type)}</Badge>
          </p>
          <p className="text-sm text-muted">
            {trace.initial_weight} kg listed → {trace.current_weight} kg now
          </p>
          <ol className="mt-4 space-y-3">
            {trace.events.map((ev, i) => (
              <li key={`${ev.event_type}-${i}`} className="rounded-xl border border-line p-4">
                <p className="font-medium">{ev.event_type}</p>
                <p className="text-sm text-muted">
                  {new Date(ev.timestamp).toLocaleString("en-IN")} · {ev.location} · {ev.weight ?? "—"} kg
                </p>
                <p className="text-sm">{ev.notes}</p>
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </div>
  );
}
