import { FormEvent, useState } from "react";
import { pickupApi } from "../api/pickupApi";
import type { Pickup } from "../api/types";
import { useAuth } from "../lib/auth";

const steps = ["REQUESTED", "ASSIGNED", "CONFIRMED", "ON_THE_WAY", "ARRIVED", "COLLECTED", "COMPLETED"];

export function TrackPage() {
  const { token } = useAuth();
  const [id, setId] = useState("");
  const [pickup, setPickup] = useState<Pickup | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    try {
      setPickup(await pickupApi.get(token, id.trim()));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Not found");
    }
  }

  if (!token) return <p>Sign in to track a pickup.</p>;

  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold">Track pickup</h1>
      <form onSubmit={load} className="flex max-w-xl gap-2">
        <input
          className="flex-1 rounded-2xl border border-line bg-white px-4 py-3 text-xl text-ink outline-none placeholder:text-muted focus:border-emerald"
          placeholder="Pickup UUID"
          value={id}
          onChange={(e) => setId(e.target.value)}
        />
        <button className="rounded-full bg-emerald px-4 py-2 text-sm font-semibold text-cream">Load</button>
      </form>
      {error ? <p className="text-sm text-[#a0443a]">{error}</p> : null}
      {pickup ? (
        <ol className="space-y-3">
          {steps.map((s) => {
            const idx = steps.indexOf(pickup.status);
            const done = steps.indexOf(s) <= idx && pickup.status !== "CANCELLED";
            return (
              <li key={s} className={`rounded-xl border px-4 py-3 ${done ? "border-emerald bg-emerald/10" : "border-line"}`}>
                {s.replaceAll("_", " ")}
              </li>
            );
          })}
        </ol>
      ) : null}
    </div>
  );
}
