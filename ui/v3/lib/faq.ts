// FAQ shared between /landing and /help. Single source of truth for the
// public-facing questions; /help can extend with logged-in-user topics.

export type FaqItem = { q: string; a: string };

export const PUBLIC_FAQ: FaqItem[] = [
  {
    q: "How is this different from a template builder?",
    a: "Template builders pick from a fixed gallery — you get one of N designs everyone else can also pick. Pebble synthesizes a fresh design DNA per build: fonts, palette, layout posture, signature interactions. Two builds for the same business look like two different studios made them. That's the point.",
  },
  {
    q: "Can I bring my existing site over?",
    a: "Yes — paste the URL on /migrate. Pebble extracts your business name, industry, contact details, color hints, and a short text sample. You confirm what's right, fix what's wrong, then continue into the build. Nothing is uploaded to a third party.",
  },
  {
    q: "Will my site work on phones?",
    a: "Yes. Every build targets mobile-first with 16px-minimum input fonts, 100dvh-safe heights for mobile browsers, and tested across phone breakpoints. Mobile correctness is one of the 33 FOUNDATION eval checks every site has to pass.",
  },
  {
    q: "Do you sell my data or run trackers?",
    a: "No. Pebble ships sites with zero third-party trackers by default — no Google Analytics, no Meta Pixel, no Hotjar, no Mixpanel. The eval suite fails any build that embeds them. If you want analytics later, you'll add it explicitly.",
  },
  {
    q: "What if I don't like what Pebble built?",
    a: "Try a different DNA — regenerate from the same brief and you'll get a different site. Or click into the visual editor and tweak directly. Every change is undoable. We're also planning a refund window once billing launches.",
  },
];

// /help adds these — they assume the user is signed in and has built at
// least one site. The wording stays universal-design: never references
// "for beginners" or skill level.
export const ACCOUNT_FAQ: FaqItem[] = [
  {
    q: "How do I publish my site?",
    a: "Open your project, click Publish in the top right, then Publish now. If Cloudflare keys are configured (Account ID + API token in .env), Pebble pushes the site live to a free URL on Cloudflare Pages. Otherwise you get a downloadable ZIP you can drop into any host like Vercel or Netlify.",
  },
  {
    q: "Can I use my own domain?",
    a: "Yes. After publishing, expand the Connect a custom domain panel on the publish page, enter your domain (like yourbiz.com), and Pebble shows the exact CNAME record to add at your DNS provider. Once DNS propagates we mark it Live automatically.",
  },
  {
    q: "I forgot my password.",
    a: "Click 'Forgot your password?' under the sign-in button, type the email you used, and we send a one-time reset link that's good for an hour. Set a new password and you're back in — every other signed-in device gets signed out automatically for safety.",
  },
  {
    q: "Where do I see what changed on my site?",
    a: "Open any project workspace, click the History icon in the top-right. Every refinement, visual edit, and rollback creates a snapshot — click Restore on any row to roll back to that version. The dashboard also shows the most recent activity across all your projects.",
  },
  {
    q: "Are my style tweaks free or do they cost credits?",
    a: "Style tweaks are free — clicking an element on the preview to change its text, color, or font size costs nothing. So do the 'Simpler' and 'Change colors' refinement chips. The 'Friendlier' / 'Professional' / 'Add booking' chips use the LLM and are billable (we mark them with an amber dot vs. the green free dot).",
  },
  {
    q: "Can I delete my account?",
    a: "Not via the UI yet — email us. (We're shipping the dashboard self-delete shortly.) Until then, every project's files live at output/<slug>/ on the engine host; remove the directory to drop a project.",
  },
];

export const FAQ_BY_SECTION: { title: string; items: FaqItem[] }[] = [
  { title: "First questions", items: PUBLIC_FAQ },
  { title: "Once you've signed up", items: ACCOUNT_FAQ },
];
