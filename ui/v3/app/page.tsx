"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { InfiniteGrid } from "@/components/ui/the-infinite-grid";
import { PromptInputBox } from "@/components/ui/ai-prompt-box";
import { ThemeToggle } from "@/components/theme-toggle";
import { patchBrief } from "@/lib/state";

const STARTER_CHIPS = [
  { label: "Business website", prompt: "A business website that introduces what I do and lets people reach out." },
  { label: "Online store",     prompt: "An online store where customers can browse products and check out." },
  { label: "Portfolio",        prompt: "A portfolio site that showcases my work and bio." },
  { label: "Booking site",     prompt: "A booking site where clients can schedule appointments with me." },
  { label: "Restaurant menu",  prompt: "A restaurant site with my menu, hours, and a reservation option." },
  { label: "Real estate",      prompt: "A real-estate page that showcases listings and lets buyers contact me." },
];

export default function WelcomePage() {
  const router = useRouter();
  const [prefill, setPrefill] = useState<string | null>(null);

  const handleSend = (message: string, files?: File[]) => {
    if (typeof window === "undefined") return;
    patchBrief({
      extra_context: message,
      business_name: "Untitled Project",
    });
    if (files && files.length > 0) {
      sessionStorage.setItem(
        "pebble.pendingFiles",
        JSON.stringify(files.map((f) => ({ name: f.name, type: f.type, size: f.size }))),
      );
    }
    router.push("/intake");
  };

  return (
    <InfiniteGrid className="min-h-screen">
      <header className="absolute top-0 inset-x-0 z-10 flex justify-between items-center h-20 px-8">
        <span className="font-display text-3xl font-bold tracking-tight text-primary">Pebble.</span>
        <ThemeToggle />
      </header>

      <main className="relative z-10 flex flex-col items-center text-center px-4 max-w-3xl mx-auto space-y-8 pointer-events-none py-32">
        <div className="space-y-3 pointer-events-auto">
          <h1 className="font-display text-5xl md:text-6xl font-bold tracking-tight text-foreground drop-shadow-sm">
            What would you like to build today?
          </h1>
          <p className="text-xl text-muted-foreground max-w-xl mx-auto">
            Tell me in your own words. I&apos;ll handle the technical parts.
          </p>
        </div>

        <div className="w-full max-w-2xl pointer-events-auto">
          <PromptInputBox
            onSend={handleSend}
            placeholder={
              prefill ??
              "Example: I run a bakery in Brooklyn and I want a website where customers can see my menu and order online."
            }
          />
        </div>

        <div className="flex flex-wrap justify-center gap-2 pointer-events-auto">
          {STARTER_CHIPS.map((chip) => (
            <button
              key={chip.label}
              onClick={() => setPrefill(chip.prompt)}
              className="px-4 py-2 bg-card hover:bg-accent border border-border rounded-full text-sm font-semibold text-foreground transition-colors"
            >
              {chip.label}
            </button>
          ))}
        </div>
      </main>

      <footer className="absolute bottom-0 inset-x-0 py-8 text-center px-4 pointer-events-none z-10">
        <p className="text-sm text-muted-foreground max-w-lg mx-auto">
          You&apos;ll see exactly what I&apos;m doing every step of the way. Nothing is final until you say it is.
        </p>
      </footer>
    </InfiniteGrid>
  );
}
