// Reusable decorative background. "subtle" lowers opacity for dense pages.
export function GradientBg({ variant = "default" }: { variant?: "default" | "subtle" }) {
  const op = variant === "subtle" ? "opacity-50" : "opacity-100";
  return (
    <div aria-hidden className={`pointer-events-none absolute inset-0 -z-10 overflow-hidden ${op}`}>
      <div className="absolute inset-0 bg-mesh" />
      <div className="absolute inset-0 bg-grid" />
      <div className="absolute -top-32 left-1/4 h-[420px] w-[420px] rounded-full bg-primary/30 blur-3xl animate-float" />
      <div
        className="absolute -bottom-40 right-1/4 h-[520px] w-[520px] rounded-full bg-[oklch(0.6_0.2_300)]/25 blur-3xl animate-float"
        style={{ animationDelay: "-3s" }}
      />
      <div
        className="absolute top-1/3 right-1/2 h-[300px] w-[300px] rounded-full bg-[oklch(0.7_0.15_220)]/15 blur-3xl animate-float"
        style={{ animationDelay: "-1.5s" }}
      />
    </div>
  );
}
