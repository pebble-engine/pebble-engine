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


def _scrubbed_for_search(src: str) -> str:
    """Return a copy of ``src`` with JSX comments and string literals
    blanked out (replaced with same-length spaces, so character offsets
    stay aligned with the original). Used as a sieve before the regex
    matchers so we don't splice in front of a Footer that lives inside
    ``{/* ... <Footer /> ... */}`` or inside a JSX string literal.

    Same-length replacement is important: callers use the match index to
    splice into the *original* string. Shrinking the search text would
    desync offsets.
    """
    out = []
    i = 0
    n = len(src)
    while i < n:
        ch = src[i]
        # JSX comment block: {/* ... */}
        if ch == "{" and src.startswith("{/*", i):
            end = src.find("*/}", i + 3)
            if end == -1:
                out.append(" " * (n - i))
                break
            length = end + 3 - i
            out.append(" " * length)
            i = end + 3
            continue
        # C-style block comment: /* ... */
        if ch == "/" and i + 1 < n and src[i + 1] == "*":
            end = src.find("*/", i + 2)
            if end == -1:
                out.append(" " * (n - i))
                break
            length = end + 2 - i
            out.append(" " * length)
            i = end + 2
            continue
        # Single-line comment: // until newline
        if ch == "/" and i + 1 < n and src[i + 1] == "/":
            end = src.find("\n", i)
            if end == -1:
                out.append(" " * (n - i))
                break
            length = end - i
            out.append(" " * length)
            i = end
            continue
        # String literal: ", ', or `
        if ch in ('"', "'", "`"):
            quote = ch
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == quote:
                    j += 1
                    break
                j += 1
            out.append(" " * (j - i))
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _is_inside_jsx_expression(src: str, position: int) -> bool:
    """Return True if ``position`` looks like it's inside a JSX expression
    where inserting a sibling element would break the syntax (the classic
    bad case is ``{showFooter && <Footer />}``).

    Counting all unmatched ``{`` braces in the file would also match
    ordinary function bodies and object literals — we'd refuse every
    insert in a normal Next.js page. Instead we use a local-context
    heuristic: look at the non-whitespace, non-comment chars immediately
    before ``position``. JSX content always has either ``>`` (close of
    a previous element) or ``<`` (start of a new element, e.g. our
    Footer matched at the very start of a tag); a JSX expression context
    has an operator (``&&``, ``||``, ``?``, ``:``, ``(``, ``,``).
    """
    # Walk backwards over whitespace and JSX comment blocks.
    i = position - 1
    while i >= 0:
        ch = src[i]
        if ch.isspace():
            i -= 1
            continue
        # JSX comment {/* ... */}: skip backwards through it.
        if ch == "}" and i >= 2 and src[i - 2:i + 1] == "*/}":
            start = src.rfind("{/*", 0, i)
            if start == -1:
                return False
            i = start - 1
            continue
        break
    if i < 0:
        return False

    ch = src[i]
    # Single-char operator-like contexts that indicate "we're in an
    # expression that yields one node" — inserting a sibling here is
    # broken JSX.
    if ch in "?:(,":
        return True
    if ch == "&" and i > 0 and src[i - 1] == "&":
        return True
    if ch == "|" and i > 0 and src[i - 1] == "|":
        return True
    # JSX-content contexts: a preceding `>` closes the previous element,
    # or the match position is at the very start of a fragment / parent.
    if ch == ">":
        return False
    # `{` immediately before would be the open of an unsafe expression —
    # but with content between (it's not adjacent here), we already
    # handled it via the operator chars above.
    return False


def _find_safe_match(matcher: "re.Pattern[str]", scrubbed: str, original: str):
    """Find a regex match in ``scrubbed`` whose position is NOT inside
    a JSX expression of ``original``. Walks through all matches and
    returns the first that's safe; None if none qualifies."""
    for m in matcher.finditer(scrubbed):
        if not _is_inside_jsx_expression(original, m.start()):
            return m
    return None


def _splice_page_tsx(src: str, component_name: str) -> tuple[str, str]:
    """Return ``(new_src, position_kind)`` where position_kind is one of
    ``"before-footer"`` | ``"before-main-close"`` | ``"end-of-jsx"``.

    Insertion rules, in order:

    1. Add ``import { Component } from '@/components/sections/Component';``
       on the line after the last existing ``import ...`` statement.
    2. Drop ``<Component />`` in the JSX. Preferred slot is right before
       ``<Footer .../>``. Falls back to right before ``</main>``, then
       before ``</body>``, then (degenerate) right after ``return (``.

    JSX comments (``{/* */}``), C-style comments (``/* */``), single-line
    comments (``//``), and string literals are all scrubbed before regex
    matching so a phantom ``<Footer />`` inside a comment can't fool the
    splicer. Matches inside ``{...}`` JSX expressions (e.g.
    ``{showFooter && <Footer />}``) are also skipped — inserting a
    sibling there breaks the parent expression.
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

    scrubbed = _scrubbed_for_search(src)
    for matcher, kind in (
        (_FOOTER_RENDER_RE, "before-footer"),
        (_MAIN_CLOSE_RE,    "before-main-close"),
        (_BODY_CLOSE_RE,    "before-body-close"),
    ):
        m = _find_safe_match(matcher, scrubbed, src)
        if m:
            indent = _indent_for_position(src, m.start())
            src = src[:m.start()] + render_jsx + "\n" + indent + src[m.start():]
            return src, kind

    # Last resort: drop the render right after `return (` so the block
    # at least renders somewhere visible. Better than silent failure.
    m = _RETURN_PAREN_RE.search(scrubbed)
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

    # 2) Splice page.tsx — if this fails, roll back the component file
    # so we don't leave an orphan in components/sections/. The snapshot
    # is the outer safety net; this cleanup keeps the working tree
    # consistent for the next attempt.
    try:
        page_src = page_tsx.read_text(encoding="utf-8")
        new_src, position_kind = _splice_page_tsx(page_src, final_name)
        page_tsx.write_text(new_src, encoding="utf-8")
    except Exception:
        try:
            target.unlink()
        except Exception:
            pass
        raise

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
