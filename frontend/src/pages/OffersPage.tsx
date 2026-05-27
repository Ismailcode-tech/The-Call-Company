import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { X, SlidersHorizontal, Apple, Smartphone } from "lucide-react";
import { GradientBg } from "../components/GradientBg";
import { AIAssistant } from "../components/AIAssistant";
import {  type Plan, type Provider } from "../api/plans";
import { PROVIDER_META } from "../lib/providers";
import { PlanCard } from "../components/PlanCard";
import { Navbar } from "../components/Navbar";
import { usePlans } from "../hooks/usePlans";

const DATA_OPTIONS = [
    {v:"0.5", label:"0.5GB"},
    {v:"1", label:"1GB"},
    {v:"2", label:"2GB"},
    {v:"3", label:"3GB"},
    {v:"5", label:"5GB"},
    {v:"6", label:"6GB"},
    {v:"8", label:"8GB"},
    {v:"10", label:"10GB"},
    {v:"35", label:"35GB"},
    {v:"100", label:"100GB"},
    {v:"-1", label:"Unlimited"},
];

export default function OffersPage() {
    const { plans } = usePlans();
    // Provider query param lets provider pages deep-link into pre-filtered offers.
    const [searchParams] = useSearchParams();
    const providerParam = searchParams.get("provider") as Provider | null;
    const [providers, setProviders] = useState<Provider[]>(
        providerParam ? [providerParam] : ["fone","gap","flipper"],
    );
    const [type, setType] = useState<"all" | "sim" | "phone">("all");
    const [budget, setBudget] = useState(100);
    const [data, setData] = useState<string[]>([])
    const [brand, setBrand] = useState<"any" | "apple" | "samsung">("any");
    const [calls, setCalls] = useState<"any" | "limited" | "unlimited">("any");
    const [showFilters, setShowFilters] = useState(false)

    // Keep the selected provider in sync if the URL changes.
    useEffect (() => {
        if(providerParam) setProviders([providerParam]);

    }, [providerParam]);

    // Apply all filter controls locally after the full plan list has loaded.
    const filtered = useMemo(() => {
        return plans.filter((p) => {
            if(!providers.includes(p.provider)) return false;
            if(type !== "all" && p.type !== type) return false;
            if(p.monthlyPrice > budget) return false;
            if(data.length > 0 && !data.includes(String(p.data))) return false;
            if(brand !== "any" && p.phoneBrand !== brand) return false;
            if(calls !== "any" && p.callsTexts !== calls) return false;
            return true

        });

    },[providers,type,budget,data,brand,calls]);

    // Toggle one provider checkbox without affecting the other active filters.
    const toggleProvider = (p:Provider) =>
        setProviders((cur) => (cur.includes(p) ? cur.filter((x) => x !==p) : [...cur,p]));

    // Active chips mirror selected filters and each chip knows how to clear itself.
    const activeChips: Array<{key:string; label:string; clear: () => void}> = [];
    providers.length < 3 && 
    providers.forEach((p) =>
        activeChips.push({key: `p-${p}`, label: PROVIDER_META[p].name, clear: () => toggleProvider(p) }),
    );
    if (type !== "all") activeChips.push({key: "type", label: type === "sim" ? "SIM only" : "With phone", clear: () => setType("all") });
    if(budget < 100) activeChips.push({key:"budget", label: `Under £${budget}`, clear: () => setBudget(100)});
    data.forEach((d) =>
        activeChips.push({key: `d-${d}`, label: d === "-1" ? "Unlimited": `${d}GB`,clear: () => setData((c) => c.filter((x) => x !== d)) }),

    );
    if(brand !== "any") activeChips.push({key:"brand", label:brand, clear: () => setBrand("any")})
    if(calls !== "any") activeChips.push({key:"brand", label:`${calls} calls`, clear: () => setCalls("any")})

    // Restore the full catalogue.
    const reset = () => {
        setProviders(["fone","gap","flipper"]);
        setType("all");
        setBudget(100);
        setData([]);
        setBrand("any");
        setCalls("any");
    };



    return(
        <div className="relative min-h-screen">
            <Navbar />
            <GradientBg variant="subtle"/>
            <section className="px-5 pt-14 pb-6">
                <div className="mx-auto max-w-7xl">
                    <p className="text-xs font-semibold uppercase tracking-widest text-primary">Offers</p>
                    <h1 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
                        Every plan. Every network.
                    </h1>
                    <p className="mt-3 max-w-xl text-muted-foreground">
                        {plans.length} live plans across Fone, Gap and Flipper. Filter to find yours.
                    </p>
                </div>
            </section>
            <section className="px-5 pb-24">

                <div className="mx-auto  grid max-w-7xl gap-8 lg:grid-cols-[280px_1fr]">
                    {/* Mobile filter toggle */}
                    <button
                    onClick={() => setShowFilters((v) => !v)}
                    className="flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm lg:hidden"
                    >
                        <SlidersHorizontal className="h-4 w-4"/>
                        {showFilters ? "Hide filters" : "Show filters"}
                    </button>
                    {/* Filters */}
                    <aside className={`${showFilters ? "block" : "hidden"} space-y-6 lg:sticky lg:top-24 lg:block lg:h-fit`}>

                        <div className="glass rounded-3xl p-5">
                            <FilterBlock title="Provider">
                                <div className="space-y-2">
                                    {(["fone","gap", "flipper"] as Provider[]).map((p) => {
                                        const m =PROVIDER_META[p];
                                        const active = providers.includes(p);
                                        return(
                                            <label key={p} className="flex cursor-pointer items-center justify-between rounded-xl px-2 py-1.5 hover:bg-white/5">
                                                <span className="flex items-center gap-2 text-sm">
                                                    <span  className="h-2 w-2 rounded-full" style={{background:m.color}} />
                                                    {m.name}
                                                </span>
                                                <input 
                                                type="checkbox"
                                                checked={active}
                                                onChange={() => toggleProvider(p)}
                                                className="h-4 w-4 cursor-pointer accent-[var(--primary)]"
                                                />
                                            </label>
                                        );
                                    })}

                                </div>
                            </FilterBlock>
                            <FilterBlock title="Plan type">
                                <div className="grid grid-cols-3 gap-1.5">
                                    {[
                                        {v:"all", l:"All"},
                                        {v:"sim", l:"SIM"},
                                        {v:"phone", l:"Phone"},

                                    ].map((o) =>(
                                        <button
                                        key={o.v}
                                        onClick={() =>setType(o.v as typeof type)}
                                        className={`rounded-xl px-3 py-2 text-xs font-medium transition-colors ${
                                            type === o.v
                                            ? "bg-primary text-primary-foreground"
                                            :  "bg-white/5 text-muted-foreground hover:bg-white/10"
                                        }`}
                                        >
                                            {o.l}
                                        </button>
                                    ))}
                                </div>
                            </FilterBlock>
                            <FilterBlock title={`Budget · £${budget}/mo `}>
                            <input 
                            type="range"
                            min={5}
                            max={100}
                            step={1}
                            value={budget}
                            onChange={(e) => setBudget(parseInt(e.target.value))}
                            className="w-full accent-[var(--primary)]" 
                            />
                            <div className="mt-1 flex justify-between text-[10px] text-muted-foreground">
                                <span>£5</span>
                                <span>£100</span>
                            </div>
                            </FilterBlock>

                            <FilterBlock title="Data">
                                <div className="flex flex-wrap gap-1.5">

                                    {DATA_OPTIONS.map((o) => {
                                        const active = data.includes(o.v);
                                        return(
                                            <button
                                            key={o.v}
                                            onClick={() => setData((c) => (active ? c.filter((x) => x !== o.v) : [...c, o.v]))}
                                            className={`rounded-full px-2.5 py-1 text-[11px] transition-colors ${
                                                active
                                                ? "bg-primary text-primary-foreground"
                                                : "bg-white/5 text-muted-foreground hover:bg-white/10"
                                            }`}
                                            >
                                                {o.label}
                                            </button>                                   
                                        );
                                    })}
                                </div>
                            </FilterBlock>
                            <FilterBlock title="Phone brand">
                                <div className="grid grid-cols-3 gap-1.5">
                                    {[
                                        {v:"any", l:"Any", icon:null},
                                        {v:"apple", l:"Apple",icon:Apple},
                                        {v:"samsung", l:"Samsung",icon:Smartphone}
                                    ].map((o) => {

                                        const Icon = o.icon;
                                        return(
                                            <button
                                            key={o.v}
                                            onClick={() => setBrand(o.v as typeof brand)}
                                            className={`flex items-center justify-center gap-1 rounded-xl px-2 py-2 text-xs font-medium transition-colors ${
                                                brand === o.v
                                                ? "bg-primary text-primary-foreground"
                                                : "bg-white/5 text-muted-foreground hover:bg-white/10"
                                            } `}
                                            >
                                                {Icon && <Icon className="h-3.5 w-3.5"/>}
                                                {o.l}
                                            </button>
                                        );
                                    })}
                                </div>
                            </FilterBlock>
                            <FilterBlock title="Calls & texts">
                                <div className="grid grid-cols-3 grid-1.5">
                                    {[
                                        {v:"any", l:"Any"},
                                        {v:"limited", l:"Limited"},
                                        {v:"unlimited", l:"Unlimited"},
                                    ].map((o) => {
                                        return(
                                             <button
                                        key={o.v}
                                        onClick={() => setCalls(o.v as typeof  calls)}
                                        className={`rounded-xl px-2 py-2 text-xs font-medium transition-colors ${
                                            calls === o.v
                                            ? "bg-primary text-primary-foreground"
                                            : "bg-white/5 text-muted-foreground hover:bg-white/10"
                                        }`}                                           
                                        >
                                            {o.l}
                                        </button>
                                        )                                      
                                    })}
                                </div>
                            </FilterBlock>
                            <button
                            onClick={reset}
                            className="mt-2 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-muted-foreground hover:bg-white/10 hover:text-foreground"
                            >
                                Reset all filters                              
                            </button>
                        </div>
                    </aside>
                    {/* Grid */}
                    <div>
                        <div className="mb-4 flex flex-wrap items-center gap-2">
                            <p className="text-sm text-muted-foreground">
                                <span className="font-semibold text-foreground">{filtered.length}</span>
                            </p>
                            {activeChips.length > 0 && <span className="f text-muted-foreground">.</span>}
                            {activeChips.map((c) => (
                                <button
                                key={c.key}
                                onClick={c.clear}
                                className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] text-foreground transition-colors hover:bg-white/10"
                                >
                                    {c.label}
                                    <X className="h-3 w-3"/>
                                </button>
                            ))}
                        </div>
                        {filtered.length === 0 ? (
                            <EmptyState onReset={reset} />
                        ): (
                            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                                {filtered.map((p: Plan) => (
                                    <div key={p.id} className="animate-fade-up">
                                        <PlanCard plan={p}/>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>   

                </div>
            </section>
            <AIAssistant />
        </div>
    );
}


// Groups a filter label and its controls with consistent spacing.
function FilterBlock({title, children}: {title:string; children: React.ReactNode }) {
    return (
        <div className="border-b border-white/5 pb-4 last:border-0 last:pb-0 [&:not(:first-child)]:mt-4 [&:not(:first-child)]:pt-4">
            <p className="mb-2.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                {title}
            </p>
            {children}
        </div>
    );
}


// Empty state for over-constrained filters.
function EmptyState({onReset} : {onReset: () => void}) {
    return (
        <div className="grid place-items-center rounded-3xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-20 text-center">
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-primary/15 text-primary">
                <SlidersHorizontal className="h-6 w-6" />
            </div>
            <h3 className="mt-5 text-xl font-semibold">No plans match those filters.</h3>
            <p className="mt-2 max-w-sm text-sm text-muted-foreground">  Try widening your budget or removing a filter.</p>
            <button
            onClick={onReset}
             className="mt-5 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
            >
                Reset filters

            </button>
        </div>
    );
}
