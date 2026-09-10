export function Badge({ children, tone = "demo" }: { children: string; tone?: "demo" | "ok" | "warn" | "muted" }) {
  const cls =
    tone === "ok"
      ? "bg-emerald/15 text-forest"
      : tone === "warn"
        ? "bg-amber/15 text-amber"
        : tone === "muted"
          ? "bg-line/40 text-muted"
          : "bg-stone/20 text-ink";
  return <span className={`inline-flex rounded-full px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide ${cls}`}>{children}</span>;
}
