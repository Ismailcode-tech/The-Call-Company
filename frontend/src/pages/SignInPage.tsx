import { Link , useNavigate } from "react-router-dom";
import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { Navbar } from "../components/Navbar";                   
import { AIAssistant } from "../components/AIAssistant";
import { GradientBg } from "../components/GradientBg";           
import { signIn } from "../api/auth"; 




export default function SignInPage(){
    const navigate = useNavigate();
    // The backend accepts either an email address or a membership id.
    const [emailOrId, setEmailOrId] = useState("");
    const [pw, setPw] = useState("");
    const [loading, setLoading] = useState(false);
    const [err, setErr] = useState<string | null>(null); 

    // Submit credentials and move the user forward after a successful sign-in response.
    const submit = async (e:React.FormEvent) =>{
        e.preventDefault();
        setLoading(true);
        try{
            const result = await signIn({emailOrId, password:pw});
            // backend returns { requires2FA: true, email: "..." }
            if(result.requires2FA){
                    navigate("/verify-2fa", {
                    state: {
                    email: result.email,
                    emailOrId: emailOrId,
                    password: pw,
                    }
                });

            

            // If OTP verification is not required, log in directly and go to the dashboard
            }   else {
                navigate("/dashboard");
            }
          
            
        }catch(err: any){
            setErr(err.message || "Invalid email or password")
        } finally{
            setLoading(false);
        }
    };
    return(
        <div className="relative min-h-screen">
            <Navbar/>
            <GradientBg/>
            <section className="relative grid place-items-center px-5 py-24">
                <div className="relative w-full max-w-md">
                    <div className="absolute -inset-8 -z-10 rounded-[40px] bg-primary/20 blur-3xl"/>
                    <div className="glass-strong rounded-3xl p-8 shadow-2xl ">
                        <h1 className="text-3xl font-semibold tracking-tight">Welcome back</h1>
                        <p className="mt-1 text-sm text-muted-foreground"> Sign in to manage your plan.</p>
                        {/* Login form state is controlled by React state above. */}
                        <form action="" onSubmit={submit} className="mt-6 space-y-4">
                            <input type="text" 
                            placeholder="Email or Membership ID" 
                            value={emailOrId} 
                            onChange={((e) => setEmailOrId(e.target.value))}
                            required
                            className="block w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3.5 text-sm placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/30"
                            />
                            <input 
                            type="password" 
                            placeholder="Password" 
                            value={pw} 
                            onChange={((e) => setPw(e.target.value))}
                            required
                            className="block w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3.5 text-sm placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/30" 
                            />
                            <div className="flex justify-end">
                                <a href="verify-email" className="text-xs text-muted-foreground hover:text-foreground">
                                    Forget pasword?
                                </a>
                            </div>
                            {err && (
                                <p className="text-xs text-destructive">{err}</p>
                            )}


                            <button 
                            type="submit" 
                            disabled={loading} 
                            className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-5 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] disabled:opacity-60"
                            >
                                {loading ? "Signing in..." : "Sign In" }
                                <ArrowRight className="h-4 w-4"/>
                            </button>
                        </form>
                        <p className="mt-5 text-center text-sm text-muted-foreground">
                            Don't have an account?{" "}
                            <Link to="/signup" className="text-foreground hover:text-primary">Sign Up</Link>
                        </p>
                    </div>
                </div>
            </section>
            <AIAssistant/>
        </div>
    )
}
