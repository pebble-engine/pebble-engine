"""Block library — the registry of drop-in sections + their renderers.

Adding a new block:

1. Write a ``_render_<id>`` function that returns the JSX file content
   for a single ``components/sections/<ComponentName>.tsx`` file.
2. Add a :class:`BlockSpec` entry to :data:`BLOCK_REGISTRY`.
3. Cover it in ``tests/test_blocks.py``.

All renderers use ``__TOKEN__`` placeholders (replaced via :func:`_apply`)
to keep JSX-brace syntax readable. Don't switch to f-strings or
``.format()`` — JSX has many literal ``{...}`` patterns that would force
brace-doubling and obscure the template.
"""
from __future__ import annotations

from pebble.blocks.base import BlockSpec, ThemeTokens


# ---- Kicker rendering (DNA-aware eyebrows) -------------------------------

def _kicker(tokens: ThemeTokens, number: str, title: str) -> str:
    """Return the JSX for a section eyebrow in the DNA's voice.

    `number` is a section ordinal like '02'; `title` is the section name.
    Each style maps onto a corresponding DNA. When in doubt the
    'mono-uppercase' fallback works for every DNA.
    """
    style = tokens.kicker_label_style
    title_upper = title.upper()
    if style == "section-numeral":
        return f"§ {number} · {title_upper}"
    if style == "terminal":
        return f"&gt; SECTION_{number}: {title_upper}"
    if style == "blueprint":
        return f"{number}.00 — {title_upper}"
    if style == "numbered":
        return f"{number}."
    if style == "roman":
        # Crude — only ever used for 'II' / 'III' which is plenty.
        return {"01": "I.", "02": "II.", "03": "III."}.get(number, f"{number}.")
    if style == "stencil":
        return f"REF-{number} / {title_upper}"
    if style == "small-caps":
        return f"ISSUE {number} — {title_upper}"
    if style == "soft-eyebrow":
        return f"◐ {title_upper}"
    if style == "marquee":
        return f"{title_upper} · {title_upper} · {title_upper}"
    return f"FIG. {number} — {title_upper}"


def _apply(tpl: str, tokens: ThemeTokens, **extras: str) -> str:
    """Replace ``__TOKEN__`` placeholders in ``tpl``. Extras override
    defaults. Missing tokens are left intact (so the renderer fails
    visibly in tests instead of silently)."""
    repl: dict[str, str] = {
        "__BG__":            tokens.bg_hex,
        "__INK__":           tokens.ink_hex,
        "__ACCENT__":        tokens.accent_hex,
        "__SECONDARY__":     tokens.secondary_hex or tokens.accent_hex,
        "__DISPLAY_STACK__": tokens.display_stack(),
        "__BODY_STACK__":    tokens.body_stack(),
        "__MONO_STACK__":    tokens.mono_stack(),
        "__RADIUS__":        tokens.radius_class,
        "__DARK_BORDER__":   "rgba(255,255,255,0.12)" if tokens.is_dark else "rgba(0,0,0,0.08)",
    }
    repl.update(extras)
    out = tpl
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


# ---- Renderers -----------------------------------------------------------

