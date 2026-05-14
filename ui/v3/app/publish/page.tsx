"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Share2, Eye, Edit3, Droplet } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { getLastBuild } from "@/lib/state";

export default function PublishPage() {
  const router = useRouter();
  const [build, setBuild] = useState<ReturnType<typeof getLastBuild>>(null);
  const [shareLabel, setShareLabel] = useState("Share");

  useEffect(() => {
    const b = getLastBuild();
    if (!b) {
      router.push("/");
      return;
    }
    setBuild(b);
  }, [router]);

  const slug = (build?.slug as string) || "your-site";
  const previewUrl = (build?.preview_url as string) || "#";

  const handleShare = () => {
    navigator.clipboard?.writeText(`${slug}.pebble.site`);
    setShareLabel("Copied!");
    setTimeout(() => setShareLabel("Share"), 1500);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav />
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <motion.div
          initial={{ scale: 0.4, opacity: 0, rotate: -8 }}
          animate={{ scale: 1, opacity: 1, rotate: 0 }}
          transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
          className="mb-10 text-primary relative"
        >
          <div className="pebble-ripple absolute -inset-12 flex items-center justify-center" />
          <Droplet className="w-12 h-12 fill-current relative z-10" strokeWidth={1.5} />
        </motion.div>

        <motion.div
          initial="hidden"
          animate="visible"
          variants={{
            hidden: {},
            visible: { transition: { staggerChildren: 0.1 } },
          }}
          className="max-w-2xl w-full text-center space-y-10"
        >
          <motion.h1
            variants={{
              hidden: { opacity: 0, y: 16 },
              visible: { opacity: 1, y: 0 },
            }}
            transition={{ duration: 0.5 }}
            className="font-display text-5xl md:text-6xl font-bold tracking-tight text-foreground"
          >
            Your website is live.
          </motion.h1>

          <motion.div
            variants={{
              hidden: { opacity: 0, y: 16 },
              visible: { opacity: 1, y: 0 },
            }}
            transition={{ duration: 0.5 }}
            className="bg-card border border-border rounded-2xl p-8 md:p-10 shadow-[var(--shadow-1)] space-y-8"
          >
            <div className="flex flex-col items-center">
              <div className="bg-accent border border-border rounded-lg px-6 py-3 mb-3">
                <span className="font-mono text-xl tracking-tight text-primary">{slug}.pebble.site</span>
              </div>
              <p className="text-muted-foreground text-xs font-bold uppercase tracking-widest">URL active</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t border-border">
              <motion.button
                onClick={handleShare}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.96 }}
                className="flex flex-col items-center gap-3 p-4 rounded-lg hover:bg-accent transition-colors group"
              >
                <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center group-hover:scale-105 transition-transform">
                  <Share2 className="w-5 h-5" />
                </div>
                <span className="text-sm font-semibold">{shareLabel}</span>
              </motion.button>
              <motion.a
                href={previewUrl}
                target="_blank"
                rel="noopener"
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.96 }}
                className="flex flex-col items-center gap-3 p-4 rounded-lg hover:bg-accent transition-colors group"
              >
                <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center group-hover:scale-105 transition-transform">
                  <Eye className="w-5 h-5" />
                </div>
                <span className="text-sm font-semibold">View as visitor</span>
              </motion.a>
              <motion.button
                onClick={() => router.push("/workspace")}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.96 }}
                className="flex flex-col items-center gap-3 p-4 rounded-lg hover:bg-accent transition-colors group"
              >
                <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center group-hover:scale-105 transition-transform">
                  <Edit3 className="w-5 h-5" />
                </div>
                <span className="text-sm font-semibold">Keep editing</span>
              </motion.button>
            </div>
          </motion.div>

          <motion.p
            variants={{
              hidden: { opacity: 0 },
              visible: { opacity: 1 },
            }}
            transition={{ duration: 0.6 }}
            className="text-muted-foreground"
          >
            Everything is editable later. You don&apos;t have to be done.
          </motion.p>
        </motion.div>
      </main>
    </div>
  );
}
