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
