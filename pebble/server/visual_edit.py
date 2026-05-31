"""POST /api/visual-edit — deterministic in-place edits triggered by a
click on the preview iframe.

The workspace UI runs a bridge script in the iframe (injected at preview-
serve time by ``_handle_preview``). When the user clicks an element, the
bridge sends ``{type: 'pebble-select', selector, text, ...}`` to the
parent via postMessage. The parent opens a side panel; when the user
saves a change, we POST here.

Edits supported (deterministic, never invoke the LLM):

- ``text``           — replace a text node identified by a CSS selector
- ``color``          — change a Tailwind color class or inline style fill
- ``font-size``      — change the inline ``style="font-size"`` of an element
- ``font-family``    — set the fontFamily inline style on an element

The edit looks for the selector across every .tsx/.html/.css/.json file in
the site/ tree and applies a precise replacement. If multiple files match
we update the first one and report ``ambiguous: true`` so the UI can warn.

Every edit snapshots the site first — visual edits are still undoable.
Every edit is marked ``billable: false`` in the response: the whole point
is to give users a way to tweak presentation WITHOUT spending credits.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pebble.history import snapshot_site, diff_against_snapshot
from pebble.log import log
from pebble.engagement import log_event as _log_engagement
from pebble.security import project_lock, require_project_owner
from pebble.visual_ids import find_element_span, load_manifest


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


# ---- Inline-style helpers (surgical edits) --------------------------------

def _upsert_jsx_style(tag_text: str, prop: str, value: str) -> str:
    """Upsert ``style={{prop: 'value', ...}}`` into a JSX opening tag.

    React requires style to be an object literal in JSX, not a string —
    so for .tsx/.jsx files we always emit the object form. CSS property
    names are mapped to camelCase (font-size → fontSize, color → color).
    """
    is_self_closing = tag_text.endswith("/>")
    inner = tag_text[1:-1]
    if is_self_closing:
        inner = inner.rstrip("/").rstrip()

    # Convert CSS-hyphenated names (font-size → fontSize) to camelCase.
    # If the prop has no hyphens it is already camelCase — preserve it as-is
    # so callers can pass either form ("font-family" or "fontFamily").
    if "-" in prop:
        camel = re.sub(r"-([a-z])", lambda m: m.group(1).upper(), prop.lower())
    else:
        camel = prop

    sm = re.search(r"\bstyle\s*=\s*\{\{([^}]*)\}\}", inner)
    if sm:
        existing = sm.group(1).strip().rstrip(",").strip()
        prop_re = re.compile(r"\b" + re.escape(camel) + r"\s*:\s*['\"][^'\"]*['\"]")
        new_decl = f"{camel}: '{value}'"
        if prop_re.search(existing):
            new_obj = prop_re.sub(new_decl, existing)
        else:
            new_obj = (existing + ", " if existing else "") + new_decl
        new_inner = inner[:sm.start()] + f" style={{{{ {new_obj} }}}}" + inner[sm.end():]
    else:
        new_inner = inner + f" style={{{{ {camel}: '{value}' }}}}"
    return "<" + new_inner + (" />" if is_self_closing else ">")


def _upsert_html_style(tag_text: str, prop: str, value: str) -> str:
    """Upsert ``style="prop: value; ..."`` into an HTML opening tag."""
    is_self_closing = tag_text.endswith("/>")
    inner = tag_text[1:-1]
    if is_self_closing:
        inner = inner.rstrip("/").rstrip()

    sm = re.search(r'\bstyle\s*=\s*"([^"]*)"', inner)
    if sm:
        decls: dict[str, str] = {}
        for d in sm.group(1).split(";"):
            if ":" in d:
                k, v = d.split(":", 1)
                decls[k.strip().lower()] = v.strip()
        decls[prop.lower()] = value
        new_style = "; ".join(f"{k}: {v}" for k, v in decls.items() if v) + ";"
        new_inner = inner[:sm.start()] + f' style="{new_style}"' + inner[sm.end():]
    else:
        new_inner = inner + f' style="{prop}: {value};"'
    return "<" + new_inner + (" />" if is_self_closing else ">")


def _upsert_style(file_path: Path, tag_text: str, prop: str, value: str) -> str:
    """Pick JSX-style or HTML-style upsert based on file extension."""
    if file_path.suffix.lower() in (".tsx", ".jsx"):
        return _upsert_jsx_style(tag_text, prop, value)
    return _upsert_html_style(tag_text, prop, value)


# ---- Surgical edits via the pebble-id manifest ----------------------------

def _edit_text_by_id(site_dir: Path, pebble_id: str, manifest: dict,
                     original_text: str, new_text: str) -> Optional[dict]:
    """Surgical text edit using the manifest. Returns None to signal the
    caller should fall back to the substring heuristic."""
    entry = manifest.get(pebble_id)
    if not entry:
        return None
    file_path = site_dir / entry["file"]
    if not file_path.exists():
        return None
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        return None
    span = find_element_span(text, pebble_id)
    if not span:
        return None
    _, open_end, close_start, _ = span
    inner = text[open_end:close_start]

    # Transparent text-container wrappers: a motion primitive like
    # <RevealWords>Headline</RevealWords> or <CountUp suffix="+">480</CountUp>
    # wraps a single editable string. At runtime RevealWords splits the text
    # into per-word spans (spacing via CSS margins), so the live DOM
    # textContent the bridge captures is DE-SPACED ("OldTitle") and won't match
    # the spaced source. Treat the wrapper as transparent and edit the string
    # inside it directly, independent of original_text.
    _WRAPPER_RE = re.compile(
        r"^(\s*<(RevealWords|CountUp)\b[^>]*>)(.*?)(</\2>\s*)$",
        re.DOTALL,
    )
    wrap_m = _WRAPPER_RE.match(inner)
    if wrap_m:
        new_inner = wrap_m.group(1) + new_text + wrap_m.group(4)
    elif "<" in inner:
        # Has child elements — only replace if original_text appears verbatim.
        if not original_text or original_text not in inner:
            return None
        new_inner = inner.replace(original_text, new_text, 1)
    else:
        # Leaf text node — replace entire content.
        if original_text and original_text.strip() and original_text.strip() not in inner.strip():
            return None
        new_inner = new_text

    new_text_file = text[:open_end] + new_inner + text[close_start:]
    if new_text_file == text:
        return {"files_changed": [], "ambiguous": False, "replacements": 0}
    file_path.write_text(new_text_file, encoding="utf-8")
    return {
        "files_changed": [entry["file"]],
        "ambiguous":     False,
        "replacements":  1,
    }


def _edit_style_by_id(site_dir: Path, pebble_id: str, manifest: dict,
                      prop: str, value: str) -> Optional[dict]:
    """Surgical style upsert (color, font-size, etc.) using the manifest."""
    entry = manifest.get(pebble_id)
    if not entry:
        return None
    file_path = site_dir / entry["file"]
    if not file_path.exists():
        return None
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        return None
    span = find_element_span(text, pebble_id)
    if not span:
        return None
    open_start, open_end, _, _ = span
    tag_text = text[open_start:open_end]
    new_tag = _upsert_style(file_path, tag_text, prop, value)
    if new_tag == tag_text:
        return {"files_changed": [], "ambiguous": False}
    new = text[:open_start] + new_tag + text[open_end:]
    file_path.write_text(new, encoding="utf-8")
    return {
        "files_changed": [entry["file"]],
        "ambiguous":     False,
    }


# ---- Edit operations ------------------------------------------------------

def _candidate_files(site_dir: Path) -> list[Path]:
    """Files we'll search through for a visual edit. Keep this list tight:
    arbitrary scanning grows expensive as projects grow."""
    out: list[Path] = []
    for pattern in ("**/*.tsx", "**/*.jsx", "**/*.html", "**/*.css"):
        out.extend(site_dir.glob(pattern))
    return out


def _edit_text(site_dir: Path, original_text: str, new_text: str) -> dict:
    """Find ``original_text`` as a literal substring across the site and
    replace it with ``new_text``. Returns
    ``{files_changed, ambiguous, replacements}``.

    Safety: only matches if the original text appears in a JSX/text
    context (not inside an import or comment line). This is a heuristic —
    full AST analysis would be safer but is slow for a click handler.
    """
    if not original_text or not isinstance(original_text, str):
        return {"files_changed": [], "ambiguous": False, "replacements": 0}

    files_changed: list[str] = []
    total_replacements = 0
    for f in _candidate_files(site_dir):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if original_text not in text:
            continue
        # Apply replacement only on lines that look like JSX/text — skip
        # lines that look like an import or a code-only path.
        new = []
        local_count = 0
        for line in text.splitlines(keepends=True):
            stripped = line.lstrip()
            is_import = stripped.startswith("import ") or stripped.startswith("from ")
            is_comment = stripped.startswith("//") or stripped.startswith("/*")
            if not is_import and not is_comment and original_text in line:
                new_line = line.replace(original_text, new_text)
                local_count += new_line.count(new_text) - line.count(new_text)
                # ^ rough count delta; not perfect but good enough for UI feedback
                line = new_line
            new.append(line)
        new_text_file = "".join(new)
        if new_text_file != text:
            f.write_text(new_text_file, encoding="utf-8")
            files_changed.append(f.relative_to(site_dir).as_posix())
            total_replacements += local_count
    return {
        "files_changed": files_changed,
        "ambiguous":     len(files_changed) > 1,
        "replacements":  total_replacements,
    }


_COLOR_HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")


def _edit_color_for_selector(site_dir: Path, selector_hint: str, new_color: str) -> dict:
    """Crude color edit: find a hex literal near a string matching
    ``selector_hint`` (e.g. a className substring or a unique text snippet)
    and replace it. Best for the case where the user clicked an element
    that has a distinguishing class or text.
    """
    if not _COLOR_HEX_RE.match(new_color):
        return {"files_changed": [], "error": "new_color must be #RRGGBB"}
    files_changed: list[str] = []
    for f in _candidate_files(site_dir):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if selector_hint and selector_hint not in text:
            continue
        idx = text.find(selector_hint) if selector_hint else 0
        # Search 200 chars around the hint for the nearest hex color.
        start, end = max(0, idx - 200), min(len(text), (idx if selector_hint else 0) + 400)
        window = text[start:end]
        m = _COLOR_HEX_RE.search(window)
        if not m:
            continue
        replace_at = start + m.start()
        new_text = text[:replace_at] + new_color + text[replace_at + 7:]
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            files_changed.append(f.relative_to(site_dir).as_posix())
    return {
        "files_changed": files_changed,
        "ambiguous":     len(files_changed) > 1,
    }


_FONT_SIZE_RE = re.compile(r"(\"|')font-size(\"|'):\s*(\"|')(\d+(?:\.\d+)?)(px|rem|em)(\"|')")
_TAILWIND_TEXT_RE = re.compile(r"text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)\b")
_TW_SIZE_ORDER = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl", "7xl", "8xl", "9xl"]


def _edit_font_size_for_selector(site_dir: Path, selector_hint: str, delta: int) -> dict:
    """Bump font size up or down by ``delta`` Tailwind steps or by a
    proportional pixel/rem amount. Looks near ``selector_hint`` to scope
    the change."""
    if delta == 0:
        return {"files_changed": [], "details": "no change"}
    files_changed: list[str] = []
    for f in _candidate_files(site_dir):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if selector_hint and selector_hint not in text:
            continue
        idx = text.find(selector_hint) if selector_hint else 0
        start, end = max(0, idx - 200), min(len(text), (idx if selector_hint else 0) + 400)
        window = text[start:end]

        # Try Tailwind first.
        m_tw = _TAILWIND_TEXT_RE.search(window)
        if m_tw:
            current = m_tw.group(1)
            try:
                cur_idx = _TW_SIZE_ORDER.index(current)
            except ValueError:
                cur_idx = _TW_SIZE_ORDER.index("base")
            new_idx = max(0, min(len(_TW_SIZE_ORDER) - 1, cur_idx + delta))
            new_size = _TW_SIZE_ORDER[new_idx]
            if new_size == current:
                continue
            replace_at = start + m_tw.start()
            new_text = text[:replace_at] + f"text-{new_size}" + text[replace_at + len(m_tw.group(0)):]
            f.write_text(new_text, encoding="utf-8")
            files_changed.append(f.relative_to(site_dir).as_posix())
            continue

        # Fall back to inline font-size in CSS/JSX style.
        m_fs = _FONT_SIZE_RE.search(window)
        if m_fs:
            current = float(m_fs.group(4))
            unit = m_fs.group(5)
            step = 2 if unit == "px" else 0.125
            new_size = round(current + delta * step, 3)
            replacement = f'{m_fs.group(1)}font-size{m_fs.group(2)}: {m_fs.group(3)}{new_size}{unit}{m_fs.group(6)}'
            replace_at = start + m_fs.start()
            new_text = text[:replace_at] + replacement + text[replace_at + len(m_fs.group(0)):]
            f.write_text(new_text, encoding="utf-8")
            files_changed.append(f.relative_to(site_dir).as_posix())

    return {"files_changed": files_changed, "ambiguous": len(files_changed) > 1}


# Regex that matches an existing fontFamily inline-style value in JSX or HTML.
# Captures the value so we can replace it precisely.
_FONT_FAMILY_JSX_RE = re.compile(
    r"fontFamily\s*:\s*['\"]([^'\"]*)['\"]"
)
_FONT_FAMILY_CSS_RE = re.compile(
    r"font-family\s*:\s*([^;\"}>]+)"
)


def _edit_font_family_for_selector(
    site_dir: Path, selector_hint: str, new_font_family: str
) -> dict:
    """Inject or update a ``fontFamily`` inline style near ``selector_hint``.

    Strategy (in order):
    1. If ``fontFamily: '...'`` already exists in JSX style near the hint,
       replace the existing value.
    2. If ``font-family: ...`` exists in CSS near the hint, replace it.
    3. Otherwise, find the nearest opening JSX tag enclosing the hint text
       and upsert a style prop via ``_upsert_jsx_style``.

    Falls back gracefully — never raises.
    """
    if not new_font_family or not isinstance(new_font_family, str):
        return {"files_changed": [], "error": "new_font_family is required"}

    # Build the generic fallback value: "Font Name, sans-serif"
    # The caller can pass a family string with fallbacks already — we use it
    # verbatim. If there are no commas we append a generic fallback.
    value = new_font_family.strip()
    if "," not in value:
        # Determine a sensible generic: serif families get ", serif"
        _serif_hints = ("Playfair", "Merriweather", "Georgia", "Garamond",
                        "EB Garamond", "Lora", "Crimson", "PT Serif")
        _mono_hints  = ("Mono", "Code", "Courier", "Fira Code", "Source Code")
        if any(h.lower() in value.lower() for h in _serif_hints):
            fallback = "serif"
        elif any(h.lower() in value.lower() for h in _mono_hints):
            fallback = "monospace"
        else:
            fallback = "sans-serif"
        value = f"{value}, {fallback}"

    files_changed: list[str] = []

    for f in _candidate_files(site_dir):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if selector_hint and selector_hint not in text:
            continue

        idx = text.find(selector_hint) if selector_hint else 0
        start = max(0, idx - 300)
        end   = min(len(text), (idx if selector_hint else 0) + 500)
        window = text[start:end]

        # --- Case 1: existing JSX fontFamily prop in the window ---
        m_jsx = _FONT_FAMILY_JSX_RE.search(window)
        if m_jsx:
            new_decl = f"fontFamily: '{value}'"
            replace_at = start + m_jsx.start()
            replace_end = start + m_jsx.end()
            new_text = text[:replace_at] + new_decl + text[replace_end:]
            if new_text != text:
                f.write_text(new_text, encoding="utf-8")
                files_changed.append(f.relative_to(site_dir).as_posix())
            continue

        # --- Case 2: existing CSS font-family property in the window ---
        m_css = _FONT_FAMILY_CSS_RE.search(window)
        if m_css and f.suffix.lower() in (".css", ".html"):
            old_val = m_css.group(1)
            new_decl = f"font-family: {value}"
            replace_at = start + m_css.start()
            replace_end = start + m_css.end()
            new_text = text[:replace_at] + new_decl + text[replace_end:]
            if new_text != text:
                f.write_text(new_text, encoding="utf-8")
                files_changed.append(f.relative_to(site_dir).as_posix())
            continue

        # --- Case 3: find the opening tag that contains the hint and upsert ---
        # Locate the start of the enclosing tag (last "<" before idx).
        tag_start = text.rfind("<", 0, idx)
        if tag_start == -1:
            continue
        # Find the closing ">" of that tag (not closing tag, just the
        # opening angle-bracket group).
        tag_end = text.find(">", tag_start)
        if tag_end == -1:
            continue
        tag_text = text[tag_start:tag_end + 1]
        # Skip closing tags and comments.
        inner_tag = tag_text[1:].lstrip()
        if inner_tag.startswith("/") or inner_tag.startswith("!"):
            continue
        # Only mutate .tsx / .jsx files in the fallback case.
        if f.suffix.lower() not in (".tsx", ".jsx"):
            continue
        new_tag = _upsert_jsx_style(tag_text, "font-family", value)
        if new_tag == tag_text:
            continue
        new_text = text[:tag_start] + new_tag + text[tag_end + 1:]
        f.write_text(new_text, encoding="utf-8")
        files_changed.append(f.relative_to(site_dir).as_posix())

    return {
        "files_changed": files_changed,
        "ambiguous":     len(files_changed) > 1,
    }


# ---- Image-swap op --------------------------------------------------------

def _edit_image_swap(site_dir: Path, original_src: str, new_src: str) -> dict:
    """Replace every occurrence of ``original_src`` with ``new_src`` across
    all .tsx, .ts, and .css files in the site.

    This is intentionally a literal string replacement — no URL parsing or
    path normalisation. The caller (the workspace UI) passes the src exactly
    as it appears in the rendered DOM (``img.src`` or ``img.getAttribute("src")``),
    so a literal match is the safest and most predictable approach.

    Returns ``{files_changed: [...]}`` — ``ambiguous: false`` always because
    image-swap intentionally replaces ALL occurrences everywhere (you want the
    same photo swapped consistently across the site, not just one instance).
    """
    if not original_src or not isinstance(original_src, str):
        return {"files_changed": [], "error": "original_src is required"}
    if not new_src or not isinstance(new_src, str):
        return {"files_changed": [], "error": "new_src is required"}

    files_changed: list[str] = []
    # Scan .tsx, .ts, and .css — images live in JSX props and CSS url() calls.
    patterns = ("**/*.tsx", "**/*.ts", "**/*.css")
    for pattern in patterns:
        for f in site_dir.glob(pattern):
            try:
                text = f.read_text(encoding="utf-8")
            except Exception:
                continue
            if original_src not in text:
                continue
            new_text = text.replace(original_src, new_src)
            if new_text != text:
                f.write_text(new_text, encoding="utf-8")
                files_changed.append(f.relative_to(site_dir).as_posix())

    return {
        "files_changed": files_changed,
        "ambiguous":     False,
    }


# ---- Palette-swap op (global CSS variable update) -------------------------

import colorsys as _colorsys

_HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

# CSS variable names we allow palette-swap to target. Ordered so that
# the most common ones appear first for readability in the UI.
_PALETTE_VAR_NAMES = (
    "primary", "secondary", "accent",
    "background", "foreground",
    "primary-foreground", "secondary-foreground", "accent-foreground",
    "muted", "muted-foreground",
    "card", "card-foreground",
    "border", "ring",
)


def _hex_to_hsl_css(hex_color: str) -> str:
    """Convert #RRGGBB to Tailwind/shadcn HSL channel string 'H S% L%'."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    # colorsys uses HLS order, not HSL — note the swap.
    h_val, l_val, s_val = _colorsys.rgb_to_hls(r, g, b)
    return f"{round(h_val * 360, 1)} {round(s_val * 100, 1)}% {round(l_val * 100, 1)}%"


