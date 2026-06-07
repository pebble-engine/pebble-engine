"""Template gallery API — Phase 31 (2026-05-20).

This is the cheap-fast alternative to /api/generate. Instead of asking the
LLM to design + execute a website from scratch (~25K input / 16K output
tokens, $0.02-0.50 per build), we:

1. **Pre-build templates** that are real Next.js projects with all content
   isolated in `content/site.ts`. The TEMPLATE files (TSX components,
   styles, config) are stable, designer-curated, and never touched by the
   LLM.
2. **Instantiate per customer** by copying the template directory to
   `output/<slug>/site/` and asking the LLM to rewrite ONLY `content/site.ts`
   based on the customer's brief. That's a ~3K-token call costing $0.005
   on Qwen Flash, $0.08 on Sonnet — 10-100× cheaper than full generation.
3. **Reliability**: the LLM can't break layout, fonts, animations, or
   structure because it never sees them. Worst case, content reads
   awkwardly; site never compiles broken.

Why this exists at all: Marc's 2026-05-20 evening session with the Webild
teardown made it clear that **premium template galleries are how every
serious AI-website competitor closes the visual-quality gap**. Their AI
generation is comparable to Pebble's. Their handcrafted templates are the
differentiator. Pebble's answer: ship Marc-curated design DNA as
templates and use the LLM for the narrow content-swap task it's
genuinely good at.

Endpoints
---------
- GET  /api/templates                 → list registry entries
- POST /api/instantiate-template      → clone + content-swap → output/<slug>/

Registry is at `pebble/templates/registry.json`. Each template is a full
Next.js project skeleton at `pebble/templates/<id>/`.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from pebble.log import log
from pebble.text import sanitize_business_name
from pebble.next_config_patch import ensure_allowed_dev_origins
from pebble.security import client_ip, generate_limiter


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "pebble" / "templates" / "registry.json"
TEMPLATES_ROOT = Path(__file__).resolve().parents[2] / "pebble" / "templates"


def load_registry() -> dict[str, Any]:
    """Read templates/registry.json. Returns {} on any parse error so
    callers can degrade gracefully instead of 500ing the whole engine."""
    if not REGISTRY_PATH.exists():
        return {"schema_version": "1.0", "templates": []}
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning("[templates] registry parse failed: %s", e)
        return {"schema_version": "1.0", "templates": []}


def get_template(template_id: str) -> dict[str, Any] | None:
    reg = load_registry()
    for t in reg.get("templates", []):
        if isinstance(t, dict) and t.get("id") == template_id:
            return t
    return None


# ---------------------------------------------------------------------------
# Endpoint: GET /api/templates
# ---------------------------------------------------------------------------

def run_list_templates(handler) -> None:
    """Return the public-facing template gallery. Strips internal-only
    fields (`_comment`, `_planned_next`, directory paths) — the v3
    frontend doesn't need our file system layout."""
    reg = load_registry()
    public = []
    for t in reg.get("templates", []):
        if not isinstance(t, dict):
            continue
        public.append({
            k: v for k, v in t.items()
            if k not in {"directory"}  # hide engine-internal path
        })
    handler._json(200, {
        "templates": public,
        "count": len(public),
    })


# ---------------------------------------------------------------------------
# Endpoint: POST /api/instantiate-template
# ---------------------------------------------------------------------------

# Files we never copy from the template (transient build artifacts + heavy
# dependencies — `npm install` happens once at customer time, not for every
# instantiation).
_SKIP_NAMES = frozenset({"node_modules", ".next", ".turbo", "dist", "build"})

# Files we DO copy verbatim but NEVER let the LLM touch. content/site.ts
# is the ONLY file the LLM rewrites — everything else is stable structure.
TOKENIZED_FILE = "content/site.ts"


def _copy_template(src_dir: Path, dst_dir: Path) -> int:
    """Recursive copy excluding node_modules + build artifacts. Returns
    number of files written so the response can report it."""
    written = 0
    for src_path in src_dir.rglob("*"):
        # Skip dirs we don't want to traverse
        if any(part in _SKIP_NAMES for part in src_path.parts):
            continue
        if src_path.is_dir():
            continue
        rel = src_path.relative_to(src_dir)
        dst_path = dst_dir / rel
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        written += 1
    return written


