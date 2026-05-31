# v2 Compiler Section-Files Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the v2 compiler emit each block as its own `components/sections/SectionNN.tsx` file (preserving the full component body, hooks, and `"use client"`), with `page.tsx` importing and rendering them in order — instead of flattening every block into one `page.tsx`.

**Architecture:** Today `blocks_compiler._build_page_tsx` strips each block down to bare JSX (`_extract_jsx_body`) and inlines it as `const SectionNN = () => (...)`. That discards any React hooks a block declares before its `return`, which blocks the motion work (sub-project B) and the future section-reorder editor (task #232). This refactor writes each rendered block verbatim to its own section file and builds a thin `page.tsx` of imports + tags. It is behavior-preserving for the current static blocks (same rendered DOM) and additive for future hook-using blocks.

**Tech Stack:** Python 3 (engine), pytest, Next.js 14 App Router output, `@/*` path alias (already configured in scaffolded `tsconfig.json`).

---

## Background facts (verified 2026-05-30)

- `pebble/blocks_compiler.py`:
  - `compile_site(*, registry, block_picks, palette, out_dir)` renders each pick, hard-fails on
    leftover `{{...}}`, then calls `_build_page_tsx(rendered_blocks)` and writes `app/page.tsx`,
    then `_write_scaffolding(out_dir)`.
  - `_build_page_tsx(rendered_blocks: list[tuple[str,str]])` flattens via `_extract_jsx_body` +
    `_extract_imports`, producing `const SectionNN = () => (jsx)` inside one `page.tsx`.
  - `_extract_imports(body)` returns `(imports: list[str], clean_body: str)` — used today to hoist
    imports. After this refactor, section files keep their own imports, so it is no longer called
    from the page builder (leave the function defined; other code may use it).
- `pebble/server/build_v2.py` (lines 131-136) resolves Pexels **only** on `app/page.tsx`. After this
  refactor, images live in section files, so resolution must iterate them.
- Scaffolded `tsconfig.json` already maps `"@/*": ["./*"]` from the site root, and `components/` is a
  sibling of `app/`, so `@/components/sections/SectionNN` resolves correctly.
- Real library blocks are full `export default function Name() { return (...); }` components.

## File Structure

- **Modify** `pebble/blocks_compiler.py`:
  - Add `_normalize_section_source(source: str) -> str` — hoist a `"use client"` directive to line 1.
  - Add `_write_section_files(rendered_blocks, out_dir) -> list[str]` — write each block to
    `components/sections/SectionNN.tsx`, return component names.
  - Replace `_build_page_tsx` body with an imports+tags builder taking `section_names: list[str]`.
  - Rewire `compile_site` to call the two new helpers.
- **Modify** `pebble/server/build_v2.py` — Pexels resolution iterates `components/sections/*.tsx`.
- **Create** `tests/test_blocks_compiler_sections.py` — unit tests for the new helpers + hook survival.
- **Update** existing compiler tests that assert the old single-`page.tsx` shape (discovered in Task 5).

---

### Task 1: `_normalize_section_source` — hoist `"use client"` to line 1

**Files:**
- Modify: `pebble/blocks_compiler.py` (add function near the other private helpers, before `_build_page_tsx`)
- Test: `tests/test_blocks_compiler_sections.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_blocks_compiler_sections.py
from pebble.blocks_compiler import _normalize_section_source


def test_normalize_hoists_use_client_to_first_line():
    src = 'import {motion} from "framer-motion";\n"use client";\nexport default function H(){return null;}'
    out = _normalize_section_source(src)
    assert out.splitlines()[0] == '"use client";'
    # directive appears exactly once
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_blocks_compiler_sections.py -q`
Expected: FAIL with `ImportError: cannot import name '_normalize_section_source'`

- [ ] **Step 3: Write minimal implementation**

```python
# pebble/blocks_compiler.py  (add near the top-level private helpers)

# Matches a leading "use client" / 'use client' directive (optionally already
# at the very top), with optional trailing semicolon and surrounding whitespace.
_USE_CLIENT_RE = re.compile(r'''["']use client["'];?''')


def _normalize_section_source(source: str) -> str:
    """Return source with a single `"use client";` directive on line 1 iff the
    block declared one anywhere; otherwise return the stripped source unchanged.

    A `"use client"` directive is only valid as the first statement of a module,
    so when a block author (or the motion pass) includes it, we must guarantee it
    lands on line 1 — above the imports.
    """
    stripped = source.strip()
    if not _USE_CLIENT_RE.search(stripped):
        return stripped
    # Remove every occurrence of the directive, then re-prepend exactly one.
    without = _USE_CLIENT_RE.sub("", stripped).strip()
    return '"use client";\n\n' + without
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_blocks_compiler_sections.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add pebble/blocks_compiler.py tests/test_blocks_compiler_sections.py
git commit -m "feat(compiler): _normalize_section_source hoists use-client to line 1"
```

---

### Task 2: `_write_section_files` — one file per block

**Files:**
- Modify: `pebble/blocks_compiler.py`
- Test: `tests/test_blocks_compiler_sections.py`

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_blocks_compiler_sections.py
from pathlib import Path
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
    # full component body preserved (NOT stripped to bare JSX)
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
    assert "const r=useRef(null)" in text   # hook body survived
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_blocks_compiler_sections.py -q`
Expected: FAIL with `ImportError: cannot import name '_write_section_files'`

- [ ] **Step 3: Write minimal implementation**

```python
# pebble/blocks_compiler.py

def _write_section_files(
    rendered_blocks: list[tuple[str, str]],
    out_dir: Path,
) -> list[str]:
    """Write each rendered block to components/sections/SectionNN.tsx verbatim
    (full default-exported component, hooks intact). Returns the component names
    in order, for page.tsx to import.
    """
    sections_dir = out_dir / "components" / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)
    names: list[str] = []
    for i, (_block_id, body) in enumerate(rendered_blocks):
        name = f"Section{i:02d}"
        source = _normalize_section_source(body)
        (sections_dir / f"{name}.tsx").write_text(source + "\n", encoding="utf-8")
        names.append(name)
    return names
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_blocks_compiler_sections.py -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add pebble/blocks_compiler.py tests/test_blocks_compiler_sections.py
git commit -m "feat(compiler): _write_section_files emits one component file per block"
```

---

### Task 3: New `_build_page_tsx` — imports + render tags

**Files:**
- Modify: `pebble/blocks_compiler.py` (`_PAGE_TEMPLATE` + `_build_page_tsx`)
- Test: `tests/test_blocks_compiler_sections.py`

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_blocks_compiler_sections.py
from pebble.blocks_compiler import _build_page_tsx


def test_build_page_tsx_imports_and_renders_sections_in_order():
    page = _build_page_tsx(["Section00", "Section01"])
    assert 'import Section00 from "@/components/sections/Section00";' in page
    assert 'import Section01 from "@/components/sections/Section01";' in page
    # rendered in order inside <main>
    i0 = page.index("<Section00 />")
    i1 = page.index("<Section01 />")
    assert i0 < i1
    assert "export default function Page()" in page
    # no leftover inline arrow-component pattern from the old builder
    assert "= () => (" not in page
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_blocks_compiler_sections.py::test_build_page_tsx_imports_and_renders_sections_in_order -q`
Expected: FAIL — the current `_build_page_tsx` takes `rendered_blocks` (list of tuples), not a list of names, so it raises a `TypeError`/`ValueError` or produces the old inline shape (the `"= () => ("` assertion fails).

