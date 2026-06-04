export function GradientBg({ variant = "default" }: { variant?: "default" | "subtle" }) {
  const op = variant === "subtle" ? "opacity-80" : "opacity-100";
  return (
    <div aria-hidden className={`pointer-events-none absolute inset-0 -z-10 overflow-hidden ${op}`}>
      <div className="absolute inset-0 bg-mesh" />
      <div className="absolute inset-0 bg-grid" />

      {/* indigo — top left */}
      <div
        className="absolute -top-40 left-1/4 h-[700px] w-[700px] animate-float rounded-full"
        style={{
          background: "radial-gradient(circle, rgba(99,102,241,0.6) 0%, transparent 70%)",
          filter: "blur(80px)",
        }}
      />

      {/* purple — bottom right */}
      <div
        className="absolute -bottom-40 right-1/4 h-[800px] w-[800px] animate-float rounded-full"
        style={{
          background: "radial-gradient(circle, rgba(139,92,246,0.5) 0%, transparent 70%)",
          filter: "blur(80px)",
          animationDelay: "-3s",
        }}
      />

      {/* teal — middle */}
      <div
        className="absolute top-1/3 left-1/2 h-[600px] w-[600px] animate-float rounded-full"
        style={{
          background: "radial-gradient(circle, rgba(56,189,248,0.4) 0%, transparent 70%)",
          filter: "blur(80px)",
          animationDelay: "-1.5s",
        }}
      />

      {/* pink — top right */}
      <div
        className="absolute -top-20 right-1/3 h-[500px] w-[500px] animate-float rounded-full"
        style={{
          background: "radial-gradient(circle, rgba(244,114,182,0.35) 0%, transparent 70%)",
          filter: "blur(80px)",
          animationDelay: "-2.5s",
        }}
      />

      {/* blue — bottom left */}
      <div
        className="absolute bottom-1/4 -left-20 h-[500px] w-[500px] animate-float rounded-full"
        style={{
          background: "radial-gradient(circle, rgba(99,102,241,0.4) 0%, transparent 70%)",
          filter: "blur(80px)",
          animationDelay: "-4s",
        }}
      />
    </div>
  );
}



