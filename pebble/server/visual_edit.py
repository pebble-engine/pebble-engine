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

from pebble.history import snapshot_site
from pebble.log import log


def _engine():
    return sys.modules.get("pebble_engine") or sys.modules["__main__"]


def _output_dir() -> Path:
    return _engine().OUTPUT_DIR


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


# ---- HTTP entry point ------------------------------------------------------

def run_visual_edit(handler) -> None:
    """POST /api/visual-edit. Body shape:

        { slug, op, selector_hint?, original_text?, new_text?, new_color?, delta? }

    ``op`` is one of ``text`` | ``color`` | ``font-size``. The other fields
    are op-specific. Response includes ``billable: false`` always — visual
    edits never spend credits.
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
    if op not in ("text", "color", "font-size"):
        handler._json(400, {"error": "op must be 'text', 'color', or 'font-size'"}); return

    site_dir = _output_dir() / slug / "site"
    if not site_dir.exists():
        handler._json(404, {"error": f"site not found: {slug}"}); return

    # Always snapshot first — visual edits are undoable.
    snap = snapshot_site(slug, reason=f"visual-edit-{op}", source=f"POST /api/visual-edit {op}")
    snapshot_id = snap.name if snap else None

    try:
        if op == "text":
            original = body.get("original_text", "")
            new = body.get("new_text", "")
            result = _edit_text(site_dir, original, new)
        elif op == "color":
            hint = body.get("selector_hint") or body.get("original_text") or ""
            new_color = body.get("new_color", "")
            result = _edit_color_for_selector(site_dir, hint, new_color)
        else:  # font-size
            hint = body.get("selector_hint") or body.get("original_text") or ""
            delta = int(body.get("delta", 0))
            result = _edit_font_size_for_selector(site_dir, hint, delta)
    except Exception as e:
        log.warning("visual-edit failed: %s", e)
        handler._json(500, {"error": f"edit failed: {e}"}); return

    if result.get("error"):
        handler._json(400, {"error": result["error"]}); return

    handler._json(200, {
        "slug":          slug,
        "op":            op,
        "files_changed": result.get("files_changed", []),
        "ambiguous":     bool(result.get("ambiguous")),
        "billable":      False,
        "snapshot_id":   snapshot_id,
        "applied_at":    datetime.now(timezone.utc).isoformat(),
    })


# ---- Iframe bridge script --------------------------------------------------

PEBBLE_VISUAL_EDIT_BRIDGE = r"""
/* Pebble visual-edit bridge — injected into every /preview/<slug>/ HTML
   response by the engine. Listens for clicks, sends an "I clicked this"
   message to the parent workspace, draws a hover outline. */
(function() {
  if (window.__pebbleBridgeInstalled) return;
  window.__pebbleBridgeInstalled = true;

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
    document.head.appendChild(style);
  }

  var lastSelected = null;

  function describeElement(el) {
    if (!el || el.nodeType !== 1) return null;
    var tag = el.tagName.toLowerCase();
    var cls = (el.className && typeof el.className === "string") ? el.className.trim() : "";
    var id  = el.id || "";
    var text = (el.textContent || "").trim().slice(0, 200);
    var rect = el.getBoundingClientRect();
    var style = window.getComputedStyle(el);
    return {
      type: "pebble-select",
      tag: tag,
      id: id,
      className: cls,
      text: text,
      rect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
      style: {
        color:    style.color,
        fontSize: style.fontSize,
        fontFamily: style.fontFamily,
        background: style.backgroundColor,
      },
    };
  }

  document.addEventListener("mouseover", function(e) {
    if (e.target && e.target !== lastSelected) {
      e.target.classList && e.target.classList.add("__pebble-hover");
    }
  }, true);
  document.addEventListener("mouseout", function(e) {
    if (e.target) e.target.classList && e.target.classList.remove("__pebble-hover");
  }, true);
  document.addEventListener("click", function(e) {
    var el = e.target;
    if (!el || el === document.body) return;
    e.preventDefault();
    e.stopPropagation();
    if (lastSelected) lastSelected.classList.remove("__pebble-selected");
    lastSelected = el;
    el.classList.add("__pebble-selected");
    var msg = describeElement(el);
    if (msg && window.parent !== window) {
      window.parent.postMessage(msg, "*");
    }
  }, true);
})();
"""