- [ ] **Step 3: Write minimal implementation**

Replace the existing `_PAGE_TEMPLATE` and `_build_page_tsx` with:

```python
# pebble/blocks_compiler.py

_PAGE_TEMPLATE = """\
{imports}

export default function Page() {{
  return (
    <main>
{section_tags}
    </main>
  );
}}
"""


def _build_page_tsx(section_names: list[str]) -> str:
    """Build page.tsx that imports each section component and renders them in
    order inside <main>. Section bodies live in their own files (see
    _write_section_files), so page.tsx is a thin composition root.
    """
    imports_block = "\n".join(
        f'import {name} from "@/components/sections/{name}";'
        for name in section_names
    )
    section_tags_block = "\n".join(f"      <{name} />" for name in section_names)
    return _PAGE_TEMPLATE.format(
        imports=imports_block,
        section_tags=section_tags_block,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_blocks_compiler_sections.py::test_build_page_tsx_imports_and_renders_sections_in_order -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pebble/blocks_compiler.py tests/test_blocks_compiler_sections.py
git commit -m "feat(compiler): page.tsx imports section files instead of inlining JSX"
```

---

### Task 4: Rewire `compile_site` to emit section files

**Files:**
- Modify: `pebble/blocks_compiler.py` (`compile_site`)
- Test: `tests/test_blocks_compiler_sections.py`

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_blocks_compiler_sections.py
from pebble.blocks.registry import BlockRegistry
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
    # slot substitution still happened, into the section file
    assert ">Hi<" in sec0.read_text(encoding="utf-8")
    assert "We bake." in sec1.read_text(encoding="utf-8")
    # hook survived end-to-end through compile_site
    assert "useRef(null)" in sec0.read_text(encoding="utf-8")
    assert sec0.read_text(encoding="utf-8").splitlines()[0] == '"use client";'
    # page.tsx is the thin composition root
    assert 'import Section00 from "@/components/sections/Section00";' in page.read_text(encoding="utf-8")