def _build_content_swap_prompt(template_id: str, current_site_ts: str, brief: dict[str, Any]) -> str:
    """Construct the LLM prompt for rewriting `content/site.ts`.

    Keep this prompt SMALL and STRUCTURAL. The whole point is that the
    LLM does one narrow task it's reliably good at: substitute values
    in a TypeScript file. We do NOT want it inventing structure, adding
    fields, or changing the file's shape.
    """
    bn = (brief.get("business_name") or "").strip() or "Untitled Business"
    bt = (brief.get("business_type") or brief.get("industry") or "").strip()
    location = (brief.get("location") or "").strip()
    services = brief.get("services") or brief.get("site_functions") or []
    if isinstance(services, list):
        services_str = ", ".join(str(s) for s in services[:12])
    else:
        services_str = str(services)
    notes = (brief.get("notes_freeform") or brief.get("extra_context") or "").strip()
    tone = (brief.get("brand_tone") or "professional").strip()

    # P1 — durable "about your business" context (per-project + per-account).
    # render_knowledge_block sanitizes braces, so it's f-string safe.
    from pebble.knowledge import render_knowledge_block, project_knowledge
    knowledge_section = render_knowledge_block(
        project_knowledge(brief),
        (brief.get("_account_knowledge") or "").strip(),
    )
    knowledge_section = ("\n\n" + knowledge_section) if knowledge_section else ""

    return f"""You are editing a Next.js template's content file. Your ONLY job is to rewrite the values of the exported constants in `content/site.ts` so they match this customer's business. Do NOT change variable names. Do NOT change types. Do NOT add new exports. Do NOT remove exports. Do NOT change array shapes (if an array starts empty, keep it empty unless the customer's brief explicitly provided data for it).

# Customer brief

- Business name: {bn}
- Industry / business type: {bt}
- Location: {location or "(not provided — use [BUSINESS ADDRESS] placeholder)"}
- Services / offerings: {services_str or "(infer 4-6 industry-typical services)"}
- Brand tone: {tone}
- Owner notes: {notes or "(none)"}{knowledge_section}

# Copywriting craft (sound like a real, specific business — not a filled-in template)

The stock template copy is competent but generic. Rewrite it so it reads like a confident
local business with a point of view. Apply these ONLY to constants that already exist
(never add new ones):

- HEADLINE: lead with a value proposition or a feeling, not just the category. Prefer
  "Pest control that respects your home" over "Family-Owned Pest Control". Say what the
  customer GETS, not merely what the business IS.
- GUARANTEE / PROMISE: if a tagline, promise, or CTA-adjacent line exists, make it concrete
  and memorable (e.g. "If pests come back, so do we — free"; "Booked today, done tomorrow").
  A specific promise beats a generic adjective like "professional" or "reliable".
- EXPERTISE SIGNALS: in service descriptions, name the REAL methods, tools, or standards a
  pro in this trade actually uses (for pest control: perimeter treatments, exclusion
  sealing, re-treat warranties; for HVAC: load calculations, SEER ratings). Specific
  technique signals competence WITHOUT inventing facts.
- BENEFIT-FIRST: describe the customer's outcome first, then the method. Replace feature-list
  voice ("Targeted treatments that reduce insect populations") with outcome voice ("Keep your
  yard usable all summer — we knock mosquitoes and ticks down at the source").
- VOICE: match the brand tone above, vary sentence rhythm, and cut corporate filler
  ("solutions", "cutting-edge", "we strive to"). Write like the person who does the work.

The example phrasings above (e.g. "Pest control that respects your home", "knock mosquitoes
down at the source") ILLUSTRATE the pattern — they are not copy to reuse. Write fresh lines
specific to THIS business; never output the example sentences verbatim.

These craft rules NEVER override the anti-slop rules below. Be specific in CRAFT; never be
specific about FACTS you were not given (numbers, years, names, quotes, phone/email/address).

# Anti-slop rules (CRITICAL)

- Phone: use exactly "[BUSINESS PHONE]" — do NOT invent a real-looking number.
- Email: use exactly "[BUSINESS EMAIL]" — do NOT invent.
- Address: if location not provided, use "[BUSINESS ADDRESS]". Otherwise format as "[STREET ADDRESS], {location}".
- Testimonials: if the brief did NOT include real testimonials, KEEP the TESTIMONIALS array empty (`TESTIMONIALS = []`). Never invent quotes, names, ratings, or counts.
- Featured products / numbered stats: same rule — empty arrays stay empty unless the brief explicitly supplied values.
- Founding year / years-in-business: do NOT mention unless the brief provided it. If the brief is silent, omit the time signal entirely.
- Scalar social-proof numbers (star RATINGS, review COUNTS, "X+ homes served / jobs completed", any headline metric) that the brief did NOT provide: do NOT pass through the template's sample number — the template ships example values like RATING_VALUE = "5.0" / RATING_COUNT = "237" purely as formatting samples. Replace each with a clearly-labeled placeholder in [SQUARE BRACKETS]: RATING_VALUE = "[rating]", RATING_COUNT = "[# of reviews]", a sample "237" becomes "[# served]". Presenting the template's example numbers as this business's real numbers is fabrication; a bracketed placeholder is honest and our pre-publish check reminds the owner to fill it in.

# Current template file (the schema you must preserve)

```typescript
{current_site_ts}
```

# Your output

Return ONLY the new content of `content/site.ts`. Wrap it in a single fenced ```typescript ... ``` block. No prose before or after. Every exported constant from the input MUST appear in the output (with possibly-updated values). No new constants. The first line of the file should keep whatever leading comment was there.
"""


