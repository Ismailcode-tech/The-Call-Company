import { useEffect, useState } from "react";
import { getPlanById, type Plan } from "../api/plans";

// Loads a single plan by id. Useful when a page starts from membership or URL state.
export function usePlan(id: string | undefined) {
    const [plan, setPlan] = useState<Plan | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // No id means there is no plan to fetch yet, but loading should still end.
        if(!id) { setLoading(false); return; }
        getPlanById(id)
        .then((p) => setPlan(p ?? null))
        .finally(() => setLoading(false));
    }, [id]);
    return { plan, loading};

}