def test_compile_site_still_hard_fails_on_unfilled_placeholder(tmp_path: Path):
    import pytest
    reg = _FakeRegistry({"hero_x": _FakeBlock(
        'export default function Hero(){return <section>{{never_filled}}</section>;}'
    )})
    with pytest.raises(ValueError, match="unfilled placeholder"):
        compile_site(registry=reg, block_picks=[{"block_id": "hero_x"}],
                     palette={}, out_dir=tmp_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_blocks_compiler_sections.py -q`
Expected: FAIL — current `compile_site` writes the inline `page.tsx` and no `components/sections/` dir, so the section-file assertions fail.

- [ ] **Step 3: Write minimal implementation**

In `compile_site`, replace the page-building + write block (current lines ~587-593):

```python
    # Build the page.tsx
    page_tsx = _build_page_tsx(rendered_blocks)

    # Write output
    app_dir = out_dir / "app"
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / "page.tsx").write_text(page_tsx, encoding="utf-8")
```

with:

```python
    # Write each block as its own section file (full body + hooks preserved),
    # then a thin page.tsx that imports and renders them in order.
    section_names = _write_section_files(rendered_blocks, out_dir)
    page_tsx = _build_page_tsx(section_names)

    app_dir = out_dir / "app"
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / "page.tsx").write_text(page_tsx, encoding="utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_blocks_compiler_sections.py -q`
Expected: PASS (all tests)

- [ ] **Step 5: Remove now-dead inlining helper (if unreferenced)**

Run: `grep -rn "_extract_jsx_body" pebble/ tests/`
If the only definition+no other callers remain, delete the `_extract_jsx_body` function and its
`_EXPORT_DEFAULT_FUNCTION_RE` regex. If any test references it, leave both in place.

- [ ] **Step 6: Commit**

```bash
git add pebble/blocks_compiler.py tests/test_blocks_compiler_sections.py
git commit -m "refactor(compiler): compile_site emits per-section files preserving hooks"
```

---

### Task 5: Update existing compiler tests to the new page shape

**Files:**
- Modify: existing compiler tests discovered below.

- [ ] **Step 1: Find tests that assert the old single-page shape**

Run: `grep -rln "= () => (\|_build_page_tsx\|app/page.tsx\|const Section" tests/`
These are tests written against the old inline `page.tsx`. Open each hit.

- [ ] **Step 2: Run the full compiler-related suite to see real breakages**

Run: `python -m pytest tests/ -k "compiler or build_v2 or blocks" -q`
Expected: some FAILs in pre-existing tests that assert inline `const SectionNN = () => (` in
`page.tsx`, or that read images from `page.tsx`.

- [ ] **Step 3: Update each failing assertion to the new contract**

For each failure, update the assertion to the new shape. Examples of the mechanical change:

```python
# OLD assertion (no longer true):
assert "const Section00 = () => (" in page_text
# NEW assertion:
assert 'import Section00 from "@/components/sections/Section00";' in page_text
```

```python
# OLD: image lived in page.tsx
page = (out / "app" / "page.tsx").read_text(encoding="utf-8")
assert "pexels" in page or "{{hero_image}}" in page
# NEW: image lives in a section file
sec = (out / "components" / "sections" / "Section00.tsx").read_text(encoding="utf-8")
assert "{{hero_image}}" in sec
```

Do not weaken intent — preserve what each test was verifying, just point it at the new location.

- [ ] **Step 4: Run the suite to verify green**

Run: `python -m pytest tests/ -k "compiler or build_v2 or blocks" -q`
Expected: PASS (0 failed)

- [ ] **Step 5: Commit**

```bash
git add tests/
git commit -m "test(compiler): update assertions for section-files page shape"
```

---

### Task 6: Pexels resolution iterates section files in build_v2

**Files:**
- Modify: `pebble/server/build_v2.py:131-136`
- Test: `tests/test_blocks_compiler_sections.py`

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_blocks_compiler_sections.py
def test_pexels_resolves_across_section_files(tmp_path: Path, monkeypatch):
    # Compile a site whose image src is a plain query (Sonnet style).
    reg = _FakeRegistry({"hero_x": _FakeBlock(
        'export default function Hero(){return <img src="{{hero_image}}"/>;}'
    )})
    site_dir = tmp_path / "site"
    compile_site(
        registry=reg,
        block_picks=[{"block_id": "hero_x",
                      "slot_values": {"hero_image": "rustic bread loaves"}}],
        palette={}, out_dir=site_dir,
    )
    # Simulate build_v2's resolution loop (placeholder fallback, no API key).
    from pebble.pexels_resolver import resolve_pexels_tags
    sections_dir = site_dir / "components" / "sections"
    for sec in sorted(sections_dir.glob("*.tsx")):
        sec.write_text(resolve_pexels_tags(sec.read_text(encoding="utf-8")),
                       encoding="utf-8")
    text = (sections_dir / "Section00.tsx").read_text(encoding="utf-8")
    # the plain query was swapped for a real URL (picsum fallback when no key)
    assert 'src="rustic bread loaves"' not in text
    assert "https://" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_blocks_compiler_sections.py::test_pexels_resolves_across_section_files -q`
Expected: PASS for the loop logic itself OR FAIL if `resolve_pexels_tags` import path differs —
this test validates the *loop shape* we are about to put in build_v2. If it passes, it confirms the
approach; proceed to wire it into build_v2 in Step 3.

- [ ] **Step 3: Wire the loop into build_v2**

Replace `pebble/server/build_v2.py` lines 131-136:

```python
    # Pexels resolution — turn [pexels:query] tags into real image URLs.
    # Without this the generated site 404s on every image.
    page_tsx = site_dir / "app" / "page.tsx"
    if page_tsx.exists():
        resolved = resolve_pexels_tags(page_tsx.read_text(encoding="utf-8"))
        page_tsx.write_text(resolved, encoding="utf-8")
```

with:

```python
    # Pexels resolution — turn image queries into real URLs across every
    # section file (images now live in components/sections/, not page.tsx).
    # Without this the generated site 404s on every image.
    sections_dir = site_dir / "components" / "sections"
    if sections_dir.exists():
        for sec in sorted(sections_dir.glob("*.tsx")):
            resolved = resolve_pexels_tags(sec.read_text(encoding="utf-8"))
            sec.write_text(resolved, encoding="utf-8")
```

- [ ] **Step 4: Run the build_v2 + compiler suite**

Run: `python -m pytest tests/ -k "build_v2 or compiler or blocks" -q`
Expected: PASS (0 failed)

- [ ] **Step 5: Commit**

```bash
git add pebble/server/build_v2.py tests/test_blocks_compiler_sections.py
git commit -m "feat(build_v2): resolve Pexels across section files, not just page.tsx"
```

---

### Task 7: Full regression + live compile sanity

**Files:** none (verification only)

- [ ] **Step 1: Run the entire test suite**

Run: `python -m pytest -q`
Expected: PASS (no new failures vs. the pre-refactor baseline).

- [ ] **Step 2: Live compile one site and boot it**

Recompile an existing brief through the v2 path (or re-run a saved brief) into a scratch slug, then:

```bash
cd output/<scratch-slug>/site && npm install --silent && npx next dev -p 4010
curl -s -o /dev/null -w "%{http_code}\n" --max-time 90 http://localhost:4010/
```
Expected: `200`, and `components/sections/Section00.tsx` … exist with full component bodies, and
`app/page.tsx` imports them. No `Module not found`, no `{{...}}` leaks.

- [ ] **Step 3: Commit any doc/notes**

```bash
git add -A && git commit -m "chore: v2 section-files refactor verified end-to-end" || echo "nothing to commit"
```

---

## Self-Review

**Spec coverage** (against `2026-05-30-pebble-v2-motion-and-layout-variety-design.md` §"Compiler upgrade: section files"):
- ✅ Each block → own section file (Task 2)
- ✅ Full function body + hooks preserved (Task 2 test `..preserves_hooks`, Task 4 end-to-end)
- ✅ `"use client"` preserved on line 1 (Task 1, Task 4)
- ✅ page.tsx imports + renders in order (Task 3) → enables future section reorder (task #232)
- ✅ Placeholder leak hard-fail retained (Task 4 test)
- ✅ Pexels resolution runs across section files (Task 6)
- Not in this plan (correctly deferred to B/C/D): motion primitives, new block types, data-pebble-id tagging.

**Placeholder scan:** No TBD/TODO; every code step shows complete code; Task 5's "discover existing
tests" uses concrete grep commands, not vague instructions.

**Type consistency:** `_normalize_section_source(str)->str`, `_write_section_files(list[tuple],Path)->list[str]`,
`_build_page_tsx(list[str])->str` are used consistently across Tasks 1-4. `compile_site` signature is
unchanged (public API stable).
