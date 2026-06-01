import {Link, useNavigate, useParams} from "react-router-dom";
import { useState } from "react";
import { Navbar } from "../components/Navbar";
import { AIAssistant } from "../components/AIAssistant";
import { GradientBg } from "../components/GradientBg";

import { ProviderBadge } from "../components/ProviderBadge"; 
import { PROVIDER_META } from "../lib/providers";
import { deviceImage } from "../lib/device-images"; 
import { setSelectedPlan, setPaymentMethod } from "../lib/selection";  
import { ArrowLeft, Wifi, CreditCard, Lock,Check, Phone, Calendar, Shield, ArrowRight} from "lucide-react";
import { usePlans } from "../hooks/usePlans";

export default function PlanDetailsPage() {
    const {plans: allPlans} = usePlans();
    // The route id chooses one plan from the cached plan list.
    const {planId} = useParams<{planId: string}>();
    const navigate = useNavigate();
    const plan = allPlans.find((p) => p.id === planId);
    const [agreed, setAgreed] = useState(true);

    if(!plan){
        return (
            <div className="relative min-h-screen">
                <Navbar />
                <GradientBg variant="subtle"/>
                <div className="mx-auto max-w-xl px-5 py-32 text-center">
                    <h1 className="text-3xl font-semibold tracking-tight">
                        Plan not found
                    </h1>
                    <Link
                    to="/offers"
                    className="mt-6 inline-flex rounded-full bg-primary px-5 py-3 text-sm font-medium text-primary-foreground"
                    >
                        Browse plans
                    </Link>
                </div>
            </div>
        );
    }

    const meta = PROVIDER_META[plan.provider];
    const total2yr = plan.monthlyPrice * (plan.contractMonths === 1 ? 24 : plan.contractMonths);

    // Store the choice for checkout, then move to payment.
    const continueToCheckout = () => {
        setSelectedPlan(plan.id);
        setPaymentMethod("card");
        navigate("/checkout");
    };
    return (


        <div className="relative min-h-screen">
            <Navbar />
            <GradientBg variant="subtle" />
            <section className="px-5 pt-10 pb-20">
                <div className="mx-auto max-w-6xl">
                    <button
                    type="button"
                    onClick={() => window.history.back()}
                    className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
                    >
                        <ArrowLeft className="h-4 w-4"/>
                    </button>
                    <div className="mt-8 grid gap-10 lg:grid-cols-[1.1fr_minmax(0,460px)]">
                        {/* Hero */}
                        <div className="relative  overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] p-8">
                          <div className="absolute inset-x-0 -top-32 h-72 opacity-50 blur-3xl"
                          style={{background: `radial-gradient(closest-side, ${meta.color}, transparent)`}}
                          />
                          <div className="relative flex items-start justify-between">
                            <ProviderBadge provider={plan.provider}  size="md"/>
                            <span className="text-[10px] uppercase tracking-widest text-muted-foreground">
                                {plan.tier}
                            </span>
                          </div>
                          <div className="relative my-6 grid h-72 place-items-center">
                            <img 
                            src={deviceImage(plan)}
                            alt={plan.phoneModel ?? "SIM card"}
                            className="max-h-full w-auto object-contain drop-shadow-[0_30px_50px_rgba(0,0,0,0.5)]"
                            />
                          </div>
                          <h1 className="relative text-balance text-4xl font-semibold tracking-tight md:text-5xl">
                            {plan.name}
                            {plan.phoneModel ? (
                                <span className="text-muted-foreground"> · {plan.phoneModel}
                                </span>
                            ) : null}
                          </h1>
                          <p className="relative mt-2 text-sm text-muted-foreground">
                            Powered by {meta.name}.{" "}
                            {plan.contractMonths === 1
                               ? "No commitment, cancel anytime."
                               : `${plan.contractMonths}-month contract.`}
                          </p>
                          <div className="relative mt-8 grid gap-3 sm:grid-cols-3">
                            <Spec icon={<Wifi className="h-4 w-4"/>} label="Data" value={plan.dataLabel} />
                            <Spec 
                            icon={<Phone className="h-4 w-4"/>}
                            label="Calls & texts"
                            value={plan.callsTexts === "unlimited" ? "Unlimited" : "Limited"}
                            />
                            <Spec icon={<Calendar className="h-4 w-4"/>}
                            label="Contract"
                            value={plan.contractMonths === 1 ? "Rolling" : `${plan.contractMonths} months`}
                            />
                          </div>

                          <div className="relative mt-8 space-y-2.5 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm">
                                <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                                    What's included
                                </h3>
                                <Bullet>5G coverage where available</Bullet>
                                <Bullet>EU roaming included</Bullet>
                                <Bullet>Free network switch & number transfer</Bullet>
                                {plan.phoneModel && (
                                    <Bullet>Brand-new {plan.phoneModel} delivered next day</Bullet>
                                )}
                          </div>       
                        </div>
                        {/* Payment */}
                        <aside className="glass-strong h-fit rounded-3xl p-7">
                            <p className="text-[10px] font-semibold uppercase tracking-widest text-primary">
                                Order summary
                            </p>
                            <div className="mt-3 flex items-end justify-between">
                                <div>
                                    <p className="text-4xl font-semibold tracking-tight">
                                        £{plan.monthlyPrice}
                                        <span className="text-base font-normal text-muted-foreground">
                                            /mo
                                        </span>
                                    </p>
                                    <p className="mt-1 text-xs text-muted-foreground">
                                        2-year cost · £{total2yr}
                                    </p>
                                </div>
                            </div>
                            <div className="mt-6 rounded-2xl border border-primary/40 bg-primary/10 p-4 ring-1 ring-primary/30">
                               <div className="flex items-center gap-3">
                                <div className="grid h-10 w-10 place-items-center rounded-xl bg-white/10 text-foreground">
                                   <CreditCard className="h-5 w-5" />
                                </div>
                                <div className="flex-1">
                                    <p className="text-sm font-semibold">Credit / Debit Card</p>
                                    <p className="text-xs text-muted-foreground">Visa · Mastercard · Amex</p>
                                </div>
                                <div className="grid h-6 w-6 place-items-center rounded-full bg-primary text-primary-foreground">
                                    <Check className="h-3.5 w-3.5" />
                                </div>
                               </div>
                               <p className="mt-3 inline-flex items-center gap-1.5 text-[11px] text-muted-foreground">
                                 <Lock className="h-3 w-3"/> Secured by 256-bit encryption
                               </p>
                            </div>
                            <label className="mt-5 flex cursor-pointer items-start gap-3 text-xs text-muted-foreground">
                                <input 
                                type="checkbox"
                                checked={agreed}
                                onChange={(e) => setAgreed(e.target.checked)}
                                className="mt-0.5 h-4 w-4 cursor-pointer accent-[var(--primary)]"
                                />
                                <span>

                                    I agree to the terms, fair-use police and{" "}
                                    {plan.contractMonths === 1
                                      ? "monthly billing"
                                      : `${plan.contractMonths}}-month contract`
                                    }.
                                </span>
                            </label>
                            <button
                            type="button"
                            disabled={!agreed}
                            onClick={continueToCheckout}
                            className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-5 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] transition-transform hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-5"
                            
                            >
                                Pay with card <ArrowRight className="h-4 w-4" />
                            </button>
                            <p className="mt-4 inline-flex items-center gap-1.5 text-[11px] text-muted-foreground">
                                <Shield className="h-3 w-3" /> 30-day money-back guarantee
                            </p>
                        </aside>
                    </div>
                </div>
            </section>
            <AIAssistant />
        </div>
    )
}


// Small spec tile for data, calls, and contract details.
function Spec({
    icon, label, value, 
}: {
     icon: React.ReactNode; label: string; value: string
}) {
    return(
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-center gap-2 text-muted-foreground">
                {icon}
            <span className="text-[10px] uppercase tracking-widest">{label}</span>

            </div>
            <p className="mt-1.5 text-base font-semibold">
                {value}
            </p>
            
        </div>
     
    );
}

// Checkmarked bullet used in the "What's included" list.
function Bullet({ children }: { children: React.ReactNode }) {
  return (
    <p className="flex items-start gap-2">
      <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
      <span className="text-foreground/90">{children}</span>
    </p>
  );
}
