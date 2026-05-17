"""Tests for the DNA-themed block library.

Three layers:

1. **Unit tests** — palette extraction, theme-token derivation, each
   block renderer's output shape, JSX escaping.
2. **Insertion tests** — surgically write a fake site dir, splice
   ``app/page.tsx``, verify the import + render slots land in the right
   places + collisions resolve.
3. **HTTP e2e** — GET /api/blocks and POST /api/projects/<slug>/blocks/insert
   through the real engine. Covers auth gating, snapshotting, and the
   ``billable: false`` contract.

The HTTP fixture mirrors ``tests/test_forms.py``.
"""
from __future__ import annotations

import json
import socket
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import pebble_engine
import pebble.history as history_mod
from pebble.blocks import (
    BLOCK_REGISTRY,
    derive_theme_from_dna,
    extract_palette_hexes,
    insert_block_into_site,
    list_blocks,
    render_block,
)
from pebble.blocks.base import ThemeTokens, _hex_brightness
from pebble.blocks.insert import _splice_page_tsx, _unique_component_name
from pebble.blocks.library import _jsx_safe, _jsx_string, _kicker
from style_dna import DNA_CARDS


# ---- Palette + theme tokens ---------------------------------------------

def test_extract_palette_normalizes_hex_and_dedupes():
    s = "warm off-white #FAF8F3 page, ink #0e0e10 type, accent #6B2B2B and again #6b2b2b"
    out = extract_palette_hexes(s)
    assert out == ["#faf8f3", "#0e0e10", "#6b2b2b"]


def test_extract_palette_handles_short_hex():
    """`#abc` should normalize to `#aabbcc`."""
    out = extract_palette_hexes("hero color #abc on dark")
    assert out == ["#aabbcc"]


def test_extract_palette_returns_empty_on_empty_input():
    assert extract_palette_hexes("") == []
    assert extract_palette_hexes("no colors here") == []


def test_hex_brightness_bounds():
    assert _hex_brightness("#000000") < 0.01
    assert _hex_brightness("#ffffff") > 0.99
    assert 0.4 < _hex_brightness("#888888") < 0.6


def test_theme_falls_back_when_no_dna():
    tokens = derive_theme_from_dna(None)
    assert tokens.dna_id == ""
    assert tokens.bg_hex == "#fafaf7"
    assert tokens.ink_hex == "#1a1a1a"
    assert "Inter" in tokens.body_stack()


@pytest.mark.parametrize("card", DNA_CARDS)
def test_theme_derives_clean_tokens_for_every_dna_card(card):
    """Every DNA card in style_dna.py should produce a usable ThemeTokens
    — none should crash, and the palette must produce at least background
    + ink hex values."""
    tokens = derive_theme_from_dna(card)
    assert tokens.dna_id == card["id"]
    assert tokens.dna_label == card["label"]
    assert tokens.bg_hex.startswith("#")
    assert tokens.ink_hex.startswith("#")
    assert tokens.accent_hex.startswith("#")
    assert tokens.display_font == card["display_font"]
    assert tokens.body_font == card["body_font"]
    assert "Inter" in tokens.body_stack() or "monospace" in tokens.body_stack() or "serif" in tokens.body_stack()


def test_theme_detects_dark_canvas():
    """DNAs with near-black palette_posture should produce ``is_dark=True``."""
    black_card = next(c for c in DNA_CARDS if c["id"] == "terminal_operator")
    tokens = derive_theme_from_dna(black_card)
    assert tokens.is_dark is True


def test_theme_detects_light_canvas():
    """Light-background DNAs report ``is_dark=False``."""
    light_card = next(c for c in DNA_CARDS if c["id"] == "swiss_magazine")
    tokens = derive_theme_from_dna(light_card)
    assert tokens.is_dark is False


# ---- Kicker voice --------------------------------------------------------

