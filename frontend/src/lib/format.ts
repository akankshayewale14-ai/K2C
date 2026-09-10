export function inr(value: number | null | undefined) {
  if (value == null || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value);
}

export function dataBadge(type?: string) {
  return type === "LIVE" ? "LIVE" : type === "HISTORICAL" ? "HISTORICAL" : "DEMO";
}
