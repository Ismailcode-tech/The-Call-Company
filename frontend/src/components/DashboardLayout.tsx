import { Sidebar } from "./Sidebar";
import { AIAssistant } from "./AIAssistant";


// Shared shell for signed-in pages: sidebar navigation, page content, and assistant.
export function DashboardLayout({ children }: { children: React.ReactNode }) {


  return (
    <div className="flex min-h-screen w-full">
      <Sidebar />
      <main className="relative flex-1 overflow-hidden">
        <div className="absolute inset-0 -z-10 bg-mesh opacity-40" />
        <div className="mx-auto max-w-6xl px-5 py-10 lg:px-10 lg:py-12">{children}</div>
      </main>
      <AIAssistant />
    </div>
  );
}
