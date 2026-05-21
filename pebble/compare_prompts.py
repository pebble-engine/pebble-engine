"""Playground-vs-Pebble prompt comparison harness (Phase 14b, 2026-05-20).

Lets us measure prompt-diet progress concretely. Marc's playground HTMLs
(C:/Users/marci/Qwen 3.6/Web1.html etc.) prove Qwen produces excellent
output when given a clean ~500-token prompt. This harness reproduces
that by sending the SAME brief through two paths:

  1. Pebble's full prompt (current diet ON or OFF, configurable)
  2. A playground-style mini prompt (~500 tokens) that names the
     industry, DNA, fonts, palette, and lets Qwen design

Outputs a side-by-side comparison: tokens sent, files received, size,
distinctive patterns (custom CSS tokens, image URLs, design system
sophistication). Lets us answer "is the diet enough, or do we need to go
further?"

Usage:
    python -m pebble.compare_prompts <brief.json>            # both paths
    python -m pebble.compare_prompts <brief.json> --diet-only
    python -m pebble.compare_prompts <brief.json> --playground-only
    python -m pebble.compare_prompts <brief.json> --dry-run  # prompts only, no LLM

Output is a markdown report written to:
    output/<slug>/compare_prompts_report.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from pebble.llm import LLMError, get_llm_client
from pebble.log import log


# ─────────────────────────────────────────────────────────────────────
# Playground-style mini prompt
# ─────────────────────────────────────────────────────────────────────

PLAYGROUND_SYSTEM = """You are a senior frontend engineer who builds production-quality marketing sites. \
You output complete, working code — no stubs, no TODOs, no preamble. \
Your output starts immediately with <pebble-file path="..."> tags."""


PLAYGROUND_USER_TEMPLATE = """Build a complete Next.js 14 marketing site for the business below.

# The business
- Name: {business_name}
- Type: {business_type}
- Location: {location}
- Audience: {audience}
- Voice/tone: {brand_tone}

# Visual direction
- Style: {dna_label} — {dna_feel}
- Palette: {palette}
- Fonts: {fonts}
- Layout: {layout_label} — {layout_feel}

