import { Link, useNavigate } from "react-router-dom";
import React, { useState } from "react";
import { ArrowLeft,ArrowRight, Apple, Smartphone, Check } from "lucide-react";
import { Navbar } from "../components/Navbar";
import { AIAssistant } from "../components/AIAssistant";
import { GradientBg } from "../components/GradientBg";



interface Answers {
    path?: "phone" | "sim" | "both";
    justPhone?: boolean;
    brand?: "apple" | "samsung" | "any";
    data?: number;
    calls?: 500 | 750 | -1;
    priority?: "price" | "data" | "unlimited"
    budget?: number;
}

export default function PlanFinderPage() {
    const navigate = useNavigate();
    // step controls which question is visible; a stores every answer collected so far.
    const [step, setStep] = useState(0);
    const [a, setA] = useState<Answers>({});
    const totalSteps = a.path === "sim" ? 5 : 6;
    const next = () => setStep((s) => s+1);
    const back = () => setStep((s) => Math.max(0,s - 1));

    // Serialize answers into the results page query string.
    const finish = (final: Answers) => {
        const params = new URLSearchParams();
        const resolvedPath = final.path === "both" ? "phone" : final.path;
        if(resolvedPath) params.set("path", resolvedPath);
        if(final.justPhone) params.set("justPhone", "1");
        if(final.brand && final.brand !== "any") params.set("brand", final.brand)
        if(final.data !== undefined) params.set("data", String(final.data))
        if(final.calls !== undefined) params.set("calls", String(final.calls))
        if(final.priority) params.set("priority", final.priority)
        if(final.budget !== undefined) params.set("budget", String(final.budget))
        navigate(`/results?${params.toString()}`);
    };

 
  return (
    <div className="relative min-h-screen">
      <Navbar />
      <GradientBg variant="subtle" />

      <div className="relative mx-auto flex min-h-[calc(100vh-4rem)] max-w-3xl flex-col px-5 pb-20 pt-10">
        
        {/* Progress bar — INSIDE main container */}
        <div className="mb-12">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Step {step + 1} of {totalSteps}</span>
            <Link to="/" className="hover:text-foreground">Cancel</Link>
          </div>
          {/* ← outer div NOT self-closing */}
          <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/5">
            <div
              className="h-full rounded-full bg-gradient-to-r from-primary to-[oklch(0.55_0.22_300)] transition-all duration-500"
              style={{ width: `${((step + 1) / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Questions — INSIDE main container */}
        <div className="flex-1">
          {step === 0 && (
            <Question title="What are you looking for?">
              <Choice
                onClick={() => { setA({ ...a, path: "both", justPhone: false }); next(); }}
                selected={a.path === "both"}
                title="Phone + SIM plan"
                desc="A new device bundled with data, calls and texts."
              />
              <Choice
                onClick={() => { setA({ ...a, path: "sim", justPhone: false, brand: undefined }); next(); }}
                selected={a.path === "sim"}
                title="SIM only"
                desc="Bring your own phone — flexible monthly plans, no commitment."
              />
              <Choice
                onClick={() => {
                  const final: Answers = { ...a, path: "phone", justPhone: true, brand: undefined };
                  setA(final);
                  finish(final);
                }}
                selected={a.path === "phone" && a.justPhone === true}
                title="Phone only"
                desc="Just the handset on a 24-month plan — skip straight to devices."
              />
            </Question>
          )}

          {step === 1 && a.path === "both" && (
            <Question title="Got a phone preference?">
              <Choice
                onClick={() => { setA({ ...a, brand: "apple" }); next(); }}
                selected={a.brand === "apple"}
                title="Apple"
                icon={<Apple className="h-5 w-5" />}
                desc="iPhone 14 Pro, iPhone 14 or iPhone 13."
              />
              <Choice
                onClick={() => { setA({ ...a, brand: "samsung" }); next(); }}
                selected={a.brand === "samsung"}
                title="Samsung"                                    // ← was "Apple" bug fixed
                icon={<Smartphone className="h-5 w-5" />}
                desc="Galaxy S22 or Galaxy S21."
              />
              <Choice
                onClick={() => { setA({ ...a, brand: "any" }); next(); }}
                selected={a.brand === "any"}
                title="No preference"
                desc="Show me the best of both worlds."
              />
            </Question>
          )}

          {((step === 2 && a.path === "both") || (step === 1 && a.path === "sim")) && (
            <Question title="How much data do you need?">
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[
                  { v: 1, l: "Light", h: "Up to 1GB" },
                  { v: 5, l: "Average", h: "5GB" },
                  { v: 35, l: "Heavy", h: "35GB+" },
                  { v: -1, l: "Unlimited", h: "No caps" },
                ].map((o) => (
                  <button
                    key={o.v}
                    onClick={() => { setA({ ...a, data: o.v }); next(); }}
                    className={`group rounded-2xl border p-5 text-left transition-all ${
                      a.data === o.v
                        ? "border-primary/60 bg-primary/10 ring-1 ring-primary/40"
                        : "border-white/10 bg-white/[0.03] hover:bg-white/[0.07]"
                    }`}
                  >
                    <p className="text-xl font-semibold tracking-tight">{o.l}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{o.h}</p>
                  </button>
                ))}
              </div>
            </Question>
          )}

          {((step === 3 && a.path === "both") || (step === 2 && a.path === "sim")) && (
            <Question title="How many calls & texts do you need?">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                {[
                  { v: 500 as const, l: "500", h: "Light caller — 500 mins / texts" },
                  { v: 750 as const, l: "750", h: "Balanced — 750 mins / texts" },
                  { v: -1 as const, l: "Unlimited", h: "Talk & text without limits" },
                ].map((o) => (
                  <button
                    key={o.v}
                    onClick={() => { setA({ ...a, calls: o.v }); next(); }}
                    className={`group rounded-2xl border p-5 text-left transition-all ${
                      a.calls === o.v
                        ? "border-primary/60 bg-primary/10 ring-1 ring-primary/40"
                        : "border-white/10 bg-white/[0.03] hover:bg-white/[0.07]"
                    }`}
                  >
                    <p className="text-xl font-semibold tracking-tight">{o.l}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{o.h}</p>
                  </button>
                ))}
              </div>
            </Question>
          )}

          {((step === 4 && a.path === "both") || (step === 3 && a.path === "sim")) && (
            <Question title="What matters most to you?">
              <Choice
                onClick={() => { setA({ ...a, priority: "price" }); next(); }}
                selected={a.priority === "price"}
                title="Best Price"
                desc="Lowest monthly cost — keep it lean."
              />
              <Choice
                onClick={() => { setA({ ...a, priority: "data" }); next(); }}
                selected={a.priority === "data"}
                title="Most Data"
                desc="Stream, scroll and tether without thinking."
              />
              <Choice
                onClick={() => { setA({ ...a, priority: "unlimited" }); next(); }}
                selected={a.priority === "unlimited"}
                title="Unlimited Talk & Text"
                desc="Calls and messages without limits."
              />
            </Question>
          )}

          {((step === 5 && a.path === "both") || (step === 4 && a.path === "sim")) && (
            <Question title="What's your monthly budget?">
              <BudgetSlider
                value={a.budget ?? (a.path === "both" ? 60 : 20)}
                onChange={(v) => setA({ ...a, budget: v })}
              />
              <button
                onClick={() => finish({ ...a, budget: a.budget ?? (a.path === "both" ? 60 : 20) })}
                className="mt-8 inline-flex items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-sm font-medium text-primary-foreground shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] transition-transform hover:scale-[1.02]"
              >
                Match my plans
                <ArrowRight className="h-4 w-4" />
              </button>
            </Question>
          )}
        </div>

        {/* Back button — INSIDE main container */}
        {step > 0 && (
          <button
            onClick={back}
            className="mt-12 inline-flex w-fit items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
        )}
      </div>

      <AIAssistant />
    </div>
  );
}

// Shared wrapper for each question screen.
function Question({title, children}: {title:string; children:React.ReactNode}) {
    return (
        <div className="animate-fade-up">
            <h1 className="text-balance text-4xl font-semibold tracking-tight md:text-5xl">{title}</h1>
            <div className="mt-10 space-y-3">{children}</div>
        </div>
    );
}

// Large selectable option row used across multiple finder steps.
function Choice({title, desc, onClick, selected, icon,

}: {
    title: string; desc: string; onClick: () => void; selected?: boolean; icon?: React.ReactNode;
}) {

    return(
        <button 
        onClick={onClick}
        className={`group flex w-full items-center justify-between rounded-2xl border p-5 text-left transition-all ${
            selected ? "border-primary/60 bg-primary/10 ring-1 ring-primary/40"
            : "border-white/10 bg-white/[0.03] hover:-translate-y-0.5 hover:border-white/20 hover:bg-white/[0.07]"
        }`}
        >
            <div className="flex items-center gap-4">
                {icon && (
                    <div className="grid h-10 w-10 place-items-center rounded-xl bg-white/5 text-foreground">
                        {icon}
                    </div>
                )}
                <div>
                    <p className="text-lg  font-semibold tracking-tight">{title}</p>
                    <p className="mt-0.5  text-sm text-muted-foreground">{desc}</p>
                </div>
            </div>
            <div className={`grid h-7 w-7 place-items-center rounded-full transition-all ${
               selected
               ? "bg-primary text-primary-foreground shadow-[0_0_24px_rgba(99,102,241,0.6)]"
               : "border border-white/10 text-transparent group-hover:border-white/30"
                }`}>
                    <Check className="h-4 w-4"/>
            </div>
        </button>
    );
}


// Budget input for the final finder step.
function BudgetSlider({value, onChange}: {value:number; onChange: (v:number) => void}) {
    return(
        <div className="rouned-2xl border border-white/10 bg-white/[0.03] p-7">

            <div className="flex items-baseline justify-between">
                <p className="text-xs uppercase tracking-widest text-muted-foreground">Up to</p>
                <p className="text-5xl font-semibold tracking-tight">
                    £{value}
                    <span className="text-base font-normal text-muted-foreground">/mo</span>
                </p>
            </div>
            <input
            type="range"
            min={5}
            max={100}
            step={1}
            value={value}
            onChange={(e) => onChange(parseInt(e.target.value))}
            className="mt-6 w-full accent-[var(--primary)]"
            />
            <div className="mt-1 flex justify-between text-[10px] text-muted-foreground">
                <span>£5</span>
                <span>£100</span>
            </div>
        </div>
    );
}
