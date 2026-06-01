import { useEffect, useState } from "react";

import { getAllPlans, type Plan } from "../api/plans";

// Module-level cache prevents repeat page visits from refetching the same plan list.
let cache: Plan[] | null = null;

// Loads all plans once and exposes them with a loading flag for pages.
export function usePlans() {
    const [plans, setPlans] = useState<Plan[]>(cache ?? []);
    const [loading, setLoading] = useState(!cache);


    useEffect(() =>  {
        // If another component already fetched plans, reuse them immediately.
        if(cache) {
            setPlans(cache)
            setLoading(false);
            return;
        }

        // First caller fetches from Flask, stores the cache, and updates React state.
        getAllPlans()
        .then((data) => {
            cache = data;
            setPlans(data);
        })
        .finally(() => setLoading(false));
    }, []);

    return { plans, loading };
}
