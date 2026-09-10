import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { priceApi } from "../api/priceApi";
import type { Price } from "../api/types";
import { Badge } from "../components/Badge";
import { dataBadge, inr } from "../lib/format";

export function PricesPage() {
  const [rows, setRows] = useState<Price[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState<Price | null>(null);

  useEffect(() => {
    priceApi
      .list()
      .then((data) => {
        setRows(data);
        setActive(data[0] ?? null);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="text-[#a0443a]">{error}</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl font-bold">Bengaluru prices</h1>
        <p className="text-sm text-muted">Every row shows its data type. DEMO means prototype seed tables, not a live exchange.</p>
      </div>
      <div className="overflow-x-auto rounded-2xl border border-line">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-white/60 text-muted">
            <tr>
              <th className="px-3 py-2">Material</th>
              <th>Low</th>
              <th>High</th>
              <th>Recommended</th>
              <th>Source</th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.material}
                className={`cursor-pointer border-t border-line ${active?.material === r.material ? "bg-emerald/10" : ""}`}
                onClick={() => setActive(r)}
              >
                <td className="px-3 py-2 font-medium">{r.material_name}</td>
                <td>{inr(r.low)}</td>
                <td>{inr(r.high)}</td>
                <td>{inr(r.recommended)}</td>
                <td className="max-w-[220px] truncate">{r.source}</td>
                <td>
                  <Badge tone={r.is_live ? "ok" : "demo"}>{dataBadge(r.data_type)}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {active ? (
        <div className="rounded-2xl border border-line bg-white/40 p-4">
          <h2 className="font-display text-xl">{active.material_name} range</h2>
          <p className="text-sm text-muted">
            Confidence {active.confidence != null ? `${Math.round(active.confidence * 100)}%` : "n/a"} · retrieved {new Date(active.retrieved_at).toLocaleString("en-IN")}
          </p>
          <div className="mt-4 h-56">
            <ResponsiveContainer>
              <LineChart data={active.chart_points.map((v, i) => ({ i, v }))}>
                <XAxis dataKey="i" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="v" stroke="#3D7A5F" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          {active.neighborhoods.length ? (
            <ul className="mt-4 grid gap-2 md:grid-cols-2">
              {active.neighborhoods.map((n) => (
                <li key={n.area} className="flex justify-between text-sm">
                  <span>{n.area}</span>
                  <span>
                    {inr(n.price)} <Badge>{dataBadge(n.data_type)}</Badge>
                  </span>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
