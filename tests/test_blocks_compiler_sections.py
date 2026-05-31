"""Tests for the section-files compiler refactor (sub-project A).

Covers _normalize_section_source, _write_section_files, the new _build_page_tsx,
the rewired compile_site, and Pexels resolution across section files.
"""
from pathlib import Path

from pebble.blocks_compiler import _normalize_section_source


def test_normalize_hoists_use_client_to_first_line():
    src = 'import {motion} from "framer-motion";\n"use client";\nexport default function H(){return null;}'
    out = _normalize_section_source(src)
    assert out.splitlines()[0] == '"use client";'
    assert out.count("use client") == 1


def test_normalize_leaves_static_block_unchanged_except_strip():
    src = 'import Image from "next/image";\nexport default function H(){return null;}'
    out = _normalize_section_source(src)
    assert not out.startswith('"use client"')
    assert 'import Image from "next/image";' in out


def test_normalize_handles_single_quoted_directive_at_top():
    src = "'use client';\nexport default function H(){return null;}"
    out = _normalize_section_source(src)
    assert out.splitlines()[0] == '"use client";'
    assert out.count("use client") == 1


from pebble.blocks_compiler import _write_section_files


def test_write_section_files_writes_one_file_per_block(tmp_path: Path):
    blocks = [
        ("hero_x", 'export default function Hero(){return <section>A</section>;}'),
        ("about_y", 'export default function About(){return <section>B</section>;}'),
    ]
    names = _write_section_files(blocks, tmp_path)
    assert names == ["Section00", "Section01"]
    f0 = tmp_path / "components" / "sections" / "Section00.tsx"
    f1 = tmp_path / "components" / "sections" / "Section01.tsx"
    assert f0.exists() and f1.exists()
    assert "export default function Hero()" in f0.read_text(encoding="utf-8")
    assert "<section>B</section>" in f1.read_text(encoding="utf-8")


def test_write_section_files_preserves_hooks(tmp_path: Path):
    body = (
        '"use client";\n'
        'import {useRef} from "react";\n'
        'export default function Hero(){const r=useRef(null);return <section ref={r}/>;}'
    )
    names = _write_section_files([("hero_x", body)], tmp_path)
    text = (tmp_path / "components" / "sections" / f"{names[0]}.tsx").read_text(encoding="utf-8")
    assert text.splitlines()[0] == '"use client";'
    assert "const r=useRef(null)" in text


from pebble.blocks_compiler import _build_page_tsx


def test_build_page_tsx_imports_and_renders_sections_in_order():
    page = _build_page_tsx(["Section00", "Section01"])
    assert 'import Section00 from "@/components/sections/Section00";' in page
    assert 'import Section01 from "@/components/sections/Section01";' in page
    i0 = page.index("<Section00 />")
    i1 = page.index("<Section01 />")
    assert i0 < i1
    assert "export default function Page()" in page
    assert "= () => (" not in page


import pytest
from pebble.blocks_compiler import compile_site


class _FakeBlock:
    def __init__(self, template):
        self.template_source = template


class _FakeRegistry:
    def __init__(self, mapping):
        self._m = mapping
    def __getitem__(self, block_id):
        return self._m[block_id]


def test_compile_site_writes_section_files_and_thin_page(tmp_path: Path):
    reg = _FakeRegistry({
        "hero_x": _FakeBlock(
            '"use client";\nimport {useRef} from "react";\n'
            'export default function Hero(){const r=useRef(null);'
            'return <section ref={r}>{{headline}}</section>;}'
        ),
        "about_y": _FakeBlock(
            'export default function About(){return <section>{{body}}</section>;}'
        ),
    })
    picks = [
        {"block_id": "hero_x", "slot_values": {"headline": "Hi"}},
        {"block_id": "about_y", "slot_values": {"body": "We bake."}},
    ]
    compile_site(registry=reg, block_picks=picks, palette={}, out_dir=tmp_path)

    sec0 = tmp_path / "components" / "sections" / "Section00.tsx"
    sec1 = tmp_path / "components" / "sections" / "Section01.tsx"
    page = tmp_path / "app" / "page.tsx"
    assert sec0.exists() and sec1.exists() and page.exists()
    assert ">Hi<" in sec0.read_text(encoding="utf-8")
    assert "We bake." in sec1.read_text(encoding="utf-8")
    assert "useRef(null)" in sec0.read_text(encoding="utf-8")
    assert sec0.read_text(encoding="utf-8").splitlines()[0] == '"use client";'
    assert 'import Section00 from "@/components/sections/Section00";' in page.read_text(encoding="utf-8")


def test_compile_site_still_hard_fails_on_unfilled_placeholder(tmp_path: Path):
    reg = _FakeRegistry({"hero_x": _FakeBlock(
        'export default function Hero(){return <section>{{never_filled}}</section>;}'
    )})
    with pytest.raises(ValueError, match="unfilled placeholder"):
        compile_site(registry=reg, block_picks=[{"block_id": "hero_x"}],
                     palette={}, out_dir=tmp_path)
