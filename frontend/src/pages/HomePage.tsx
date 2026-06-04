import { Link } from "react-router-dom";
import {
  ArrowRight,
  Sparkles,
  Search,
  ShieldCheck,
  Zap,
  Layers,
  CheckCircle2,
} from "lucide-react";
import { Navbar } from "../components/Navbar";
import { GradientBg } from "../components/GradientBg";
import { PROVIDER_META } from "../lib/providers";
import { usePlans } from "../hooks/usePlans";

export default function HomePage() {
  // Homepage stats come from the same plan list used by browse pages.
  const {plans: allPlans} = usePlans();
  const total = allPlans.length;
  const cheapest = allPlans.length ? Math.min(...allPlans.map((p) => p.monthlyPrice)) : 0;

  return (
    <div className="relative min-h-screen ">
      <Navbar />

      {/* Hero */}
      <section className="relative px-5 pt-20 pb-32 md:pt-32 md:pb-40">
        <GradientBg />
        <div className="mx-auto max-w-6xl text-center">
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-muted-foreground backdrop-blur">
            <span className="grid h-4 w-4 place-items-center rounded-full bg-primary/20">
              <Sparkles className="h-2.5 w-2.5 text-primary" />
            </span>
            Now with smart matching across {total} live allPlans
          </div>

          <h1 className="mt-6 text-balance text-5xl font-semibold leading-[1.02] tracking-tight md:text-7xl lg:text-[88px]">
            One company.
            <br />
            <span className="text-gradient">Three networks.</span>
            <br />
            Your perfect plan.
          </h1>

          <p className="mx-auto mt-6 max-w-xl text-pretty text-base leading-relaxed text-muted-foreground md:text-lg">
            The Call brings Fone, Gap and Flipper under one roof — so you can
            compare every SIM and phone deal in one place, and switch in minutes.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              to="/plan-finder"
              className="group relative inline-flex items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] transition-transform hover:scale-[1.03]"
            >
              <Search className="h-4 w-4" />
              Find My Plan
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              to="/signin"
              className="inline-flex items-center justify-center gap-2 rounded-full border border-white/10 bg-white/5 px-6 py-3.5 text-sm font-medium text-foreground backdrop-blur transition-colors hover:bg-white/10"
            >
              Sign In
            </Link>
          </div>

          {/* Floating provider cards */}
          <div className="relative mx-auto mt-20 grid max-w-4xl gap-5 md:grid-cols-3">
            {(Object.keys(PROVIDER_META) as Array<keyof typeof PROVIDER_META>).map(
              (key, i) => {
                // Each provider card summarizes its plan count and cheapest monthly price.
                const m = PROVIDER_META[key];
                const planCount = allPlans.filter((p) => p.provider === key).length;
                const min = Math.min(
                  ...allPlans.filter((p) => p.provider === key).map((p) => p.monthlyPrice),
                );
                
                return (
                  <Link
                    to="/offers"
                    key={key}
                    style={{ animationDelay: `${i * 120}ms` }}
                    className="group relative flex flex-col rounded-3xl border border-white/8 bg-white/[0.03] p-6 text-left backdrop-blur-xl transition-all duration-500 hover:-translate-y-2 hover:border-white/15 animate-fade-up"
                  >
                    <div
                      className="absolute -inset-px -z-10 rounded-3xl opacity-0 blur-2xl transition-opacity group-hover:opacity-60"
                      style={{
                        background: `radial-gradient(closest-side, ${m.color}, transparent)`,
                      }}
                    />
                    <div className="flex items-center justify-between">
                      <span
                        className="text-xs font-semibold uppercase tracking-widest"
                        style={{ color: m.color }}
                      >
                        {m.name}
                      </span>
                      <span
                        className="h-2 w-2 rounded-full"
                        style={{
                          background: m.color,
                          boxShadow: `0 0 16px ${m.color}`,
                        }}
                      />
                    </div>
                    <p className="mt-5 text-2xl font-semibold tracking-tight">
                      {m.tagline}
                    </p>
                    <p className="mt-2 text-sm text-muted-foreground">{m.description}</p>
                    <div className="mt-6 flex items-center justify-between border-t border-white/5 pt-4 text-xs">
                      <span className="text-muted-foreground">{planCount} allPlans</span>
                      <span className="font-medium">From £{min}/mo</span>
                    </div>
                  </Link>
                );
              },
            )}
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="relative px-5">
        <div className="mx-auto max-w-6xl">
          <div className="glass flex flex-col items-stretch divide-white/5 rounded-3xl px-6 py-8 md:flex-row md:items-center md:divide-x">
            {[
              { v: `${total}+`, l: "Live allPlans across 3 networks" },
              { v: `From £${cheapest}`, l: "Cheapest monthly SIM" },
              { v: "5", l: "Phone models in stock" },
              { v: "<2 min", l: "Average match time" },
            ].map((s) => (
              <div key={s.l} className="flex-1 px-6 py-3">
                <p className="text-3xl font-semibold tracking-tight">{s.v}</p>
                <p className="mt-1 text-sm text-muted-foreground">{s.l}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="relative px-5 py-28">
        <div className="mx-auto max-w-6xl">
          <div className="text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-primary">
              How it works
            </p>
            <h2 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
              From "what should I get?" to swapped, in minutes.
            </h2>
          </div>

          <div className="mt-14 grid gap-5 md:grid-cols-3">
            {[
              { i: "01", t: "Tell us what you need", d: "Phone or SIM, how much data, your budget. Three quick taps." },
              { i: "02", t: "We compare 45+ allPlans", d: "Across Fone, Gap and Flipper — instantly, with zero spin." },
              { i: "03", t: "Activate in one click", d: "Join, get your membership ID, and you're on the network." },
            ].map((s) => (
              <div
                key={s.i}
                className="group relative overflow-hidden rounded-3xl border border-white/8 bg-white/[0.03] p-7 transition-all hover:border-white/15 hover:bg-white/[0.06]"
              >
                <span className="text-xs font-mono text-primary">{s.i}</span>
                <h3 className="mt-3 text-xl font-semibold tracking-tight">{s.t}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.d}</p>
                <div className="mt-6 h-px w-full bg-gradient-to-r from-primary/40 via-transparent to-transparent" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why The Call */}
      <section className="relative px-5 py-28">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-10 md:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-primary">
                Why The Call
              </p>
              <h2 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
                The home for every network you'd actually pick.
              </h2>
              <p className="mt-5 max-w-md text-muted-foreground">
                We're not a comparison site. We're the company behind all three.
                That means honest pricing, real stock, and one place to manage everything.
              </p>
            </div>
            <div className="grid gap-3">
              {[
                { i: ShieldCheck, t: "One trusted account", d: "Manage every plan, payment and upgrade from a single dashboard." },
                { i: Zap, t: "Real-time stock", d: "Every device shown is in stock and ready to ship." },
                { i: Layers, t: "Switch without friction", d: "Move between Fone, Gap and Flipper with no porting fees." },
                { i: CheckCircle2, t: "Designed for under-18s", d: "Soft £15 spending caps for younger members." },
              ].map((f) => (
                <div
                  key={f.t}
                  className="flex gap-4 rounded-2xl border border-white/8 bg-white/[0.03] p-4 transition-colors hover:bg-white/[0.06]"
                >
                  <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary/15 text-primary">
                    <f.i className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{f.t}</p>
                    <p className="mt-0.5 text-sm text-muted-foreground">{f.d}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Comparison teaser */}
      <section className="relative px-5 pb-28">
        <div className="mx-auto max-w-6xl">
          <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.05] via-transparent to-primary/10 p-10 md:p-16">
            <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-primary/30 blur-3xl" />
            <div className="relative max-w-xl">
              <h2 className="text-3xl font-semibold tracking-tight md:text-4xl">
                See every network, side by side.
              </h2>
              <p className="mt-3 text-muted-foreground">
                Pricing, data caps, phone options, contract terms — laid out so the
                winners are obvious.
              </p>
              <Link
                to="/providers"
                className="mt-6 inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-medium text-primary-foreground shadow-[0_8px_30px_-10px_rgba(99,102,241,0.7)] transition-transform hover:scale-[1.02]"
              >
                See Full Comparison
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

// Simple footer links for the public marketing pages.
function Footer() {
  return (
    <footer className="border-t border-white/5 px-5 py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 text-sm text-muted-foreground md:flex-row">
        <p>© {new Date().getFullYear()} The Call. All networks, one home.</p>
        <div className="flex gap-5">
          <Link to="/providers" className="hover:text-foreground">Providers</Link>
          <Link to="/offers" className="hover:text-foreground">Offers</Link>
          <Link to="/plan-finder" className="hover:text-foreground">Find My Plan</Link>
        </div>
      </div>
    </footer>
  );
}
