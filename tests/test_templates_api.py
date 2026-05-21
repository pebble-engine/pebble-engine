"""Template gallery API tests (Phase 31, 2026-05-20).

Pins the contract for the cheap-fast template-instantiation path that
sits alongside /api/generate. The actual filesystem copying + LLM
content-swap happens inside HTTP handlers; these tests target the pure
helpers (registry loading, validation, prompt construction) so the
suite stays fast and doesn't require booting the engine.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from pebble.server import templates_api


# ------------------------------------------------------------------ #
# Registry loading                                                    #
# ------------------------------------------------------------------ #


def test_load_registry_returns_dict():
    reg = templates_api.load_registry()
    assert isinstance(reg, dict)
    assert "templates" in reg
    assert isinstance(reg["templates"], list)


def test_registry_has_schema_version():
    reg = templates_api.load_registry()
    assert reg.get("schema_version") == "1.0"


def test_registry_contains_service_pro_and_luxe_beauty():
    """The two flagship templates shipped in Phase 31b + 31c."""
    reg = templates_api.load_registry()
    ids = [t.get("id") for t in reg.get("templates", []) if isinstance(t, dict)]
    assert "service_pro" in ids
    assert "luxe_beauty" in ids


def test_registry_entries_have_required_fields():
    reg = templates_api.load_registry()
    required = {"id", "directory", "name", "vibe", "source_dna", "applicable_industries", "fonts", "tier"}
    for t in reg.get("templates", []):
        if not isinstance(t, dict):
            continue
        missing = required - set(t.keys())
        assert not missing, f"template {t.get('id')} missing fields: {missing}"


def test_get_template_lookup():
    found = templates_api.get_template("service_pro")
    assert found is not None
    assert found["id"] == "service_pro"


def test_get_template_unknown_returns_none():
    assert templates_api.get_template("does_not_exist_xyz") is None


# ------------------------------------------------------------------ #
# Validation helper — every original export must survive the swap     #
# ------------------------------------------------------------------ #


def test_validate_swap_passes_when_all_exports_preserved():
    original = """\
export const SITE_TITLE = "Original";
export const TAGLINE = "Old";
export const PHONE = "[BUSINESS PHONE]";
"""
    new = """\
export const SITE_TITLE = "New Brand";
export const TAGLINE = "New tagline";
export const PHONE = "[BUSINESS PHONE]";
"""
    ok, msg = templates_api._validate_swapped_site_ts(new, original)
    assert ok, msg


def test_validate_swap_fails_when_export_dropped():
    original = """\
export const SITE_TITLE = "Original";
export const TAGLINE = "Old";
"""
    new = """\
export const SITE_TITLE = "New Brand";
// LLM accidentally dropped TAGLINE
"""
    ok, msg = templates_api._validate_swapped_site_ts(new, original)
    assert not ok
    assert "TAGLINE" in msg


def test_validate_swap_allows_added_exports():
    """Strictly we want to flag added exports too, but for now the
    contract is 'never lose what was there' — adding extras is ignored.
    Pin the current behavior so future tightening is deliberate."""
    original = "export const A = 1;\n"
    new = "export const A = 1;\nexport const B = 2;\n"
    ok, _ = templates_api._validate_swapped_site_ts(new, original)
    assert ok


# ------------------------------------------------------------------ #
# Content-swap prompt construction                                    #
# ------------------------------------------------------------------ #


def test_prompt_includes_business_name():
    prompt = templates_api._build_content_swap_prompt(
        "service_pro",
        "export const X = 1;",
        {"business_name": "Joe's Plumbing"},
    )
    assert "Joe's Plumbing" in prompt


def test_prompt_includes_anti_slop_phone_rule():
    prompt = templates_api._build_content_swap_prompt(
        "service_pro",
        "export const X = 1;",
        {"business_name": "T"},
    )
    assert "[BUSINESS PHONE]" in prompt
    assert "do not invent" in prompt.lower()


def test_prompt_includes_anti_slop_testimonials_rule():
    prompt = templates_api._build_content_swap_prompt(
        "service_pro",
        "export const X = 1;",
        {"business_name": "T"},
    )
    assert "TESTIMONIALS" in prompt
    assert "empty" in prompt.lower()


def test_prompt_includes_location_placeholder_when_blank():
    prompt = templates_api._build_content_swap_prompt(
        "service_pro",
        "export const X = 1;",
        {"business_name": "T"},
    )
    assert "[BUSINESS ADDRESS]" in prompt or "not provided" in prompt.lower()


def test_prompt_includes_full_template_content_as_schema():
    template_ts = "export const FOO = 'baz';\nexport const BAR = 42;\n"
    prompt = templates_api._build_content_swap_prompt("x", template_ts, {"business_name": "T"})
    assert template_ts in prompt


# ------------------------------------------------------------------ #
# Typescript-block extraction from LLM responses                      #
# ------------------------------------------------------------------ #


def test_extract_typescript_block_handles_typescript_fence():
    raw = "Here you go:\n\n```typescript\nexport const A = 1;\n```\n\nDone."
    extracted = templates_api._extract_typescript_block(raw)
    assert extracted == "export const A = 1;"


def test_extract_typescript_block_handles_ts_fence():
    raw = "```ts\nexport const A = 1;\n```"
    extracted = templates_api._extract_typescript_block(raw)
    assert extracted == "export const A = 1;"


def test_extract_typescript_block_handles_bare_fence():
    raw = "```\nexport const A = 1;\n```"
    extracted = templates_api._extract_typescript_block(raw)
    assert extracted == "export const A = 1;"


def test_extract_typescript_block_falls_back_to_raw_when_no_fence():
    """Some LLMs respond with bare TS no fence. We accept if it starts
    with `export ` so we can still recover."""
    raw = "export const A = 1;\nexport const B = 2;\n"
    extracted = templates_api._extract_typescript_block(raw)
    assert extracted == raw.strip()


def test_extract_typescript_block_returns_none_on_garbage():
    raw = "I'm sorry, I cannot do that."
    extracted = templates_api._extract_typescript_block(raw)
    assert extracted is None


# ------------------------------------------------------------------ #
# Registry references existing DNA specs                              #
# ------------------------------------------------------------------ #


def test_every_template_source_dna_exists():
    """Each registry entry's source_dna must have a JSON spec on disk."""
    reg = templates_api.load_registry()
    dna_dir = Path(__file__).resolve().parent.parent / "pebble" / "templates" / "dna"
    for t in reg.get("templates", []):
        if not isinstance(t, dict):
            continue
        dna_id = t.get("source_dna", "")
        assert (dna_dir / f"{dna_id}.json").exists(), (
            f"template {t.get('id')} references missing DNA {dna_id}"
        )


def test_dna_files_are_valid_json():
    dna_dir = Path(__file__).resolve().parent.parent / "pebble" / "templates" / "dna"
    for p in dna_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            pytest.fail(f"{p.name} is not valid JSON: {e}")
        assert "dna_id" in data, f"{p.name} missing dna_id"
        assert "palette" in data, f"{p.name} missing palette"
        assert "fonts" in data, f"{p.name} missing fonts"
