import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { ArrowRight, AlertOctagon } from "lucide-react";

import  { DashboardLayout } from "../components/DashboardLayout";    
import { ProviderBadge } from "../components/ProviderBadge"; 
import { getMembership, cancelMembership } from "../api/membership"; 
import { usePlans } from "../hooks/usePlans";
import { type Plan } from "../api/plans";
import { deviceImage } from "../lib/device-images";                       

export default function MyPlanPage() {

    const navigate = useNavigate();
    const {plans: allPlans} = usePlans();
    // The page needs both the active plan and the membership start date for the timeline.
    const [plan, setPlan] = useState<Plan | null>(null);
    const [startedAt, setStartedAt] = useState<Date | null>(null);

    // Load the active membership, then match its plan id against the fetched plan list.
    useEffect(() => {
        getMembership().then((m) => {
            if(m) {
                setPlan(allPlans.find((p) => p.id === m.planId) ?? null);
                setStartedAt(new Date(m.startedAt));
            }
        });
    }, []);

    if(!plan) {
        return (
            <DashboardLayout>
                <div className="grid place-items-center rounded-3xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-20 text-center">
                    <h1 className="text-2xl font-semibold">
                        No active plan
                    </h1>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Pick a plan to see it here.
                    </p>
                    <Link
                    to="/offers"
                    className="mt-5 rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground"   
                    >
                        Browse plans
                    </Link>
                </div>
            </DashboardLayout>
        );
    }
    const total2yr = plan.monthlyPrice * 24;
    // Timeline progress is calculated in months across the fixed 24-month contract.
    const months = 24;
    const elapsed = startedAt
       ? Math.min(months, Math.max(0, monthsBetween(startedAt, new Date()))) 
       : 0;
       const pct = (elapsed / months) * 100;

  return (
    <DashboardLayout>
      <p className="text-xs font-semibold uppercase tracking-widest text-primary">My Plan</p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight md:text-4xl">
        {plan.name}{plan.phoneModel ? ` · ${plan.phoneModel}` : ""}
      </h1>
      <div className="mt-2">
        <ProviderBadge provider={plan.provider} size="md" />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_420px]">
        <div className="space-y-4">
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-lg font-semibold">Plan breakdown</h2>
            <dl className="mt-4 grid grid-cols-2 gap-4 text-sm">
              <Item k="Tier" v={plan.tier} />
              <Item k="Data" v={plan.dataLabel} />
              <Item k="Calls & texts" v={plan.callsTexts === "unlimited" ? "Unlimited" : "Limited"} />
              <Item k="Phone" v={plan.phoneModel ?? "—"} />
              <Item k="Monthly" v={`£${plan.monthlyPrice}`} />
              {/* Contract display is fixed to the plan duration used by the seeded plans. */}
              <Item k="Contract" v="24 months" />
              <Item k="2-year total" v={`£${total2yr}`} />
              <Item k="Started" v={startedAt ? startedAt.toLocaleDateString() : "—"} />
            </dl>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <div className="flex items-end justify-between">
              <div>
                <h2 className="text-lg font-semibold">Contract timeline</h2>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  Month {elapsed} of {months}
                </p>
              </div>
              <p className="text-sm text-muted-foreground">
                {Math.max(0, months - elapsed)} months left
              </p>
            </div>
            <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/5">
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary to-[oklch(0.55_0.22_300)]"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link
              to="/plan-finder"
              className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-medium text-primary-foreground shadow-[0_8px_30px_-10px_rgba(99,102,241,0.7)]"
            >
              Upgrade Plan <ArrowRight className="h-4 w-4" />
            </Link>
            <button
              onClick={async () => {
                if (confirm("Cancel your membership? This can't be undone.")) {
                  await cancelMembership();
                  navigate("/dashboard");                                
                }
              }}
              className="inline-flex items-center gap-2 rounded-full border border-destructive/30 bg-destructive/10 px-5 py-3 text-sm text-destructive hover:bg-destructive/20"
            >
              <AlertOctagon className="h-4 w-4" /> Cancel Membership
            </button>
          </div>
        </div>

        
        <aside className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex h-64 items-center justify-center">
            <img
              src={deviceImage(plan)}
              alt={plan.phoneModel ?? "SIM card"}
              className="h-full w-auto max-w-[220px] object-contain drop-shadow-2xl"
            />
          </div>
          <p className="mt-4 text-center text-xs text-muted-foreground">
            {plan.phoneModel ?? "SIM only plan"}
          </p>
        </aside>
      </div>
    </DashboardLayout>
  );
}


// Displays one plan detail in the breakdown grid.
function Item({k, v} : {k:string; v:string}) {
    return (
        <div>
            <p className="text-[10px] uppercase tracking-widest text-muted-foreground">{k}</p>
            <p className="mt-1 text-sm font-medium">{v}</p>
        </div>
    );
}

// Month difference used for contract progress.
function monthsBetween(a: Date, b:Date) {
    return (b.getFullYear() - a.getFullYear()) * 12 + (b.getMonth() - a.getMonth());
}
