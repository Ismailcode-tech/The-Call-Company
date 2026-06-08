import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Smartphone,
  Building2,
  Tag,
  UserCircle2,
  LogOut,
} from "lucide-react";
import { Logo } from "./Logo";
import { signOut } from "../api/auth";


// Signed-in dashboard navigation items and their icons.
const items = [
  { to: "/dashboard",     label: "Dashboard",   icon: LayoutDashboard },
  { to: "/my-plan",       label: "My Plan",     icon: Smartphone },
  { to: "/providers",     label: "Providers",   icon: Building2 },
  { to: "/offers",        label: "Offers",      icon: Tag },
  { to: "/my-portfolio",  label: "My Portfolio",icon: UserCircle2 },
] as const;

export function Sidebar() {
  // Current route decides which sidebar item is highlighted.
  const { pathname } = useLocation();
  const navigate = useNavigate();


  return (
    <aside className="hidden w-64 shrink-0 border-r border-white/5 bg-sidebar/80 backdrop-blur-xl lg:flex lg:flex-col">
      <div className="flex h-16 items-center border-b border-white/5 px-5">
        <Logo />
      </div>
      <nav className="flex-1 space-y-0.5 p-3">
        {items.map((it) => {
          const active = pathname === it.to;
          const Icon = it.icon;
          return (
            <Link
              key={it.to}
              to={it.to}
              className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all ${
                active
                  ? "bg-primary/15 text-foreground ring-1 ring-primary/30"
                  : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
              }`}
            >
              <Icon
                className={`h-4 w-4 ${active ? "text-primary" : ""}`}
                strokeWidth={2}
              />
              <span>{it.label}</span>
              {active && (
                <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary shadow-[0_0_10px_var(--primary)]" />
              )}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-white/5 p-3">
        <button
          onClick={async () => {
            await signOut();
            navigate("/");
          }}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground transition-all hover:bg-destructive/10 hover:text-destructive"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
