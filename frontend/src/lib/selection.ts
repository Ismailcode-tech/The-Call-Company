import { getPlanById, type Plan } from "../api/plans";

const SELECTED_KEY = "thecall.selectedPlan";

// Store the plan chosen on the details page until checkout reads it.
export function setSelectedPlan(planId: string) {
    if(typeof window === "undefined") return;
    sessionStorage.setItem(SELECTED_KEY, planId);
}

// Rehydrate the selected plan from session storage by fetching the latest plan data.
export async function getSelectedPlan(): Promise<Plan | null> {
    if(typeof window === "undefined") return null;
    const id = sessionStorage.getItem(SELECTED_KEY);
    if(!id) return null;
    return await getPlanById(id) ?? null;
    


}

// Clear the selected plan after checkout or when abandoning the flow.
export function clearSelectedPlan() {
    if (typeof window === "undefined") return;
    sessionStorage.removeItem(SELECTED_KEY)
    
}

export type PaymentMethod = "card" | "apple-pay" | "google-pay" | "paypal";

const PAYMENT_KEY = "thecall.paymentMethod";

// Remember which payment method the user picked for the current browser tab.
export function setPaymentMethod(method: PaymentMethod) {
    if ( typeof window === "undefined") return;
    sessionStorage.setItem(PAYMENT_KEY, method);
}

// Read the chosen payment method for checkout UI.
export function getPaymentMethod(): PaymentMethod | null {
    if(typeof window === "undefined") return null;
    return (sessionStorage.getItem(PAYMENT_KEY) as PaymentMethod) ?? null;
}
