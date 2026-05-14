# Pebble — Marketing Site

The public landing page at **getpebble.net** (eventually). Next.js 14,
Tailwind v3, Resend for the waitlist form.

Brand follows `../BRAND_BOOK.md`. Project plan in `../PROJECT_PLAN.md`
(Chapter 5).

---

## Local dev

```powershell
cd C:\Users\marci\pebble-engine\pebble-marketing

# One-time setup
npm install

# Copy + fill .env.local
cp .env.example .env.local
notepad .env.local
# (Drop in your Resend API key + your email)

# Run dev server
npm run dev
# Opens at http://localhost:3000
```

---

## Deploy to getpebble.net via Vercel

You already have:

- Vercel account on Hobby tier (Pebble Gmail)
- GitHub repo at github.com/pebble-engine/pebble-engine
- Domain getpebble.net (registered with your registrar)

### One-time setup

```
1.  Push the latest commits to GitHub (auto-handled — main branch
    is what Vercel watches).

2.  Sign in to Vercel with your Pebble Gmail.

3.  Click "Add New..." → "Project".

4.  Connect your GitHub account (first time only). Pick:
       pebble-engine/pebble-engine

5.  Vercel asks "Root Directory":
       Change from "./" to "pebble-marketing"
       (because the marketing site lives in a subfolder of the repo)

6.  Framework Preset: Vercel auto-detects "Next.js" — leave it.

7.  Environment Variables — Click "Add" for each:
       RESEND_API_KEY       =  (your Resend key)
       WAITLIST_TO_EMAIL    =  (your Pebble Gmail address)
       WAITLIST_FROM_EMAIL  =  onboarding@resend.dev  (for now)
       WAITLIST_AUDIENCE_ID =  (optional, leave blank for now)

8.  Click "Deploy". Vercel builds + deploys in ~2 min.

9.  Visit the temporary URL Vercel gives you (e.g.
    pebble-engine.vercel.app). Verify the page loads.
```

### Connect getpebble.net

```
1.  In Vercel project dashboard → Settings → Domains.

2.  Click "Add" and type: getpebble.net

3.  Vercel shows you DNS records to add at your registrar.
    There are two ways:

       (a) Easiest — transfer DNS to Vercel.
           Vercel manages the nameservers; you change them
           at your registrar's site (one-time).

       (b) Or — add A + CNAME records manually at your registrar.
           Vercel shows you the exact values.

4.  Wait ~10 min for DNS to propagate.

5.  Vercel automatically provisions an SSL cert (free, automatic).

6.  Visit getpebble.net — it's your site.
```

### Verify the waitlist form works

```
1.  Go to getpebble.net
2.  Enter an email address
3.  Click "Join the waitlist"
4.  Within ~30 seconds:
       → That email gets added to your Resend Audience
       → You get an email notification at WAITLIST_TO_EMAIL
5.  Browser shows "✓ You're on the list."
```

If nothing happens, check:

- Vercel project → "Logs" tab for runtime errors
- Resend dashboard → "Logs" to see if the API call hit Resend
- `.env.local` matches what's in Vercel's environment variables

---

## What's included

```
app/
  layout.tsx          Inter + Fraunces + Plex Mono fonts, brand metadata
  page.tsx            Composes all sections in order
  globals.css         Brand tokens, reduced-motion handling
  actions/
    waitlist.ts       Resend Server Action for the form

components/
  ui/
    AnimatedHeading.tsx   Per-character entrance, a11y-safe
    FadeIn.tsx            Opacity wrapper, reduced-motion aware
  layout/
    Navbar.tsx            Light-themed nav with wordmark
  sections/
    Hero.tsx              Main waitlist hero
    Problem.tsx           "You've been told you should have a website..."
    Promise.tsx           Three things make Pebble different
    HowItWorks.tsx        3-step explanation
    Pricing.tsx           Free / $29 / $59 + $99 setup call
    Footer.tsx            Wordmark + nav + copyright
  forms/
    WaitlistForm.tsx      Resend-wired email capture

lib/
  email.ts            Resend client wrapper (server-only)
```

---

## What's NOT here yet (future commits)

- About / story page
- Privacy + Terms of Service (Marc + a lawyer)
- Blog / changelog (when there's something to say)
- Site preview gallery showing actual generated Pebble sites
- Social Open Graph image (currently using browser default)
- Analytics (Plausible or Google Analytics)