def _edit_palette_swap(site_dir: Path, palette: dict) -> dict:
    """Update CSS custom-property values in app/globals.css.

    ``palette`` maps variable names (without ``--``) to hex colors:
        {"primary": "#1a3a6b", "secondary": "#f5a623"}

    Only variables present in ``_PALETTE_VAR_NAMES`` are touched; any
    key outside the allowlist is silently ignored so the LLM can't
    inject arbitrary CSS.

    Returns ``{files_changed: [...]}`` or ``{files_changed: [], error: "..."}``.
    """
    if not palette or not isinstance(palette, dict):
        return {"files_changed": [], "error": "palette must be a non-empty dict"}

    # Validate every hex value up front.
    clean: dict[str, str] = {}
    for key, val in palette.items():
        if key not in _PALETTE_VAR_NAMES:
            continue  # silently skip unknown vars
        if not isinstance(val, str) or not _HEX_COLOR_RE.match(val):
            return {"files_changed": [], "error": f"invalid hex color for {key!r}: {val!r}"}
        clean[key] = val

    if not clean:
        return {"files_changed": []}

    # Resolve globals.css — try the shadcn/Tailwind default location first,
    # then fall back to a recursive search.
    candidates = [
        site_dir / "app" / "globals.css",
        site_dir / "styles" / "globals.css",
        site_dir / "globals.css",
    ]
    css_file: Path | None = next((p for p in candidates if p.exists()), None)
    if css_file is None:
        found = list(site_dir.glob("**/*.css"))
        css_file = next((p for p in found if "globals" in p.name.lower()), None)
    if css_file is None:
        return {"files_changed": [], "error": "globals.css not found in site"}

    try:
        original = css_file.read_text(encoding="utf-8")
    except Exception as e:
        return {"files_changed": [], "error": f"could not read globals.css: {e}"}

    text = original
    for var_name, hex_val in clean.items():
        hsl = _hex_to_hsl_css(hex_val)
        # Match:  --primary: <old value>;
        # The value is everything up to the next semicolon.
        pattern = re.compile(
            r"(--" + re.escape(var_name) + r"\s*:\s*)([^;]+)(;)"
        )
        text = pattern.sub(lambda m: m.group(1) + hsl + m.group(3), text)

    if text == original:
        return {"files_changed": []}

    try:
        css_file.write_text(text, encoding="utf-8")
    except Exception as e:
        return {"files_changed": [], "error": f"could not write globals.css: {e}"}

    return {"files_changed": [css_file.relative_to(site_dir).as_posix()]}


