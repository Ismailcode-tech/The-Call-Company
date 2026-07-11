import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { ArrowRight, Copy, Check, Search, Building2, MessageCircle } from "lucide-react";

import { DashboardLayout } from "../components/DashboardLayout";
import { ProviderBadge } from "../components/ProviderBadge";
import { getCurrentUser, type User } from "../api/auth";
import { getMembership, type Membership } from "../api/membership";
import { type Plan } from "../api/plans";
import { usePlan } from "../hooks/usePlan";

export default function DashboardPage() {
    const [membership, setMembership] = useState<Membership | null>(null);
    // The membership only stores a plan id, so this hook fetches the full plan.
    const { plan } = usePlan(membership?.planId);
    const [user, setUser] = useState<User | null>(null);
    const [renewal, setRenewal] = useState<string>("");
    const [copied, setCopied] = useState(false);
    


    // Load the signed-in user and active membership when the dashboard opens.
    useEffect(() => {
        setUser(getCurrentUser());

         getMembership().then((m) => {
        if(m) {
            setMembership(m);
            setRenewal(
                new Date(m.renewalDate).toLocaleDateString(undefined, {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                }),
            );
        }
    });


    }, []);
   
return (
    <DashboardLayout>
         <header>
            <p className="text-xs font-semibold uppercase tracking-widest text-primary">
                Dashboard
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight md:text-4xl">
                {user ? `Hi, ${user.fname || "there"}.` : "Welcome."}
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">Everything in one quiet place.</p>
        </header>
        {plan ? (
        <section className="mt-8 overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-primary/15 via-white/[0.02] to-transparent p-6 md:p-8">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <ProviderBadge provider={plan.provider} size="md" />
              <h2 className="mt-3 text-2xl font-semibold tracking-tight md:text-3xl">
                {plan.name}{plan.phoneModel ? ` · ${plan.phoneModel}` : ""}
              </h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Renews {renewal} · {plan.dataLabel} · {plan.callsTexts === "unlimited" ? "Unlimited calls & texts" : "Limited calls & texts"}
              </p>
            </div>
            <div className="text-right">
              <p className="text-4xl font-semibold tracking-tight">
                £{plan.monthlyPrice}
                <span className="text-sm font-normal text-muted-foreground">/mo</span>
              </p>
              <Link
                to="/my-plan"
                className="mt-2 inline-flex items-center gap-1 text-xs text-primary hover:underline"
              >
                View Full Plan Details <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </div>
        </section>
      ) : (
        <section className="mt-8 grid place-items-center rounded-3xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-14 text-center">
            <h2 className="text-xl font-semibold">
                No active plan yet
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
                Find your match in under 2 minutes.
            </p>
            <Link
            to="/plan-finder"
            className="mt-5 rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground"
            >
                Find My Plan
            </Link>
        </section>
      )}
      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
    
        <State label="Monthly cost" value={plan ? `£${plan.monthlyPrice}` : "—"} />
        <State label="Data allowance" value={plan?.dataLabel ?? "—"}/>
        <State 
        label="Contract ends"
        value={plan ? (plan.contractMonths === 1 ? "Rolling" : renewalEnd(plan)) :  "—"}
        />
        <State label="Membership"
        value={user ? `#${user.membershipId || membership?.membershipId}` : "—"}
        mono
        action={
            user && (
                <button
                onClick={() => {
                    navigator.clipboard.writeText(`#${user.membershipId || membership?.membershipId}`);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 1500);
                }}
                className="text-primary"
                >
                    {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}

                </button>
            )
        }
        />
      </section>
      <section className="mt-8 grid gap-3 sm:grid-cols-3">
        <QuickAction to="/plan-finder" icon={Search} title="Find a New Plan" />
        <QuickAction to="/providers" icon={Building2} title="View Providers" />
        <QuickAction to="/my-portfolio" icon={MessageCircle} title="Account & Support" />

      </section>

    </DashboardLayout>
);

};


// Calculate the visible contract end date from today's date and plan length.
function renewalEnd(p: Plan) {
    const d = new Date();
    d.setMonth(d.getMonth() + p.contractMonths);
    return d.toLocaleDateString(undefined, {month: "short", year: "numeric"})

}


// Compact metric tile used for dashboard account stats.
function State({
    label,value,mono, action,
}: {
    label: string; value: string; mono?: boolean; action?:React.ReactNode;

}) {
    return(
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foregroun">
                {label}
            </p>
            <div className="mt-2 flex items-center justify-between gap-2">
                <p className={`text-xl font-semibold tracking-tight ${mono ? "font-mono text-base" : ""}`}>
                    {value}
                </p>
                {action}
            </div>
        </div>
    );
}

// Small dashboard shortcut card with a lucide icon.
function QuickAction({
    to, icon: Icon, title
} : {
    to : string; icon: typeof Search; title: string
}) {
    return (
        <Link
        to={to}
        className="group flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition-colors hover:bg-white/[0.06]"
        
        >
            <div className="flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary/15 text-primary">
                    <Icon className="h-4 w-4"/>
                </div>
                <p className="text-sm font-medium">
                    {title}
                </p>
            </div>
            <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
        
        </Link>
    )
}
