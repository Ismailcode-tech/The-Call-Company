import { Link } from "react-router-dom";
import { Wifi, Phone, Calendar, ArrowRight } from "lucide-react";
import type { Plan } from "../api/plans";
import { deviceImage } from "../lib/device-images";
import { ProviderBadge } from "./ProviderBadge";
import { PROVIDER_META } from "../lib/providers";

function formatCallsTexts(plan: Plan): string {
  if (plan.callsTexts === "unlimited") return "Unlimited";
  if (plan.calls && plan.texts && plan.calls === plan.texts) {
    return `${plan.calls} mins / texts`;
  }
  if (plan.calls || plan.texts) {
    return [plan.calls, plan.texts].filter(Boolean).join(" / ");
  }
  return "—";
}

// Reusable plan preview used by offers, providers, and recommendation results.
export function PlanCard({
  plan,
  best = false,
  compact = false,
}: {
  plan: Plan;
  best?: boolean;
  compact?: boolean;
}) {
  // Provider metadata controls the glow color and badge styling.
  const meta = PROVIDER_META[plan.provider];
  return (
    <div
      className={`group relative flex flex-col overflow-hidden rounded-3xl border border-white/8 bg-white/[0.03] p-5 transition-all duration-300 hover:-translate-y-1 hover:border-white/15 hover:bg-white/[0.06] ${
        best ? "ring-1 ring-primary/60 shadow-[0_0_60px_-12px_rgba(99,102,241,0.5)]" : ""
      }`}
    >
      {best && (
        <div className="absolute -top-px left-1/2 z-10 -translate-x-1/2 rounded-b-full bg-gradient-to-r from-primary to-[oklch(0.55_0.22_300)] px-3 py-1 text-[10px] font-semibold uppercase tracking-widest text-white shadow-lg">
          Best Value
        </div>
      )}
      <div
        className="absolute inset-x-0 -top-24 h-48 opacity-50 blur-3xl transition-opacity group-hover:opacity-80"
        style={{
          background: `radial-gradient(closest-side, ${meta.color}, transparent)`,
        }}
      />
      <div className="relative flex items-start justify-between">
        <ProviderBadge provider={plan.provider} />
        <span className="text-[10px] uppercase tracking-widest text-muted-foreground">
          {plan.tier}
        </span>
      </div>

      {/* Fixed image container keeps every card the same height. */}
      <div className={`relative my-4 ${compact ? "h-32" : "h-44"} flex items-center justify-center`}>
        <img
          src={deviceImage(plan)}
          alt={plan.phoneModel ?? "SIM card"}
          loading="lazy"
          className="max-h-full w-auto max-w-[180px] object-contain drop-shadow-[0_20px_30px_rgba(0,0,0,0.4)] transition-transform duration-500 group-hover:scale-105"
        />
      </div>

      <div className="relative space-y-2">
        <h3 className="text-lg font-semibold tracking-tight">
          {plan.name}
          {plan.phoneModel ? (
            <span className="ml-1 text-muted-foreground"> · {plan.phoneModel}</span>
          ) : null}
        </h3>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <Wifi className="h-3.5 w-3.5" /> {plan.dataLabel}
          </span>
          <span className="inline-flex items-center gap-1">
            <Phone className="h-3.5 w-3.5" /> {formatCallsTexts(plan)}
          </span>
          <span className="inline-flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5" /> 24 mo
          </span>
        </div>
        <div className="flex items-end justify-between pt-2">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-muted-foreground">From</p>
            <p className="text-3xl font-semibold tracking-tight">
              £{plan.monthlyPrice}
              <span className="text-sm font-normal text-muted-foreground">/mo</span>
            </p>
          </div>
          <Link
            to={`/plan-details/${plan.id}`}
            className="inline-flex items-center gap-1 rounded-full bg-white/5 px-3 py-2 text-xs font-medium text-foreground transition-all hover:bg-primary hover:text-primary-foreground hover:shadow-[0_8px_30px_-10px_rgba(99,102,241,0.7)]"
          >
            View Plan <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