# ---- HTTP entry point ------------------------------------------------------

def run_visual_edit(handler) -> None:
    """POST /api/visual-edit. Body shape:

        { slug, op, selector_hint?, original_text?, new_text?,
          new_color?, delta?, new_font_family?, pebble_id? }

    ``op`` is one of ``text`` | ``color`` | ``font-size`` | ``font-family`` |
    ``image-swap`` | ``palette-swap``.
    The other fields are op-specific. Response includes ``billable: false``
    always — visual edits never spend credits.
    """
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length header"}); return
    if length <= 0:
        handler._json(400, {"error": "empty request body"}); return
    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    slug = body.get("slug")
    op = body.get("op")
    if not isinstance(slug, str) or not slug:
        handler._json(400, {"error": "slug is required"}); return
    _VALID_OPS = ("text", "color", "font-size", "font-family", "image-swap", "palette-swap")
    if op not in _VALID_OPS:
        handler._json(400, {"error": f"op must be one of: {', '.join(_VALID_OPS)}"}); return

    # Auth gate — see refine.py + the 2026-05-15 evening NLM pass.
    caller_uid = require_project_owner(handler, slug)
    if caller_uid is None:
        return

    site_dir = _output_dir() / slug / "site"
    if not site_dir.exists():
        handler._json(404, {"error": f"site not found: {slug}"}); return

    with project_lock(slug) as got_lock:
        if not got_lock:
            handler._json(409, {"error": "another edit is already in progress; try again in a moment"})
            return

        # Always snapshot first — visual edits are undoable.
        snap = snapshot_site(slug, reason=f"visual-edit-{op}", source=f"POST /api/visual-edit {op}")
        snapshot_id = snap.name if snap else None

        manifest = load_manifest(site_dir)
        pebble_id = body.get("pebble_id") or ""
        used_manifest = False

        try:
            result: Optional[dict] = None
            if op == "text":
                original = body.get("original_text", "")
                new = body.get("new_text", "")
                if pebble_id:
                    result = _edit_text_by_id(site_dir, pebble_id, manifest, original, new)
                    used_manifest = result is not None
                if result is None:
                    result = _edit_text(site_dir, original, new)
            elif op == "color":
                new_color = body.get("new_color", "")
                if not _COLOR_HEX_RE.match(new_color):
                    handler._json(400, {"error": "new_color must be #RRGGBB"}); return
                if pebble_id:
                    result = _edit_style_by_id(site_dir, pebble_id, manifest, "color", new_color)
                    used_manifest = result is not None
                if result is None:
                    hint = body.get("selector_hint") or body.get("original_text") or ""
                    result = _edit_color_for_selector(site_dir, hint, new_color)
            elif op == "font-size":
                new_font_size = (body.get("new_font_size") or "").strip()
                delta = int(body.get("delta", 0))
                if pebble_id and new_font_size:
                    result = _edit_style_by_id(site_dir, pebble_id, manifest, "font-size", new_font_size)
                    used_manifest = result is not None
                if result is None:
                    hint = body.get("selector_hint") or body.get("original_text") or ""
                    result = _edit_font_size_for_selector(site_dir, hint, delta)
            elif op == "font-family":
                new_font_family = (body.get("new_font_family") or "").strip()
                if not new_font_family:
                    handler._json(400, {"error": "new_font_family is required for font-family op"}); return
                if pebble_id:
                    # Pass the CSS-hyphenated name so _upsert_jsx_style's
                    # camelCase converter produces "fontFamily" correctly.
                    result = _edit_style_by_id(site_dir, pebble_id, manifest, "font-family", new_font_family)
                    used_manifest = result is not None
                if result is None:
                    hint = body.get("selector_hint") or body.get("original_text") or ""
                    result = _edit_font_family_for_selector(site_dir, hint, new_font_family)
            elif op == "image-swap":
                original_src = (body.get("original_src") or "").strip()
                new_src_val  = (body.get("new_src") or "").strip()
                if not original_src:
                    handler._json(400, {"error": "original_src is required for image-swap op"}); return
                if not new_src_val:
                    handler._json(400, {"error": "new_src is required for image-swap op"}); return
                result = _edit_image_swap(site_dir, original_src, new_src_val)
            else:  # palette-swap
                palette_raw = body.get("palette") or {}
                if not isinstance(palette_raw, dict) or not palette_raw:
                    handler._json(400, {"error": "palette must be a non-empty object"}); return
                result = _edit_palette_swap(site_dir, palette_raw)
        except Exception as e:
            log.warning("visual-edit failed: %s", e)
            handler._json(500, {"error": f"edit failed: {e}"}); return

        if result.get("error"):
            handler._json(400, {"error": result["error"]}); return

    # Phase 35 — diff panel data. Visual edits typically touch 1-2 files
    # so this is a cheap, exact diff. The UI shows it inline with the
    # change confirmation. Best-effort — failure leaves diff=None.
    diff_payload = None
    if snapshot_id:
        try:
            ds = diff_against_snapshot(slug, snapshot_id)
            if ds is not None:
                diff_payload = ds.to_dict()
        except Exception as _exc:
            log.warning("diff_against_snapshot failed (visual-edit %s): %s", op, _exc)

    handler._json(200, {
        "slug":          slug,
        "op":            op,
        "files_changed": result.get("files_changed", []),
        "ambiguous":     bool(result.get("ambiguous")),
        "billable":      False,
        "snapshot_id":   snapshot_id,
        "diff":          diff_payload,
        "used_manifest": used_manifest,
        "applied_at":    datetime.now(timezone.utc).isoformat(),
    })
    # Per-user engagement signal (T17). NEVER pass op/text/color/etc.
    _log_engagement(caller_uid, "visual_edit_used")

    # 2026-05-23 — Task C of Fly.io integration. Push the post-edit state
    # to the Fly app so the next /preview hit reflects the click-to-edit
    # change. No-ops when PEBBLE_PREVIEW_BACKEND isn't "fly".
    try:
        from pebble.fly_preview import deploy_in_background as _fly_bg_deploy
        _fly_bg_deploy(slug, site_dir)
    except Exception as _exc:
        log.info("[fly] background deploy hook errored after visual-edit for %s: %s", slug, _exc)


