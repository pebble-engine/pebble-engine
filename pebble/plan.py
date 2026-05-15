"""Pebble Plan — the structured "here's what I'll build" summary the UI
shows users between the questionnaire and the actual generation.

This module is a pure function: it takes the brief (answers), the
industry intel entry, and the chosen design DNA, and returns a JSON-
serializable dict matching the 7-field structure from the May 2026
product spec:

    {
      "audience":     str,
      "goal":         str,
      "pages":        [{id, title, route, purpose, foundation}, ...],
      "features":     [{id, label, source}, ...],
      "style":        {dna_id, label, mood, fonts, palette},
      "setup_needs":  [{id, label, status, notes}, ...],
      "next_steps":   [str, ...],
      "meta":         {business_name, industry_key, generated_at, engine_version},
    }

The Plan is:
- Cheap to compute (no LLM call).
- Deterministic given the same inputs.
- Editable: when the UI is wired, users will be able to tweak fields
  before the engine spends tokens on generation.

NOTE: ``setup_needs`` lists the spec's 14-item Launch Setup checklist with
HONEST statuses ("auto" = wired today, "pending" = not yet built,
"manual" = user must supply). Do not flip a status to "auto" until the
underlying infra actually exists — over-promising is the failure mode
NotebookLM called out in the Lovable/Base44 critique.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pebble.industry import PAGE_CATALOG, UNIVERSAL_EXTRA_PAGES


PLAN_SCHEMA_VERSION = "1.0"


# Foundation pages — generated for every build (independent of industry).
_FOUNDATION_PAGES = [
    {"id": "homepage", "title": "Homepage",  "route": "/",         "purpose": "Landing page with the main story, hero, and primary CTA."},
    {"id": "services", "title": "Services",  "route": "/services", "purpose": "Detail every service offered — full-bleed layout, not a card grid."},
    {"id": "about",    "title": "About",     "route": "/about",    "purpose": "Editorial story about the business — who, why, what makes them different."},
    {"id": "contact",  "title": "Contact",   "route": "/contact",  "purpose": "Real working contact form (Resend-wired) plus phone, email, address."},
]


# Universal extras — generated on top of foundation pages for every build.
_UNIVERSAL_EXTRAS = {
    "faq":     {"title": "FAQ",            "route": "/faq",     "purpose": "Promoted from the homepage FAQ section — 6-10 questions grouped by topic."},
    "privacy": {"title": "Privacy Policy", "route": "/privacy", "purpose": "Plain-English privacy policy — what's collected, what's not, who to contact."},
    "terms":   {"title": "Terms of Service","route": "/terms",  "purpose": "Plain-English terms — what the business agrees to, what the customer agrees to."},
}


# Launch Setup checklist — matches the May 2026 spec's 14 items.
# Status values:
#   "auto"    — Pebble already handles this in the build today
#   "pending" — Not yet built; UI should mark it "Coming soon"
#   "manual"  — User must supply or do this themselves
#
# When you wire new infrastructure (e.g. domain provisioning), flip the
# corresponding entry's status to "auto" and update the notes line.
_LAUNCH_SETUP_TEMPLATE = [
    {"id": "project_name",    "label": "Project name",      "status": "auto",    "notes": "Set from the business name in the brief."},
    {"id": "website_address", "label": "Website address",   "status": "pending", "notes": "Domain provisioning not wired yet."},
    {"id": "hosting",         "label": "Hosting",           "status": "pending", "notes": "Deployment pipeline not wired yet."},
    {"id": "business_email",  "label": "Business email",    "status": "pending", "notes": "Email-provider integration not wired yet."},
    {"id": "logo_photos",     "label": "Logo & photos",     "status": "manual",  "notes": "Pexels placeholders used until user supplies real assets."},
    {"id": "pages",           "label": "Pages",             "status": "auto",    "notes": "Industry-aware page system generates 7-10 pages per build."},
    {"id": "forms",           "label": "Forms",             "status": "auto",    "notes": "Contact form is wired via Resend Server Action."},
    {"id": "booking",         "label": "Booking",           "status": "pending", "notes": "Booking-provider integration not wired yet."},
    {"id": "payments",        "label": "Payments",          "status": "pending", "notes": "Payment-provider integration not wired yet."},
    {"id": "seo_basics",      "label": "SEO basics",        "status": "auto",    "notes": "Next.js metadata, semantic HTML, sitemap-ready output."},
    {"id": "analytics",       "label": "Analytics",         "status": "pending", "notes": "Analytics provider not wired yet."},
    {"id": "language_region", "label": "Language & region", "status": "pending", "notes": "English-only today; multilingual not wired yet."},
    {"id": "accessibility",   "label": "Accessibility",     "status": "auto",    "notes": "WCAG-AAA font sizes and contrast enforced by eval checks."},
    {"id": "publish",         "label": "Publish",           "status": "pending", "notes": "Deploy pipeline not wired yet."},
]


def _resolve_audience(answers: dict, industry_intel: Optional[dict]) -> str:
    """Pull audience from the brief; fall back to industry-derived default."""
    explicit = (answers.get("audience") or "").strip()
    if explicit:
        return explicit
    if industry_intel:
        tone = industry_intel.get("tone", "").strip()
        emotion = industry_intel.get("emotion", "").strip()
        if tone or emotion:
            return f"Typical {answers.get('business_type', 'business')} customers — {emotion or tone}.".strip()
    return "Not specified — the engine will infer from the industry profile."


def _resolve_goal(answers: dict) -> str:
    """Pull the primary visitor action from the brief."""
    fns = answers.get("site_functions") or []
    fn_labels = {
        "booking":   "let visitors book appointments online",
        "payment":   "accept online payments",
        "portfolio": "showcase past work",
        "leads":     "capture leads via a contact form",
        "ecommerce": "sell products online",
        "presence":  "establish a clear business presence (hours, location, contact)",
    }
    parts = [fn_labels.get(f, f) for f in fns if f]
    if parts:
        return "Visitors should be able to " + ", ".join(parts) + "."
    return "Establish a credible online presence and convert visitors into contacts."


def _resolve_pages(industry_intel: Optional[dict]) -> list[dict]:
    """Combine foundation + universal extras + industry-specific pages."""
    pages: list[dict] = []
    for fp in _FOUNDATION_PAGES:
        pages.append({**fp, "foundation": True})

    for ext_id in UNIVERSAL_EXTRA_PAGES:
        spec = _UNIVERSAL_EXTRAS.get(ext_id)
        if not spec:
            continue
        pages.append({"id": ext_id, "foundation": False, **spec})

    industry_pages = []
    if industry_intel and isinstance(industry_intel.get("pages"), list):
        industry_pages = list(industry_intel["pages"])
    for pid in industry_pages:
        spec = PAGE_CATALOG.get(pid)
        if not spec:
            continue
        primary_title = spec["title_options"][0]
        route = "/" + spec["route_segment"]
        pages.append({
            "id":         pid,
            "title":      primary_title,
            "route":      route,
            "purpose":    spec["purpose"],
            "foundation": False,
        })
    return pages


def _resolve_features(answers: dict, industry_intel: Optional[dict]) -> list[dict]:
    """Derive feature chips from the brief + industry intel."""
    out: list[dict] = []
    seen: set[str] = set()

    def _add(fid: str, label: str, source: str) -> None:
        if fid in seen:
            return
        seen.add(fid)
        out.append({"id": fid, "label": label, "source": source})

    fns = answers.get("site_functions") or []
    fn_labels = {
        "booking":   "Online booking",
        "payment":   "Online payments",
        "portfolio": "Portfolio gallery",
        "leads":     "Lead capture form",
        "ecommerce": "Online store",
        "presence":  "Business hours & location",
    }
    for f in fns:
        if f in fn_labels:
            _add(f, fn_labels[f], "brief")

    if industry_intel:
        sections = industry_intel.get("key_sections") or []
        section_labels = {
            "hero":              "Cinematic hero",
            "trust_bar":         "Trust bar (logos, badges, certifications)",
            "services":          "Services overview",
            "guarantee":         "Guarantee callout",
            "local_area":        "Service-area map",
            "faq":               "FAQ accordion",
            "emergency_service": "24/7 emergency callout",
            "financing":         "Financing options",
            "maintenance_plans": "Maintenance plans",
            "reviews":           "Customer reviews",
            "menu":              "Menu / offerings",
            "team":              "Team bios",
            "process":           "Process / how-we-work",
            "specialties":       "Specialties",
            "schedule":          "Class / event schedule",
            "pricing":           "Pricing tiers",
            "portfolio":         "Portfolio grid",
        }
        for s in sections:
            if s in section_labels:
                _add(s, section_labels[s], "industry")

        for ts in (industry_intel.get("trust_signals") or [])[:3]:
            ts_id = "trust_" + ts.lower().replace(" ", "_").replace("/", "_")[:30]
            _add(ts_id, f"Trust signal: {ts}", "industry")

    _add("contact_form", "Working contact form (Resend)", "universal")
    return out


def _resolve_style(design_dna: Optional[dict], industry_intel: Optional[dict]) -> dict:
    """Render the style chip for the UI: DNA name + mood + fonts + palette."""
    palette = {}
    if industry_intel and isinstance(industry_intel.get("colors"), dict):
        palette = {
            "primary":    industry_intel["colors"].get("primary", ""),
            "accent":     industry_intel["colors"].get("accent", ""),
            "background": industry_intel["colors"].get("background", ""),
        }

    if design_dna:
        return {
            "dna_id":  design_dna.get("id"),
            "label":   design_dna.get("label", "Unnamed DNA"),
            "mood":    design_dna.get("posture") or design_dna.get("emotion") or "",
            "fonts": {
                "display": design_dna.get("display_font", ""),
                "body":    design_dna.get("body_font", ""),
            },
            "palette": palette,
        }
    return {
        "dna_id":  None,
        "label":   "Default Pebble style",
        "mood":    industry_intel.get("emotion", "") if industry_intel else "",
        "fonts":   {"display": "", "body": ""},
        "palette": palette,
    }


def _resolve_setup_needs() -> list[dict]:
    return [dict(item) for item in _LAUNCH_SETUP_TEMPLATE]


def _resolve_next_steps(answers: dict) -> list[str]:
    steps = [
        "Review the plan above — edit anything before generation.",
        "Generate the first draft (Pebble fills in the pages, copy, and style).",
        "Try a style variant (Friendlier, More Professional, More Visual, Simpler, Premium).",
    ]
    if not (answers.get("phone") or "").strip():
        steps.append("Add your business phone number so contact CTAs link correctly.")
    if not (answers.get("email") or "").strip():
        steps.append("Add a business email so the contact form has a destination.")
    return steps


def build_pebble_plan(
    answers: dict,
    industry_intel: Optional[dict] = None,
    design_dna: Optional[dict] = None,
    engine_version: str = "",
) -> dict:
    """Build a Pebble Plan dict from the brief, industry intel, and DNA.

    Pure function — no I/O, no LLM calls. Safe to call before generation
    to preview what will be built, or after generation to record what was
    built.

    Args:
        answers: the validated brief (output of ``validate_build_payload``).
        industry_intel: the industry intel dict from
            ``resolve_industry_intel()``; may be ``None`` if the industry
            wasn't found.
        design_dna: the DNA dict from ``pick_random_dna()`` or
            ``pick_dna_by_id()``; may be ``None`` if DNA module isn't loaded.
        engine_version: optional engine version string for the meta block.

    Returns:
        A JSON-serializable dict matching ``PLAN_SCHEMA_VERSION`` 1.0.
    """
    # Resolve the build's target language for the meta block. If the
    # brief has _language stamped, use it; otherwise detect from the
    # brief's free text. detect_language always returns a code that's in
    # the LANGUAGES registry, so language_display() can't fail.
    try:
        from pebble.language import detect_language, language_display
        lang_code = detect_language(answers)
        lang = language_display(lang_code)
    except Exception:
        lang_code = "en"
        lang = {"english_name": "English", "native_name": "English", "html_lang": "en"}

    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "audience":       _resolve_audience(answers, industry_intel),
        "goal":           _resolve_goal(answers),
        "pages":          _resolve_pages(industry_intel),
        "features":       _resolve_features(answers, industry_intel),
        "style":          _resolve_style(design_dna, industry_intel),
        "setup_needs":    _resolve_setup_needs(),
        "next_steps":     _resolve_next_steps(answers),
        "language": {
            "code":         lang_code,
            "english_name": lang["english_name"],
            "native_name":  lang["native_name"],
            "html_lang":    lang["html_lang"],
        },
        "meta": {
            "business_name":  answers.get("business_name", ""),
            "industry_key":   answers.get("_industry_intel_key"),
            "generated_at":   datetime.now().isoformat(),
            "engine_version": engine_version,
        },
    }


__all__ = [
    "PLAN_SCHEMA_VERSION",
    "build_pebble_plan",
]