def test_kicker_terminal_style():
    tokens = derive_theme_from_dna(next(c for c in DNA_CARDS if c["id"] == "terminal_operator"))
    assert ">" in _kicker(tokens, "02", "Testimonials") or "SECTION" in _kicker(tokens, "02", "Testimonials")


def test_kicker_default_is_mono_uppercase():
    """Any DNA without a custom kicker style falls back to FIG-style mono."""
    tokens = ThemeTokens(
        dna_id="unknown_card", dna_label="X",
        display_font="Inter", body_font="Inter", mono_font="IBM Plex Mono",
        bg_hex="#fff", ink_hex="#000", accent_hex="#205661", secondary_hex="",
        is_dark=False, motion_intensity="subtle",
        radius_class="rounded-md", kicker_label_style="mono-uppercase",
    )
    out = _kicker(tokens, "02", "Testimonials")
    assert "FIG. 02" in out and "TESTIMONIALS" in out


# ---- Renderer shape ------------------------------------------------------

@pytest.mark.parametrize("block_id", list(BLOCK_REGISTRY.keys()))
def test_every_block_renders_against_every_dna(block_id):
    """Cross-product smoke test: every (block, DNA) pair must produce
    valid-looking JSX that exports the expected component and doesn't
    leak template tokens."""
    for card in DNA_CARDS:
        tokens = derive_theme_from_dna(card)
        out = render_block(block_id, tokens, {"business_name": "Wildflower Bakery"})
        spec = BLOCK_REGISTRY[block_id]
        assert f"export function {spec.component_name}(" in out, \
            f"missing export for {block_id} on DNA {card['id']}"
        assert f'data-pebble-block="{block_id}"' in out, \
            f"missing data-pebble-block on {block_id} for DNA {card['id']}"
        # No leftover template tokens
        assert "__BG__" not in out
        assert "__INK__" not in out
        assert "__ACCENT__" not in out
        assert "__DISPLAY_STACK_JSX__" not in out
        assert "__KICKER__" not in out


def test_cta_uses_business_name_in_button():
    tokens = derive_theme_from_dna(DNA_CARDS[0])
    out = render_block("cta_banner", tokens, {"business_name": "Wildflower Bakery"})
    assert "Wildflower Bakery" in out


def test_cta_business_name_escapes_jsx_braces():
    """A malicious business_name with `{` or `<` must NOT inject JSX."""
    tokens = derive_theme_from_dna(DNA_CARDS[0])
    out = render_block("cta_banner", tokens, {"business_name": "{evil} <script>"})
    # Raw braces must not survive into the JSX body — they'd be parsed as
    # JS expressions and break the file. Confirm via the HTML entity.
    assert "{evil}" not in out
    assert "<script>" not in out
    # Either the escape entity OR the safe replacement should land.
    assert "&#123;" in out or "&lt;" in out or "evil" in out


# ---- JSX escape helpers --------------------------------------------------

def test_jsx_string_double_quoted():
    assert _jsx_string("'Inter', sans-serif") == "\"'Inter', sans-serif\""


def test_jsx_string_strips_newlines_and_backslashes():
    """Defense against backslash-injection in a font name."""
    val = "Bad\\Font\n', 'extra"
    out = _jsx_string(val)
    assert "\n" not in out
    assert "\\\\" not in out  # we strip backslashes entirely


def test_jsx_safe_escapes_brace_and_angle():
    assert _jsx_safe("hello {world}") == "hello &#123;world&#125;"
    assert _jsx_safe("<img src=x>") == "&lt;img src=x&gt;"


def test_jsx_safe_strips_control_chars():
    assert _jsx_safe("hello\x00world") == "helloworld"


# ---- Registry + listing --------------------------------------------------

def test_list_blocks_returns_each_registered_block():
    out = list_blocks()
    ids = {b["id"] for b in out}
    assert ids == set(BLOCK_REGISTRY.keys())


