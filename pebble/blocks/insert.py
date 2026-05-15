"""Block insertion — write the JSX file + splice into ``app/page.tsx``.

The insertion is deliberately surgical: a single new component file
under ``components/sections/`` plus two edits to ``app/page.tsx``
(import + render). Anything else the user wants to tweak goes through
the existing visual editor — blocks are meant to be drop-in starting
points, not the final shape.

Filename collisions are resolved by appending a numeric suffix
(``Testimonials.tsx`` → ``Testimonials2.tsx``) so a user can insert the
same block twice without losing either.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ---- Result shape --------------------------------------------------------

@dataclass
class InsertResult:
    block_id:        str
    component_name:  str
    files_written:   list[str]
    files_modified:  list[str]
    snapshot_id:     Optional[str]
    position:        str           # "before-footer" | "before-main-close" | "end-of-file"
    page_file:       str           # the file we edited ("app/page.tsx")

    def to_dict(self) -> dict:
        return {
            "block_id":        self.block_id,
            "component_name":  self.component_name,
            "files_written":   list(self.files_written),
            "files_modified":  list(self.files_modified),
            "snapshot_id":     self.snapshot_id,
            "position":        self.position,
            "page_file":       self.page_file,
        }


# ---- Page.tsx splicing ---------------------------------------------------

# Match either `<Footer ... />`, `<Footer ...>`, `<Footer/>` or `<Footer>`.
# Tag-prefix variant — we also accept namespaced footers like `<layout.Footer>`
# although that's not what the engine emits today.
_FOOTER_RENDER_RE = re.compile(r"<\s*(?:[A-Za-z_][\w.]*\.)?Footer\b")
_MAIN_CLOSE_RE   = re.compile(r"</\s*main\s*>")
_BODY_CLOSE_RE   = re.compile(r"</\s*body\s*>")
_RETURN_PAREN_RE = re.compile(r"return\s*\(")
_IMPORT_LINE_RE  = re.compile(r"^\s*import\b.*?;\s*$", re.MULTILINE)


def _unique_component_name(site_dir: Path, base_name: str) -> str:
    """Find a non-colliding component name. Checks both the target file
    on disk and whether the name is already imported in ``app/page.tsx``."""
    sections_dir = site_dir / "components" / "sections"
    page_tsx = site_dir / "app" / "page.tsx"
    page_src = page_tsx.read_text(encoding="utf-8") if page_tsx.exists() else ""

    candidate = base_name
    n = 1
    while True:
        path = sections_dir / f"{candidate}.tsx"
        # Already-imported check is intentionally string-based — we look
        # for a word-boundary match of the symbol in the source.
        already_imported = re.search(rf"\b{re.escape(candidate)}\b", page_src) is not None
        if not path.exists() and not already_imported:
            return candidate
        n += 1
        candidate = f"{base_name}{n}"


def _splice_page_tsx(src: str, component_name: str) -> tuple[str, str]:
    """Return ``(new_src, position_kind)`` where position_kind is one of
    ``"before-footer"`` | ``"before-main-close"`` | ``"end-of-jsx"``.

    Insertion rules, in order:

    1. Add ``import { Component } from '@/components/sections/Component';``
       on the line after the last existing ``import ...`` statement.
    2. Drop ``<Component />`` in the JSX. Preferred slot is right before
       ``<Footer .../>``. Falls back to right before ``</main>``, then
       before ``</body>``, then (degenerate) right after ``return (``.
    """
    # ---- import injection ----
    imports = list(_IMPORT_LINE_RE.finditer(src))
    import_line = f"import {{ {component_name} }} from '@/components/sections/{component_name}';"
    if imports:
        last = imports[-1]
        # Insert with leading newline after the last import.
        src = src[:last.end()] + "\n" + import_line + src[last.end():]
    else:
        # No imports? Stick it at the very top — unusual but safe.
        src = import_line + "\n" + src

    # ---- render injection ----
    render_jsx = f"<{component_name} />"
    position_kind = "end-of-jsx"

    for matcher, kind in (
        (_FOOTER_RENDER_RE, "before-footer"),
        (_MAIN_CLOSE_RE,    "before-main-close"),
        (_BODY_CLOSE_RE,    "before-body-close"),
    ):
        m = matcher.search(src)
        if m:
            indent = _indent_for_position(src, m.start())
            src = src[:m.start()] + render_jsx + "\n" + indent + src[m.start():]
            return src, kind

    # Last resort: drop the render right after `return (` so the block
    # at least renders somewhere visible. Better than silent failure.
    m = _RETURN_PAREN_RE.search(src)
    if m:
        # Skip past any newline + whitespace immediately after `return (`.
        idx = m.end()
        # Find the next non-whitespace character but keep the original
        # indent for the inserted JSX.
        indent_match = re.match(r"\s*", src[idx:])
        indent = indent_match.group(0) if indent_match else ""
        src = src[:idx] + indent + render_jsx + "\n" + src[idx:]
        return src, position_kind

    # Truly degenerate — append at end of file.
    return src + "\n" + render_jsx + "\n", position_kind


def _indent_for_position(src: str, position: int) -> str:
    """Return the leading whitespace of the line containing ``position``
    so the inserted JSX lines up under the same column."""
    line_start = src.rfind("\n", 0, position) + 1
    m = re.match(r"[ \t]*", src[line_start:position])
    return m.group(0) if m else "      "


# ---- Public API ----------------------------------------------------------

def insert_block_into_site(
    site_dir: Path,
    block_id: str,
    component_name: str,
    rendered_tsx: str,
    snapshot_id: Optional[str] = None,
) -> InsertResult:
    """Write the rendered component file and splice ``app/page.tsx``.

    Raises ``FileNotFoundError`` if the site doesn't have the standard
    Next.js layout; the HTTP handler maps that to a 404 or 409.
    """
    if not site_dir.exists():
        raise FileNotFoundError(f"site dir does not exist: {site_dir}")

    page_tsx = site_dir / "app" / "page.tsx"
    if not page_tsx.exists():
        raise FileNotFoundError("site has no app/page.tsx — can't auto-insert")

    final_name = _unique_component_name(site_dir, component_name)

    # 1) Write the component file
    sections_dir = site_dir / "components" / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)
    target = sections_dir / f"{final_name}.tsx"
    # The rendered template was generated with a placeholder component
    # name (the spec.component_name). Replace those usages with the
    # final unique name so the file's export + the page import agree.
    file_content = rendered_tsx
    if final_name != component_name:
        # Be specific: only rewrite the export identifier, not random
        # occurrences. The block templates emit `export function Foo()`
        # and use the same identifier in `data-pebble-block` strings
        # (which we don't want to touch — those are stable analytics
        # markers tied to the block_id, not the component name).
        file_content = re.sub(
            rf"\b{re.escape(component_name)}\b",
            final_name,
            file_content,
        )
    target.write_text(file_content, encoding="utf-8")
    files_written = [str(target.relative_to(site_dir).as_posix())]

    # 2) Splice page.tsx
    page_src = page_tsx.read_text(encoding="utf-8")
    new_src, position_kind = _splice_page_tsx(page_src, final_name)
    page_tsx.write_text(new_src, encoding="utf-8")

    return InsertResult(
        block_id=block_id,
        component_name=final_name,
        files_written=files_written,
        files_modified=[page_tsx.relative_to(site_dir).as_posix()],
        snapshot_id=snapshot_id,
        position=position_kind,
        page_file=page_tsx.relative_to(site_dir).as_posix(),
    )


def load_dna_for_site(brief_path: Path) -> Optional[dict]:
    """Resolve the DNA card for an existing build. Tolerates missing or
    unreadable ``brief.json`` (returns None — the renderer falls back
    to the neutral default)."""
    if not brief_path.exists():
        return None
    try:
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    dna_id = (brief.get("_design_dna") or brief.get("_design_dna_id") or "").strip()
    if not dna_id:
        return None
    try:
        from style_dna import pick_dna_by_id
    except Exception:
        return None
    return pick_dna_by_id(dna_id)


def load_brief(brief_path: Path) -> dict:
    """Return the project's brief as a dict, or ``{}`` if unreadable."""
    if not brief_path.exists():
        return {}
    try:
        return json.loads(brief_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