def _render_testimonials(tokens: ThemeTokens, brief: dict) -> str:
    """Three-quote testimonial trio.

    Layout is DNA-radius- and palette-driven. The DNA's kicker style
    sets the eyebrow voice (§ 02 · KIND WORDS vs. REF-02 / TESTIMONIALS).
    """
    kicker = _kicker(tokens, "02", "Kind words")
    business = brief.get("business_name") or "us"
    name1 = brief.get("_inspire_dna_hint") and "Maya R." or "Maya R."  # static placeholders
    # The three quotes are intentionally evergreen + editable — the user
    # will overwrite them via the visual editor. We don't pull anything
    # from the brief that wasn't explicitly placeholder-friendly.
    tpl = """
export function Testimonials() {
  const quotes = [
    {
      quote: "Genuinely the easiest experience I've had with a small business. Recommended without reservation.",
      name:  "Maya R.",
      detail: "Park Slope, Brooklyn",
    },
    {
      quote: "They listened. They followed up. They did exactly what they said they would, on time.",
      name:  "Daniel T.",
      detail: "Returning customer",
    },
    {
      quote: "Best decision we made all quarter. Already booked two more visits.",
      name:  "Aisha K.",
      detail: "Verified review",
    },
  ];
  return (
    <section
      data-pebble-block="testimonials_trio"
      className="py-20 md:py-28 px-6 md:px-12"
      style={{ backgroundColor: '__BG__', color: '__INK__', fontFamily: __BODY_STACK_JSX__ }}
    >
      <div className="max-w-6xl mx-auto">
        <p
          className="text-xs uppercase tracking-[0.18em] mb-3"
          style={{ color: '__ACCENT__', fontFamily: __MONO_STACK_JSX__ }}
        >
          __KICKER__
        </p>
        <h2
          className="text-3xl md:text-5xl font-semibold mb-12 max-w-2xl"
          style={{ fontFamily: __DISPLAY_STACK_JSX__, letterSpacing: '-0.01em' }}
        >
          What people say about working with us.
        </h2>
        <div className="grid md:grid-cols-3 gap-6 md:gap-8">
          {quotes.map((q, i) => (
            <figure
              key={i}
              className="__RADIUS__ p-6 md:p-8 flex flex-col gap-4"
              style={{
                border: '1px solid __DARK_BORDER__',
                background: 'transparent',
              }}
            >
              <span
                aria-hidden
                className="text-5xl leading-none -mb-2"
                style={{ color: '__ACCENT__', fontFamily: __DISPLAY_STACK_JSX__ }}
              >
                &ldquo;
              </span>
              <blockquote
                className="text-base md:text-lg leading-relaxed"
                style={{ fontFamily: __BODY_STACK_JSX__ }}
              >
                {q.quote}
              </blockquote>
              <figcaption className="mt-auto">
                <p className="font-semibold text-sm">{q.name}</p>
                <p className="text-xs opacity-70" style={{ fontFamily: __MONO_STACK_JSX__ }}>
                  {q.detail}
                </p>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
""".lstrip()
    return _apply(tpl, tokens,
                  __KICKER__=kicker,
                  __DISPLAY_STACK_JSX__=_jsx_string(tokens.display_stack()),
                  __BODY_STACK_JSX__=_jsx_string(tokens.body_stack()),
                  __MONO_STACK_JSX__=_jsx_string(tokens.mono_stack()))


