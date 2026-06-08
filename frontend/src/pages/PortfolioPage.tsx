import {Link, useNavigate} from "react-router-dom";
import { useEffect, useState } from "react";
import { Copy, Check, ShieldCheck, KeyRound, UserCog, AlertOctagon } from "lucide-react";
import { DashboardLayout } from "../components/DashboardLayout";
import { ProviderBadge } from "../components/ProviderBadge";
import { getCurrentUser, signOut, type User } from "../api/auth";
import { getMembership, getHistory,cancelMembership, type HistoryEntry} from "../api/membership";
import {type Plan } from "../api/plans";
import { usePlans } from "../hooks/usePlans";

export default function PortfolioPage() {
    const navigate = useNavigate();
    const  {plans: allPlans} = usePlans();
    // Portfolio combines user details, active plan, and membership history.
    const [user, setUser] = useState<User | null>(null);
    const [plan, setPlan] = useState<Plan | null>(null);
    const [history, setHistory] = useState<HistoryEntry[]>([]);
    const [copied, setCopied] = useState(false);


    // Load all account data needed for the overview and timeline.
    useEffect(() => {
        setUser(getCurrentUser());
        getMembership().then((m) => {
            if (m) setPlan(allPlans.find((p) => p.id === m.planId) ?? null);

        });
        getHistory().then(setHistory);
    },[])
    const total2yr = plan ? plan.monthlyPrice * (plan.contractMonths === 1 ? 24 : plan.contractMonths) : 0
    const cap = user?.isUnder18 ? 15 : null;

    return(
        <DashboardLayout>
            <p className="text-xs font-semibold uppercase tracking-widest text-primary">
                My Portfolio
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight md:text-4xl">
                Your account.
            </h1>
            <div className="mt-8 grid gap-6 lg:grid-cols-[380px_1fr]">
                <aside className="space-y-6">
                    <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-primary/15 via-white/[0.02] to-transparent p-6">
                        <div className="flex items-center gap-4">
                            <div className="grid h-14 w-14 place-items-center rounded-full bg-gradient-to-br from-primary to-[oklch(0.5_0.2_300)] text-lg font-semibold text-white">
                                {user ? `${user.fname} ${user.lname}`.split(" ").filter(Boolean).map((n) => n[0]).slice(0, 2).join("").toUpperCase() : "—"}

                            </div>
                        </div>
                        <dl>
                            <Row 
                            
                            k="Membership"
                            v={user ? `#${user.membershipId}` :  "—"}
                            mono
                            action={user ? (
                                <button
                                onClick={() => {
                                    navigator.clipboard.writeText(`#${user.membershipId}`);
                                    setCopied(true);
                                    setTimeout(() => setCopied(false), 1500)
                                }}
                                className="text-primary"
                                >
                                    {copied ? <Check className="h-3.5 w-3.5"/> : <Copy  className="h-3.5 w-3.5"/>}

                                </button>
                            ): null}
                            />
                            <Row k="Member since" v={user ? new Date(user.memberSince).toLocaleDateString() : "—"}/>
                            <Row k="Date of birth" v={user?.dateOfBirth ?? "—"}/>
                        </dl>
                        {user?.isUnder18 && (
                            <div className="mt-5 inline-flex items-center gap-2 rounded-full  border border-amber-400/30 bg-amber-400/10 px-3 py-1.5 text-[11px] text-amber-300">
                                <ShieldCheck className="h-3.5 w-3.5"/> Under-18 · £15 cap
                            </div>
                        )}
                    </div>
                    <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
                        <h3 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">
                            Account
                        </h3>
                        <div className="mt-4 space-y-1.5">
                            <Action icon={UserCog} label="Edit profile"/>
                            <Action icon={KeyRound} label="Change password"/>
                            <button
                            onClick={async () => {
                                if (!confirm("Cancel your membership")) return;
                                await cancelMembership()
                                navigate("/dashboard");
                            }}
                            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-destructive hover:bg-destructive/10"
                            >
                                <AlertOctagon  className="h-4 w-4"/> Cancel membership
                            </button>
                            <button
                            onClick={async () => { await signOut(); navigate("/")}}
                            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground hover:bg-white/5"
                            >
                                Sign out
                            </button>
                        </div>
                    </div>
                </aside>
                <div className="space-y-6">
                    {plan ? (
                        <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
                            <div className="flex items-center justify-between">
                                <ProviderBadge provider={plan.provider} size="md"/>
                                <Link
                                to="/my-plan" className="text-xs text-primary hover:underline"
                                >
                                    View details 
                                </Link>
                            </div>
                            <h2 className="mt-3 text-2xl font-semibold tracking-tight">
                                {plan.name} {plan.phoneModel ? ` · ${plan.phoneModel}` :""}
                            </h2>
                            <p className="mt-1 text-sm text-muted-foreground">
                                {plan.dataLabel} · {plan.callsTexts}
                            </p>
                        </div>
                    ) : (
                        <div className="rounded-3xl  border border-dashed border-white/10 bg-white/[0.02] p-6 text-center text-sm text-muted-foreground">
                            No active plan. <Link to="/plan-finder" className="text-primary">Find one</Link>
                        </div>
                    )}
                    <div className="grid gap-4 sm:grid-cols-3">
                        <Stat label="Monthly cost" value={plan ? `£${plan.monthlyPrice}` :  "—"}/>
                        <Stat label="2-year total" value={plan ? `£${total2yr}` :"—"}/>
                        <Stat label="Spending cap" value={cap ? `£${cap}/mo`: "None"}/>
                    </div>
                    <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
                    <h3 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">
                        Plan history
                    </h3>
                    {history.length === 0 ? (
                        <p className="mt-4 text-sm text-muted-foreground">
                            Nothing here yet — your plan timeline will live here
                        </p>
                    ) : (
                        <ol className="mt-4 space-y-3">
                            {history.map((h, i) =>(
                                <li
                                key={i}
                                className="flex items-center gap-4 rounded-2xl border border-white/5 bg-white/[0.02] p-3"
                                >
                                   <span className="grid h-8 w-8 place-items-center rounded-full bg-primary/15 text-xs font-semibold text-primary">
                                     {history.length - i}
                                   </span>
                                   <div className="flex-1">
                                    <p className="text-sm font-medium">
                                        {h.planSnapshot.name} {h.planSnapshot.phoneModel ? `· ${h.planSnapshot.phoneModel}`: ""}
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                        {new Date(h.startedAt).toLocaleDateString()}{" "}
                                        {h.endedAt ? `→ ${new Date(h.endedAt).toLocaleDateString()}` : "· active"}
                                    </p>
                                   </div>
                                   <p className="text-sm font-semibold">
                                        £{h.planSnapshot.monthlyPrice}/mo
                                   </p>
                                </li>
                            ))}
                        </ol>
                    )}
                    </div>
                </div>
            </div>
        </DashboardLayout>

    )
}

// Account profile row with optional copy/action control.
function Row({
    k, v, mono, action
}: {
    k:string; v:string; mono?:boolean; action?: React.ReactNode;
}) {
    return(
        <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-widest text-muted-foreground">{k}</span>
            <span className={`text-sm font-medium ${mono ? "font-mono" : ""} flex items-center gap-2`}>
                {v} {action}
            </span>
        </div>
    )
}

// Compact stat tile for monthly cost, total cost, and spending cap.
function Stat({label,value} : {label:string; value: string}) {
    return(
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                {label}
            </p>
            <p className="mt-2 text-xl font-semibold tracking-tight">{value}</p>
        </div>
    )
}

// Placeholder account action button.
function Action({icon:Icon, label} : {icon: typeof KeyRound; label: string}) {
    return (
        <button className="flex w-full items-center gap-3 rounded-xl  px-3 py-2.5 text-sm text-muted-foreground hover:bg-white/5 hover:text-foreground">
            <Icon className="h-4 w-4"/> {label}
        </button>
    )
}
