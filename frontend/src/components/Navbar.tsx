
import { Link, useLocation, useNavigate } from "react-router-dom";  
import { useEffect, useState } from "react";
import { ChevronDown, LogOut, LayoutDashboard, User as UserIcon, Menu, X } from "lucide-react";
import { Logo } from "./Logo";
import { getCurrentUser, signOut, type User } from "../api/auth";   

// Primary marketing navigation links.
const links = [
  { to: "/providers", label: "Providers" },
  { to: "/offers", label: "Offers" },
  { to: "/plan-finder", label: "Find My Plan" },
] as const;



export function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();                                    
  const pathname = location.pathname;                                 
  const [user, setUser] = useState<User | null>(null);
  const [open, setOpen] = useState(false);
  const [menu, setMenu] = useState(false);
  const displayName = user?.fname || user?.email || "User";
  const firstName = displayName.split(" ")[0];
const initials = displayName
  .split(" ")
  .map((n) => n[0])
  .slice(0, 2)
  .join("")
  .toUpperCase();

  // Refresh user state after route changes so auth buttons update after sign-in/out.
  useEffect(() => {
    setUser(getCurrentUser());
  }, [pathname]);


  return (

  <header className="sticky top-0 z-[60] px-4 pt-3 pb-2">
    <div className="mx-auto max-w-7xl">

      {/* floating pill */}
      <div
        className="flex h-14 items-center justify-between rounded-2xl px-5"
        style={{
          background: "rgba(10, 10, 25, 0.65)",
          backdropFilter: "blur(24px)",
          WebkitBackdropFilter: "blur(24px)",
          border: "1px solid rgba(255,255,255,0.08)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
        }}
      >
        <Logo />

        {/* Desktop navigation. */}
        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => {
            const active = pathname === l.to;
            return (
              <Link
                key={l.to}
                to={l.to}
                className={`relative rounded-full px-4 py-2 text-sm transition-colors ${
                  active
                    ? "text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {active && (
                  <span className="absolute inset-0 -z-10 rounded-full bg-white/5 ring-1 ring-white/10" />
                )}
                {l.label}
              </Link>
            );
          })}
        </nav>

        {/* Desktop account actions. */}
        <div className="hidden items-center gap-2 md:flex">
          {user ? (
            <div className="relative">
              <button
                onClick={() => setOpen((v) => !v)}
                className="group flex items-center gap-2 rounded-full border border-white/10 bg-white/5 py-1.5 pl-1.5 pr-3 text-sm transition-colors hover:bg-white/10"
              >
                <span className="grid h-7 w-7 place-items-center rounded-full bg-gradient-to-br from-primary to-[oklch(0.5_0.2_300)] text-xs font-semibold text-white">
                  {initials}
                </span>
                <span className="max-w-[120px] truncate">{firstName}</span>
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              </button>
              {open && (
                <div
                  onMouseLeave={() => setOpen(false)}
                  className="glass-strong absolute right-0 top-12 w-56 rounded-2xl p-1.5 shadow-2xl"
                >
                  <Link
                    to="/dashboard"
                    onClick={() => setOpen(false)}
                    className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm hover:bg-white/5"
                  >
                    <LayoutDashboard className="h-4 w-4" /> Dashboard
                  </Link>
                  <Link
                    to="/my-portfolio"
                    onClick={() => setOpen(false)}
                    className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm hover:bg-white/5"
                  >
                    <UserIcon className="h-4 w-4" /> My Portfolio
                  </Link>
                  <div className="my-1 h-px bg-white/10" />
                  <button
                    onClick={() => {
                      signOut();
                      setUser(null);
                      setOpen(false);
                      navigate("/");                                 
                    }}
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm text-destructive/90 hover:bg-destructive/10"
                  >
                    <LogOut className="h-4 w-4" /> Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <>
              <Link
                to="/signin"
                className="rounded-full px-4 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-[0_8px_30px_-10px_rgba(99,102,241,0.7)] transition-transform hover:scale-[1.02] hover:bg-primary/90"
              >
                Get Started
              </Link>
            </>
          )}
        </div>


        {/* Mobile menu button */}
        <button
          onClick={() => setMenu((v) => !v)}
          className="rounded-lg p-2 text-foreground md:hidden"
          aria-label="Menu"
        >
          {menu ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {menu && (
        // Mobile navigation drawer.
        <div className="border-t border-white/5 bg-background/90 px-5 py-4 backdrop-blur-xl md:hidden">
          <div className="flex flex-col gap-1">
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setMenu(false)}
                className="rounded-xl px-3 py-3 text-base text-foreground hover:bg-white/5"
              >
                {l.label}
              </Link>
            ))}
            <div className="my-2 h-px bg-white/10" />
            {user ? (
              <>
                <Link to="/dashboard" onClick={() => setMenu(false)} className="rounded-xl px-3 py-3 text-base hover:bg-white/5">Dashboard</Link>
                <Link to="/my-portfolio" onClick={() => setMenu(false)} className="rounded-xl px-3 py-3 text-base hover:bg-white/5">My Portfolio</Link>
                <button
                  onClick={() => {
                    signOut();
                    setMenu(false);
                    navigate("/");                                   
                  }}
                  className="rounded-xl px-3 py-3 text-left text-base text-destructive/90 hover:bg-destructive/10"
                >Sign Out</button>
              </>
            ) : (
              <>
                <Link to="/signin" onClick={() => setMenu(false)} className="rounded-xl px-3 py-3 text-base hover:bg-white/5">Sign In</Link>
                <Link to="/signup" onClick={() => setMenu(false)} className="rounded-xl bg-primary px-3 py-3 text-base font-medium text-primary-foreground">Get Started</Link>
              </>
            )}
          </div>
        </div>
      )}
    </div>  
  </header>
  );
}
