# Business Intelligence Skill — Industry Profiles & Recommendations

## Purpose

This skill provides deep, researched knowledge about business website patterns so the engine builds industry-appropriate sites automatically. When a business type is identified, the engine applies the correct aesthetic, tone, page structure, CTA hierarchy, and recommended tools WITHOUT needing to ask the user.

This skill is also the source of truth for the UI recommendation system. Every recommendation shown in the quiz comes from this file.

---

## How This Works

When a brief arrives with a business type:

1. **Industry detection** — Match business type to category below
2. **Apply ALL recommendations** — Visual aesthetic, tone, motion, structure, CTAs, tools
3. **Override user choices when necessary** — If user picks dark mode for a plumber, this skill overrides it
4. **Explain the override** — "For local service businesses, light backgrounds convert 3x better"

---

## Complete Industry Profiles

Each profile includes:
- Customer psychology
- Target audience default
- Primary conversion goal
- Brand positioning
- Brand tone
- **Visual aesthetic** (NEW — light/dark, color direction)
- **Motion intensity** (NEW — how much animation)
- Page structure
- Copy rules
- CTA hierarchy
- Booking/payment tools
- Trust signals

---

### 1. Home Services (plumbing, HVAC, electrical, pest control, cleaning, landscaping, roofing, painting, locksmith, handyman, garage door, appliance repair)

**Customer psychology:** Urgency and trust. Usually searching because something is broken or they're anxious. Want proof you're legitimate and a way to contact you in 30 seconds.

**Target audience:** Homeowners (residential property owners in the service area)

**Primary conversion goal:** Call Now (Emergency Dispatch)

**Brand positioning:** Professional & Established (not luxury, not budget — trustworthy middle ground)

**Brand tone:** Friendly & Approachable (warm, not formal or technical)

