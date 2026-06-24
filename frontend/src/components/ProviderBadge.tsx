import type { Provider } from "../api/plans";
import { PROVIDER_META } from "../lib/providers";

// Small provider pill with colors pulled from the central provider metadata.
export function ProviderBadge({
  provider,
  size = "sm",
}: {
  provider: Provider;
  size?: "sm" | "md";
}) {
  // Size only changes padding and text scale; colors always come from PROVIDER_META.
  const meta = PROVIDER_META[provider] ?? {
    name: provider,
    color: "transparent",
    dot: "bg-white/10",
    tagline: "",
    description: "",
    accent: "",
    bgGlow: "",
  };
  const px = size === "md" ? "px-3 py-1.5 text-xs" : "px-2.5 py-1 text-[11px]";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${px} font-medium uppercase tracking-wider`}
      style={{
        color: meta.color,
        borderColor: `color-mix(in oklab, ${meta.color} 35%, transparent)`,
        background: `color-mix(in oklab, ${meta.color} 10%, transparent)`,
      }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: meta.color }} />
      {meta.name}
    </span>
  );
}
