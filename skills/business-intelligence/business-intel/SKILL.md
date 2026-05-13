# business-intel

A business website intelligence skill for Pebble Engine. When called, read this entire document before writing any code or copy. This skill encodes how real people actually behave on business websites — not best-practice theory, but what moves someone from landing on a page to calling, booking, or buying.

---

## How to use this skill

When building a business website, answer these three questions first from the brief, then apply the appropriate sections below:

1. **What type of business is this?** — Use the business-type index to find the section.
2. **What does the site need to do?** — Booking, payment, lead capture, portfolio, or just presence.
3. **What is the primary visitor state?** — Are they in pain right now (emergency pest problem), planning ahead (scheduling a dental cleaning), or browsing (choosing a gym)? The answer changes everything about the page structure.

---

## Universal truths about business websites

These apply regardless of industry. Ignore them at the cost of conversions.

### Above the fold: three questions visitors ask in under 5 seconds
Every landing page must answer all three, in order, without scrolling:

1. **"Can you solve my specific problem?"** — Not vague ("we help businesses grow"). Specific ("Same-day plumbing repair in Suffolk County").
2. **"Can I trust you?"** — A real face, a specific credential, years in business, named reviews.
3. **"What do I do right now?"** — One clear action. Not three buttons. One.

If any of these is missing above the fold, expect 40–70% of visitors to leave immediately.

### Phone number placement
For service businesses (plumbing, pest control, HVAC, dental, legal, medical): **the phone number belongs in the top-right of the header, in the largest non-heading font on the page**. Not in the footer. Not buried in a contact form. In the header. On every page. This is not optional.

Mobile traffic for local service businesses is 65–80%. "Click to call" on mobile is the most valuable conversion mechanism available — more valuable than any form.

### Mobile-first is non-negotiable for service businesses
Build the mobile layout first. Every tap target must be at least 44×44px. Forms must be keyboard-friendly. The primary CTA must be reachable with one thumb, in the natural grip zone (bottom center of screen).

### Social proof placement
The testimonials that convert best are:
- Specific (name, outcome, before/after)
- Near the action they're validating ("book now" button with a review right above it)
- Short (under 50 words per quote)
- Real (no stock headshot = more credible than stock headshot)

Generic five-star widgets with no context convert poorly. One specific named quote beats ten anonymous stars.

### Pricing transparency
For service businesses: showing a price range dramatically increases lead quality. "Pest control starting at $89" filters out tire-kickers and builds trust. "Contact us for pricing" is a conversion killer for most service categories.

Exception: high-end consulting, custom work, and medical practices where pricing is genuinely variable. In those cases: "Free consultation" replaces the price.

### Response time expectations
Set them immediately and explicitly:
- Emergency services: "We answer 24/7" or "Same-day response"
- Appointment-based: "Respond within 1 business day" or "Book instantly online"
- E-commerce: "Ships in 2–3 business days"

Failing to set expectations increases anxiety and reduces conversions.

---

## Business type index

### Home Services (plumbing, HVAC, electrical, pest control, landscaping, cleaning)

**Visitor state:** Usually in pain or planning maintenance. High urgency.

**What the site must do:**
- Answer "do you service my area?" in the first sentence
- Show a phone number prominently — this is the primary CTA
- List services with brief descriptions (not marketing copy)
- Show licensing, insurance, and any certifications above the fold or immediately below

**Page structure that works:**
1. Header: logo + phone number (large) + service area
2. Hero: specific headline ("Pest-free since 1987. Bait station only — no foggers.") + primary CTA
3. Service area confirmation + response time
4. Services list (not cards — a scan-friendly list with prices if possible)
5. About the owner (photo, story, credential) — this one section does more conversion work than anything else on the page
6. Reviews (3 specific ones, not a grid of stars)
7. Contact / booking