def test_listing_omits_internal_fields():
    """to_listing() must NOT expose render callable or component_name."""
    out = list_blocks()
    assert all("render" not in b for b in out)
    assert all("component_name" not in b for b in out)


def test_listing_has_categories():
    cats = {b["category"] for b in list_blocks()}
    # At least these three exist among the seed blocks
    assert "social-proof" in cats
    assert "monetization" in cats
    assert "explainer" in cats


# ---- Insertion (file system) --------------------------------------------

def _make_fake_site(tmp_path: Path, with_footer: bool = True) -> Path:
    """Create a Next.js-shaped site dir minimal enough to test splicing."""
    site = tmp_path / "site"
    (site / "app").mkdir(parents=True)
    (site / "components" / "sections").mkdir(parents=True)
    (site / "components" / "layout").mkdir(parents=True)

    footer_render = "        <Footer />\n" if with_footer else ""
    page_tsx = (
        "import { Hero } from '@/components/sections/Hero';\n"
        + ("import { Footer } from '@/components/layout/Footer';\n" if with_footer else "")
        + "\n"
        + "export default function Page() {\n"
        + "  return (\n"
        + "    <>\n"
        + "      <main>\n"
        + "        <Hero />\n"
        + footer_render
        + "      </main>\n"
        + "    </>\n"
        + "  );\n"
        + "}\n"
    )
    (site / "app" / "page.tsx").write_text(page_tsx, encoding="utf-8")
    return site


def test_insert_writes_component_file(tmp_path):
    site = _make_fake_site(tmp_path)
    tokens = derive_theme_from_dna(DNA_CARDS[0])
    tsx = render_block("testimonials_trio", tokens, {})
    spec = BLOCK_REGISTRY["testimonials_trio"]
    result = insert_block_into_site(site, "testimonials_trio", spec.component_name, tsx)
    assert result.files_written == ["components/sections/Testimonials.tsx"]
    target = site / "components" / "sections" / "Testimonials.tsx"
    assert target.exists()
    assert "export function Testimonials(" in target.read_text(encoding="utf-8")