def _render_pricing(tokens: ThemeTokens, brief: dict) -> str:
    """Three-tier pricing card row.

    The middle tier is highlighted via the accent color. Placeholder
    plans are evergreen ('Starter / Plus / Premium') — the user will
    rename via the visual editor.
    """
    kicker = _kicker(tokens, "03", "Plans")
    tpl = """
export function Pricing() {
  const tiers = [
    {
      name: "Starter",
      price: "$0",
      cadence: "free forever",
      features: ["The essentials, working today", "Email support", "Cancel anytime"],
      highlighted: false,
    },
    {
      name: "Plus",
      price: "$29",
      cadence: "per month",
      features: ["Everything in Starter", "Priority response", "Concierge onboarding"],
      highlighted: true,
    },
    {
      name: "Premium",
      price: "$79",
      cadence: "per month",
      features: ["Everything in Plus", "Dedicated specialist", "Custom workflows"],
      highlighted: false,
    },
  ];
  return (
    <section
      data-pebble-block="pricing_tiers"
      className="py-20 md:py-28 px-6 md:px-12"
      style={{ backgroundColor: '__BG__', color: '__INK__', fontFamily: __BODY_STACK_JSX__ }}
    >
      <div className="max-w-6xl mx-auto">
        <p
          className="text-xs uppercase tracking-[0.18em] mb-3"
          style={{ color: '__ACCENT__', fontFamily: __MONO_STACK_JSX__ }}
        >
          __KICKER__
        </p>
        <h2
          className="text-3xl md:text-5xl font-semibold mb-12 max-w-2xl"
          style={{ fontFamily: __DISPLAY_STACK_JSX__, letterSpacing: '-0.01em' }}
        >
          Pick the level that fits today. Change it whenever.
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {tiers.map((t) => (
            <div
              key={t.name}
              className="__RADIUS__ p-8 flex flex-col"
              style={{
                border: t.highlighted ? '2px solid __ACCENT__' : '1px solid __DARK_BORDER__',
                background: t.highlighted ? '__ACCENT__10' : 'transparent',
                position: 'relative',
              }}
            >
              {t.highlighted && (
                <span
                  className="absolute -top-3 left-6 text-[10px] uppercase tracking-widest px-2 py-1 __RADIUS__"
                  style={{
                    color: '__BG__',
                    background: '__ACCENT__',
                    fontFamily: __MONO_STACK_JSX__,
                  }}
                >
                  Most chosen
                </span>
              )}
              <h3
                className="text-xl font-semibold mb-1"
                style={{ fontFamily: __DISPLAY_STACK_JSX__ }}
              >
                {t.name}
              </h3>
              <p className="mb-6">
                <span className="text-4xl font-bold" style={{ fontFamily: __DISPLAY_STACK_JSX__ }}>
                  {t.price}
                </span>{" "}
                <span className="text-sm opacity-70">{t.cadence}</span>
              </p>
              <ul className="space-y-2 mb-8 flex-1">
                {t.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <span aria-hidden style={{ color: '__ACCENT__' }}>✓</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <a
                href="#contact"
                className="__RADIUS__ px-5 py-3 text-center text-sm font-semibold transition-opacity hover:opacity-80"
                style={{
                  background: t.highlighted ? '__ACCENT__' : 'transparent',
                  color: t.highlighted ? '__BG__' : '__INK__',
                  border: t.highlighted ? '0' : '1px solid __DARK_BORDER__',
                }}
              >
                Start with {t.name}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
""".lstrip()
    rendered = _apply(tpl, tokens,
                      __KICKER__=kicker,
                      __DISPLAY_STACK_JSX__=_jsx_string(tokens.display_stack()),
                      __BODY_STACK_JSX__=_jsx_string(tokens.body_stack()),
                      __MONO_STACK_JSX__=_jsx_string(tokens.mono_stack()))
    # __ACCENT__10 needs to become a real low-opacity color. Easiest path:
    # replace the placeholder with an rgba derived from the accent.
    return rendered.replace("'__ACCENT__10'", _rgba_with_alpha(tokens.accent_hex, 0.08))


def _render_faq(tokens: ThemeTokens, brief: dict) -> str:
    """Collapsible FAQ accordion with 5 placeholder questions.

    Uses native ``<details>`` / ``<summary>`` so it works without
    JavaScript and respects ``prefers-reduced-motion`` automatically.
    """
    kicker = _kicker(tokens, "04", "Questions")
    tpl = """
export function FAQ() {
  const items = [
    {
      q: "How fast can we get started?",
      a: "Usually within a single business day. We confirm details, agree on scope, and book the first appointment.",
    },
    {
      q: "What happens if I need to change something later?",
      a: "Nothing is locked in. Reach out anytime and we adjust — no extra fees for reasonable revisions.",
    },
    {
      q: "Do you offer guarantees?",
      a: "Yes. If you're not satisfied within the first week, we refund without questions.",
    },
    {
      q: "How do you handle confidentiality?",
      a: "Everything you share is treated as confidential. We sign an NDA on request, but it's our default posture either way.",
    },
    {
      q: "Can I talk to a real person before committing?",
      a: "Always. Book a free 15-minute call below and we'll answer specifics for your situation.",
    },
  ];
  return (
    <section
      data-pebble-block="faq_accordion"
      className="py-20 md:py-28 px-6 md:px-12"
      style={{ backgroundColor: '__BG__', color: '__INK__', fontFamily: __BODY_STACK_JSX__ }}
    >
      <div className="max-w-3xl mx-auto">
        <p
          className="text-xs uppercase tracking-[0.18em] mb-3"
          style={{ color: '__ACCENT__', fontFamily: __MONO_STACK_JSX__ }}
        >
          __KICKER__
        </p>
        <h2
          className="text-3xl md:text-5xl font-semibold mb-10"
          style={{ fontFamily: __DISPLAY_STACK_JSX__, letterSpacing: '-0.01em' }}
        >
          Things people ask before they hire us.
        </h2>
        <div className="divide-y" style={{ borderColor: '__DARK_BORDER__' }}>
          {items.map((item, i) => (
            <details key={i} className="py-5 group">
              <summary
                className="flex items-center justify-between gap-4 cursor-pointer list-none"
                style={{ fontFamily: __DISPLAY_STACK_JSX__ }}
              >
                <span className="text-lg font-semibold">{item.q}</span>
                <span
                  aria-hidden
                  className="text-2xl leading-none transition-transform group-open:rotate-45"
                  style={{ color: '__ACCENT__' }}
                >
                  +
                </span>
              </summary>
              <p className="mt-3 text-sm md:text-base leading-relaxed opacity-80">
                {item.a}
              </p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
""".lstrip()
    return _apply(tpl, tokens,
                  __KICKER__=kicker,
                  __DISPLAY_STACK_JSX__=_jsx_string(tokens.display_stack()),
                  __BODY_STACK_JSX__=_jsx_string(tokens.body_stack()),
                  __MONO_STACK_JSX__=_jsx_string(tokens.mono_stack()))


