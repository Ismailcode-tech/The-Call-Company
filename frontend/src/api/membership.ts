import { apiFetch } from "./_base";
import type { Plan } from "./plans";

// Active membership shape returned by the backend.
export interface Membership {
    membershipId: string;
    planId : string;
    startedAt: string;
    renewalDate: string;
}

// History entries include a plan snapshot so old plans still display correctly.
export interface HistoryEntry extends Membership {
    endedAt?: string;
    planSnapshot: Plan;
}

// Create or replace the current membership after a payment succeeds.
export async function activateMembership(plan: Plan) : Promise<Membership> {
    return apiFetch<Membership>(
        "membership/activate",
        { method: "POST", body: JSON.stringify({ planId: plan.id }) }
    );
}

// Load the current user's active membership, or null if they have no plan yet.
export async function getMembership(): Promise<Membership | null> {
    return apiFetch<Membership | null>("/membership");
    
}

// Ask the backend to cancel the current active membership.
export async function cancelMembership(): Promise<void> {
    return apiFetch<void>(
        "membership/cancel",
        {method: "POST"},
    );
}

// Fetch previous memberships for the portfolio timeline.
export async function getHistory(): Promise<HistoryEntry[]> {
    return apiFetch<HistoryEntry[]>("/membership/history");
}
