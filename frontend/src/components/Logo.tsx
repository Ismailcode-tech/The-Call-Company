import { Radio } from "lucide-react";
import { Link } from "react-router-dom";

// Brand mark used in the navbar and dashboard sidebar.
export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link
      to="/"
      className={`group inline-flex items-center gap-2 ${className}`}
      aria-label="The Call — home"
    >
      <span className="relative grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-primary to-[oklch(0.55_0.22_295)] shadow-[0_0_24px_-4px_rgba(99,102,241,0.7)]">
        <Radio className="h-4 w-4 text-white" strokeWidth={2.5} />
        <span className="absolute inset-0 rounded-lg ring-1 ring-white/20" />
      </span>
      <span className="text-[15px] font-semibold tracking-tight text-foreground">
        The Call
      </span>
    </Link>
  );
}
