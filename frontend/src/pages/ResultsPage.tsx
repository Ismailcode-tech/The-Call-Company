import { Link, useSearchParams } from "react-router-dom";
import { useEffect, useState } from "react";

import { ArrowLeft, Search } from "lucide-react";
import { Navbar } from "../components/Navbar";
import { AIAssistant } from "../components/AIAssistant";
import { GradientBg } from "../components/GradientBg";
import { getRecommendedPlans, type Plan, type Provider } from "../api/plans";
import { PlanCard } from "../components/PlanCard";
   




export default function ResultsPage() {
    const [searchParams] = useSearchParams();
    // Matches start empty and get replaced by backend recommendations.
    const [matches, setMatches] = useState<Plan[]>([]);
    const [loading, setLoading] = useState(true);
    const [sortBy, setSortBy] = useState<"match" | "price" | "data">("match");
    const [providerFilter, setProviderFilter] = useState<Provider | "all">("all")


    // Convert the plan finder query params into the recommendation endpoint request.
    useEffect(() => {
        const params = new URLSearchParams();
        const path = searchParams.get("path");
        const justPhone = searchParams.get("justPhone");
        const brand = searchParams.get("brand");
        const data = searchParams.get("data");
        const calls = searchParams.get("calls");
        const priority = searchParams.get("priority");
        const budget = searchParams.get("budget");

        if(path) params.set("path", path);
        if(justPhone) params.set("justPhone", justPhone);
        if(brand) params.set("brand", brand);
        if(data) params.set("data", data);
        if(calls) params.set("calls", calls);
        if(priority) params.set("priority", priority);
        if(budget) params.set("budget", budget);
        
        setLoading(true)
        getRecommendedPlans({
            path: searchParams.get("path") ?? undefined,
            justPhone: searchParams.get("justPhone") ?? undefined,
            brand: searchParams.get("brand") ?? undefined,
            data: searchParams.get("data") ?? undefined,
            calls: searchParams.get("calls") ?? undefined,
            priority: searchParams.get("priority") ?? undefined,
            budget: searchParams.get("budget") ?? undefined,
        })
        .then(setMatches)
        .catch(() => setMatches([]))
        .finally(() => setLoading(false));
          
    }, [searchParams]);

    // Client-side sort and filter on top of Flask results.
    const displayed = [...matches]
    .filter((p) => providerFilter === "all" || p.provider === providerFilter)
    .sort((a,b) => {
        if(sortBy === "price") return a.monthlyPrice - b.monthlyPrice;
        if(sortBy === "data") {
            const ad = a.data === -1 ? Infinity : a.data;
            const bd = b.data === -1 ? Infinity : b.data;
            return bd - ad
        }
        return 0;
    });

    // The first displayed plan gets the "Best Value" badge while in match order.
    const best = displayed[0]


    return (

        <div className="relative min-h-screen">
            <Navbar />
            <GradientBg variant="subtle" />

            <section className="px-5 pt-12 pb-6">
                <div className="mx-auto max-w-7xl">
                    <Link
                    to="/plan-finder"
                    className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"

                    >
                        <ArrowLeft className="h-4 w-4" /> Refine answers                                       
                    </Link>
                    <h1 className="mt-5 text-4xl  font-semibold tracking-tight md:text-5xl">
                        Your matches.
                    </h1>
                    <p className="mt-2 text-muted-foreground">
                        {
                        loading ? "Finding your plans…"
                                : `${displayed.length} ${displayed.length === 1 ? "plan" : "plans"} fit your shape. `                          
                        }
                    </p>
                </div>
            </section>

            <section className="px-5 pb-24">
                <div className="mx-auto max-w-7xl">
                    {/* Toolbar */}
                    <div className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-3">
                        <div className="flex flex-wrap gap-1.5">
                            {(["all", "fone", "gap", "flipper"] as const).map((p) => (
                                <button
                                key={p}
                                onClick={() => setProviderFilter(p)}
                                className={`rounded-full  px-3 py-1.5 text-xs font-medium transition-colors ${
                                    providerFilter === p
                                     ? "bg-primary text-primary-foreground"
                                     : "bg-white/5 text-muted-foreground hover:bg-white/10"
                                }`}
                                >
                                    {p === "all" ? "All providers" : p.toUpperCase()}
                                </button>
                            ))}
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                            <span className="text-muted-foreground">
                                Sort by
                            </span>
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                                className="cursor-pointer rounded-lg border border-white/10 bg-white/5 px-2 py-1.5 text-xs focus:outline-none"
                            >
                                <option value="match">Best match</option>
                                <option value="price">Lowest price</option>
                                <option value="data">Most data</option>
                            </select>
                        </div>
                    </div>
                    {/* Loading state */}

                    {loading ? (

                        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                            {[1,2,3].map((i) => (
                                <div 
                                  key={i}
                                  className="h-80 animate-pulse rounded-3xl border border-white/8 bg-white/[0.03]"
                                />
                            ))}
                        </div>
                    ) : (
                        displayed.length === 0 ? (
                            <Empty />
                        ) : (
                            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                                {displayed.map((p:Plan) => (
                                    <div key={p.id} className="animate-fade-up">
                                        <PlanCard plan={p} best={best?.id === p.id && sortBy === "match"}/>
                                    </div>
                                ))}

                            </div>
                        )
                    )}
                </div>

            </section>
            <AIAssistant />
        </div>
    )
} 

// Empty state when no recommended plans remain after filtering.
function Empty() {
    return (
        <div className="grid place-items-center rounded-3xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-20 text-center">
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-primary/15 text-primary">
            <Search className="h-6 w-6" />
            </div>
            <h3 className="mt-5 text-xl font-semibold">No exact matches.</h3>
            <p className="mt-2 max-w-sm text-sm text-muted-foreground">
                Try widening your budget or relaxing a preference.
            </p>
            <Link
             to="/plan-finder"
             className="mt-5 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
            >
                Refine answers
            </Link>
        </div>
    );
}
