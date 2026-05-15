"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { InfiniteGrid } from "@/components/ui/the-infinite-grid";
import { PromptInputBox } from "@/components/ui/ai-prompt-box";
import { ThemeToggle } from "@/components/theme-toggle";
import { patchBrief, getUserProfile, setUserProfile } from "@/lib/state";

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
  const [firstName, setFirstName] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const profile = getUserProfile();
    setFirstName(profile.firstName || null);
    setMounted(true);
  }, []);

  const handleNameSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const input = e.currentTarget.elements.namedItem("name") as HTMLInputElement;
    const name = input.value.trim();
    if (!name) return;
    setUserProfile({ firstName: name });
    setFirstName(name);
  };

  const handleSend = (message: string, files?: File[]) => {
    if (typeof window === "undefined") return;
    patchBrief({
      extra_context: message,
      business_name: "Untitled Project",
      user_first_name: firstName || undefined,
    });
    if (files && files.length > 0) {
      sessionStorage.setItem(
        "pebble.pendingFiles",
        JSON.stringify(files.map((f) => ({ name: f.name, type: f.type, size: f.size }))),
      );
    }
    router.push("/intake");
  };

  // Headline rotates based on whether we know the user's name.
  const headline = firstName
    ? `What's on your mind, ${firstName}?`
    : "What would you like to build today?";

  return (
    <InfiniteGrid className="min-h-screen">
      <header className="absolute top-0 inset-x-0 z-10 flex justify-between items-center h-20 px-8">
        <span className="font-display text-3xl font-bold tracking-tight text-primary">Pebble.</span>
        <ThemeToggle />
      </header>

      <main className="relative z-10 flex flex-col items-center text-center px-4 max-w-3xl mx-auto space-y-8 pointer-events-none py-32">
        <div className="space-y-3 pointer-events-auto min-h-[170px]">
          <AnimatePresence mode="wait">
            <motion.h1
              key={firstName ?? "anon"}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.4 }}
              className="font-display text-5xl md:text-6xl font-bold tracking-tight text-foreground drop-shadow-sm"
            >
              {headline}
            </motion.h1>
          </AnimatePresence>
          <p className="text-xl text-muted-foreground max-w-xl mx-auto">
            Tell me in your own words. I&apos;ll handle the technical parts.
          </p>
        </div>

        {/* First-visit ask for name — small, friendly, dismissable by just typing the prompt instead */}
        {mounted && !firstName && (
          <motion.form
            onSubmit={handleNameSubmit}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="pointer-events-auto flex items-center gap-2 px-4 py-2 bg-card/80 backdrop-blur rounded-full border border-border"
          >
            <span className="text-sm text-muted-foreground">What should I call you?</span>
            <input
              name="name"
              autoComplete="given-name"
              placeholder="First name"
              className="bg-transparent text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none w-32"
            />
            <button
              type="submit"
              className="text-sm font-semibold text-primary hover:underline"
            >
              Save
            </button>
          </motion.form>
        )}

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