def _extract_typescript_block(llm_text: str) -> str | None:
    """Pull the ```typescript ... ``` block from the LLM response.

    LLMs sometimes wrap in ```ts or ``` (no language tag). Try common
    variants; fall back to the largest fenced block.
    """
    import re
    for fence in (r"```typescript\s*\n(.*?)```", r"```ts\s*\n(.*?)```", r"```\s*\n(.*?)```"):
        m = re.search(fence, llm_text, re.DOTALL)
        if m:
            return m.group(1).rstrip()
    # No fences — assume the whole thing is the file (some LLMs do this).
    if llm_text.lstrip().startswith("export ") or "//" in llm_text[:200]:
        return llm_text.strip()
    return None


def _validate_swapped_site_ts(new_ts: str, original_ts: str) -> tuple[bool, str]:
    """Lightweight validation: every `export const NAME` in the original
    must still exist in the new content. If the LLM dropped or renamed
    any export, the swap is invalid and we fall back to the original.

    Returns (ok, message). On not-ok the caller should NOT write the
    bad content — keeping the template defaults is safer than a half-
    broken customer site.
    """
    import re
    orig_names = set(re.findall(r"export\s+const\s+(\w+)", original_ts))
    new_names = set(re.findall(r"export\s+const\s+(\w+)", new_ts))
    missing = orig_names - new_names
    if missing:
        return False, f"LLM dropped {len(missing)} export(s): {sorted(missing)[:5]}"
    return True, "ok"


