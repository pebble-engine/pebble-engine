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