# Tech stack
- Next.js 14 App Router, React 18, TypeScript, Tailwind CSS v3
- Real Unsplash or Pexels images (use real URLs like https://images.unsplash.com/photo-{{id}}?auto=format&fit=crop&w=1600&q=80)
- GSAP + ScrollTrigger via CDN (or `gsap` npm package)
- Resend SDK for the contact form (Server Action)

# Pages required
- app/page.tsx (homepage)
- app/services/page.tsx
- app/about/page.tsx
- app/contact/page.tsx
- app/faq/page.tsx
- app/privacy/page.tsx
- app/terms/page.tsx

# Output format
Emit each file as a `<pebble-file path="...">` block. First character of \
your response is `<`. No commentary, no preamble. Output package.json, \
next.config.mjs, tailwind.config.ts, tsconfig.json, app/layout.tsx, \
app/globals.css, all the pages above, all components, contact Server Action, \
and the lib/email.ts helper.

Make it the kind of site you'd be proud to ship. Use the Style direction \
above as your design opinion — own it. Avoid generic SaaS template look."""


def _flatten_palette(dna: Optional[dict]) -> str:
    if not dna:
        return "designer's choice"
    posture = dna.get("palette_posture", "")
    hexes = re.findall(r"#[0-9A-Fa-f]{6}", posture)
    return ", ".join(hexes[:5]) if hexes else posture[:200]


def build_playground_prompt(brief: dict, dna: Optional[dict], layout: Optional[dict]) -> tuple[str, str]:
    """Return (system, user) for the playground-style mini prompt."""
    if dna is None:
        dna = {"label": "your choice", "feel": "modern marketing site",
               "display_font": "designer's pick", "body_font": "designer's pick"}
    if layout is None:
        layout = {"label": "your choice", "feel": "standard hero + sections"}

    user = PLAYGROUND_USER_TEMPLATE.format(
        business_name=brief.get("business_name", "Acme"),
        business_type=brief.get("business_type", brief.get("industry", "small business")),
        location=brief.get("location", "—"),
        audience=brief.get("audience", "general public"),
        brand_tone=brief.get("brand_tone", "professional"),
        dna_label=dna.get("label", "Modern"),
        dna_feel=dna.get("feel", "clean, opinionated marketing site"),
        palette=_flatten_palette(dna),
        fonts=f"{dna.get('display_font', 'Inter')} (display), {dna.get('body_font', 'Inter')} (body)",
        layout_label=layout.get("label", "Standard"),
        layout_feel=layout.get("feel", "hero + sections + footer"),
    )
    return PLAYGROUND_SYSTEM, user


# ─────────────────────────────────────────────────────────────────────
# Pebble's full prompt — reuse the engine's build_prompt
# ─────────────────────────────────────────────────────────────────────

def build_pebble_prompt(brief: dict) -> tuple[str, str]:
    """Return (system, user) using Pebble's full prompt assembly."""
    import pebble_engine
    # Pebble's user prompt is built by build_prompt(); system comes from
    # pebble.server.build inline. Reproduce a minimal system here that
    # mirrors what run_build sends.
    user = pebble_engine.build_prompt(brief, ds_text="", notes=[])
    system = (
        "You are a senior web engineer executing a precise build specification. "
        "Read the brief, read every skill file, build exactly what is specified. "
        "Output ONLY <pebble-file> blocks. First character is `<`."
    )
    return system, user


# ─────────────────────────────────────────────────────────────────────
# Output analysis
# ─────────────────────────────────────────────────────────────────────

@dataclass
class PromptRun:
    label: str
    system_chars: int = 0
    user_chars: int = 0
    response_chars: int = 0
    elapsed_seconds: float = 0.0
    files_emitted: int = 0
    has_real_image_urls: bool = False
    has_custom_css_tokens: bool = False
    has_tailwind_config_extension: bool = False
    has_gsap_wired: bool = False
    has_resend_server_action: bool = False
    has_schema_jsonld: bool = False
    file_list: list[str] = field(default_factory=list)
    error: Optional[str] = None

    def as_markdown_row(self) -> str:
        return (
            f"| {self.label} | "
            f"{self.system_chars + self.user_chars:,} | "
            f"{self.response_chars:,} | "
            f"{self.elapsed_seconds:.1f}s | "
            f"{self.files_emitted} | "
            f"{'Y' if self.has_real_image_urls else 'N'} | "
            f"{'Y' if self.has_custom_css_tokens else 'N'} | "
            f"{'Y' if self.has_tailwind_config_extension else 'N'} | "
            f"{'Y' if self.has_gsap_wired else 'N'} | "
            f"{'Y' if self.has_resend_server_action else 'N'} | "
            f"{'Y' if self.has_schema_jsonld else 'N'} |"
        )


_IMG_RE = re.compile(r"https?://(images\.unsplash\.com|images\.pexels\.com|[^\s\"']+\.pexels\.com)/")
_CSS_TOKEN_RE = re.compile(r":root\s*\{[^}]*--[a-z\-]+\s*:", re.IGNORECASE)
_TAILWIND_EXT_RE = re.compile(r"theme\s*:\s*\{[^}]*extend", re.IGNORECASE | re.DOTALL)
_GSAP_RE = re.compile(r"(import\s+\{\s*gsap\s*\}|gsap\.registerPlugin|ScrollTrigger)")
_RESEND_RE = re.compile(r"resend\.emails\.send|Resend\s*\(\s*process\.env\.RESEND_API_KEY")
_JSONLD_RE = re.compile(r'application/ld\+json|"@context"\s*:\s*"https://schema\.org"')


def analyze_response(label: str, response: str, system_chars: int, user_chars: int,
                     elapsed: float) -> PromptRun:
    run = PromptRun(label=label)
    run.system_chars = system_chars
    run.user_chars = user_chars
    run.response_chars = len(response)
    run.elapsed_seconds = elapsed
    # File count
    file_paths = re.findall(r'<pebble-file\s+path="([^"]+)"', response)
    run.file_list = file_paths
    run.files_emitted = len(file_paths)
    # Pattern flags
    run.has_real_image_urls = bool(_IMG_RE.search(response))
    run.has_custom_css_tokens = bool(_CSS_TOKEN_RE.search(response))
    run.has_tailwind_config_extension = bool(_TAILWIND_EXT_RE.search(response))
    run.has_gsap_wired = bool(_GSAP_RE.search(response))
    run.has_resend_server_action = bool(_RESEND_RE.search(response))
    run.has_schema_jsonld = bool(_JSONLD_RE.search(response))
    return run


# ─────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────

def run_one(label: str, system: str, user: str, client, dry_run: bool, max_tokens: int = 60000) -> PromptRun:
    if dry_run:
        log.info("[compare] DRY RUN — %s prompt only, no LLM call", label)
        return PromptRun(
            label=label, system_chars=len(system), user_chars=len(user),
            response_chars=0, elapsed_seconds=0.0, files_emitted=0,
        )
    log.info("[compare] %s: %d system chars + %d user chars → calling LLM…",
             label, len(system), len(user))
    t0 = time.time()
    try:
        response = client.generate(system=system, user=user, max_tokens=max_tokens)
    except LLMError as e:
        elapsed = time.time() - t0
        run = PromptRun(label=label)
        run.system_chars = len(system)
        run.user_chars = len(user)
        run.elapsed_seconds = elapsed
        run.error = str(e)
        return run
    elapsed = time.time() - t0
    return analyze_response(label, response, len(system), len(user), elapsed)


def render_report(brief: dict, runs: list[PromptRun]) -> str:
    lines = [
        f"# Prompt comparison report — {brief.get('business_name', 'untitled')}",
        f"_Generated {time.strftime('%Y-%m-%d %H:%M:%S')}_",
        "",
        "## Brief",
        "```json",
        json.dumps(brief, indent=2),
        "```",
        "",
        "## Side-by-side",
        "",
        "| Path | Prompt chars | Response chars | Time | Files | Real img URLs | CSS tokens | Tailwind config | GSAP wired | Resend Server Action | schema.org |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in runs:
        lines.append(r.as_markdown_row())
    lines.append("")
    for r in runs:
        lines.append(f"### {r.label} — file list ({r.files_emitted})")
        if r.error:
            lines.append(f"**ERROR:** {r.error}")
        for f in r.file_list:
            lines.append(f"- `{f}`")
        lines.append("")
    return "\n".join(lines)


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m pebble.compare_prompts",
        description="Compare Pebble's full prompt vs a playground-style mini prompt.",
    )
    parser.add_argument("brief", type=Path, help="Path to brief.json")
    parser.add_argument("--diet-only", action="store_true",
                        help="Run only the Pebble path (skip playground)")
    parser.add_argument("--playground-only", action="store_true",
                        help="Run only the playground path (skip Pebble)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build prompts but don't call LLM (cost-free)")
    parser.add_argument("--max-tokens", type=int, default=60000)
    args = parser.parse_args(argv)

    import pebble_engine  # triggers .env loading
    _ = pebble_engine

    if not args.brief.exists():
        print(f"brief not found: {args.brief}", file=sys.stderr)
        return 2
    brief = json.loads(args.brief.read_text(encoding="utf-8"))

    # Resolve DNA + Layout for the playground prompt
    dna = None
    layout = None
    try:
        from style_dna import pick_dna_for_brief
        dna = pick_dna_for_brief(brief)
    except Exception:
        pass
    try:
        from pebble.layout_dna import pick_layout_for_brief
        layout = pick_layout_for_brief(brief, creative_direction=brief.get("creative_direction", ""))
    except Exception:
        pass

    runs: list[PromptRun] = []
    client = None
    if not args.dry_run:
        client, reason = get_llm_client()
        if not client:
            print(f"LLM not configured: {reason}", file=sys.stderr)
            return 3

    if not args.diet_only:
        system, user = build_playground_prompt(brief, dna, layout)
        runs.append(run_one("Playground (mini)", system, user, client, args.dry_run, args.max_tokens))

    if not args.playground_only:
        system, user = build_pebble_prompt(brief)
        runs.append(run_one("Pebble (full)", system, user, client, args.dry_run, args.max_tokens))

    report = render_report(brief, runs)
    print(report)

    # Write to disk under output/<slug>/
    slug = brief.get("_slug") or brief.get("slug") or args.brief.parent.name
    out_dir = Path("output") / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "compare_prompts_report.md").write_text(report, encoding="utf-8")
    log.info("[compare] report written to %s", out_dir / "compare_prompts_report.md")

    return 0


if __name__ == "__main__":
    sys.exit(cli())