def _render_feature_grid(tokens: ThemeTokens, brief: dict) -> str:
    """Six-cell feature grid with mini glyph + label + description.

    Glyphs are inline SVG circles/squares/triangles colored with the
    accent — no Lucide-import dependency. Each cell is editable through
    the visual editor like everything else.
    """
    kicker = _kicker(tokens, "02", "Features")
    tpl = """
export function FeatureGrid() {
  const features = [
    { title: "Built for clarity",   desc: "Plain language, no jargon. You see exactly what you're getting." },
    { title: "Fast to start",       desc: "Most projects are confirmed and underway within one business day." },
    { title: "Honest pricing",      desc: "No surprises. Quoted up front, billed exactly as quoted." },
    { title: "Local & accountable", desc: "We answer the phone. We follow up. We make it right when we miss." },
    { title: "Quality assured",     desc: "If a result doesn't meet our standard, we redo it at no extra charge." },
    { title: "Easy to reach",       desc: "Call, text, or email — we reply within the same business day." },
  ];
  return (
    <section
      data-pebble-block="feature_grid"
      className="py-20 md:py-28 px-6 md:px-12"
      style={{ backgroundColor: '__BG__', color: '__INK__', fontFamily: __BODY_STACK_JSX__ }}
    >
      <div className="max-w-6xl mx-auto">
        <p
          className="text-xs uppercase tracking-[0.18em] mb-3"
          style={{ color: '__ACCENT__', fontFamily: __MONO_STACK_JSX__ }}
        >
          __KICKER__
        </p>
        <h2
          className="text-3xl md:text-5xl font-semibold mb-10 max-w-3xl"
          style={{ fontFamily: __DISPLAY_STACK_JSX__, letterSpacing: '-0.01em' }}
        >
          The things you can count on when you work with us.
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {features.map((f, i) => (
            <div key={i} className="flex flex-col gap-2">
              <span
                aria-hidden
                className="inline-flex items-center justify-center w-10 h-10 __RADIUS__"
                style={{ background: '__ACCENT__', color: '__BG__' }}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </span>
              <h3
                className="text-lg font-semibold"
                style={{ fontFamily: __DISPLAY_STACK_JSX__ }}
              >
                {f.title}
              </h3>
              <p className="text-sm leading-relaxed opacity-80">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
""".lstrip()
    return _apply(tpl, tokens,
                  __KICKER__=kicker,
                  __DISPLAY_STACK_JSX__=_jsx_string(tokens.display_stack()),
                  __BODY_STACK_JSX__=_jsx_string(tokens.body_stack()),
                  __MONO_STACK_JSX__=_jsx_string(tokens.mono_stack()))


