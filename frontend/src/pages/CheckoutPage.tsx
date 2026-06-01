import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { ArrowRight, CreditCard, Lock, Shield, AlertTriangle } from "lucide-react";
import { Navbar } from "../components/Navbar";
import { AIAssistant } from "../components/AIAssistant";
import { GradientBg } from "../components/GradientBg";
import { getSelectedPlan } from "../lib/selection";     
import { getCurrentUser } from "../api/auth";
import { activateMembership } from "../api/membership";
import { confirmPayment } from "../api/payment";    
import { ProviderBadge } from "../components/ProviderBadge";    
import { deviceImage } from "../lib/device-images"; 
import type { Plan } from "../api/plans";  


export default function CheckoutPage() {

    const navigate = useNavigate();
    // Checkout reads the selected plan from sessionStorage, not from the URL.
    const [plan, setPlan] = useState<Plan | null>(null);
    const [cardNumber, setCardNumber] = useState("");
    const [expiry, setExpiry] = useState("");
    const [cvv, setCvv] = useState("");
    const [loading, setLoading] = useState(false);
    const [under18, setUnder18] = useState(false);


    // Load the selected plan and signed-in user's age flag when checkout opens.
    useEffect(() => {
        getSelectedPlan().then(setPlan)
        const u = getCurrentUser();
        if (u) setUnder18(u.isUnder18)
    },[]);

    // Demo payment flow: confirm payment, activate membership, then show confirmation.
    const submit = async (e: React.FormEvent) => {
        e.preventDefault();
        if(!plan) return;
        setLoading(true);
        try {
            await confirmPayment(plan.id);
            await activateMembership(plan);
            navigate("/confirmation")
        } finally {
            setLoading(false);
        }
    };
    // If the user opens checkout directly, send them back to pick a plan.
    if(!plan) {
        return (
            <div className="relative min-h-screen">
                <Navbar />
                <GradientBg variant="subtle" />
                <div className="mx-auto max-w-xl px-5 py-32 text-center">
                    <h1 className="text-3xl font-semibold tracking-tight">
                        No plan selected 
                    </h1>
                    <p className="mt-2 text-muted-foreground">
                        Pick a plan to continue to checkout.
                    </p>
                    <Link
                    to="/offers"
                    className="mt-6 inline-flex rounded-full bg-primary px-5 py-3 text-sm font-medium text-primary-foreground"
                    >
                        Browse plans
                    </Link>
                </div>
                <AIAssistant />
            </div>
        );
    }

    const total2yr = plan.monthlyPrice * 24;

    return (
        <div className="relative min-h-screen">
            <Navbar />
            <GradientBg variant="subtle" />
            <section className="px-5 py-12">
                <div className="mx-auto max-w-6xl">
                    <p className="text-xs font-semibold uppercase tracking-widest text-primary">
                        Step 3 of 3
                    </p>
                    <h1 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
                        Almost yours.
                    </h1>

                    <div className="mt-10 grid gap-8 lg:grid-cols-[1fr_minmax(0,420px)]">
                        {/* Card form */}
                        <div className="glass rounded-3xl p-7">
                            <h2 className="text-xl font-semibold">
                                Payment details
                            </h2>
                            <p className="mt-1 text-sm text-muted-foreground">
                                Your card  won't be charged — this is a demo payment step.
                            </p>

                            {under18 && (
                                <div className="mt-4 flex  items-start gap-2 rounded-xl border border-amber-400/30 bg-amber-400/10 p-3 text-xs text-amber-300">
                                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                                    <p>You're under 18 — a £15/month soft spending cap will apply to your account.</p>
                                </div>
                            )}

                            <form onSubmit={submit} className="mt-6 space-y-4">
                                {/* Card number */}
                                <div>

                                    <label className="mb-1.5 block text-xs font-medium uppercase tracking-widest text-muted-foreground">
                                        Card number
                                    </label>
                                    <div className="relative">
                                        <CreditCard className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                                        <input 
                                        
                                        type="text" 
                                        placeholder="1234 5678 9012 3456"
                                        value={cardNumber}
                                        onChange={(e) => setCardNumber(e.target.value)}
                                        maxLength={19}
                                        required
                                        className="block w-full rounded-xl border border-white/10 bg-white/5 py-3.5 pl-11 pr-4 text-sm placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/30"
                                        />
                                    </div>
                                </div>
                                {/* Expiry + CVV */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>

                                        <label className="mb-1.5 block text-xs font-medium uppercase tracking-widest text-muted-foreground">
                                            Expiry 
                                        </label>
                                        <input 
                                        type="text" 
                                        placeholder="MM / YY"
                                        value={expiry}
                                        onChange={(e) => setExpiry(e.target.value)}
                                        maxLength={7}
                                        required
                                        className="block w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3.5 text-sm placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/30"
                                        />                                       
                                    </div>
                                
                                   <div>
                                        <label className="mb-1.5 block text-xs font-medium uppercase tracking-widest text-muted-foreground">
                                            CVV
                                        </label>
                                        <input 
                                        
                                        type="text"
                                        placeholder="123"
                                        value={cvv}
                                        onChange={(e) => setCvv(e.target.value)}
                                        maxLength={4}
                                        required
                                        className="block w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3.5 text-sm placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/30"
                                        />                                
                                    </div>
                                </div>


                                <p className="inline-flex items-center gap-1.5 text-[11px] text-muted-foreground">
                                    <Lock className="h-3 w-3" /> Secured by 256-bit encryption

                                </p>
                                <button
                                type="submit"
                                disabled={loading}
                                className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-5 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] disabled:opacity-60"
                                >
                                    {loading ? "Confirming…" : "Confirm & Continue"}
                                    <ArrowRight className="h-4 w-4" />
                                </button>
                                <p className="inline-flex items-center gap-1.5 text-[11px] text-muted-foreground">
                                    <Shield className="h-3 w-3" /> 30-day money-back guarantee
                                </p>
                            </form>
                        </div>

                        {/* Plan summary shown beside the payment form. */}
                        <aside className="glass-strong h-fit rounded-3xl p-7">
                            <ProviderBadge provider={plan.provider} size="md" />
                            <div className="mt-4 grid place-items-center">
                                <img
                                    src={deviceImage(plan)}
                                    alt=""
                                    className="h-44 w-auto object-contain drop-shadow-2xl"                                 
                                />
                            </div>
                            <h3 className="mt-2 text-2xl font-semibold tracking-tight">
                                {plan.name} {plan.phoneModel ? `· ${plan.phoneModel}` : ""}
                            </h3>
                            <p className="mt-1 text-sm text-muted-foreground">
                                {plan.tier}
                            </p>
                            <div className="mt-5 space-y-2 text-sm">
                                <Row k="Data" v={plan.dataLabel}/>
                                <Row  k="Calls & texts" v={plan.callsTexts === "unlimited" ? "Unlimited" : "Limited"}/>
                                <Row k="Contract" v="24 months" />
                                <Row  k="Monthly" v={`£${plan.monthlyPrice}`} />
                            </div>
                            <div className="mt-5 flex items-end justify-between border-t border-white/10 pt-5">
                                <p className="text-xs uppercase tracking-widest text-muted-foreground">2-year cost</p>
                                <p className="text-3xl font-semibold tracking-tight">£{total2yr}</p>
                            </div>
                        </aside>
                    </div>
                </div>
            </section>
        </div>
    )
}

// Small label/value row used in the checkout plan summary.
function Row ({k, v} : {k: string; v:string}) {

    return (
        <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{k}</span>
            <span className="font-medium text-foreground">{v}</span>
        </div>
    )
}