def test_insert_adds_import_and_renders_before_footer(tmp_path):
    site = _make_fake_site(tmp_path, with_footer=True)
    tokens = derive_theme_from_dna(DNA_CARDS[0])
    tsx = render_block("faq_accordion", tokens, {})
    spec = BLOCK_REGISTRY["faq_accordion"]
    result = insert_block_into_site(site, "faq_accordion", spec.component_name, tsx)

    page_src = (site / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "import { FAQ } from '@/components/sections/FAQ';" in page_src
    # Render appears in the JSX
    assert "<FAQ />" in page_src
    # Render lands BEFORE the Footer
    idx_faq = page_src.find("<FAQ />")
    idx_footer = page_src.find("<Footer />")
    assert idx_faq != -1 and idx_footer != -1
    assert idx_faq < idx_footer
    assert result.position == "before-footer"


def test_insert_falls_back_to_main_close_when_no_footer(tmp_path):
    site = _make_fake_site(tmp_path, with_footer=False)
    tokens = derive_theme_from_dna(DNA_CARDS[0])
    tsx = render_block("cta_banner", tokens, {"business_name": "ACME"})
    spec = BLOCK_REGISTRY["cta_banner"]
    result = insert_block_into_site(site, "cta_banner", spec.component_name, tsx)
    page_src = (site / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "<CTABanner />" in page_src
    assert result.position == "before-main-close"
    # Render must precede </main>
    assert page_src.find("<CTABanner />") < page_src.find("</main>")


def test_insert_unique_name_avoids_collision(tmp_path):
    site = _make_fake_site(tmp_path)
    # Pre-create the natural name so the next insert must suffix.
    (site / "components" / "sections" / "Testimonials.tsx").write_text("// pre-existing\n")

    tokens = derive_theme_from_dna(DNA_CARDS[0])
    tsx = render_block("testimonials_trio", tokens, {})
    spec = BLOCK_REGISTRY["testimonials_trio"]
    result = insert_block_into_site(site, "testimonials_trio", spec.component_name, tsx)

    assert result.component_name == "Testimonials2"
    page_src = (site / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "import { Testimonials2 } from '@/components/sections/Testimonials2';" in page_src
    assert "<Testimonials2 />" in page_src

    # The component file must export under the new name AND should still
    # be valid (the rendered template was generated for "Testimonials"
    # — the insert renames the export identifier).
    body = (site / "components" / "sections" / "Testimonials2.tsx").read_text(encoding="utf-8")
    assert "export function Testimonials2(" in body
    # data-pebble-block must remain the block_id, NOT the component name
    assert 'data-pebble-block="testimonials_trio"' in body


def test_insert_raises_when_no_page_tsx(tmp_path):
    site = tmp_path / "broken-site"
    site.mkdir()
    with pytest.raises(FileNotFoundError):
        insert_block_into_site(site, "testimonials_trio", "Testimonials", "// content\n")


def test_unique_component_name_skips_imported_symbol(tmp_path):
    """If page.tsx already imports a symbol called X, the next insert
    can't reuse that name — even if the file doesn't exist."""
    site = _make_fake_site(tmp_path)
    page = site / "app" / "page.tsx"
    page.write_text(
        page.read_text(encoding="utf-8")
        + "\n// stale ref to Testimonials elsewhere\n",
        encoding="utf-8",
    )
    name = _unique_component_name(site, "Testimonials")
    assert name == "Testimonials2"


def test_splice_page_tsx_handles_self_closing_footer():
    src = (
        "import { Hero } from '@/components/sections/Hero';\n"
        "import { Footer } from '@/components/layout/Footer';\n"
        "export default function Page() {\n"
        "  return (\n"
        "    <main>\n"
        "      <Hero />\n"
        "      <Footer />\n"
        "    </main>\n"
        "  );\n"
        "}\n"
    )
    out, pos = _splice_page_tsx(src, "Pricing")
    assert pos == "before-footer"
    assert "import { Pricing } from '@/components/sections/Pricing';" in out
    assert out.find("<Pricing />") < out.find("<Footer />")


def test_splice_skips_footer_inside_jsx_comment():
    """A `{/* <Footer /> */}` placeholder must NOT confuse the splicer.
    The actual Footer below it should be the insertion target."""
    src = (
        "import { Hero } from '@/components/sections/Hero';\n"
        "import { Footer } from '@/components/layout/Footer';\n"
        "export default function Page() {\n"
        "  return (\n"
        "    <main>\n"
        "      <Hero />\n"
        "      {/* TODO swap out <Footer /> later */}\n"
        "      <Footer />\n"
        "    </main>\n"
        "  );\n"
        "}\n"
    )
    out, pos = _splice_page_tsx(src, "Pricing")
    assert pos == "before-footer"
    # The render must land between the comment and the real Footer.
    comment_idx = out.find("TODO swap out")
    pricing_idx = out.find("<Pricing />")
    footer_idx = out.rfind("<Footer />")
    assert comment_idx < pricing_idx < footer_idx, (
        "Pricing must land BETWEEN the comment and the real Footer"
    )


def test_splice_skips_footer_inside_block_comment():
    """C-style `/* <Footer /> */` block comments also shouldn't trip
    the regex. Same defense as JSX comments."""
    src = (
        "import { Footer } from '@/components/layout/Footer';\n"
        "/* note: don't use <Footer /> directly here */\n"
        "export default function Page() {\n"
        "  return (\n"
        "    <main>\n"
        "      <Footer />\n"
        "    </main>\n"
        "  );\n"
        "}\n"
    )
    out, pos = _splice_page_tsx(src, "Pricing")
    assert pos == "before-footer"
    # The Pricing render lands before the REAL Footer (line 6), not
    # before the commented-out one (line 2).
    assert out.find("<Pricing />") > out.find("note: don't use")


def test_splice_skips_footer_inside_string_literal():
    """A string literal like `const x = 'use <Footer />'` shouldn't
    match — strings are scrubbed before regex search."""
    src = (
        "import { Footer } from '@/components/layout/Footer';\n"
        "const help = 'See <Footer /> for examples';\n"
        "export default function Page() {\n"
        "  return (\n"
        "    <main>\n"
        "      <Footer />\n"
        "    </main>\n"
        "  );\n"
        "}\n"
    )
    out, pos = _splice_page_tsx(src, "Pricing")
    assert pos == "before-footer"
    # The string literal stays untouched.
    assert "'See <Footer /> for examples'" in out


def test_splice_skips_footer_inside_conditional_expression():
    """`{showFooter && <Footer />}` — inserting a sibling JSX node before
    the Footer here breaks the parent expression. The splicer must skip
    this match and fall through to </main>."""
    src = (
        "import { Footer } from '@/components/layout/Footer';\n"
        "export default function Page() {\n"
        "  return (\n"
        "    <main>\n"
        "      {showFooter && <Footer />}\n"
        "    </main>\n"
        "  );\n"
        "}\n"
    )
    out, pos = _splice_page_tsx(src, "Pricing")
    # Should fall through to </main> rather than break the conditional.
    assert pos == "before-main-close"
    # The conditional is untouched
    assert "showFooter && <Footer />" in out


def test_insert_cleans_up_orphan_on_splice_failure(tmp_path, monkeypatch):
    """If page.tsx splice raises (e.g. permission denied), the new
    component file must be removed so we don't accumulate orphans."""
    site = _make_fake_site(tmp_path)

    def _boom(*_a, **_kw):
        raise PermissionError("simulated write failure")

    # Patch _splice_page_tsx via the module to force a failure AFTER the
    # component file is written. The cleanup branch should then unlink it.
    import pebble.blocks.insert as insert_mod
    monkeypatch.setattr(insert_mod, "_splice_page_tsx", _boom)

    tokens = derive_theme_from_dna(DNA_CARDS[0])
    tsx = render_block("testimonials_trio", tokens, {})
    spec = BLOCK_REGISTRY["testimonials_trio"]
    with pytest.raises(PermissionError):
        insert_block_into_site(site, "testimonials_trio", spec.component_name, tsx)

    # The orphan file must be gone.
    assert not (site / "components" / "sections" / "Testimonials.tsx").exists()


def test_jsx_safe_escapes_double_quote_for_attribute_context():
    """A business_name containing `"` would otherwise break out of an
    attribute value if a future template does aria-label='__VAL__'."""
    out = _jsx_safe('Acme " onClick={alert(1)} "')
    assert '"' not in out
    assert "&quot;" in out
    # The brace-escape catches the JS expression too.
    assert "{alert" not in out


def test_jsx_safe_escapes_ampersand_first_to_avoid_double_encode():
    """`&` must be escaped before `<` and `{` so we don't end up with
    `&amp;lt;` from a literal `<` in input (defensive vs. ordering bugs)."""
    out = _jsx_safe("Sue's & Co")
    assert "&amp;" in out
    # The apostrophe also gets escaped for attribute safety.
    assert "&#39;" in out


# ---- HTTP fixture --------------------------------------------------------

def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def engine_server(tmp_path, monkeypatch):
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(pebble_engine, "OUTPUT_DIR", out)
    monkeypatch.setattr(history_mod, "OUTPUT_DIR", out)
    port = _find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), pebble_engine.PebbleHandler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.1)
    try:
        yield {"base": f"http://127.0.0.1:{port}", "output": out}
    finally:
        server.shutdown()
        server.server_close()


def _request(method: str, base: str, path: str, body=None, headers=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    hdrs = {"Content-Type": "application/json"} if data else {}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(f"{base}{path}", data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(text)
            except Exception:
                return resp.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(text)
        except Exception:
            return e.code, text


def _signup(base: str, email: str, password: str) -> tuple[str, str]:
    """Returns (cookie_header, user_id)."""
    data = json.dumps({"email": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/auth/signup",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        sc = resp.headers.get("Set-Cookie", "")
        body = json.loads(resp.read().decode("utf-8"))
    cookie = sc.split(";", 1)[0].strip() if sc else ""
    return cookie, body["user"]["id"]


def _seed_project(output: Path, slug: str, owner_id: str | None = None, dna_id: str = "swiss_magazine"):
    project = output / slug
    project.mkdir()
    site = project / "site"
    (site / "app").mkdir(parents=True)
    (site / "components" / "sections").mkdir(parents=True)
    (site / "components" / "layout").mkdir(parents=True)
    (site / "app" / "page.tsx").write_text(
        "import { Hero } from '@/components/sections/Hero';\n"
        "import { Footer } from '@/components/layout/Footer';\n"
        "export default function Page() {\n"
        "  return (\n"
        "    <main>\n"
        "      <Hero />\n"
        "      <Footer />\n"
        "    </main>\n"
        "  );\n"
        "}\n",
        encoding="utf-8",
    )
    brief = {"business_name": slug, "_design_dna": dna_id}
    if owner_id:
        brief["_user_id"] = owner_id
    (project / "brief.json").write_text(json.dumps(brief), encoding="utf-8")
    return project


# ---- HTTP tests ----------------------------------------------------------

def test_list_blocks_endpoint_returns_catalog(engine_server):
    status, body = _request("GET", engine_server["base"], "/api/blocks")
    assert status == 200
    assert isinstance(body["blocks"], list)
    assert body["count"] == len(BLOCK_REGISTRY)
    # Each entry must be JSON-clean (no callable left over)
    for entry in body["blocks"]:
        assert set(entry.keys()) >= {"id", "label", "category", "description", "icon"}


def test_insert_block_requires_auth(engine_server):
    """Without a session cookie, /blocks/insert returns 401."""
    out: Path = engine_server["output"]
    _seed_project(out, "test-project", owner_id="user-1")
    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/test-project/blocks/insert",
        body={"block_id": "testimonials_trio"},
    )
    assert status == 401
    assert "sign in" in (body.get("error") or "").lower()


def test_insert_block_404_when_project_missing(engine_server):
    cookie, _ = _signup(engine_server["base"], "blocker@example.com", "blockblock123")
    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/does-not-exist/blocks/insert",
        body={"block_id": "testimonials_trio"},
        headers={"Cookie": cookie},
    )
    assert status == 404


def test_insert_block_403_when_wrong_owner(engine_server):
    out: Path = engine_server["output"]
    _seed_project(out, "owned-by-other", owner_id="some-other-user")
    cookie, _ = _signup(engine_server["base"], "intruder@example.com", "intruder1234")
    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/owned-by-other/blocks/insert",
        body={"block_id": "testimonials_trio"},
        headers={"Cookie": cookie},
    )
    assert status == 403


def test_insert_block_rejects_unknown_block_id(engine_server):
    out: Path = engine_server["output"]
    cookie, uid = _signup(engine_server["base"], "owner1@example.com", "owner1pass123")
    _seed_project(out, "test-project", owner_id=uid)
    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/test-project/blocks/insert",
        body={"block_id": "not_a_real_block"},
        headers={"Cookie": cookie},
    )
    assert status == 400
    assert "available" in body


def test_insert_block_succeeds_and_themes_against_dna(engine_server):
    out: Path = engine_server["output"]
    cookie, uid = _signup(engine_server["base"], "owner2@example.com", "owner2pass123")
    _seed_project(out, "owned-project", owner_id=uid, dna_id="brutalist_editorial")

    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/owned-project/blocks/insert",
        body={"block_id": "pricing_tiers"},
        headers={"Cookie": cookie},
    )
    assert status == 200, body
    assert body["billable"] is False
    assert body["dna_id"] == "brutalist_editorial"
    assert body["component_name"] == "Pricing"
    assert "components/sections/Pricing.tsx" in body["files_written"]
    assert body["snapshot_id"]

    # Verify the file landed and uses Tektur (brutalist DNA's display font).
    site = out / "owned-project" / "site"
    pricing_tsx = (site / "components" / "sections" / "Pricing.tsx").read_text(encoding="utf-8")
    assert "Tektur" in pricing_tsx
    assert "Geist" in pricing_tsx
    # The signature accent (electric orange) from the DNA palette must
    # appear at least once (CTA background) — proves the theme actually
    # propagated.
    assert "#ff5a1f" in pricing_tsx.lower()

    # Page.tsx got the import + render slot
    page = (site / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "import { Pricing } from '@/components/sections/Pricing';" in page
    assert "<Pricing />" in page


def test_insert_block_snapshots_for_undo(engine_server):
    out: Path = engine_server["output"]
    cookie, uid = _signup(engine_server["base"], "owner3@example.com", "owner3pass123")
    _seed_project(out, "snap-project", owner_id=uid)
    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/snap-project/blocks/insert",
        body={"block_id": "faq_accordion"},
        headers={"Cookie": cookie},
    )
    assert status == 200
    snapshot_id = body["snapshot_id"]
    # The snapshot directory must exist under output/<slug>/history/
    history_root = out / "snap-project" / "history" / snapshot_id
    assert history_root.exists()
    # And the reason should mark the block id (used by the dashboard feed).
    # The history layer normalizes underscores to hyphens in the slug suffix.
    assert "insert-block-faq" in snapshot_id


