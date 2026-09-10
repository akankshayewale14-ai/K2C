import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="space-y-16">
      <section className="grid gap-8 lg:grid-cols-2 lg:items-center">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald">Bengaluru</p>
          <h1 className="mt-3 font-display text-4xl font-extrabold leading-tight md:text-6xl">
            Your scrap. A better price. A smarter journey.
          </h1>
          <p className="mt-4 max-w-xl text-lg text-muted">
            List household or bulk scrap, compare collector offers, book pickup, and follow the material through recycling — with every price clearly marked DEMO or LIVE.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/sell" className="rounded-full bg-emerald px-5 py-3 text-sm font-semibold text-cream">
              Sell scrap
            </Link>
            <Link to="/prices" className="rounded-full border border-line px-5 py-3 text-sm font-semibold">
              See prices
            </Link>
          </div>
        </div>
        <div className="rounded-3xl bg-forest p-8 text-cream">
          <p className="text-sm uppercase tracking-widest text-emerald-light">How it works</p>
          <ol className="mt-4 space-y-3 text-sm">
            <li>1. Photograph scrap and enter quantity</li>
            <li>2. Compare ranked offers from collectors</li>
            <li>3. Accept one offer and request pickup</li>
            <li>4. Track status in real time on the Bengaluru map</li>
            <li>5. Follow the lot through processing</li>
          </ol>
        </div>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        {[
          ["Price intelligence", "Ranges, neighbourhood diffs, and source labels — never a fake live ticker."],
          ["Verified network", "Collectors show platform KYC or submitted authority records."],
          ["Traceability", "Try seeded lot BLR-EW-2026-00827 to see a full chain."],
        ].map(([t, d]) => (
          <article key={t} className="rounded-2xl border border-line bg-white/40 p-6">
            <h2 className="font-display text-xl font-semibold">{t}</h2>
            <p className="mt-2 text-sm text-muted">{d}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
