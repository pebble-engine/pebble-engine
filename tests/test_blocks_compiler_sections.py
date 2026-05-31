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
