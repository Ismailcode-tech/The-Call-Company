import { useEffect, useRef, useState } from "react";
import { Send, X, Sparkles } from "lucide-react";
import { chat } from "../api/ai";

// Local message shape for the floating assistant conversation.
interface Msg { id: string; role: "user" | "assistant"; content: string }

// Quick prompts shown before the user sends their first message.
const SUGGESTIONS = [

    "Find me the cheapest plan",
    "What's included in Spender",
    "Help me choose a phone",
    "What's my spending cap?"
];


export function AIAssistant(){
    const [open, setOpen] = useState(false);
    const [msgs, setMsgs] = useState<Msg[]>([
        {
            id: "intro",
            role: "assistant",
            content: "Hey — I'm your Call Assistant. Ask me anything about plans, providers or pricing.",
        },
        
    ]);
    const [input, setInput] = useState("");
    const [typing, setTyping] = useState(false)
    const scrollRef = useRef<HTMLDivElement>(null)

    // Keep the newest message in view as the conversation grows.
    useEffect(() => {
        scrollRef.current?.scrollTo({top:scrollRef.current.scrollHeight, behavior: "smooth"});
    }, [msgs, typing]);

    // Add the user's message immediately, then append the backend assistant reply.
    async function send(text:string) {
        const t = text.trim();
        if(!t) return;
        setInput("");
        setMsgs((m) => [...m, {id: crypto.randomUUID(), role:"user", content: t}]);
        setTyping(true);
        try{
            const reply = await chat(t)
            setMsgs((m) => [...m, {id: crypto.randomUUID(), role: "assistant", content: reply}]);
        } finally {
            setTyping(false);
        }        
    }

    return (
        <>
            {!open && (
                <button
                onClick={() => setOpen(true)}
                aria-label="Open assistant"
                className="fixed bottom-6 right-6 z-50 grid h-14 w-14 place-items-center rounded-full bg-gradient-to-br from-primary to-[oklch(0.55_0.22_300)] text-white shadow-[0_18px_60px_-12px_rgba(99,102,241,0.7)] animate-pulse-ring transition-transform hover:scale-105"
                >
                    <Sparkles className="h-6 w-6" />
                </button>
            )}

            {open && (
                <div className="fixed bottom-6 right-6 z-[100] w-[min(92vw,380px)] animate-fade-up">
                    <div className="overflow-hidden rounded-3xl shadow-[0_30px_80px_-20px_rgba(0,0,0,0.8)]"
                         style={{background:"rgba(10,10,20,0.95)", backdropFilter: "blur(40px)", border: "1px solid rgba(255,255,255,0.10)"}}
                    >
                        {/* Assistant header and close control. */}
                        <div className="flex items-center justify-between border-b border-white/10 bg-gradient-to-r from-primary/15 to-transparent px-4 py-3">
                            <div className="flex items-center gap-2">
                                <div className="grid  h-8 w-8 place-items-center rounded-full bg-primary/20">
                                    <Sparkles className="h-4 w-4 text-primary" />
                                </div>
                                <div className="leading-tight">
                                    <p className="text-sm font-semibold">The Call Assistant</p>
                                    <p className="text-[11px] text-muted-foreground">Always on · AI</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setOpen(false)}
                                className="rounded-lg p-1.5 text-muted-foreground hover:bg-white/5 hover:text-foreground"
                                aria-label="Close"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        </div>
                        {/* Conversation thread. */}
                        <div ref={scrollRef} className="max-h-[360px] space-y-3 overflow-y-auto p-4" 
                             style={{background: "rgba(10,10,20,0.95)"}}>
                                 
                            {msgs.map((m) => (
                                <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                                    <div 
                                      className={`max-w-[85%] rounded-2xl px-3.5 py-2 text-[13px] leading-relaxed ${
                                        m.role === "user"
                                            ? "bg-primary text-primary-foreground"
                                            : "bg-white/5 text-foreground"
                                      }`}
                                      dangerouslySetInnerHTML={{
                                        __html: m.content.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
                                      }}
                                    />
                                </div>
                            ))}

                            {typing && (
                                <div className="flex justify-start">
                                    <div className="flex items-center gap-1 rounded-2xl bg-white/5 px-3.5 py-3">
                                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
                                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
                                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground" />                                     
                                    </div>
                                </div>
                            )}
                        </div>
                        {msgs.length <= 1 && (
                            // Suggestions disappear after the first real exchange.
                            <div className="flex flex-wrap gap-1.5 px-4 pb-3">
                                {SUGGESTIONS.map((s) => (
                                    <button
                                        key={s}
                                        onClick={() => send(s)}
                                        className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-[11px] text-muted-foreground transition-colors hover:bg-white/10 hover:text-foreground"
                                    >
                                        {s}
                                    </button>
                                ))}

                            </div>
                        )}
                        <form
                        onSubmit={(e) => {e.preventDefault(); send(input); }}
                        className="flex items-center gap-2 border-t border-white/10 p-3"
                        >
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Ask anything…"
                                className="flex-1 bg-transparent px-2 py-1.5 text-sm placeholder:text-muted-foreground focus:outline-none"
                            />
                            <button
                            type="submit"
                            aria-label="Send"
                            className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground transition-transform hover:scale-105 disabled:opacity-50"
                            disabled={!input.trim()}
                            >
                                <Send className="h-4 w-4" />
                            </button>
                        </form>
                    </div>
                </div>
            )}        
        </>
    )
}   
