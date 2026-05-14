"""
Pebble Engine — smoke tests.

These are the safety net for refactors. They lock down the contracts:
- env loading
- industries.json shape + lookup
- DNA picking + block rendering
- prompt building end-to-end (without calling any LLM)
- file parsing from a fake LLM response
- engine module imports cleanly

Run:
    pytest tests/ -v
"""
from __future__ import annotations
import json
import os
from pathlib import Path

import pebble_engine
import style_dna


PROJECT_ROOT = Path(__file__).parent.parent.resolve()


# ---------------------------------------------------------------------------
# 1. Env loader — empty-string env vars get overridden by .env values
# ---------------------------------------------------------------------------

def test_env_loader_overrides_empty_strings(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_PEBBLE_KEY=real-value\n", encoding="utf-8")
    monkeypatch.setenv("TEST_PEBBLE_KEY", "")  # simulate stale empty value
    pebble_engine.load_env_file(env_file)
    assert os.environ["TEST_PEBBLE_KEY"] == "real-value"


def test_env_loader_does_not_touch_set_values(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_PEBBLE_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("TEST_PEBBLE_KEY", "already-set")
    pebble_engine.load_env_file(env_file)
    assert os.environ["TEST_PEBBLE_KEY"] == "already-set"


# ---------------------------------------------------------------------------
# 2. industries.json — schema + lookup
# ---------------------------------------------------------------------------

def test_industries_json_schema():
    """Every entry has the fields the prompt template expects."""
    data = json.loads(PROJECT_ROOT.joinpath("industries.json").read_text(encoding="utf-8"))
    assert len(data) >= 50, f"expected 50+ industries, got {len(data)}"
    required = ["emotion", "visual_style", "hero_type", "colors", "tone",
                "key_sections", "trust_signals", "avoid"]
    for key, entry in data.items():
        for field in required:
            assert field in entry, f"industries.json[{key!r}] missing {field!r}"
        assert "primary" in entry["colors"], f"{key} colors missing primary"
        assert entry["hero_type"] in {"video", "image"}, f"{key} hero_type invalid"


def test_industry_intel_lookup_resolves_plumbing():
    """Fuzzy lookup finds plumbing whether the user types 'plumbing' or 'plumber'."""
    key, entry = pebble_engine.resolve_industry_intel("plumbing")
    assert key == "plumbing"
    assert entry is not None
    assert "colors" in entry


# ---------------------------------------------------------------------------
# 3. Style DNA — picker + block rendering
# ---------------------------------------------------------------------------

def test_dna_cards_have_complete_schema():
    """Every DNA card has the fields build_dna_block reads from it."""
    required = ["id", "label", "feel", "display_font", "body_font", "mono_font",
                "palette_posture", "hero_structure", "motion_intensity",
                "motion_rules", "layout_grid", "image_treatment",
                "signature_moves", "forbidden"]
    for card in style_dna.DNA_CARDS:
        for field in required:
            assert field in card, f"DNA {card.get('id','?')} missing {field!r}"
        assert len(card["signature_moves"]) >= 3, \
            f"DNA {card['id']} needs >=3 signature moves"


def test_dna_picker_is_random_but_bounded():
    """100 calls produce more than one distinct DNA (sanity check on randomness)."""
    rolls = {style_dna.pick_random_dna()["id"] for _ in range(100)}
    assert len(rolls) >= 5, "DNA picker is suspiciously deterministic"


def test_dna_block_contains_override_framing():
    """The injected block must contain language strong enough to override the rest of the prompt."""
    dna = style_dna.pick_random_dna(seed=0)
    block = style_dna.build_dna_block(dna)
    assert "OVERRIDE" in block.upper()
    assert dna["display_font"] in block
    assert dna["body_font"] in block
    assert "signature_moves" not in block  # we render the LIST, not the key name


# ---------------------------------------------------------------------------
# 4. Prompt builder — end-to-end, no network calls
# ---------------------------------------------------------------------------

def test_build_prompt_renders_with_minimal_inputs():
    """A minimal answers dict produces a non-empty prompt with all required blocks."""
    answers = {
        "business_name": "Test Co",
        "business_type": "plumbing",
        "industry": "plumbing",
        "location": "Brooklyn, NY",
        "services_offered": "drain cleaning",
        "phone": "",
        "email": "",
        "address": "",
        "brand_position": "professional",
        "brand_tone": "professional_formal",
        "output_mode": "full",
        "visitor_action": "general",
    }
    _, intel = pebble_engine.resolve_industry_intel("plumbing")
    prompt = pebble_engine.build_prompt(
        answers, ds_text="", notes=[], research_text="",
        images={"hero": "https://images.pexels.com/example.jpg"},
        industry_intel=intel,
    )
    assert len(prompt) > 5000, "prompt suspiciously short"
    assert "Test Co" in prompt
    assert "plumbing" in prompt
    assert "INDUSTRY INTELLIGENCE" in prompt


def test_build_prompt_with_dna_injects_override_block():
    """When a DNA is supplied, the prompt MUST start with the DNA override block."""
    answers = {
        "business_name": "Test Co",
        "business_type": "plumbing",
        "industry": "plumbing",
        "output_mode": "full",
    }
    _, intel = pebble_engine.resolve_industry_intel("plumbing")
    dna = style_dna.pick_random_dna(seed=42)
    prompt = pebble_engine.build_prompt(
        answers, ds_text="", notes=[], industry_intel=intel, design_dna=dna,
    )
    assert prompt.startswith("# =====")
    assert "DESIGN DNA" in prompt[:500]
    assert dna["display_font"] in prompt


# ---------------------------------------------------------------------------
# 5. Slug + utility helpers
# ---------------------------------------------------------------------------

def test_slugify_strips_unsafe_chars():
    assert pebble_engine._slugify("Iron Cesspool!") == "iron-cesspool"
    assert pebble_engine._slugify("Squito Pest Control") == "squito-pest-control"
    assert pebble_engine._slugify("") == "untitled"
    assert pebble_engine._slugify("a/b") == "ab"


# ---------------------------------------------------------------------------
# 6. LLM file parser — extracts <pebble-file> blocks from a fake response
# ---------------------------------------------------------------------------

def test_parse_files_extracts_pebble_blocks():
    fake_llm_output = (
        '<pebble-file path="package.json">\n{"name": "test"}\n</pebble-file>\n'
        '<pebble-file path="app/page.tsx">\nexport default function Page() { return null }\n</pebble-file>\n'
    )
    files = pebble_engine.parse_files(fake_llm_output)
    assert len(files) == 2
    paths = [f[0] for f in files]
    assert "package.json" in paths
    assert "app/page.tsx" in paths


def test_parse_files_returns_empty_on_garbage():
    assert pebble_engine.parse_files("just some prose with no tags") == []


def test_parse_files_tolerates_typo_in_closing_tag():
    """Gemini has been observed to typo `</peble-file>`. A strict paired
    regex would silently merge the next file's body into the typo'd one's;
    the tolerant boundary-based parser keeps each file separate."""
    fake = (
        '<pebble-file path="content/sections.ts">\n'
        'export const SECTIONS = ["a"];\n'
        '</peble-file>\n'                 # ← typo, missing 'b'
        '<pebble-file path="content/services.ts">\n'
        'export const services = [];\n'
        '</pebble-file>\n'
    )
    files = pebble_engine.parse_files(fake)
    paths = [f[0] for f in files]
    assert paths == ["content/sections.ts", "content/services.ts"]
    # services.ts content survived (would be lost under the strict regex)
    services_body = dict(files)["content/services.ts"]
    assert "export const services" in services_body
    # sections.ts shouldn't have swallowed the next file
    sections_body = dict(files)["content/sections.ts"]
    assert "services" not in sections_body


def test_parse_files_ends_block_at_pebble_delete_tag():
    """A <pebble-delete/> tag right after a <pebble-file> block must NOT
    end up inside the file's body — the boundary detector treats it as the
    end-of-file marker. This was a real bug after the delete tag was first
    introduced."""
    fake = (
        '<pebble-file path="app/page.tsx">\n'
        'content line\n'
        '</pebble-file>\n'
        '<pebble-delete path="src/old.tsx"/>\n'
    )
    files = pebble_engine.parse_files(fake)
    assert files == [("app/page.tsx", "content line")]
    deletes = pebble_engine.parse_deletions(fake)
    assert deletes == ["src/old.tsx"]


def test_parse_deletions_handles_both_self_close_forms():
    fake = (
        '<pebble-delete path="a.tsx"/>\n'
        '<pebble-delete path="b.tsx"></pebble-delete>\n'
    )
    assert pebble_engine.parse_deletions(fake) == ["a.tsx", "b.tsx"]


# ---------------------------------------------------------------------------
# 7. Module import sanity — no missing deps, no syntax errors
# ---------------------------------------------------------------------------

def test_engine_module_imports_cleanly():
    """If pebble_engine fails to import, every test above would also fail —
    but having this assertion makes import errors obvious in test output."""
    assert hasattr(pebble_engine, "build_prompt")
    assert hasattr(pebble_engine, "resolve_industry_intel")
    assert hasattr(pebble_engine, "PebbleHandler")
    assert hasattr(pebble_engine, "serve")


def test_style_dna_module_imports_cleanly():
    assert hasattr(style_dna, "DNA_CARDS")
    assert hasattr(style_dna, "pick_random_dna")
    assert hasattr(style_dna, "build_dna_block")
    assert len(style_dna.DNA_CARDS) >= 10


# ---------------------------------------------------------------------------
# 8. Request validation — server-side defense for /api/build /api/generate
# ---------------------------------------------------------------------------

def test_validate_accepts_minimal_valid_payload():
    payload = {"business_name": "Acme", "business_type": "hvac"}
    cleaned, err = pebble_engine.validate_build_payload(payload)
    assert err is None
    assert cleaned["business_name"] == "Acme"


def test_validate_rejects_missing_business_name():
    cleaned, err = pebble_engine.validate_build_payload({"business_type": "hvac"})
    assert cleaned is None
    assert err["field"] == "business_name"


def test_validate_rejects_blank_business_name():
    cleaned, err = pebble_engine.validate_build_payload({"business_name": "   ", "business_type": "hvac"})
    assert cleaned is None
    assert err["field"] == "business_name"


def test_validate_accepts_industry_in_place_of_business_type():
    cleaned, err = pebble_engine.validate_build_payload({"business_name": "Acme", "industry": "hvac"})
    assert err is None
    assert cleaned is not None


def test_validate_rejects_missing_business_type_and_industry():
    cleaned, err = pebble_engine.validate_build_payload({"business_name": "Acme"})
    assert cleaned is None
    assert err["field"] == "business_type"


def test_validate_rejects_oversized_field():
    cleaned, err = pebble_engine.validate_build_payload({
        "business_name": "Acme",
        "business_type": "hvac",
        "extra_context": "x" * (pebble_engine._STRING_LIMITS["extra_context"] + 1),
    })
    assert cleaned is None
    assert err["field"] == "extra_context"


def test_validate_rejects_non_object_root():
    cleaned, err = pebble_engine.validate_build_payload(["not", "an", "object"])
    assert cleaned is None
    assert err["field"] == "_root"


def test_validate_rejects_oversized_image_attachments():
    big = "A" * (pebble_engine.MAX_ATTACHMENT_BYTES + 1)
    cleaned, err = pebble_engine.validate_build_payload({
        "business_name": "Acme",
        "business_type": "hvac",
        "design_reference_images": [{"media_type": "image/png", "data": big}],
    })
    assert cleaned is None
    assert err["field"] == "design_reference_images"


def test_validate_rejects_too_many_image_attachments():
    img = {"media_type": "image/png", "data": "AAAA"}
    cleaned, err = pebble_engine.validate_build_payload({
        "business_name": "Acme",
        "business_type": "hvac",
        "design_reference_images": [img] * (pebble_engine.MAX_ATTACHMENT_COUNT + 1),
    })
    assert cleaned is None
    assert err["field"] == "design_reference_images"


def test_validate_rejects_bad_image_media_type():
    cleaned, err = pebble_engine.validate_build_payload({
        "business_name": "Acme",
        "business_type": "hvac",
        "design_reference_images": [{"media_type": "application/pdf", "data": "AAAA"}],
    })
    assert cleaned is None
    assert err["field"] == "design_reference_images"


def test_validate_accepts_well_formed_full_payload():
    cleaned, err = pebble_engine.validate_build_payload({
        "business_name": "Acme Plumbing",
        "business_type": "plumbing",
        "industry": "plumbing",
        "location": "Brooklyn, NY",
        "services_offered": "drain cleaning, water heaters",
        "phone": "(555) 555-0100",
        "email": "hello@acme.com",
        "address": "123 Main St",
        "brand_position": "premium",
        "brand_tone": "warm_professional",
        "site_functions": ["contact_form", "service_pages"],
        "output_mode": "full",
        "design_reference_images": [{"media_type": "image/png", "data": "AAAA"}],
    })
    assert err is None
    assert cleaned is not None
    assert cleaned["business_name"] == "Acme Plumbing"


def test_validate_coerces_numeric_scalar_to_string():
    """The quiz sometimes posts numeric phone or zip values — accept and stringify."""
    cleaned, err = pebble_engine.validate_build_payload({
        "business_name": "Acme",
        "business_type": "hvac",
        "phone": 5555550100,
    })
    assert err is None
    assert cleaned["phone"] == "5555550100"


# ---------------------------------------------------------------------------
# 9. Server routes — verify the extracted pebble.server.build module wires up
# ---------------------------------------------------------------------------

def test_build_route_module_imports_and_hoists_engine_symbols():
    """Smoke check on the route extraction: importing pebble.server.build
    must succeed, run_build must exist, and the engine-symbol hoist inside
    it must find every name it references (typos here surface as
    ``AttributeError`` the moment a build is invoked in production)."""
    from pebble.server import build as build_route
    assert hasattr(build_route, "run_build")

    # The hoist sources symbols off the live pebble_engine module. Every
    # name listed below must exist there or the extracted handler will
    # break the first request.
    expected = [
        "MAX_REQUEST_BYTES", "OUTPUT_DIR", "_DNA_OK",
        "FILE_FORMAT_INSTRUCTION", "LITE_FILE_FORMAT_INSTRUCTION",
        "_slugify", "validate_build_payload", "build_ui_query",
        "build_prompt", "audit_design_system", "get_pexels_images",
        "get_placeholder_images", "get_pexels_hero_video",
        "localize_pexels_video", "figma_file_summary", "parse_files",
        "apply_imagen_to_site", "post_build_run_dev_server",
        "post_build_screenshots", "generate_design_system", "pick_random_dna",
    ]
    for name in expected:
        assert hasattr(pebble_engine, name), f"pebble_engine missing required symbol: {name}"


def test_build_route_engine_resolver_finds_module():
    """``pebble.server.build._engine`` must return the pebble_engine module
    in test contexts (where it's loaded under its real name)."""
    from pebble.server.build import _engine
    assert _engine() is pebble_engine


def test_handler_delegates_to_extracted_run_build():
    """PebbleHandler._handle_build must be the thin delegate, not a 300-line method."""
    import inspect
    src = inspect.getsource(pebble_engine.PebbleHandler._handle_build)
    assert "run_build" in src
    assert "pebble.server.build" in src
    # The delegate should be very short — if this grows, the body crept
    # back into the handler.
    assert src.count("\n") < 12
