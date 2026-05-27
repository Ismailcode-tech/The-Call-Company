// src/pages/SignUpPage.tsx
import { Link, useNavigate } from "react-router-dom";           
import React, { useMemo, useState } from "react";
import { AlertTriangle, ArrowRight, Eye, EyeOff } from "lucide-react";
import { Navbar } from "../components/Navbar";                   
import { AIAssistant } from "../components/AIAssistant";         
import { GradientBg } from "../components/GradientBg";           
import { signUp } from "../api/auth";                            

// Simple password strength score used to drive the four-bar strength meter.
function strength(pw: string) {
  let s = 0;
  if (pw.length >= 8) s++;
  if (/[A-Z]/.test(pw)) s++;
  if (/[0-9]/.test(pw)) s++;
  if (/[^A-Za-z0-9]/.test(pw)) s++;
  return s;
}

// Calculates age from the date input so under-18 users can get the spending-cap warning.
function ageFromDob(dob: string) {
  if (!dob) return null;
  const d = new Date(dob);
  if (isNaN(d.getTime())) return null;
  const now = new Date();
  let a = now.getFullYear() - d.getFullYear();
  const m = now.getMonth() - d.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < d.getDate())) a--;
  return a;
}

export default function SignUpPage() {                           
  const navigate = useNavigate();
  // Each input is controlled so validation and submit can read the latest values.
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [dob, setDob] = useState("");
  const [pw, setPw] = useState("");
  const [pw2, setPw2] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const age = ageFromDob(dob);
  const under18 = age !== null && age < 18;
  const s = useMemo(() => strength(pw), [pw]);

  // Validate local form rules before sending account data to the backend.
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    if (pw !== pw2) { setErr("Passwords don't match"); return; }
    if (s < 2) { setErr("Use a stronger password"); return; }
    setLoading(true);
    try {
      await signUp({ fullName, email, password: pw, dateOfBirth: dob });
      navigate("/dashboard");                                    
    } catch {
      setErr("Couldn't create account");
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
            <h1 className="text-3xl font-semibold tracking-tight">Join The Call</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              50,000+ members already onboard.
            </p>

            <form onSubmit={submit} className="mt-6 space-y-4">
              <Field label="Full name" value={fullName} onChange={setFullName} type="text" required />
              <Field label="Date of birth" value={dob} onChange={setDob} type="date" required />
              {under18 && (
                <div className="flex items-start gap-2 rounded-xl border border-amber-400/30 bg-amber-400/10 p-3 text-xs text-amber-300">
                  <AlertTriangle className="mt-0.5 h-4 h-4 w-4 shrink-0" />
                  <p>
                    You're under 18. A soft <strong>£15/month spending cap</strong> will be applied to your account.
                  </p>
                </div>
              )}
              <Field label="Email" value={email} onChange={setEmail} type="email" required />
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
                {pw && (
                  <div className="mt-2 flex gap-1">
                    {[0, 1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className={`h-1 flex-1 rounded-full transition-colors ${
                          i < s
                            ? s >= 3 ? "bg-emerald-400" : s === 2 ? "bg-amber-400" : "bg-rose-400"
                            : "bg-white/10"
                        }`}
                      />
                    ))}
                  </div>
                )}
              </div>
              <Field label="Confirm password" value={pw2} onChange={setPw2} type={show ? "text" : "password"} required />

              {err && <p className="text-xs text-destructive">{err}</p>}

              <button
                type="submit"
                disabled={loading}
                className="group relative inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-5 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] transition-transform hover:scale-[1.01] disabled:opacity-60"
              >
                {loading ? "Creating…" : "Create Account"}
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </button>
            </form>

            <p className="mt-5 text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link to="/signin" className="text-foreground hover:text-primary">Sign In</Link>
            </p>
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