# ---- Iframe bridge script --------------------------------------------------

PEBBLE_VISUAL_EDIT_BRIDGE = r"""
/* Pebble visual-edit bridge — injected into every /preview/<slug>/ HTML
   response by the engine. Listens for clicks, looks up the nearest tagged
   ancestor (data-pebble-id), and posts a "pebble-select" message to the
   parent workspace.

   Hydration-safe: uses delegated event listeners on document via capture
   phase, so React hydration replacing nodes does not detach handlers. New
   elements added later still trigger the handler. Posts a "pebble-ready"
   message once installed so the workspace can show "click anywhere to edit"
   UI without guessing. */
(function() {
  if (window.__pebbleBridge && window.__pebbleBridge.installed) return;
  window.__pebbleBridge = { installed: true, ready: false, version: 2 };

  var STYLE_ID = "__pebble-bridge-styles";
  var style = document.getElementById(STYLE_ID);
  if (!style) {
    style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = ""
      + ".__pebble-hover{outline:2px dashed rgba(32,86,97,0.5)!important;"
      + "outline-offset:2px!important;cursor:pointer!important;}"
      + ".__pebble-selected{outline:2px solid #205661!important;"
      + "outline-offset:3px!important;}";
    (document.head || document.documentElement).appendChild(style);
  }

  var lastSelected = null;
  var lastHover = null;

  /* Walk up from a target node to the nearest ancestor carrying
     data-pebble-id. Falls back to the original node if none is tagged
     (e.g. an older build without injection). */
  function nearestTagged(node) {
    var cur = node;
    while (cur && cur.nodeType === 1) {
      if (cur.getAttribute && cur.getAttribute("data-pebble-id")) return cur;
      cur = cur.parentNode;
    }
    return node && node.nodeType === 1 ? node : null;
  }

  function describeElement(el) {
    if (!el || el.nodeType !== 1) return null;
    var tag = el.tagName.toLowerCase();
    var cls = (el.className && typeof el.className === "string") ? el.className.trim() : "";
    var id  = el.id || "";
    var pid = (el.getAttribute && el.getAttribute("data-pebble-id")) || "";
    var text = (el.textContent || "").trim().slice(0, 200);
    var rect = el.getBoundingClientRect();
    var cs = window.getComputedStyle(el);
    return {
      type:      "pebble-select",
      tag:       tag,
      id:        id,
      pebble_id: pid,
      className: cls,
      text:      text,
      rect:      { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
      style: {
        color:      cs.color,
        fontSize:   cs.fontSize,
        fontFamily: cs.fontFamily,
        background: cs.backgroundColor,
      },
      src: (tag === "img") ? (el.getAttribute("src") || el.src || "") : "",
    };
  }

  document.addEventListener("mouseover", function(e) {
    var el = nearestTagged(e.target);
    if (!el || el === lastSelected) return;
    if (lastHover && lastHover !== el) lastHover.classList.remove("__pebble-hover");
    lastHover = el;
    el.classList && el.classList.add("__pebble-hover");
  }, true);

  document.addEventListener("mouseout", function(e) {
    var el = nearestTagged(e.target);
    if (el && el.classList) el.classList.remove("__pebble-hover");
  }, true);

  document.addEventListener("click", function(e) {
    var el = nearestTagged(e.target);
    if (!el || el === document.body || el === document.documentElement) return;
    e.preventDefault();
    e.stopPropagation();
    if (lastSelected && lastSelected !== el) lastSelected.classList.remove("__pebble-selected");
    lastSelected = el;
    el.classList.add("__pebble-selected");
    var msg = describeElement(el);
    if (msg && window.parent !== window) {
      window.parent.postMessage(msg, "*");
    }
  }, true);

  /* Ready signal — posted once on install and again after DOMContentLoaded
     (so workspace UIs that mount after the iframe still get it). React
     hydration does not run again after this point in our generated sites. */
  function signalReady() {
    if (window.__pebbleBridge.ready) return;
    window.__pebbleBridge.ready = true;
    if (window.parent !== window) {
      window.parent.postMessage({ type: "pebble-ready", version: 2 }, "*");
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", signalReady, { once: true });
  } else {
    signalReady();
  }
})();
"""