def _render_cta_banner(tokens: ThemeTokens, brief: dict) -> str:
    """Big CTA section — headline + one-sentence promise + button.

    Inverted color treatment: this block uses the accent as background
    so the inserted band reads as a hard break from surrounding sections
    regardless of DNA palette posture.
    """
    kicker = _kicker(tokens, "05", "Get in touch")
    business = brief.get("business_name") or "us"
    tpl = """
export function CTABanner() {
  return (
    <section
      data-pebble-block="cta_banner"
      className="py-24 md:py-32 px-6 md:px-12 text-center"
      style={{ backgroundColor: '__ACCENT__', color: '__BG__', fontFamily: __BODY_STACK_JSX__ }}
    >
      <div className="max-w-3xl mx-auto">
        <p
          className="text-xs uppercase tracking-[0.22em] mb-4 opacity-90"
          style={{ fontFamily: __MONO_STACK_JSX__ }}
        >
          __KICKER__
        </p>
        <h2
          className="text-4xl md:text-6xl font-semibold mb-6"
          style={{ fontFamily: __DISPLAY_STACK_JSX__, letterSpacing: '-0.02em' }}
        >
          Ready when you are.
        </h2>
        <p className="text-base md:text-lg opacity-90 mb-10 max-w-xl mx-auto">
          One short conversation is usually all it takes to know whether we&apos;re a fit.
          No pressure, no sales script.
        </p>
        <a
          href="#contact"
          className="__RADIUS__ inline-block px-8 py-4 text-base font-semibold transition-opacity hover:opacity-90"
          style={{ background: '__BG__', color: '__INK__' }}
        >
          Talk to __BUSINESS__
        </a>
      </div>
    </section>
  );
}
""".lstrip()
    return _apply(tpl, tokens,
                  __KICKER__=kicker,
                  __BUSINESS__=_jsx_safe(business),
                  __DISPLAY_STACK_JSX__=_jsx_string(tokens.display_stack()),
                  __BODY_STACK_JSX__=_jsx_string(tokens.body_stack()),
                  __MONO_STACK_JSX__=_jsx_string(tokens.mono_stack()))


def _render_stats_strip(tokens: ThemeTokens, brief: dict) -> str:
    """Four-number stats strip. Especially natural on Brutalist Editorial
    + Industrial Freight + Cinematic IMAX DNAs, but works on all 13."""
    kicker = _kicker(tokens, "02", "By the numbers")
    tpl = """
export function StatsStrip() {
  const stats = [
    { number: "12+",   label: "Years in business" },
    { number: "2,400", label: "Customers served" },
    { number: "4.9",   label: "Average rating" },
    { number: "100%",  label: "Satisfaction guarantee" },
  ];
  return (
    <section
      data-pebble-block="stats_strip"
      className="py-20 md:py-24 px-6 md:px-12"
      style={{ backgroundColor: '__BG__', color: '__INK__', fontFamily: __BODY_STACK_JSX__ }}
    >
      <div className="max-w-6xl mx-auto">
        <p
          className="text-xs uppercase tracking-[0.18em] mb-8"
          style={{ color: '__ACCENT__', fontFamily: __MONO_STACK_JSX__ }}
        >
          __KICKER__
        </p>
        <div
          className="grid grid-cols-2 md:grid-cols-4 gap-y-10 gap-x-6"
          style={{ borderTop: '1px solid __DARK_BORDER__', paddingTop: '2rem' }}
        >
          {stats.map((s, i) => (
            <div key={i} className="flex flex-col gap-1">
              <p
                className="text-4xl md:text-6xl font-bold leading-none"
                style={{ fontFamily: __DISPLAY_STACK_JSX__, color: '__ACCENT__', letterSpacing: '-0.02em' }}
              >
                {s.number}
              </p>
              <p
                className="text-xs uppercase tracking-widest opacity-80"
                style={{ fontFamily: __MONO_STACK_JSX__ }}
              >
                {s.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
""".lstrip()
    return _apply(tpl, tokens,
                  __KICKER__=kicker,
                  __DISPLAY_STACK_JSX__=_jsx_string(tokens.display_stack()),
                  __BODY_STACK_JSX__=_jsx_string(tokens.body_stack()),
                  __MONO_STACK_JSX__=_jsx_string(tokens.mono_stack()))


# ---- Helpers --------------------------------------------------------------

