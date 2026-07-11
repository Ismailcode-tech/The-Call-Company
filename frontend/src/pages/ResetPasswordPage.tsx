// src/pages/SignUpPage.tsx
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";           
import React, { useState } from "react";
import { ArrowRight, Eye, EyeOff } from "lucide-react";
import { Navbar } from "../components/Navbar";                   
import { AIAssistant } from "../components/AIAssistant";         
import { GradientBg } from "../components/GradientBg";           
import { ResetPassword } from "../api/auth";                            
import toast from 'react-hot-toast';

export default function ResetPasswordPage() {                         
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const state = (location.state as { emailOrId?: string; email?: string } | null) ?? {};
  const resetToken = searchParams.get("token") ?? "";
  // Each input is controlled so validation and submit can read the latest values.
  const [email] = useState(state.emailOrId ?? state.email ?? "");
  const [pw, setPw] = useState("");
  const [pw2, setPw2] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

 



  // Validate local form rules before sending account data to the backend.
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    if (pw !== pw2) { setErr("Passwords don't match"); return; }
    if (!resetToken) {
      setErr("Missing reset information. Please open the reset link from your email.");
      return;
    }
    // if (s < 2) { setErr("Use a stronger password"); return; }
    setLoading(true);
    try {
      await ResetPassword({ password: pw, confirmPassword: pw2, resetToken, emailOrId: email });
        toast.success('Password changed successfully!');
      navigate("/dashboard", {
        state:{
          email,
          emailOrId: email, // since we don't have an ID until after sign-up, just reuse the email for the 2FA step
          password: pw,   // same for password, so the user doesn't have to re-enter it on the 2FA page

        }
      });                                    
    } catch {
      setErr("Couldn't reset password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen">
      <Navbar />
      <GradientBg />
      <section className="relative grid place-items-center px-5 py-20">
        <div className="relative w-full max-w-md">
          <div className="absolute -inset-8 -z-10 rounded-[40px] bg-primary/20 blur-3xl" />
          <div className="glass-strong rounded-3xl p-8 shadow-2xl">
            <h1 className="text-3xl font-semibold tracking-tight">Reset Password</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Enter your new password below.
            </p>

            <form onSubmit={submit} className="mt-6 space-y-4">
            
             
              <div>
                <Field
                  label="Password"
                  value={pw}
                  onChange={setPw}
                  type={show ? "text" : "password"}
                  required
                  suffix={
                    <button type="button" onClick={() => setShow((v) => !v)} className="text-muted-foreground">
                      {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  }
                />
                
              </div>
              <Field label="Confirm password" value={pw2} onChange={setPw2} type={show ? "text" : "password"} required />

              {err && <p className="text-xs text-destructive">{err}</p>}

              <button
                type="submit"
                disabled={loading}
                className="group relative inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-5 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] transition-transform hover:scale-[1.01] disabled:opacity-60"
              >
                {loading ? "Resetting…" : "Reset Password"}
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </button>
            </form>

            
          </div>
        </div>
      </section>
      <AIAssistant />       
    </div>
  );
}




function Field({
    label, value, onChange, type, required, suffix,


}:{
    label: string; value: string; onChange: (v:string)=> void;
    type: string; required?:boolean; suffix?:React.ReactNode; 
}) {
    const [focus, setFocus] = useState(false)
    const filled = value.length > 0;
    // Date inputs have browser placeholder text, so their label always stays floated.
    const isDate = type === "date";
    const active = focus || filled || isDate;

    return(
        <label className="relative block">
            <span className={`pointer-events-none absolute left-4 transition-all ${
                active
                ? "top-1.5 text-[10px] uppercase tracking-widest text-primary"
                :  "top-1/2 -translate-y-1/2 text-sm text-muted-foreground"
            
            }`}>
                {label}

            </span>

            <input 
            type={type}
            required={required}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={() => setFocus(true)}
            onBlur={() => setFocus(false)}
            className="block w-full rounded-xl border border-white/10 bg-white/5 px-4 pb-2 pt-7 text-sm text-foreground transition-colors focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
            {suffix && <span className="absolute right-3 top-1/2 -translate-y-1/2">{suffix}</span>}

        </label>
    )
}
