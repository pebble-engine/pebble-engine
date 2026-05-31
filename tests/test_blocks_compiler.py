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
        "block_id": f"library/{name}",
        "block_type": extra.pop("block_type", "hero"),
        "vibe_tags": extra.pop("vibe_tags", ["warm"]),
        "dna_tags": [],
        "slots": extra.pop("slots", {}),
        "palette_slots": extra.pop("palette_slots", ["bg", "fg", "accent"]),
        **extra,
    }


def _read_sections(out: Path) -> str:
    """Concatenate all generated section files. After the section-files
    refactor, rendered block content lives in components/sections/SectionNN.tsx
    (not page.tsx), so content/count/order assertions read from here."""
    d = out / "components" / "sections"
    return "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(d.glob("*.tsx"))
    )


# ---- scalar + palette ----

def test_scalar_and_palette_substitution(tmp_path):
    reg = _make_registry(tmp_path, [(
        "library", "hero",
        _base_meta(
            "hero",
            __template__='<h1 className="bg-{{bg}} text-{{fg}}">{{headline}}</h1>',
            slots={"headline": {"kind": "text"}},
        ),
    )])
    out = tmp_path / "out"
    compile_site(
        registry=reg,
        block_picks=[{"block_id": "library/hero", "slot_values": {"headline": "Welcome"}}],
        palette={"bg": "stone-50", "fg": "stone-900"},
        out_dir=out,
    )
    page = _read_sections(out)
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
        "library", "svc",
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
            "block_id": "library/svc",
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
    page = _read_sections(out)
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
        "library", "list",
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
            "block_id": "library/list",
            "slot_values": {"items": ["Alpha", "Beta", "Gamma"]},
        }],
        palette={},
        out_dir=out,
    )
    page = _read_sections(out)
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
        "library", "pricing",
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
            "block_id": "library/pricing",
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
    page = _read_sections(out)
    assert page.count("<section>") == 2
    assert page.count("<li>") == 5  # 2 + 3 features
    assert "1 loaf/wk" in page and "Custom requests" in page


# ---- safety: unfilled placeholder rejected ----

def test_unfilled_placeholder_raises(tmp_path):
    reg = _make_registry(tmp_path, [(
        "library", "broken",
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
                "block_id": "library/broken",
                "slot_values": {"headline": "Welcome"},  # tagline missing
            }],
            palette={},
            out_dir=tmp_path / "out",
        )


# ---- safety: multiple blocks concatenate in order ----

def test_multiple_blocks_concatenate_in_order(tmp_path):
    reg = _make_registry(tmp_path, [
        ("library", "a", _base_meta("a", __template__='<h1>{{x}}</h1>', slots={"x": {"kind": "text"}}, palette_slots=[])),
        ("library", "b", _base_meta("b", __template__='<h2>{{y}}</h2>', slots={"y": {"kind": "text"}}, palette_slots=[])),
    ])
    out = tmp_path / "out"
    compile_site(
        registry=reg,
        block_picks=[
            {"block_id": "library/a", "slot_values": {"x": "FIRST"}},
            {"block_id": "library/b", "slot_values": {"y": "SECOND"}},
        ],
        palette={},
        out_dir=out,
    )
    page = _read_sections(out)
    assert page.index("FIRST") < page.index("SECOND")


def test_compile_site_scaffolds_runnable_next_project(tmp_path):
    """A v2-compiled site must have all the files needed for npm install + next dev."""
    bakery = tmp_path / "library" / "bakery"
    bakery.mkdir(parents=True)
    (bakery / "hero.tsx").write_text(
        'export default function Hero() { return (<h1 className="bg-{{bg}}">{{headline}}</h1>); }'
    )
    import json
    (bakery / "hero.json").write_text(json.dumps({
        "block_id": "library/hero",
        "block_type": "hero",
        "vibe_tags": ["warm"],
        "dna_tags": [],
        "slots": {"headline": {"kind": "text"}},
        "palette_slots": ["bg"],
    }))
    from pebble.blocks.registry import BlockRegistry
    from pebble.blocks_compiler import compile_site
    reg = BlockRegistry.load(tmp_path / "library")

    out = tmp_path / "site"
    compile_site(
        registry=reg,
        block_picks=[{"block_id": "library/hero", "slot_values": {"headline": "x"}}],
        palette={"bg": "stone-50"},
        out_dir=out,
    )

    # Scaffolding files must all exist
    assert (out / "package.json").exists()
    assert (out / "next.config.mjs").exists()
    assert (out / "tsconfig.json").exists()
    assert (out / "tailwind.config.ts").exists()
    assert (out / "postcss.config.mjs").exists()
    assert (out / "app" / "layout.tsx").exists()
    assert (out / "app" / "globals.css").exists()
    assert (out / "app" / "page.tsx").exists()

    # package.json must declare next, react, react-dom, tailwindcss
    pkg = json.loads((out / "package.json").read_text(encoding="utf-8"))
    assert "next" in pkg["dependencies"]
    assert "react" in pkg["dependencies"]
    assert "react-dom" in pkg["dependencies"]
    assert "tailwindcss" in pkg["devDependencies"]

    # Layout must import globals.css + render html/body
    layout = (out / "app" / "layout.tsx").read_text(encoding="utf-8")
    assert "globals.css" in layout
    assert "<html" in layout and "<body" in layout

    # Tailwind config must include content paths for app/
    tw = (out / "tailwind.config.ts").read_text(encoding="utf-8")
    assert "./app/**/*.{ts,tsx}" in tw

    # globals.css has the 3 Tailwind directives
    css = (out / "app" / "globals.css").read_text(encoding="utf-8")
    assert "@tailwind base" in css
    assert "@tailwind components" in css
    assert "@tailwind utilities" in css


def test_real_warm_hero_produces_valid_jsx():
    """Integration: compile a real library warm hero template into runnable JSX.
    Catches the 'export default function Hero()' nested wrapper bug that
    synthetic tests missed (regression guard, 2026-05-29)."""
    from pebble.blocks.registry import BlockRegistry
    real_root = Path(__file__).parent.parent / "pebble" / "blocks"
    reg = BlockRegistry.load(real_root)

    import tempfile, shutil
    out_dir = Path(tempfile.mkdtemp())
    try:
        compile_site(
            registry=reg,
            block_picks=[{
                "block_id": "library/hero_artisan_warm",
                "slot_values": {
                    "eyebrow": "Brooklyn",
                    "headline": "Real bread",
                    "subheadline": "Made slowly.",
                    "cta_primary": "Order",
                    "cta_secondary": "About",
                    "hero_image": "https://x.com/h.jpg",
                },
            }],
            palette={"bg": "stone-50", "fg": "stone-900", "accent": "orange-700"},
            out_dir=out_dir,
        )
        sec0 = (out_dir / "components" / "sections" / "Section00.tsx").read_text(encoding="utf-8")
        page = (out_dir / "app" / "page.tsx").read_text(encoding="utf-8")

        # New contract: the block stays a proper default-exported component in
        # its own section file (full body/hooks intact), and page.tsx imports it.
        assert "export default function Hero" in sec0
        assert 'import Section00 from "@/components/sections/Section00";' in page

        # No arrow-wrapped inlining (the old flattening) anywhere.
        assert "= () => (" not in page
        assert "= () => (" not in sec0

        # The good signal — actual JSX content survived into the section file
        assert "Real bread" in sec0
        assert "stone-50" in sec0
        assert "{{" not in sec0
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
