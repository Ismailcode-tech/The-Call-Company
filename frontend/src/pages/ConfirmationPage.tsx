import { Link} from "react-router-dom";
import { useEffect, useState } from "react";
import { Check, Copy, Share2, ArrowRight } from "lucide-react";
import { Navbar } from "../components/Navbar";
import { AIAssistant } from "../components/AIAssistant";
import { GradientBg } from "../components/GradientBg"; 
import { getCurrentUser, type User } from "../api/auth";
import { getMembership, type  Membership } from "../api/membership";    
import { type Plan } from "../api/plans";
import { usePlans } from "../hooks/usePlans";
import { ProviderBadge}  from "../components/ProviderBadge"; 
import { deviceImage } from "../lib/device-images";     

const DOTS = Array.from({ length: 40 }).map((_, i) => ({
    left: `${((i * 37 + 11) % 100)}%`,
    top: `${((i * 23 + 7) % 60) + 10}%`,
    color: ["#6366F1", "#A78BFA", "#38BDF8", "#F472B6"] [i % 4],
    delay: `${((i * 0.07) % 0.6).toFixed(2)}s`,
    duration: `${3+ (i % 4)}s`,

}));


export default function ConfirmationPage() {
    const { plans: allPlans } = usePlans();
    // Confirmation combines local user data with the current backend membership.
    const [user, setUser] =useState<User | null>(null);
    const [plan, setPlan] = useState<Plan | null>(null);
    const [copied, setCopied] = useState(false);
    const displayName = user?.fname || user?.email || "User";
    const [membership, setMembership] = useState<Membership | null>(null);

    useEffect(() => {
        const CurrentUser = getCurrentUser();
        setUser(CurrentUser);
        getMembership().then((m) =>{
            setMembership(m)
        });
    }, []);
    
    

    // Load the current membership and find the matching plan for the summary card.
    useEffect(() => {
        if (membership && allPlans.length > 0) {
            const foundPlan = allPlans.find((p) => String(p.id) === String(membership.planId));
            setPlan(foundPlan ?? null);
        }
    }, [membership, allPlans]);


    const total2yr = plan ? plan.monthlyPrice * 24 : 0

    // Copying the membership id gives the user a quick account reference.
    const copy = () => {
        if(!user) return
        navigator.clipboard.writeText(`#${user.membershipId || membership?.membershipId}`)
        setTimeout(() => setCopied(false), 1500)
    };

    return (

        <div className="relative min-h-screen">
            <Navbar />
            <GradientBg />

            {/* Animated confetti dots */}

            <div className="pointer-events-none absolute inset-0 -z-0 overflow-hidden">
                {DOTS.map((d, i) => (
                    <span
                    key={i}
                    className="absolute h-2 w-2 rounded-full"
                    style={{
                        left: d.left,
                        top: d.top,
                        background: d.color,
                        opacity: 0.7,
                        animation: `floatDot ${d.duration}  ease-in-out ${d.delay} infinite alternate`,      
                    }}
                    />
                ))}
            </div>
            {/* Inject keyframes for dot movement */}
            <style>{`
                @keyframes floatDot {
                
                    0% { transform: translateY(0px) translateX(0px); opacity: 0.4; }
                    50%{ opacity: 0.9; }
                    100%{ transform: translateY(-30px) translateX(10px); opacity: 0.4; }                    
                }       
            `}</style>

            <section className="relative grid place-items-center px-5 py-20">
                <div className="w-full max-w-2xl text-center">
                    <div className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-primary/15 text-primary">
                        <Check className="h-6 w-6" strokeWidth={2.5}/>
                    </div>
                    <h1 className="mt-6 text-4xl font-semibold tracking-tight md:text-5xl">
                        You're on <span className="text-gradient">The Call.</span>
                    </h1>
                    <p className="mt-3 text-muted-foreground">
                        Welcome aboard{user ? `, ${displayName}`: "User"}.Your plan is live.
                    </p>
                    {user && (
                        <div className="mt-8 inline-flex items-center gap-3 rounded-2xl border border-primary/40 bg-primary/10 px-5 py-3 font-mono text-lg shadow-[0_0_60px_-12px_rgba(99,102,241,0.6)]">
                            <span>#{user.membershipId || membership?.membershipId}</span>
                            <button onClick={copy} className="text-primary hover:opacity-80" aria-label="Copy">
                                {copied ? <Check className="h-4 w-4"/> : <Copy className="h-4 w-4"/>}
                            </button>
                        </div>
                    )}
                    {plan && (
                        <div className="glass-strong mx-auto mt-10 max-w-md rounded-3xl p-6 text-left">
                            <div className="flex items-center justify-between">
                                <ProviderBadge provider={plan.provider} />
                                <span className="text-[10px] uppercase tracking-widest text-muted-foreground">
                                    {plan.tier}
                                </span>
                            </div>
                            {/* Fixed image container keeps the chosen plan artwork centered. */}
                            <div className="my-6 flex items-center justify-center">
                                <img 
                                src={deviceImage(plan)}
                                alt={plan.phoneModel ?? "SIM card"}
                                className="h-40 w-auto max-w-[200px] object-contain drop-shadow-[0_20px_40px_rgba(0,0,0,0.5)]"
                                />
                            </div>
                            <p className="text-lg font-semibold">
                                {plan.name} {plan.phoneModel ? ` · ${plan.phoneModel}` : ""}
                            </p>
                            <div className="mt-3 flex items-end justify-between border-t border-white/10 pt-3">
                                <p className="text-xs uppercase tracking-widest text-muted-foreground">2-year total</p>
                                <p className="text-2xl  font-semibold tracking-tight">£{total2yr}</p>
                            </div>
                        </div>
                    )}

                    <div className="mt-10  flex flex-col items-center justify-center gap-3 sm:flex-row">
                        <Link
                        to="/dashboard"
                        className="inline-flex  items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)]"
                        >
                            Go to Dashboard <ArrowRight className="h-4 w-4" />
                        </Link>
                        <button
                        onClick={() => 
                            navigator.share?.({
                                title: "I joined The Call",
                                url: typeof window !== "undefined" ? window.location.origin : "",

                            }).catch(() => {})
                        }
                        className="inline-flex items-center justify-center gap-2 rounded-full border border-white/10 bg-white/5 px-6 py-3.5 text-sm font-medium hover:bg-white/10"
                        >
                            <Share2 className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            </section>
            <AIAssistant />
        </div>
    );
}