def test_insert_block_with_unclaimed_project_works(engine_server):
    """Projects without _user_id (legacy / pre-auth) stay editable by any
    signed-in user — matches the project-listing semantics."""
    out: Path = engine_server["output"]
    _seed_project(out, "unclaimed-project")  # no owner_id
    cookie, uid = _signup(engine_server["base"], "owner4@example.com", "owner4pass123")
    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/unclaimed-project/blocks/insert",
        body={"block_id": "stats_strip"},
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert body["billable"] is False


def test_insert_block_with_missing_dna_uses_neutral_default(engine_server):
    """A project whose brief has no _design_dna shouldn't crash — the
    neutral fallback tokens should let the block render anyway."""
    out: Path = engine_server["output"]
    cookie, uid = _signup(engine_server["base"], "owner5@example.com", "owner5pass123")
    project = _seed_project(out, "no-dna-project", owner_id=uid)
    # Strip _design_dna out
    brief = json.loads((project / "brief.json").read_text())
    brief.pop("_design_dna", None)
    (project / "brief.json").write_text(json.dumps(brief), encoding="utf-8")

    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/no-dna-project/blocks/insert",
        body={"block_id": "feature_grid"},
        headers={"Cookie": cookie},
    )
    assert status == 200
    assert body["dna_id"] == ""  # neutral fallback


