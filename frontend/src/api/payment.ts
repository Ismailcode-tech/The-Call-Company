import { apiFetch } from "./_base";

// Minimal response needed after the demo payment endpoint accepts a plan.
export interface PaymentResult {
    ok: true;
    reference: string;
}

// Confirms the selected plan before the app activates the membership.
export async function confirmPayment(planId: string): Promise<PaymentResult> {

    return apiFetch<PaymentResult>(
        "/payment/confirm",
        { method: "POST", body: JSON.stringify({ planId }) },
    );
}