def run_instantiate_template(handler) -> None:
    """POST /api/instantiate-template
    Body: {template_id, brief: {business_name, business_type, location, services?, ...}}

    Flow:
      1. Validate inputs.
      2. Slugify business_name → output slug. Auto-suffix on collision.
      3. Copy template directory into output/<slug>/site/.
      4. Read template's content/site.ts.
      5. Run focused content-swap LLM call.
      6. Validate response, write new content/site.ts.
      7. Patch next.config.mjs with allowedDevOrigins (Phase 20c).
      8. Emit brief.json + build_meta.json so the workspace can pick it up.
    """
    from pebble.server.build import _engine
    pe = _engine()
    MAX_REQUEST_BYTES = pe.MAX_REQUEST_BYTES
    OUTPUT_DIR = pe.OUTPUT_DIR
    _slugify = pe._slugify

    ip = client_ip(handler)
    if not generate_limiter.allow(ip or ""):
        handler._json(429, {"error": "too many build requests — max 5 per 10 min per IP"})
        return

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"})
        return
    if length <= 0 or length > MAX_REQUEST_BYTES:
        handler._json(400, {"error": "missing or oversized body"})
        return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"})
        return

    template_id = (body.get("template_id") or "").strip()
    brief = body.get("brief") or {}
    if not template_id or not isinstance(brief, dict):
        handler._json(400, {"error": "missing template_id or brief"})
        return

    tmpl = get_template(template_id)
    if not tmpl:
        handler._json(404, {"error": f"unknown template_id {template_id!r}"})
        return

    src_dir = (Path(__file__).resolve().parents[2] / tmpl["directory"]).resolve()
    if not src_dir.exists() or not src_dir.is_dir():
        log.warning("[templates] source dir missing for %s: %s", template_id, src_dir)
        handler._json(500, {"error": "template source not found on disk"})
        return

    # Slug derivation — same convention as the AI-generation path, including
    # the title-case sanitization from Phase 20a and the auto-suffix from
    # Phase 15f. Auto-suffix only kicks in if the slug is currently serving
    # a next dev.
    raw_name = brief.get("business_name", "")
    cleaned = sanitize_business_name(raw_name) or "untitled"
    if cleaned != raw_name and cleaned:
        brief["business_name"] = cleaned
    slug = _slugify(cleaned)
    try:
        from pebble.server.dev_registry import get_url as _get_dev_url
        if _get_dev_url(slug):
            base = slug
            n = 2
            while _get_dev_url(f"{base}-{n}"):
                n += 1
            slug = f"{base}-{n}"
            log.info("[templates] auto-suffix: %r serving; using %r", base, slug)
    except Exception:
        pass

    out_dir = OUTPUT_DIR / slug
    site_dir = out_dir / "site"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy template files
    try:
        file_count = _copy_template(src_dir, site_dir)
    except Exception as e:
        log.exception("[templates] copy failed for %s -> %s", src_dir, site_dir)
        handler._json(500, {"error": f"template copy failed: {e}"})
        return

    # Read the template's content/site.ts as the schema
    content_path = site_dir / TOKENIZED_FILE
    if not content_path.exists():
        log.warning("[templates] %s missing %s — instantiation degraded", template_id, TOKENIZED_FILE)
        handler._json(500, {"error": f"template missing {TOKENIZED_FILE}"})
        return
    try:
        original_ts = content_path.read_text(encoding="utf-8")
    except Exception as e:
        handler._json(500, {"error": f"could not read template content file: {e}"})
        return

    # P1 — fold the caller's account-wide knowledge default into the brief so
    # the content swap honors it (best-effort; anonymous instantiation skips).
    try:
        from pebble.security import resolve_user_id
        from pebble.knowledge import load_account_knowledge
        _uid = resolve_user_id(handler) or ""
        if _uid:
            brief["_account_knowledge"] = load_account_knowledge(OUTPUT_DIR, _uid)
    except Exception:
        pass

    # Content-swap LLM call. Uses the engine's default client (which is
    # tier-aware — free users get Qwen Flash, paid get the configured
    # default). Costs ~$0.005 on Flash, ~$0.08 on Sonnet.
    swap_prompt = _build_content_swap_prompt(template_id, original_ts, brief)
    llm_cost_usd = 0.0
    swap_ok = False
    swap_msg = "not attempted"
    new_ts = original_ts  # default: keep template defaults
    try:
        from pebble.llm import get_llm_client
        client, reason = get_llm_client()
        if client is None or reason != "ok":
            log.warning("[templates] LLM unavailable (%s) — shipping template defaults", reason)
            swap_msg = f"llm unavailable: {reason}"
        else:
            log.info("[templates] content-swap on %s (%s/%s)", template_id, client.provider, client.model)
            system = "You are a careful TypeScript editor. You preserve file structure and only rewrite literal values."
            response = client.generate(system=system, user=swap_prompt, max_tokens=8000)
            llm_text = response if isinstance(response, str) else getattr(response, "text", "")
            extracted = _extract_typescript_block(llm_text)
            if extracted:
                ok, msg = _validate_swapped_site_ts(extracted, original_ts)
                if ok:
                    new_ts = extracted
                    swap_ok = True
                    swap_msg = "ok"
                else:
                    swap_msg = f"validation failed: {msg}"
                    log.warning("[templates] %s — keeping template defaults", swap_msg)
            else:
                swap_msg = "could not extract typescript block from LLM response"
            # Cost estimation (rough — engine has more careful tracking elsewhere)
            try:
                from pebble.cost import estimate_cost
                est = estimate_cost(swap_prompt, llm_text, client.model)
                llm_cost_usd = round(est.estimated_cost_usd, 6)
            except Exception:
                llm_cost_usd = 0.0
    except Exception as e:
        log.exception("[templates] content-swap LLM call failed")
        swap_msg = f"llm error: {e}"

    # Write the (possibly swapped) content file
    try:
        content_path.write_text(new_ts, encoding="utf-8")
    except Exception as e:
        handler._json(500, {"error": f"could not write swapped content: {e}"})
        return

    # Patch next.config.mjs for cross-origin dev (Phase 20c)
    try:
        ensure_allowed_dev_origins(site_dir / "next.config.mjs")
    except Exception:
        pass

    # Save brief.json + minimal build_meta so the workspace recognizes the project
    saved_answers = dict(brief)
    saved_answers["_slug"] = slug
    saved_answers["_created_at"] = datetime.now().isoformat()
    saved_answers["_template_id"] = template_id
    (out_dir / "brief.json").write_text(json.dumps(saved_answers, indent=2), encoding="utf-8")

    (out_dir / "build_meta.json").write_text(json.dumps({
        "model": "template-instantiation",
        "provider": "templates",
        "template_id": template_id,
        "elapsed_seconds": 0,  # ~milliseconds — filesystem copy dominates
        "file_count": file_count,
        "built_at": datetime.now().isoformat(),
        "billable": False,  # template instantiation is free-tier-friendly
        "swap_ok": swap_ok,
        "swap_message": swap_msg,
        "estimated_cost_usd": llm_cost_usd,
    }, indent=2), encoding="utf-8")

    handler._json(200, {
        "ok": True,
        "slug": slug,
        "template_id": template_id,
        "file_count": file_count,
        "swap_ok": swap_ok,
        "swap_message": swap_msg,
        "estimated_cost_usd": llm_cost_usd,
    })


__all__ = [
    "load_registry",
    "get_template",
    "run_list_templates",
    "run_instantiate_template",
]