**Booking integration recommendations:**
- Housecall Pro (purpose-built for home services, handles dispatch + payment)
- ServiceTitan (larger operations)
- Jobber (medium-sized)
- Square Appointments (small, simple)
- Simple phone + contact form (smallest operations — don't over-engineer)

**Anti-patterns:**
- Hero with drone footage stock video of suburbs
- "We are a family-owned business committed to excellence" as the headline
- Accordion FAQs above reviews
- Generic "contact us" form as the only CTA

---

### Restaurants and Food Service

**Visitor state:** Planning or impulse — deciding where to eat, checking hours, wanting the menu.

**What the site must do:**
- Show the menu (PDF is acceptable; mobile-friendly HTML is better)
- Show hours prominently
- Show address with map link
- Show reservation/order link if applicable

**What visitors need immediately:**
Hours and menu. Not your story, not your awards, not your Instagram. Hours and menu. Put them in the navigation or immediately visible on the homepage.

**Reservation/ordering integrations:**
- OpenTable (full-service restaurants)
- Resy (upscale)
- Yelp Waitlist (casual)
- Toast Online Ordering (restaurant POS, handles pickup/delivery)
- Square for Restaurants
- ChowNow (commission-free online ordering)

**Anti-patterns:**
- Autoplay background music
- Menu as an unzoomed image scan
- Splash page before the actual site
- Contact form as the only way to ask about hours

---

### Health and Wellness (dental, medical, chiropractic, physical therapy, mental health)

**Visitor state:** Anxious, evaluating trust. Decision is higher stakes than most. Speed of trust-building matters.

**What the site must do:**
- Answer "are you accepting new patients?" explicitly
- Show the provider's face and name — not a team page of stock photos
- Show what insurance is accepted OR clarify self-pay pricing immediately
- Booking must be online if at all possible — calling during business hours is a barrier

**Trust signals that work for healthcare:**
- Years in practice + credential specifics ("20 years" not "experienced")
- Before/after where applicable and appropriate
- Patient reviews with full names and specific outcomes
- Response time ("We'll confirm within 24 hours")
- HIPAA notice placement (footer, not a pop-up)

**Booking integrations:**
- Zocdoc (medical — patients already use it)
- Jane App (therapy, chiro, PT, wellness)
- SimplePractice (therapy specifically)
- Acuity Scheduling (general wellness)
- NexHealth (dental/medical with their own EMR)

**Payment:**
- Most practices collect at time of service — online payment collection is secondary
- If collecting deposits: Stripe is most compliant for healthcare adjacent
- HSA/FSA acceptance: note it explicitly if you take it

**Anti-patterns:**
- Generic stock image of white teeth / smiling doctor
- No insurance information until the contact form
- "Request an appointment" that requires 48–72 hour callback

---

### Beauty and Personal Care (salon, barbershop, spa, lash, nails, esthetics)

**Visitor state:** Evaluating aesthetic judgment. The site IS the portfolio.

**What the site must do:**
- Show actual work — real photos of real clients (with permission)
- Show the stylists/artists individually with their work, not just the brand
- Make booking friction as low as possible — every extra click loses a booking

**Booking integrations:**
- Booksy (barber and beauty — industry standard with its own marketplace)
- Vagaro (salon/spa, includes payroll + POS)
- Boulevard (upscale salon, appointment + checkout)
- GlossGenius (independent stylist, simple + clean)
- Square Appointments (simple, works well for solo operators)

**Payment:**
- Deposits on first appointments reduce no-shows significantly — build it into the booking flow
- Tipping built into the checkout (Square, Booksy, and Vagaro all handle this)

**Anti-patterns:**
- Gallery of someone else's work or obviously stock hair photos
- Booking link that opens a different website with different branding
- No individual stylist profiles

---

### Fitness and Wellness (gym, yoga, pilates, personal training, martial arts)

**Visitor state:** Aspirational but commitment-anxious. Lower barrier to the first visit = more members.

**What the site must do:**
- Show what the first visit looks like — remove the anxiety of walking in for the first time
- Offer a free trial, first class free, or free consultation as the primary CTA
- Show class schedule or training availability without requiring signup

**Booking/Scheduling integrations:**
- Mindbody (industry standard for studios — also has its own customer-facing app)
- Pike13 (mid-size studios)
- Zen Planner (martial arts, crossfit)
- Wodify (crossfit specifically)
- Acuity (personal trainers, small studios)

**Membership/payment:**
- Stripe (custom membership billing)
- Mindbody (handles billing natively)

**Anti-patterns:**
- Pricing page that doesn't show pricing
- Registration required to see the class schedule
- "Inquire about membership" as the only path

---

### Professional Services (legal, accounting, financial advising, consulting, real estate)

**Visitor state:** High-trust, high-stakes. Evaluating credibility and fit over time. Not an impulse purchase.

**What the site must do:**
- Establish credentials specifically (not "experienced attorney" — "20 years in employment law, primarily representing workers in wrongful termination cases")
- Show areas of practice / specialization with enough depth that the visitor self-qualifies
- Make the first contact low-commitment (free consultation, not "hire us")

**Trust signals:**
- Bar/license numbers and memberships (visible, not buried)
- Case results where ethically permissible
- Specific client profiles ("We work primarily with small business owners...")
- Press coverage or publications (if applicable)

**Lead capture:**
- Free consultation form — name, email, brief description of situation
- Calendly or Acuity for direct consultation booking
- Phone is still important for urgent matters (legal especially)

**Anti-patterns:**
- Generic "results-oriented" or "client-focused" language
- Case results displayed without context
- Contact form that requires every field including phone before they're qualified

---

### Retail and E-commerce

**Visitor state:** Browsing to buying — wide range. Trust is built through product detail, policy transparency, and checkout friction.

**What the site must do:**
- Product pages: real photography (multiple angles), specific descriptions, sizing/specs, shipping time, and return policy — all on the same page, no clicking around
- Cart and checkout must be as short as possible
- Show real reviews near the buy button

**Payment integrations:**
- Shopify (self-contained e-commerce — simplest for non-technical owners)
- Stripe (custom checkout — requires developer)
- Square Online (for physical retail adding online)
- WooCommerce (WordPress-based, more control)

**Anti-patterns:**
- Shipping information only in the footer
- Cart that empties on browser close
- Checkout that requires account creation before purchase

---

## Integrations quick reference

| Need | First recommendation | Notes |
|---|---|---|
| General scheduling | Calendly | Free tier, embeds anywhere, widest compatibility |
| Salon/beauty booking | Booksy | Marketplace + booking, industry standard |
| Medical/therapy | Jane App or SimplePractice | HIPAA compliant |
| Restaurant reservations | OpenTable | Customer familiarity, built-in discovery |
| Fitness studios | Mindbody | Industry standard, has its own app ecosystem |
| Online ordering | Toast or ChowNow | Toast for existing POS, ChowNow commission-free |
| Home service dispatch | Jobber or Housecall Pro | Both handle estimating + dispatch + payment |
| Payment processing | Stripe | Most flexible; handles subscriptions, deposits, custom flows |
| Payment (simple) | Square | Better for in-person-first businesses adding online |
| Marketing + CRM | GHL (GoHighLevel) | Full pipeline + booking; overkill for simple sites but powerful for agencies |
| Membership billing | Stripe or Mindbody | Stripe for custom; Mindbody for fitness with built-in scheduling |

---

## Conversion patterns by CTA type

### "Call us"
Works best for: Emergency services, legal, medical, high-trust professional services.
Make it work: Large phone number in header, click-to-call on mobile, hours next to the number.

### "Book online"
Works best for: Beauty, fitness, dental/medical, restaurants, home services with online scheduling.
Make it work: Button visible above fold, no account required for first booking, immediate confirmation.

### "Get a free quote"
Works best for: Home services, landscaping, remodeling, anything with variable pricing.
Make it work: 3-field max on the quote form (name, phone, brief description). Every additional field costs 10–15% completion rate.

### "Shop now" / "Buy"
Works best for: Retail, food products, anything with fixed-price inventory.
Make it work: Price visible before click, clear return policy near button, trust badges near checkout.

### "Start free trial" / "First class free"
Works best for: Fitness, SaaS, subscription services.
Make it work: No credit card required for trial, immediate access after signup, follow-up sequence automated.

---

## What to never do (regardless of business type)

1. **Auto-playing audio or video** — Instant close.
2. **Pop-up on arrival** — Acceptable only for age verification. Otherwise: instant close.
3. **Chat widget that opens immediately** — Place it but don't auto-open it.
4. **Infinite scroll on a business homepage** — It's not a social feed. Give it structure.
5. **Generic stock photography of the business type** — A stock dental office photo is worse than no photo. Use real photography or nothing.
6. **Hiding the phone number** — 40% of business website visitors never submit a form. They'll call if the number is visible. They won't dig for it.
7. **Making visitors create an account to get a quote** — Every unnecessary barrier cuts conversion rate.
8. **"Submit" as a button label** — Tell them what happens: "Get my free quote," "Book my appointment," "Start my free trial."
