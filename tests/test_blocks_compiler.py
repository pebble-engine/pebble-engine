from pathlib import Path
import json
import pytest

from pebble.blocks_compiler import compile_site
from pebble.blocks.registry import BlockRegistry


# ---- helpers ----

def _make_registry(tmp_path: Path, blocks: list[tuple[str, str, dict]]) -> BlockRegistry:
    """Create a minimal on-disk library with the given (industry, name, metadata) blocks.
    The .tsx content is passed as `metadata["__template__"]` and stripped before validation."""
    for industry, name, meta in blocks:
        d = tmp_path / industry
        d.mkdir(exist_ok=True)
        tpl = meta.pop("__template__")
        (d / f"{name}.tsx").write_text(tpl, encoding="utf-8")
        (d / f"{name}.json").write_text(json.dumps(meta), encoding="utf-8")
    return BlockRegistry.load(tmp_path)


def _base_meta(name: str, **extra) -> dict:
    return {
        "block_id": f"bakery/{name}",
        "block_type": extra.pop("block_type", "hero"),
        "industry": "bakery",
        "dna_tags": [],
        "slots": extra.pop("slots", {}),
        "palette_slots": extra.pop("palette_slots", ["bg", "fg", "accent"]),
        **extra,
    }


# ---- scalar + palette ----

def test_scalar_and_palette_substitution(tmp_path):
    reg = _make_registry(tmp_path, [(
        "bakery", "hero",
        _base_meta(
            "hero",
            __template__='<h1 className="bg-{{bg}} text-{{fg}}">{{headline}}</h1>',
            slots={"headline": {"kind": "text"}},
        ),
    )])
    out = tmp_path / "out"
    compile_site(
        registry=reg,
        block_picks=[{"block_id": "bakery/hero", "slot_values": {"headline": "Welcome"}}],
        palette={"bg": "stone-50", "fg": "stone-900"},
        out_dir=out,
    )
    page = (out / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "bg-stone-50" in page
    assert "text-stone-900" in page
    assert ">Welcome<" in page
    assert "{{" not in page


# ---- list iteration ----

def test_list_iteration(tmp_path):
    template = (
        '<div>{{eyebrow}}'
        '{/* {{services_list_start}} */}'
        '<article><h3>{{services[].title}}</h3><p>{{services[].body}}</p></article>'
        '{/* {{services_list_end}} */}'
        '</div>'
    )
    reg = _make_registry(tmp_path, [(
        "bakery", "svc",
        _base_meta(
            "svc",
            block_type="services",
            __template__=template,
            slots={"eyebrow": {"kind": "text"}, "services": {"kind": "list"}},
        ),
    )])
    out = tmp_path / "out"
    compile_site(
        registry=reg,
        block_picks=[{
            "block_id": "bakery/svc",
            "slot_values": {
                "eyebrow": "What we bake",
                "services": [
                    {"title": "Sourdough", "body": "Naturally leavened"},
                    {"title": "Pastries", "body": "Hand-laminated"},
                    {"title": "Bread subscription", "body": "Weekly delivery"},
                ],
            },
        }],
        palette={},
        out_dir=out,
    )
    page = (out / "app" / "page.tsx").read_text(encoding="utf-8")
    assert page.count("<article>") == 3
    assert "Sourdough" in page and "Pastries" in page and "Bread subscription" in page
    assert "Naturally leavened" in page
    assert "{{" not in page


# ---- list of strings (not objects) ----

def test_list_of_strings(tmp_path):
    template = (
        '<ul>'
        '{/* {{items_list_start}} */}'
        '<li>{{items[]}}</li>'
        '{/* {{items_list_end}} */}'
        '</ul>'
    )
    reg = _make_registry(tmp_path, [(
        "bakery", "list",
        _base_meta(
            "list",
            __template__=template,
            slots={"items": {"kind": "list"}},
            palette_slots=[],
        ),
    )])
    out = tmp_path / "out"
    compile_site(
        registry=reg,
        block_picks=[{
            "block_id": "bakery/list",
            "slot_values": {"items": ["Alpha", "Beta", "Gamma"]},
        }],
        palette={},
        out_dir=out,
    )
    page = (out / "app" / "page.tsx").read_text(encoding="utf-8")
    assert page.count("<li>") == 3
    assert "Alpha" in page and "Beta" in page and "Gamma" in page


# ---- nested list iteration ----

def test_nested_list_iteration(tmp_path):
    template = (
        '{/* {{tiers_list_start}} */}'
        '<section><h3>{{tiers[].name}}</h3>'
        '<ul>'
        '{/* {{tiers[].features_list_start}} */}'
        '<li>{{tiers[].features[]}}</li>'
        '{/* {{tiers[].features_list_end}} */}'
        '</ul></section>'
        '{/* {{tiers_list_end}} */}'
    )
    reg = _make_registry(tmp_path, [(
        "bakery", "pricing",
        _base_meta(
            "pricing",
            block_type="pricing",
            __template__=template,
            slots={"tiers": {"kind": "list"}},
            palette_slots=[],
        ),
    )])
    out = tmp_path / "out"
    compile_site(
        registry=reg,
        block_picks=[{
            "block_id": "bakery/pricing",
            "slot_values": {
                "tiers": [
                    {"name": "Basic", "features": ["1 loaf/wk", "Pick up only"]},
                    {"name": "Pro",   "features": ["3 loaves/wk", "Delivery included", "Custom requests"]},
                ],
            },
        }],
        palette={},
        out_dir=out,
    )
    page = (out / "app" / "page.tsx").read_text(encoding="utf-8")
    assert page.count("<section>") == 2
    assert page.count("<li>") == 5  # 2 + 3 features
    assert "1 loaf/wk" in page and "Custom requests" in page


# ---- safety: unfilled placeholder rejected ----

def test_unfilled_placeholder_raises(tmp_path):
    reg = _make_registry(tmp_path, [(
        "bakery", "broken",
        _base_meta(
            "broken",
            __template__='<h1>{{headline}} - {{tagline}}</h1>',
            slots={"headline": {"kind": "text"}, "tagline": {"kind": "text"}},
            palette_slots=[],
        ),
    )])
    with pytest.raises(ValueError, match="unfilled placeholder"):
        compile_site(
            registry=reg,
            block_picks=[{
                "block_id": "bakery/broken",
                "slot_values": {"headline": "Welcome"},  # tagline missing
            }],
            palette={},
            out_dir=tmp_path / "out",
        )


# ---- safety: multiple blocks concatenate in order ----

def test_multiple_blocks_concatenate_in_order(tmp_path):
    reg = _make_registry(tmp_path, [
        ("bakery", "a", _base_meta("a", __template__='<h1>{{x}}</h1>', slots={"x": {"kind": "text"}}, palette_slots=[])),
        ("bakery", "b", _base_meta("b", __template__='<h2>{{y}}</h2>', slots={"y": {"kind": "text"}}, palette_slots=[])),
    ])
    out = tmp_path / "out"
    compile_site(
        registry=reg,
        block_picks=[
            {"block_id": "bakery/a", "slot_values": {"x": "FIRST"}},
            {"block_id": "bakery/b", "slot_values": {"y": "SECOND"}},
        ],
        palette={},
        out_dir=out,
    )
    page = (out / "app" / "page.tsx").read_text(encoding="utf-8")
    assert page.index("FIRST") < page.index("SECOND")
