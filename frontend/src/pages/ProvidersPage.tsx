import { Link } from "react-router-dom";
import { ArrowRight, Check, Minus } from "lucide-react";
import { Navbar } from "../components/Navbar";
import { AIAssistant} from "../components/AIAssistant";

import { GradientBg } from "../components/GradientBg";
import { type Provider } from "../api/plans";
import { PROVIDER_META } from "../lib/providers";
import { PlanCard } from "../components/PlanCard";
import { usePlans } from "../hooks/usePlans";
import { type Plan } from "../api/plans";

export default function ProvidersPage() {
    const { plans: allPlans } = usePlans();
    // Fixed provider order controls the order of page sections and comparison columns.
    const providers: Provider[] = ["fone", "gap", "flipper"];

    return(
        <div className="relative min-h-screen">
            <Navbar />
            <GradientBg variant="subtle"/>

            <section className="px-5 pt-16 pb-10">
                <div className="mx-auto max-w-6xl text-center">
                    <p className="text-xs font-semibold uppercase tracking-widest text-primary">
                        Our Providers
                    </p>
                    <h1 className="mt-3 text-5xl font-semibold tracking-tight md:text-6xl">
                        Three networks. <span className="text-gradient">One trusted home.</span>
                    </h1>
                    <p className="mx-auto mt-5 max-w-xl text-muted-foreground">
                        Each network has its own personality. Pick the one that matches yours.
                    </p>
                </div>
            </section>
            {providers.map((p, i) => {
                // Build provider-specific stats and preview cards from the shared plan list.
                const meta = PROVIDER_META[p];
                const plans = allPlans.filter((pl) => pl.provider === p);
                const min = Math.min(...plans.map((pl) => pl.monthlyPrice));
                const maxData = plans.some((pl) => pl.data === -1) 
                    ? "Unlimited"
                    : `${Math.max(...plans.map((pl) => pl.data))}GB`;
                  const top = plans.slice(0, 6);
                return(
                    <section key={p} className="relative px-5 py-20">
                        {i > 0 && (
                            <div className="mx-auto mb-20 h-px max-w-5xl bg-gradient-to-r from-transparent via-white/15 to-transparent"/>                            
                        )}
                        <div className="mx-auto max-w-6xl">
                            <div className="grid items-end gap-8 md:grid-cols-3">
                                <div className="md:col-span-2">
                                    <p className="text-xs font-semibold uppercase tracking-[0.3em]" style={{color:meta.color}}>
                                        {meta.name}
                                    </p>
                                    <h2 className="mt-3 text-5xl font-semibold tracking-tight md:text-6xl">
                                        {meta.tagline}
                                    </h2>
                                    <p className="mt-4 max-w-lg text-muted-foreground">
                                        {meta.description}
                                    </p>
                                </div>
                                <div className="grid grid-cols-3 gap-3 md:gap-4">
                                    {[
                                        {l:"Plans", v:plans.length.toString()},
                                        {l:"From", v:`£${min}`},
                                        {l:"Max data", v:maxData},

                                    ].map((s) => (
                                        <div
                                        key={s.l}
                                        className="rounded-2xl border border-white/8 bg-white/[0.03] p-3 text-center"
                                        >
                                            <p className="text-xl font-semibold tracking-tight">
                                                {s.v}
                                            </p>
                                            <p className="mt-0.5 text-[10px] uppercase tracking-widest text-muted-foreground">
                                                {s.l}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div className="mt-10 -mx-5 overflow-x-auto px-5">
                                <div className="flex gap-5 pb-4">
                                    {top.map((pl) => (
                                        <div key={pl.id} className="w-72 shrink-0 md:w-80">
                                            <PlanCard plan={pl} compact />
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="mt-6 flex items-center justify-between">
                                <p className="text-sm text-muted-foreground">
                                    {plans.length - top.length} more {meta.name} plans available
                                </p>
                                <Link
                                to={`/offers?provider=${p}`}
                                className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm transition-colors hover:bg-white/10"
                                >
                                    View All {meta.name} Plans <ArrowRight className="h-4 w-4" />
                                </Link>    
                            </div>
                        </div>
                    </section>
                  );
                })}

                {/* Comparison table */}
                <section className="relativepx-5 pb-28">
                    <div className="mx-auto max-w-6xl">
                        <div className="text-center">
                            <p className="text-xs font-semibold uppercase tracking-widest text-primary">
                                Head to Head
                            </p>
                            <h2 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
                                The full comparison
                            </h2>
                        </div>
                        <div className="mt-12 overflow-hidden rounded-3xl border border-white/10 bg-white/[0.02]">
                            <ComparisonTable allPlans={allPlans} />
                        </div>
                    </div>
                </section>
                <AIAssistant />
        </div>
    );
}

// Compares providers by deriving winner columns from the loaded plan list.
function ComparisonTable({ allPlans }: { allPlans: Plan[] }) {
    const providers: Provider[] = ["fone", "gap", "flipper"];
    type Row = {
        label: string;
        values: Record<Provider, string>;
        winner: Provider
    };
    const rows: Row[] = (() => {
        const data: Record<Provider, ReturnType<typeof statsFor>> = {
            fone:statsFor("fone", allPlans),
            gap:statsFor("gap", allPlans),
            flipper:statsFor("flipper", allPlans),
        };

        // Helper selectors keep winner logic readable for each row.
        function lowest(metric: (s:ReturnType<typeof statsFor>) =>number) : Provider {
            return providers.reduce((best, p) => (metric(data[p]) < metric(data[best]) ? p : best), providers[0]);
        }
        function highest(metric: (s:ReturnType<typeof statsFor>) => number) : Provider {
            return providers.reduce((best, p) => (metric(data[p]) > metric(data[best]) ? p : best), providers[0]);
        }
        return[
            {
                label: "Price range",
                values: {
                    fone: `£${data.fone.min}–£${data.fone.max}`,
                    gap: `£${data.gap.min}–£${data.gap.max}`,
                    flipper: `£${data.flipper.min}–£${data.flipper.max}`,
                },
                winner: lowest((s) => s.min),
            },
            {
                label: "Max data",
                values: {
                    fone: `${data.fone.maxData}`,
                    gap: `${data.gap.maxData}`,
                    flipper: `${data.flipper.maxData}`,
                },
                winner: highest((s) => (s.maxData === "Unlimited" ? Infinity : parseInt(s.maxData)))
            },
            {
                label:"Phone options",
                values: {
                    fone: `${data.fone.phones} plans`,
                    gap: `${data.gap.phones} plans`,
                    flipper: `${data.flipper.phones} plans`,
                },
                winner: highest((s) => s.phones),
            },
            {
                label: "Calls & texts",
                values:{
                    fone:data.fone.allUnlimited ? "Unlimited" : "Mixed",
                    gap:data.gap.allUnlimited ? "Unlimited" : "Mixed",
                    flipper:data.flipper.allUnlimited ? "Unlimited" : "Mixed",
                },
                winner: highest((s) => (s.allUnlimited ? 1 : 0)),
            },
            {
                label: "Min contract",
                values: {
                    fone:`${data.fone.minContract} mo`,
                    gap:`${data.gap.minContract} mo`,
                    flipper: `${data.flipper.minContract} mo`
                },
                winner: lowest((s) => s.minContract)
            },

            
        ];
    })();

    return(
        <div className="overflow-x-auto">
            <table className="w-full min-w-[640px]">
                <thead>
                    <tr className="border-b border-white/10 bg-white/[0.03]">
                        <th className="px-6 py-5 text-left text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                            &nbsp;
                        </th>
                        {providers.map((p) => {
                            const m = PROVIDER_META[p];
                            return(
                                <th key={p} className="px-6 py-5 text-left">
                                    <span
                                    className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-widest"
                                    style={{color: m.color}}
                                    >
                                        <span 
                                        className="h-2 w-2 rounded-full"
                                        style={{background:m.color}}
                                        />
                                            {m.name}
                                        

                                    </span>

                                </th>
                            );
                        })}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((r) => (
                        <tr key={r.label} className="border-b border-white/5 last:border-0">
                            <td className="px-6 py-5 text-sm text-muted-foreground">
                                {r.label}
                            </td>
                            {providers.map((p) => {
                                const win = r.winner === p;
                                return(
                                    <td key={p} className="px-6 py-5">
                                        <span
                                        className={`inline-flex  items-center gap-2 text-sm ${
                                            win ? "font-semibold text-foreground" : "text-muted-foreground"
                                        }`}
                                        >
                                            {win ? <Check className="h-4 w-4 text-primary"/> : <Minus className="h-3 w-3 opacity-40"/>}
                                            {r.values[p]}
                                        </span>

                                    </td>
                                )
                            })}

                        </tr>

                    ))}
                </tbody>

            </table>
        </div>
    );
}

// Aggregate provider stats used by both the comparison table and section summaries.
function statsFor(p: Provider, allPlans: Plan[]) {
    const plans = allPlans.filter((pl) => pl.provider === p);
    return{
        min: Math.min(...plans.map((pl)=> pl.monthlyPrice)),
        max: Math.max(...plans.map((pl) => pl.monthlyPrice)),
        phones: plans.filter((pl) => pl.type === "phone").length,
        maxData: plans.filter((pl) => pl.data === -1) ? "Unlimited" : `${Math.max(...plans.map((pl) => pl.data))}GB`,
        allUnlimited: plans.every((pl) => pl.callsTexts === "unlimited"),
        minContract: Math.min(...plans.map((pl) => pl.contractMonths)),
    };   
}        
