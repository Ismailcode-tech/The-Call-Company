import { Link , useNavigate } from "react-router-dom";
import { useState } from "react";
import { ArrowRight,RefreshCw } from "lucide-react";
import { Navbar } from "../components/Navbar";                   
import { AIAssistant } from "../components/AIAssistant";
import { GradientBg } from "../components/GradientBg";           
import { verifyEmail } from "../api/auth"; 
import toast from 'react-hot-toast';



export default function VerifyEmailPage(){
    const navigate = useNavigate();
    // The backend accepts either an email address or a membership id.
    const [emailOrId, setEmailOrId] = useState("");
    const [loading, setLoading] = useState(false);
    const [err, setErr] = useState<string | null>(null); 
    const [resendLoading, setResendLoading] = useState(false);

    // Submit credentials and move the user forward after a successful sign-in response.
    const submit = async (e:React.FormEvent) =>{
        e.preventDefault();
        setLoading(true);
        setErr(null);
        try{
            await verifyEmail({emailOrId});
            toast.success("Verification link sent! Please check your email.", {
                duration: 6000,
            });
            setEmailOrId("")

        
        }catch(err: any){
            setErr(err.message || "Invalid email")
        } finally{
            setLoading(false);
        }
    };

    const handleResendLink = async () => {
        if (!emailOrId) {
            setErr("Please enter your email or ID first to resend the link.")
            return;
        }
    
    setResendLoading(true);
    setErr(null);
    try {
        await verifyEmail({ emailOrId });
        toast.success("Link resent successfully!");
    } catch (error: any) {
        setErr(error.message || "Failed to resend link.");
    } finally {
        setResendLoading(false);
    }
    }

    return(
        <div className="relative min-h-screen">
            <Navbar/>
            <GradientBg/>
            <section className="relative grid place-items-center px-5 py-24">
                <div className="relative w-full max-w-md">
                    <div className="absolute -inset-8 -z-10 rounded-[40px] bg-primary/20 blur-3xl"/>
                    <div className="glass-strong rounded-3xl p-8 shadow-2xl ">
                        <h1 className="text-3xl font-semibold tracking-tight">Welcome</h1>
                        <p className="mt-1 text-sm text-muted-foreground"> Verifying it's you...</p>
                        {/* Login form state is controlled by React state above. */}
                        <form action="" onSubmit={submit} className="mt-6 space-y-4">
                            <input type="text" 
                            placeholder="Email or Membership ID" 
                            value={emailOrId} 
                            onChange={((e) => setEmailOrId(e.target.value))}
                            required
                            className="block w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3.5 text-sm placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/30"
                            />
                            {err && (
                                <p className="text-xs text-destructive">{err}</p>
                            )}


                            <button 
                            type="submit" 
                            disabled={loading} 
                            className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-5 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] disabled:opacity-60"
                            >
                                {loading ? "Verify..." : " Verify" }
                                <ArrowRight className="h-4 w-4"/>
                            </button>
                        </form>
                        <div className="mt-5 text-center text-sm text-muted-foreground">
                            Didn't receive the link?{" "}
                            <button 
                                onClick={handleResendLink}
                                disabled={resendLoading}
                                className="text-foreground hover:text-primary font-medium inline-flex items-center gap-1 disabled:opacity-50"
                            >
                                {resendLoading && <RefreshCw className="h-3 w-3 animate-spin" />}
                                Resend Link
                            </button>
                        </div>

                       
                    </div>
                </div>
            </section>
            <AIAssistant/>
        </div>
    )
}
