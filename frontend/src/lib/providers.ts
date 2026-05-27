import type { Provider } from "../api/plans";

// Centralized provider branding so badges, cards, and pages stay visually consistent.
export const PROVIDER_META: Record<
  Provider,
  {
    name: string;
    tagline: string;
    description: string;
    accent: string; 
    bgGlow: string;
    color: string; 
    dot: string;
  }
> = {
  fone: {
    name: "Fone",
    tagline: "The trusted classic.",
    description:
      "Reliable coverage, generous data on the top tiers, and the largest contract phone catalogue. Built for people who just want it to work.",
    accent: "text-fone",
    bgGlow: "from-fone/30",
    color: "var(--fone)",
    dot: "bg-fone",
  },
  gap: {
    name: "Gap",
    tagline: "Truly unlimited.",
    description:
      "The only network with unlimited data on every All-in plan. Premium speeds, premium price, premium devices.",
    accent: "text-gap",
    bgGlow: "from-gap/30",
    color: "var(--gap)",
    dot: "bg-gap",
  },
  flipper: {
    name: "Flipper",
    tagline: "Best value, no fluff.",
    description:
      "Sharp pricing on SIM-only and aggressive bundles on phones. The smart choice when every pound matters.",
    accent: "text-flipper",
    bgGlow: "from-flipper/30",
    color: "var(--flipper)",
    dot: "bg-flipper",
  },
};
