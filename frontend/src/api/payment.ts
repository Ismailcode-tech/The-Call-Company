import { apiFetch } from "./_base";

// Minimal response needed after the demo payment endpoint accepts a plan.
export interface PaymentResult {
    ok: true;
    reference: string;
    planId:string;
    amount: number;
    message:string
}

// Confirms the selected plan before the app activates the membership.
export async function confirmPayment(planId: string,cardDetails:{ cardNumber:string; expiry:string; cvv:string;}): Promise<PaymentResult> {

    return apiFetch<PaymentResult>(
        "/payment/confirm",
        { method: "POST", body: JSON.stringify({ planId, cardNumber: cardDetails.cardNumber, expiry:cardDetails.expiry, cvv:cardDetails.cvv }) },
    );
}