**Visual aesthetic:** Clean & Modern
- **Background:** Light (white #FFFFFF or soft gray #F9FAFB)
- **Accent color:** Blue (trust), Green (growth/reliability), or Orange (urgency)
- **Explanation:** Light backgrounds convert 3x better for local services. Dark backgrounds reduce trust and make emergency CTAs less visible. Homeowners need to feel safe inviting you into their home — warm, clean, approachable design signals that.

**Motion intensity:** Smooth (subtle GSAP)
- Gentle fade-ins and scroll reveals
- NO cinematic parallax or pinned sections (feels gimmicky for emergency services)
- NO 3D or WebGL (wasteful for mobile-heavy traffic)
- **Explanation:** 60-70% of local service searches happen on mobile during an emergency. Fast load times and simple animations keep the focus on the phone number.

**Page structure:**
- Hero: Service area + phone number above fold. Big. Not hidden.
- Second section: The specific problem you solve + proof (photos, numbers, years)
- Services list: Specific, not vague ("German cockroach treatment" not "pest solutions")
- Service area: Map or clear city/region list
- Social proof: Real reviews, star rating count, Google/Yelp badge
- Final CTA: Second call prompt ("Still here? Call us: [number]")
- Footer: License number, insurance badge, BBB if applicable

**Copy rules:**
- First sentence names the problem, not the company
- Use the owner's name or face — people hire people, not logos
- "Family owned" and years in business are trust signals worth using
- Emergency availability is a conversion multiplier
- NEVER: "solutions," "innovative," "leading provider," "world-class service"

**CTA hierarchy:** Call now > Book online > Get a free estimate

**Booking:** Housecall Pro, Jobber, ServiceTitan, Square Appointments, or phone-primary

**Payment:** Stripe, Square, or collect on-site (offer both card and cash)

**Trust signals:** License number, insurance, years in business, owner's face, real reviews

---

### 2. Luxury & Premium (high-end real estate, yachts/boats, jewelry, luxury hospitality, high-end automotive, private aviation, luxury goods)

**Customer psychology:** Exclusivity and aspiration. They're making a high-value purchase or experience decision. They expect visual sophistication that matches the price point. Busy layouts or bright colors signal "cheap."

**Target audience:** High-net-worth individuals, luxury consumers, investors

**Primary conversion goal:** Request Private Consultation or Browse Collection

**Brand positioning:** Premium & Luxury (exclusive, sophisticated, high-end)

**Brand tone:** Professional & Refined (formal but not cold — sophisticated warmth)

**Visual aesthetic:** Premium & Editorial
- **Background:** Dark (deep charcoal #0A0A0A or navy #0F172A) OR ultra-clean white with massive whitespace
- **Accent color:** Gold (#D4AF37), Rose Gold, or deep jewel tones (emerald, sapphire)
- **Typography:** Editorial serif (Tiempos, Canela, GT Alpina) or refined sans (Söhne, ABC Monument)
- **Explanation:** Luxury buyers expect visual weight. Dark backgrounds create sophistication and let high-resolution product imagery dominate. Massive whitespace signals restraint and exclusivity. Bright colors and busy layouts reduce perceived value.

**Motion intensity:** Cinematic (parallax, pinned sections)
- Large imagery with smooth parallax scrolling
- Pinned scroll sections for featured pieces
- Subtle hover states on product cards
- **Explanation:** Luxury purchases are emotional. Cinematic scrolling creates the immersive, editorial experience that matches the price point. Product showcase needs to feel like flipping through Architectural Digest, not browsing a catalog.

**Page structure:**
- Hero: One stunning full-bleed image or video. Minimal text.
- Featured collection or property: Large imagery, minimal descriptions
- About / Heritage: Brand story, craftsmanship, exclusivity
- Private inquiry: Low-friction contact form (no public pricing)
- Social proof: Press mentions (Forbes, Robb Report, etc.) over star ratings

**Copy rules:**
- Less is more — restraint signals confidence
- Specific materials, provenance, craftsmanship over generic luxury claims
- "Hand-forged in Florence with 18k Fairmined gold" > "Luxury craftsmanship"
- Never use "affordable," "deals," or "budget-friendly"

**CTA hierarchy:** Request private consultation > Schedule viewing > Inquire

**Booking:** Calendly (custom-branded), Acuity, or concierge phone line

**Payment:** Wire transfer, private invoicing, or Stripe (hidden from public)

**Trust signals:** Press features, awards, heritage (years established), exclusivity cues

---

### 3. Professional Services (lawyer, accountant, financial advisor, therapist, consultant, architect, engineer, business coach)

**Customer psychology:** Trust and credibility. High-stakes decision about who to trust with something important. Reading carefully. Want credentials, experience, and proof you've done this before.

**Target audience:** Individuals or businesses needing specialized expertise (B2B or B2C depending on practice)

**Primary conversion goal:** Schedule Consultation

**Brand positioning:** Professional & Established (credible, experienced, trustworthy)

**Brand tone:** Professional & Formal (but not cold — authoritative warmth)

**Visual aesthetic:** Technical & Professional
- **Background:** Light (white or off-white) or neutral gray
- **Accent color:** Navy blue (trust), deep green (stability), or burgundy (authority)
- **Typography:** Professional serif (Tiempos, Fraunces) or clean sans (Inter for body OK here)
- **Explanation:** Professional services need to signal credibility and seriousness. Light, structured layouts with clear hierarchy build trust. Dark backgrounds can feel theatrical or gimmicky for fields like law or accounting.

**Motion intensity:** Minimal (fade-ins only)
- Simple fade-ins on scroll
- NO parallax, pinned sections, or hover effects
- Focus on readability and clarity
- **Explanation:** Prospects are reading carefully. Distracting animations reduce credibility. They want to focus on your credentials and case results, not watch elements float across the screen.

**Page structure:**
- Hero: Specific practice area + one-line outcome statement
- Who it's for: Narrow down client type early
- How it works: 3-step process (consultation → work → outcome)
- Credentials: Bar, CPA, certifications, years practicing, notable work
- Social proof: Written testimonials with full names (more trust than star ratings)
- FAQ: Top 5 questions every prospect asks
- CTA: Schedule a free consultation

**Copy rules:**
- Specificity builds more trust than authority claims
- "Helped 300 small businesses in Nassau County" > "Area's leading firm"
- Never invent testimonials. Real or omit.
- Write to prospect's fear, not aspiration. "Facing an audit?" not "Achieve success"

**CTA hierarchy:** Schedule consultation > Free 15-min call > Send message

**Booking:** Calendly, Acuity Scheduling, Jane App (healthcare), Cal.com

**Payment:** Invoiced after engagement; Stripe if retainer/online payment needed

**Trust signals:** Credentials, years practicing, case results, client testimonials, memberships

---

### 4. Health & Wellness (dentist, chiropractor, physical therapist, personal trainer, yoga studio, med spa, massage, acupuncture, therapy, nutrition)

**Customer psychology:** Comfort and trust. Putting their body or health in your hands. Warmth matters more than in most categories. Also want frictionless booking — they've decided to go; make it easy.

**Target audience:** Local individuals seeking health improvement or healing

**Primary conversion goal:** Book Appointment

**Brand positioning:** Accessible & Community (approachable, welcoming, not clinical or luxury unless med spa)

**Brand tone:** Friendly & Warm (calm, approachable, reassuring)

**Visual aesthetic:** Minimal & Refined
- **Background:** Light (soft white, warm cream, or pale sage)
- **Accent color:** Soft green (healing), warm terracotta (earthy), or calm blue (serenity)
- **Typography:** Warm organic serif (Fraunces, Lora) for headings; Inter or DM Sans for body only
- **Explanation:** Health and wellness need to feel calming and safe. Soft, warm backgrounds with generous whitespace create the peaceful, uncluttered aesthetic patients expect. Dark backgrounds feel heavy; bright colors feel clinical.

**Motion intensity:** Minimal to Smooth (subtle animations)
- Gentle fade-ins
- Soft image reveals
- NO aggressive parallax (creates visual tension, opposite of calming)
- **Explanation:** Wellness spaces should reduce anxiety, not create it. Calm, minimal motion reinforces the healing environment.

**Page structure:**
- Hero: Transformation you provide + warm photo of space or provider
- Services: Card layout with clear prices (when appropriate)
- Meet the team: Photos and short bios (patients pick based on personality)
- Location + hours: Always visible (missing hours kills conversion)
- Booking widget: Inline, not new tab (friction kills bookings)
- Insurance / payment: If you take insurance, say so prominently

**Copy rules:**
- Use "you" and "your" — warmth over authority
- First visit anxiety is real — describe what to expect
- Patient/client pronouns over "individuals"

**CTA hierarchy:** Book appointment > New patient form > Call the office

**Booking:** Jane App (healthcare), Mindbody (fitness/wellness), Acuity, Booksy (beauty)

**Payment:** Stripe, Square, or practice management software (SimplePractice, Jane, Mindbody)

**Trust signals:** Provider photos/bios, certifications, patient testimonials, years in practice

---

### 5. Food & Hospitality (restaurant, bakery, café, catering, food truck, bar, brewery, winery)

**Customer psychology:** Appetite and atmosphere. Want to know if they'll like the food and if the place feels right for the occasion. Photos carry more weight here than almost any category.

**Target audience:** Local diners, event planners (for catering)

**Primary conversion goal:** Order Online or Reserve Table

**Brand positioning:** Varies widely (casual to upscale based on concept)

**Brand tone:** Friendly & Inviting (warm, not formal unless fine dining)

**Visual aesthetic:** Clean & Modern OR Bold & Energetic (depends on concept)
- **Background:** Light (for casual/cafe) or warm/dark (for bar/upscale)
- **Accent color:** Warm earth tones (terracotta, mustard, olive) or vibrant food colors
- **Typography:** Friendly serif (Fraunces, Lora) or bold display (for brands with personality)
- **Explanation:** Food photography is the hero. Background should support the imagery without competing. Warm, inviting colors stimulate appetite. Dark backgrounds work for bars/upscale restaurants where ambiance matters.

**Motion intensity:** Smooth to Interactive (depending on brand personality)
- Food imagery with gentle reveals
- Hover effects on menu items OK
- Casual spots: simple. Upscale: cinematic OK.

**Page structure:**
- Hero: One full-bleed food or atmosphere photo (NO stock)
- Hours and location: Second section. Always. (Top search)
- Menu: Accessible, text-based (NOT PDF — Google reads it)
- About / Story: Brief. One paragraph.
- Order / Reserve: Inline widget if applicable
- Contact / Find us: Map embed, parking notes

**Copy rules:**
- Describe food with texture, temperature, origin — not "delicious"
- "Baked fresh at 5am with local flour" > "artisan fresh-baked goods"
- Allergy info near menu. Prominent.

**CTA hierarchy:** Order online > Reserve table > View menu

**Booking/ordering:** OpenTable, Resy (restaurants), Toast, Square for Restaurants, ChowNow

**Payment:** Integrated with POS (Square, Toast, Lightspeed)

**Trust signals:** Real food photos, chef/owner bio, press mentions, reviews

---

### 6. Tech & SaaS (software, apps, tech companies, B2B SaaS, API products, developer tools)

**Customer psychology:** Efficiency and capability. Want to know if this solves their problem better/faster than alternatives. Reading for features, integrations, and proof it works at scale.

**Target audience:** Businesses, developers, technical decision-makers

**Primary conversion goal:** Sign Up or Request Demo

**Brand positioning:** Technical & Innovative (modern, capable, forward-thinking)

**Brand tone:** Professional & Technical (clear, precise, confident)

**Visual aesthetic:** Technical & Professional OR Premium & Editorial (for high-end B2B SaaS)
- **Background:** Can use dark (#0A0A0A) for technical/developer tools, or light for B2B SaaS
- **Accent color:** Bright accent (electric blue, green, purple) or monochrome
- **Typography:** Distinctive geometric sans for headings — Syne, Manrope (heavy), or Space Mono; Söhne or ABC Monument if available; Inter is acceptable for body and data only, never for headings
- **Explanation:** Tech companies can use dark mode successfully because their audience expects it. Dark backgrounds signal sophistication and technical capability. BUT: keep text readable (high contrast required).

**Motion intensity:** Smooth to Cinematic (for high-end SaaS)
- Product screenshots with scroll reveals
- Interactive product demos
- Subtle micro-interactions
- **Explanation:** SaaS sites need to showcase the product. Smooth animations keep focus on features while adding polish. Developer tools can be minimal; enterprise SaaS can be more cinematic.

**Page structure:**
- Hero: What it does + primary benefit in one line
- How it works: Visual product tour or key features
- Integration logos: If API/platform, show what it connects to
- Social proof: Company logos (for B2B) or user count
- Pricing: Transparent pricing builds trust (unless enterprise-only)
- CTA: Start free trial or Request demo

**Copy rules:**
- Specific outcomes over vague benefits
- "Deploy in 5 minutes" > "Fast deployment"
- Show code examples for developer tools
- Use customer data: "Trusted by 10,000+ companies"

**CTA hierarchy:** Start free trial > Request demo > See pricing

**Booking:** Calendly (for demos), self-serve signup preferred

**Payment:** Stripe Billing (subscriptions), Paddle, or enterprise invoicing

**Trust signals:** Customer logos, user count, uptime metrics, security certifications

---

### 7. Creative & Agency (design agency, marketing firm, photography, video production, creative studio, branding agency)

**Customer psychology:** Taste and capability. Want to see your work and know you "get it." Portfolio is everything. They're judging your aesthetic immediately.

**Target audience:** Businesses or individuals hiring creative services

**Primary conversion goal:** Browse Portfolio or Request Consultation

**Brand positioning:** Creative & Distinctive (bold, opinionated, not generic)

**Brand tone:** Creative & Confident (personality-driven, not corporate)

**Visual aesthetic:** Bold & Energetic OR Minimal & Refined (depends on agency positioning)
- **Background:** Can go dark OR ultra-minimal white with huge whitespace
- **Accent color:** Bold, unexpected (your brand personality)
- **Typography:** Distinctive display font (NOT Inter/Poppins — this is your portfolio too)
- **Explanation:** Creative agencies are selling taste. Your website IS the portfolio. Generic design = generic work in the prospect's mind. Dark or minimal both work — boring doesn't.

**Motion intensity:** Cinematic to Interactive (showcase your capabilities)
- Portfolio pieces with impressive scroll effects
- Case study storytelling with pinned sections
- Hover states, transitions, polish
- **Explanation:** Your website proves you can deliver. Cinematic motion and interaction design showcase your technical and creative abilities.

**Page structure:**
- Hero: Bold statement or featured work
- Portfolio: Immediate. Grid or featured projects.
- Case studies: 2-3 deep dives with results
- Services: Brief. They came for the work, not a services list.
- About: Team or founder story. Keep it human.
- CTA: Let's work together / Start a project

**Copy rules:**
- Show, don't tell. Portfolio speaks louder than claims.
- Case studies need results: "Increased conversion 40%" not "Beautiful design"
- Confident, not arrogant. "We build brands that matter" not "We're the best"

**CTA hierarchy:** View work > Start a project > Schedule call

**Booking:** Calendly, Acuity, or custom inquiry form

**Payment:** Stripe (deposits/retainers), invoicing (final payment)

**Trust signals:** Portfolio, case study results, client logos, awards/press

---

### 8. E-commerce & Retail (online store, boutique, specialty goods, handmade products, subscription boxes, DTC brands)

**Customer psychology:** Discovery and desire. Browsing, not searching for a specific solution. Make them want to stay. Make finding and buying effortless.

**Target audience:** Online shoppers (B2C)

**Primary conversion goal:** Make Purchase

**Brand positioning:** Varies (boutique/premium to accessible/value depending on products)

**Brand tone:** Friendly & Engaging (warm, helpful, not salesy)

**Visual aesthetic:** Clean & Modern (most e-commerce) OR Bold & Energetic (for brands with strong personality)
- **Background:** Light (white or off-white for product focus)
- **Accent color:** Brand color (whatever differentiates you)
- **Typography:** Clean, readable (product names and prices need clarity)
- **Explanation:** Product photography is the hero. Clean backgrounds let products shine. Dark backgrounds work for luxury goods only.

**Motion intensity:** Smooth to Interactive
- Product image galleries with smooth transitions
- Hover effects on product cards (quick view, add to cart)
- Smooth cart animations
- **Explanation:** E-commerce needs polish without distraction. Smooth micro-interactions feel premium and guide the buying flow.

**Page structure:**
- Hero: Featured product or collection with "shop now"
- Featured / New arrivals: 4-6 products (not whole catalog)
- About: One paragraph — who's behind this, where products come from
- Social proof: Real customer photos beat studio shots
- Email capture: High priority for online-only brands

**Copy rules:**
- Product descriptions with specifics (materials, dimensions, care)
- Real customer reviews with photos
- Clear shipping and return policies (above the fold on product pages)

**CTA hierarchy:** Shop now > See new arrivals > Learn about us

**E-commerce platform:** Shopify (easiest), WooCommerce (WordPress), Squarespace Commerce

**Payment:** Handled by platform (Shopify Payments, Stripe, PayPal)

**Trust signals:** Customer reviews, return policy, secure checkout badges

---

### 9. Real Estate (general real estate, not ultra-luxury)

**Customer psychology:** Comparison and research. Looking at multiple properties. Want filters, clear photos, and neighborhood info.

**Target audience:** Home buyers, renters, sellers (depending on focus)

**Primary conversion goal:** Browse Listings or Schedule Tour

**Brand positioning:** Professional & Trustworthy (knowledgeable, reliable)

**Brand tone:** Professional & Friendly (approachable expert)

**Visual aesthetic:** Clean & Modern
- **Background:** Light (white or soft gray)
- **Accent color:** Blue (trust) or earth tones
- **Typography:** Professional serif (Fraunces, Playfair Display) or authority sans (Oswald, Syne) for headings; Inter is acceptable for listing data and body text only
- **Explanation:** Real estate is about the properties, not the agent's website. Clean, searchable layouts with excellent property photos. NOT dark luxury aesthetics unless serving ultra-high-end market.

**Motion intensity:** Minimal to Smooth
- Property image galleries
- Map integrations
- Search filters
- NO heavy parallax (slows down listing browsing)

**Page structure:**
- Hero: Featured properties or search bar
- Property listings: Grid with filters (price, beds, location)
- About the agent/team: Credentials, local expertise
- Neighborhood guides: For buyer education
- CTA: Schedule a tour or List your property

**Copy rules:**
- Lead with local expertise: "Suffolk County specialist since 2010"
- Specific: "Sold 200+ homes in Bayshore" > "Experienced agent"

**CTA hierarchy:** Browse listings > Schedule tour > Contact agent

**Booking:** Calendly, Acuity (for tour scheduling)

**Payment:** N/A (commission-based)

**Trust signals:** Sales numbers, years active, testimonials, certifications

---

## Booking System Decision Tree

Use this when site functions include booking:

**Appointment-based (1:1, in-person):**
- Simple/free: Calendly free tier
- Professional: Acuity Scheduling ($16/mo)
- Healthcare: Jane App (HIPAA-compliant)
- Beauty/wellness: Booksy
- Home service: Housecall Pro, Jobber

**Group bookings / classes:**
- Fitness/yoga: Mindbody
- Workshops/events: Eventbrite, Acuity with groups

**Restaurant reservations:**
- OpenTable, Resy

**E-commerce:**
- Shopify, WooCommerce, Squarespace Commerce

---

## Conversion Principles (Always Apply)

### Above the fold
Every visitor should see without scrolling:
1. What you do (specific)
2. Who you serve (area or audience)
3. How to contact you or take action

### The phone number rule
For businesses where people call: phone number in header, clickable on mobile (`tel:` link), repeated at page bottom.

### Social proof placement
Put social proof near primary CTA. Moment of action = moment they need reassurance.

### Load time and mobile
Local services: usually mobile + moment of need. Under 2 seconds. No autoplay video, compress images.

### Forms: fewer fields convert better
3 fields (name, email/phone, message) > 6 fields.

---

## What Kills Websites (By Category)

**Local services:**
1. No phone number above fold
2. No service area listed
3. Not mobile-optimized
4. Slow load time

**Professional services:**
1. Vague headline
2. No credentials visible
3. No clear CTA

**E-commerce:**
1. Hidden shipping costs
2. Complicated checkout
3. No product reviews

**Luxury:**
1. Busy layout (signals cheap)
2. Bright colors (reduces perceived value)
3. No large imagery

**Tech/SaaS:**
1. No clear value proposition
2. Hidden pricing
3. No product screenshots

---

This skill is the complete source of truth for all industry recommendations. The UI reads this data and shows it to users during the quiz.
