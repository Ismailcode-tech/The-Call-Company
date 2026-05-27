import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState, useRef, useEffect } from "react";

import { RefreshCw } from "lucide-react";
import { Navbar } from "../components/Navbar";
import { GradientBg } from "../components/GradientBg";
import { AIAssistant } from "../components/AIAssistant";
import { verify2FA, signIn } from "../api/auth";

export default function Verify2FAPage() {
    const navigate = useNavigate();
    const location = useLocation();

    // Values are passed from SignInPage through React Router navigation state.
    type Verify2FAState = {
    email?: string;
    emailOrId?: string;
    password?: string;
    };

    const state = location.state as Verify2FAState | null;

    const email = state?.email ?? "";
    const emailOrId = state?.emailOrId ?? "";
    const password = state?.password ?? "";

    // One string per input box makes focus movement and paste handling simple.
    const [code, setCode] = useState<string[]>(["","","","","",""]);
    const [loading, setLoading] = useState(false);
    const [resending, setResending] = useState(false);
    const [resent, setResent] = useState(false);
    const [err, setErr] = useState<string | null>(null);
    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    // Focus the first digit box when the page opens.
    useEffect(() => {
        inputRefs.current[0]?.focus();

    },[]);

    // Accept one digit per box and automatically advance as the user types.
    const handleChange = (index: number, value: string) => {
        if(!/^\d*$/.test(value)) return;

        const newCode = [...code];
        newCode[index] = value.slice(-1);
        setCode(newCode);
        setErr(null);

        if(value && index < 5 ) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    // Backspace from an empty box moves focus to the previous digit.
    const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
        if(e.key === "Backspace" && !code[index] && index > 0 ){
            inputRefs.current[index - 1]?.focus();
        }
    };

    // Paste support lets users paste the whole six-digit code at once.
    const handlePaste = (e: React.ClipboardEvent) => {
        e.preventDefault();
        const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6)
        const newCode = [...code];
        pasted.split("").forEach((char, i) => {
            newCode[i] = char;
        });
        setCode(newCode);

        const lastIndex = Math.min(pasted.length, 5);
        inputRefs.current[lastIndex]?.focus();

    };

    // Verify the full code with the backend before entering the dashboard.
    const submit = async (e: React.FormEvent) => {
        e.preventDefault();
        const fullCode = code.join("");
        if(fullCode.length < 6) {
            setErr("Please enter the full 6-digit code");
            return;
        }
        setLoading(true);
        setErr(null);
        try{
            await verify2FA({ email, code: fullCode });
            navigate("/dashboard");
        } catch {
            setErr("Invalid or expired code. Please try again.")
            setCode(["", "", "", "", "", ""]);
            inputRefs.current[0]?.focus();
        } finally {
            setLoading(false);
        }
    };

    // Re-submit the original credentials so the backend can issue a fresh 2FA code.
    const resend = async () => {
        if (!emailOrId || !password) return;
        setResending(true);
        try
        {
            await signIn({emailOrId, password});
            setResent(true);
            setTimeout(() => setResent(false), 3000);
        } catch {
            setErr("Couldn't resend code. Please try again")
        } finally {
            setResending(false);
        }
    };

    // Without an email in router state, the user likely refreshed or opened the page directly.
    if(!email) {
        return (
            <div className="relative min-h-screen">
                <Navbar />
                <GradientBg variant="subtle" />

                <div className="mx-auto max-w-xl px-5 py-32 text-center">
                    <h1 className="text-3xl  font-semibold tracking-tight">
                        Session expired
                    </h1>

                    <p className="mt-2 text-muted-foreground">
                        Please sign in again.
                    </p>
                    <Link
                     to="/signin"

                     className="mt-6 inline-flex rounded-full bg-primary px-5 py-3 text-sm font-medium text-primary-foreground"
                    >
                        Back to Sign In
                    
                    
                    </Link>

                </div>

            </div>
        );
    }

    return (
        <div className="relative min-h-screen">
            <Navbar />
            <GradientBg variant="subtle" />

            <section className="relative grid h-14 w-14 place-items-center px-5 py-20">
                <div className="relative w-full max-w-md">
                    <div className="absolute -inset-8 -z-10 rounded-[40px] bg-primary/20 blur-3xl" />
                    <div className="glass-strong rounded-3xl p-8 shadow-2xl">
                        {/* Icon placeholder for the verification card. */}
                        <div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-primary/15 text-primary">
                        </div>
                        
                        <h1 className="mt-5 text-center text-3xl font-semibold tracking-tight">
                            Check your email
                        </h1>
                        <p className="mt-2 text-center text-sm text-muted-foreground">
                            We sent a 6-digit code to{" "}
                            <span className="font-medium text-foreground">{email}</span>
                        </p>
                        
                        {/* Six separate inputs give a clear 2FA-code interaction. */}
                        <form
                        onSubmit={submit} className="mt-8"
                        >
                            <div className="flex items-center justify-center gap-2" onPaste={handlePaste}>
                                {code.map((digit, i) => (
                                    <input 
                                      key={i}
                                      ref={(el) => {inputRefs.current[i] = el;}}
                                      type="text" 
                                      inputMode="numeric"
                                      maxLength={1}
                                      value={digit}
                                      onChange={(e) => handleChange(i, e.target.value)}
                                      onKeyDown={(e) => handleKeyDown(i, e)}
                                      className={`h-14 w-12 rounded-2xl border text-center text-xl font-semibold tracking-widest transition-all focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                                        digit
                                          ? "border-primary/60 bg-primary/10 text-foreground"
                                          : "border-white/10 bg-white/5 text-foreground"
                                      } ${err ? "border-destructive" : ""}`}
                                      />
                                ))}
                            </div>
                            {err && (
                                <p className="mt-3 text-center text-xs text-destructive">
                                    {err}
                                </p>
                            )}
                            <button
                              type="submit"
                              disabled={loading || code.join("").length < 6}
                              className="group mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-5 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] transition-transform hover:scale-[1.01] disabled:opacity-60 disabled:cursor-not-allowed"
                            >
                                {loading ? "Verifyingâ€¦" : "Verify & Sign In"}
                            </button>
                        </form>

                        <div className="mt-5 text-center">
                            <p className="text-sm text-muted-foreground">
                                Didn't receive it?{" "}
                                <button
                                 onClick={resend}
                                 disabled={resending}
                                 className="inline-flex items-center gap-1 text-foreground hover:text-primary disabled:opacity-50"
                                >
                                    {resending ? (
                                        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                                    ) : resent ? (
                                        <span className="text-primary">Code sent âœ“</span>
                                    ) : (
                                        "Resend code"
                                    )}
                                </button>
                            </p>
                        </div>

                        <p className="mt-4 text-center text-sm text-muted-foreground">
                            Wrong account?{" "}
                            <Link to="/signin" className="text-foreground hover:text-primary">
                               Sign in again     
                            </Link>
                        </p>
                    </div>

                    
                     
                </div>

            </section>
            <AIAssistant />

        </div>
    )
}