def test_insert_block_rejects_traversal_slug(engine_server):
    """A slug like ``../config`` must 400 at the auth gate — without this
    guard, ``_output_dir() / slug`` would resolve to a neighbor dir."""
    cookie, _ = _signup(engine_server["base"], "rocker@example.com", "rocker1234")
    # Use a slug shape that the URL router will still parse but require_project_owner rejects.
    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/..something/blocks/insert",  # contains ".." segment
        body={"block_id": "testimonials_trio"},
        headers={"Cookie": cookie},
    )
    assert status == 400
    assert "invalid" in (body.get("error") or "").lower()


# ---- HTTP auth coverage for adjacent endpoints --------------------------

def _post_anon(base: str, path: str, body=None):
    return _request("POST", base, path, body=body)


def test_refine_requires_auth(engine_server):
    out: Path = engine_server["output"]
    _seed_project(out, "owned-project")
    status, body = _post_anon(
        engine_server["base"], "/api/refine",
        body={"slug": "owned-project", "refinement_id": "simpler"},
    )
    assert status == 401


def test_visual_edit_requires_auth(engine_server):
    out: Path = engine_server["output"]
    _seed_project(out, "owned-project")
    status, body = _post_anon(
        engine_server["base"], "/api/visual-edit",
        body={"slug": "owned-project", "op": "text", "original_text": "x", "new_text": "y"},
    )
    assert status == 401