def _jsx_string(value: str) -> str:
    """Turn ``"'Cormorant', Inter, ..."`` into a JSX string-literal that
    can be dropped between ``fontFamily: __X__`` — i.e. wrap in quotes and
    escape internal quotes. We use a double-quoted JSX literal so the
    single quotes inside (font names) don't need escaping."""
    # Defensive: refuse newlines (would break JSX), and any backslash that
    # could be used to break out of the string literal. Font family
    # strings never need either.
    safe = value.replace("\\", "").replace("\n", " ").replace("\r", " ")
    safe = safe.replace('"', '\\"')
    return f'"{safe}"'


def _jsx_safe(value: str) -> str:
    """Sanitise free text headed for raw JSX text — strips control chars
    and escapes braces. Brief fields like ``business_name`` get this
    treatment so a malicious or unusual name can't inject JSX."""
    safe = "".join(c for c in value if ord(c) >= 32 or c in ("\n", "\t"))
    safe = safe.replace("\\", "\\\\")
    safe = safe.replace("{", "&#123;").replace("}", "&#125;")
    safe = safe.replace("<", "&lt;").replace(">", "&gt;")
    return safe.strip()


def _rgba_with_alpha(hex_color: str, alpha: float) -> str:
    """``#205661`` + 0.08 → ``"rgba(32, 86, 97, 0.08)"`` (JSX-ready, with
    surrounding double-quotes)."""
    raw = hex_color.lstrip("#")
    if len(raw) != 6:
        return '"transparent"'
    try:
        r = int(raw[0:2], 16)
        g = int(raw[2:4], 16)
        b = int(raw[4:6], 16)
    except ValueError:
        return '"transparent"'
    a = max(0.0, min(1.0, alpha))
    return f'"rgba({r}, {g}, {b}, {a:.2f})"'


# ---- Registry -------------------------------------------------------------

BLOCK_REGISTRY: dict[str, BlockSpec] = {
    "testimonials_trio": BlockSpec(
        id="testimonials_trio",
        label="Testimonials (3)",
        category="social-proof",
        description="Three quote cards with attribution. Re-themed live to your DNA on insert.",
        component_name="Testimonials",
        icon="MessageSquareQuote",
        render=_render_testimonials,
    ),
    "pricing_tiers": BlockSpec(
        id="pricing_tiers",
        label="Pricing tiers",
        category="monetization",
        description="Three-tier pricing card row, middle tier accented.",
        component_name="Pricing",
        icon="Coins",
        render=_render_pricing,
    ),
    "faq_accordion": BlockSpec(
        id="faq_accordion",
        label="FAQ accordion",
        category="explainer",
        description="Five collapsible questions — pure HTML <details>, no JS required.",
        component_name="FAQ",
        icon="HelpCircle",
        render=_render_faq,
    ),
    "feature_grid": BlockSpec(
        id="feature_grid",
        label="Feature grid",
        category="explainer",
        description="Six features in a 2-3 column grid with accent glyphs.",
        component_name="FeatureGrid",
        icon="Grid3x3",
        render=_render_feature_grid,
    ),
    "cta_banner": BlockSpec(
        id="cta_banner",
        label="Big CTA banner",
        category="conversion",
        description="Full-width accent band with one big call-to-action button.",
        component_name="CTABanner",
        icon="Rocket",
        render=_render_cta_banner,
    ),
    "stats_strip": BlockSpec(
        id="stats_strip",
        label="Stats strip",
        category="social-proof",
        description="Four big numbers — years in business, customers served, rating, guarantee.",
        component_name="StatsStrip",
        icon="BarChart3",
        render=_render_stats_strip,
    ),
}


def list_blocks() -> list[dict]:
    """Public listing payload — ``[{id, label, category, description, icon}, ...]``."""
    return [spec.to_listing() for spec in BLOCK_REGISTRY.values()]


def render_block(block_id: str, tokens: ThemeTokens, brief: dict) -> str:
    """Render a single block as JSX. Raises ``KeyError`` if the block id
    isn't in the registry — the HTTP handler maps that to a 400."""
    spec = BLOCK_REGISTRY[block_id]
    return spec.render(tokens, brief)