def test_rollback_requires_auth(engine_server):
    out: Path = engine_server["output"]
    _seed_project(out, "owned-project")
    status, body = _post_anon(
        engine_server["base"], "/api/rollback",
        body={"slug": "owned-project", "snapshot_id": "20260515T123456-generate"},
    )
    assert status == 401


def test_get_history_requires_auth(engine_server):
    out: Path = engine_server["output"]
    _seed_project(out, "owned-project")
    status, body = _request(
        "GET", engine_server["base"], "/api/projects/owned-project/history",
    )
    assert status == 401


def test_publish_requires_auth(engine_server):
    out: Path = engine_server["output"]
    _seed_project(out, "owned-project")
    status, body = _post_anon(
        engine_server["base"], "/api/publish",
        body={"slug": "owned-project"},
    )
    assert status == 401


# ---- T17: engagement wiring -----------------------------------------------

def _wait_for_engagement_file(log_file: Path, timeout: float = 2.0) -> bool:
    """Engagement.log_event runs AFTER handler._json returns (fire-and-forget
    contract — logging must never block the user response). The HTTP client
    can return slightly before the handler thread finishes the post-response
    log write, so poll briefly for the file."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if log_file.exists():
            return True
        time.sleep(0.05)
    return False


def test_insert_block_logs_engagement_event(engine_server):
    """Block insertion on success fires `block_inserted`. The engagement
    file lives under tmp_path/output/.engagement/<user_id>.jsonl since
    engagement._engagement_dir reads pebble_engine.OUTPUT_DIR which the
    fixture monkey-patches."""
    out: Path = engine_server["output"]
    cookie, uid = _signup(engine_server["base"], "engage1@example.com", "engageblock1234")
    _seed_project(out, "engage-project", owner_id=uid)
    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/engage-project/blocks/insert",
        body={"block_id": "faq_accordion"},
        headers={"Cookie": cookie},
    )
    assert status == 200
    log_file = out / ".engagement" / f"{uid}.jsonl"
    assert _wait_for_engagement_file(log_file), f"engagement file not written: {log_file}"
    rows = [json.loads(l) for l in log_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert any(r["event"] == "block_inserted" for r in rows)


def test_insert_block_engagement_does_not_contain_block_id(engine_server):
    """PRIVACY REGRESSION — block_id (e.g. 'pricing_tiers') must NOT leak
    into engagement logs. The 'block_inserted' event is the only payload."""
    out: Path = engine_server["output"]
    cookie, uid = _signup(engine_server["base"], "engage2@example.com", "engageblock1234")
    _seed_project(out, "engage-pricing", owner_id=uid)
    status, body = _request(
        "POST",
        engine_server["base"],
        "/api/projects/engage-pricing/blocks/insert",
        body={"block_id": "pricing_tiers"},
        headers={"Cookie": cookie},
    )
    assert status == 200
    log_file = out / ".engagement" / f"{uid}.jsonl"
    assert _wait_for_engagement_file(log_file), f"engagement file not written: {log_file}"
    text = log_file.read_text(encoding="utf-8")
    assert "pricing_tiers" not in text
    assert "engage-pricing" not in text   # slug must not leak
    assert "engage2@example.com" not in text  # email must not leak
