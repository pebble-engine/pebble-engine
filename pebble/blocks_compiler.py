"""blocks_compiler — turn block_picks JSON into a runnable Next.js project.

Public API
----------
    compile_site(
        *,
        registry: BlockRegistry,
        block_picks: list[dict],
        palette: dict[str, str],
        out_dir: Path,
    ) -> None

Placeholder syntax supported
-----------------------------
  {{slot_name}}                   Scalar substitution from slot_values or palette.
  {{list_name_list_start}}        Begin iteration over slot_values[list_name].
  {{list_name_list_end}}          End iteration marker.
  {{list_name[].field}}           Access item["field"] inside list iteration.
  {{list_name[]}}                 Access the item itself (list of strings).
  {{outer[].inner_list_start}}    Begin nested inner list inside outer iteration.
  {{outer[].inner_list_end}}      End nested inner list.

All markers may appear wrapped in JSX comment syntax:
    {/* {{marker}} */}
which is stripped before processing so only the inner {{marker}} is matched.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pebble.blocks.registry import BlockRegistry

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

# Strip JSX comment wrappers:  {/* {{...}} */}  →  {{...}}
# We need to detect marker patterns both with and without comment wrappers.
_JSX_COMMENT_RE = re.compile(r'\{/\*\s*(\{\{[^}]*\}\})\s*\*/\}')

# A {{placeholder}} — any non-} chars inside double braces
_PLACEHOLDER_RE = re.compile(r'\{\{([^}]+)\}\}')

# Outer list markers (no [] prefix on the list name):
#   {{name_list_start}}  and  {{name_list_end}}
# These may be wrapped in JSX comments.
_OUTER_LIST_START_RE = re.compile(
    r'(?:\{/\*\s*)?\{\{(\w+)_list_start\}\}(?:\s*\*/\})?',
)
_OUTER_LIST_END_RE = re.compile(
    r'(?:\{/\*\s*)?\{\{(\w+)_list_end\}\}(?:\s*\*/\})?',
)

# Inner (nested) list markers inside an outer iteration scope:
#   {{outer[].inner_list_start}}  and  {{outer[].inner_list_end}}
# These may be wrapped in JSX comments.
def _inner_list_start_re(outer: str) -> re.Pattern[str]:
    return re.compile(
        rf'(?:\{{/\*\s*)?\{{\{{{re.escape(outer)}\[\]\.(\w+)_list_start\}}\}}(?:\s*\*/\}})?',
    )

def _inner_list_end_re(outer: str) -> re.Pattern[str]:
    return re.compile(
        rf'(?:\{{/\*\s*)?\{{\{{{re.escape(outer)}\[\]\.(\w+)_list_end\}}\}}(?:\s*\*/\}})?',
    )

# Import line pattern (top-of-file import statements)
_IMPORT_LINE_RE = re.compile(r'^import\s+.+;$', re.MULTILINE)


# ---------------------------------------------------------------------------
# Core rendering engine
# ---------------------------------------------------------------------------

def _render_block(template: str, slot_values: dict[str, Any], palette: dict[str, str]) -> str:
    """Render a single block template, expanding all placeholders.

    Processing order:
    1. Expand outermost list markers (outermost-first, recursively for nesting).
    2. Substitute remaining scalars from slot_values and palette.
    """
    # Step 1: expand list markers
    text = _expand_lists(template, slot_values=slot_values, palette=palette, outer_prefix=None)

    # Step 2: substitute scalars
    text = _substitute_scalars(text, slot_values=slot_values, palette=palette)

    return text


def _expand_lists(
    text: str,
    *,
    slot_values: dict[str, Any],
    palette: dict[str, str],
    outer_prefix: str | None,
) -> str:
    """Iteratively expand list markers in `text`.

    `outer_prefix` is set to the outer list-name when we are already inside an
    outer iteration scope (so we handle `{{outer[].inner_list_start}}` markers
    rather than bare `{{name_list_start}}` markers).
    """
    # Build a combined regex that finds the FIRST occurrence of any list-start
    # marker (either an outer marker, or an inner marker if outer_prefix is set).
    # We process one marker at a time, left-to-right, to handle nesting cleanly.

    while True:
        # Find the earliest list-start marker
        earliest_match = None
        earliest_list_name = None
        is_inner = False

        # Check for outer-style markers: {{name_list_start}}
        for m in _OUTER_LIST_START_RE.finditer(text):
            list_name = m.group(1)
            # Verify the end marker exists
            end_pat = re.compile(
                rf'(?:\{{/\*\s*)?\{{\{{{re.escape(list_name)}_list_end\}}\}}(?:\s*\*/\}})?',
                re.DOTALL,
            )
            end_m = end_pat.search(text, m.end())
            if end_m is None:
                continue  # malformed — skip
            if earliest_match is None or m.start() < earliest_match.start():
                earliest_match = m
                earliest_list_name = list_name
                is_inner = False

        if earliest_match is None:
            break  # no more list markers found

        list_name = earliest_list_name
        start_m = earliest_match

        # Find the matching end marker
        end_pat = re.compile(
            rf'(?:\{{/\*\s*)?\{{\{{{re.escape(list_name)}_list_end\}}\}}(?:\s*\*/\}})?',
            re.DOTALL,
        )
        end_m = end_pat.search(text, start_m.end())
        if end_m is None:
            break  # malformed template, stop

        # Extract the region between start and end markers
        inner_template = text[start_m.end():end_m.start()]

        # Get the list value from slot_values
        items = slot_values.get(list_name, [])

        # Render each item
        rendered_items = []
        for item in items:
            # Build item-scoped slot_values for substitution inside this region.
            # The item may be a dict (field access) or a scalar string ({{name[]}}).
            item_rendered = _render_list_item(
                inner_template,
                list_name=list_name,
                item=item,
                palette=palette,
                outer_slot_values=slot_values,
            )
            rendered_items.append(item_rendered)

        expanded = "".join(rendered_items)

        # Splice the expanded content back in place of the entire marker+body+marker
        text = text[:start_m.start()] + expanded + text[end_m.end():]

    return text


def _render_list_item(
    region: str,
    *,
    list_name: str,
    item: Any,
    palette: dict[str, str],
    outer_slot_values: dict[str, Any],
) -> str:
    """Render a single iteration of a list item within a region.

    Handles:
    - Nested list markers:  {{list_name[].sublist_list_start}} ... {{list_name[].sublist_list_end}}
    - Item field access:    {{list_name[].field}}
    - Item scalar:          {{list_name[]}}  (when item is a string/scalar)
    """
    text = region

    # First, expand any nested list markers of the form {{list_name[].inner_list_start}}
    text = _expand_nested_lists(text, list_name=list_name, item=item, palette=palette)

    # Then substitute {{list_name[].field}} and {{list_name[]}}
    if isinstance(item, dict):
        def replace_field(m: re.Match) -> str:
            ph = m.group(1)  # e.g. "services[].title"
            prefix = f"{list_name}[]."
            if ph.startswith(prefix):
                field = ph[len(prefix):]
                # Use empty string for optional fields (e.g. price on a dentist)
                # rather than leaving the placeholder in and failing the leak check.
                val = item.get(field, "")
                return str(val)
            return m.group(0)  # leave other placeholders alone
        text = _PLACEHOLDER_RE.sub(replace_field, text)
    else:
        # Scalar list item: substitute {{list_name[]}} with the item value
        scalar_pat = re.compile(r'\{\{' + re.escape(list_name) + r'\[\]\}\}')
        text = scalar_pat.sub(str(item), text)

    return text


def _expand_nested_lists(
    text: str,
    *,
    list_name: str,
    item: Any,
    palette: dict[str, str],
) -> str:
    """Expand nested list markers of the form:
        {{list_name[].inner_list_start}} ... {{list_name[].inner_list_end}}
    within a single outer-item's region.
    """
    if not isinstance(item, dict):
        return text

    # Pattern: {/* {{list_name[].inner_list_start}} */} or bare {{list_name[].inner_list_start}}
    start_re = re.compile(
        rf'(?:\{{/\*\s*)?\{{\{{{re.escape(list_name)}\[\]\.(\w+)_list_start\}}\}}(?:\s*\*/\}})?',
        re.DOTALL,
    )

    while True:
        start_m = start_re.search(text)
        if start_m is None:
            break

        inner_name = start_m.group(1)  # e.g. "features"

        end_re = re.compile(
            rf'(?:\{{/\*\s*)?\{{\{{{re.escape(list_name)}\[\]\.{re.escape(inner_name)}_list_end\}}\}}(?:\s*\*/\}})?',
            re.DOTALL,
        )
        end_m = end_re.search(text, start_m.end())
        if end_m is None:
            break  # malformed — stop

        inner_template = text[start_m.end():end_m.start()]
        inner_items = item.get(inner_name, [])

        rendered_items = []
        for inner_item in inner_items:
            # Nested items — substitute {{list_name[].inner_name[]}} (string list)
            # or {{list_name[].inner_name[].field}} (dict list)
            inner_text = inner_template
            if isinstance(inner_item, dict):
                def replace_inner_field(m: re.Match, _ln=list_name, _in=inner_name, _ii=inner_item) -> str:
                    ph = m.group(1)
                    prefix = f"{_ln}[].{_in}[]."
                    if ph.startswith(prefix):
                        field = ph[len(prefix):]
                        return str(_ii.get(field, f"{{{{{ph}}}}}"))
                    return m.group(0)
                inner_text = _PLACEHOLDER_RE.sub(replace_inner_field, inner_text)
            else:
                scalar_pat = re.compile(
                    r'\{\{' + re.escape(list_name) + r'\[\]\.' + re.escape(inner_name) + r'\[\]\}\}'
                )
                inner_text = scalar_pat.sub(str(inner_item), inner_text)
            rendered_items.append(inner_text)

        expanded = "".join(rendered_items)
        text = text[:start_m.start()] + expanded + text[end_m.end():]

    return text


def _substitute_scalars(text: str, *, slot_values: dict[str, Any], palette: dict[str, str]) -> str:
    """Replace {{name}} with slot_values[name] or palette[name], leaving unknowns intact."""
    def replace(m: re.Match) -> str:
        name = m.group(1)
        if name in slot_values and not isinstance(slot_values[name], list):
            return str(slot_values[name])
        if name in palette:
            return str(palette[name])
        return m.group(0)  # leave intact; will be caught by leak check

    return _PLACEHOLDER_RE.sub(replace, text)


# ---------------------------------------------------------------------------
# Import deduplication
# ---------------------------------------------------------------------------

def _extract_imports(text: str) -> tuple[list[str], str]:
    """Extract top-level import statements from text.

    Returns (imports_list, text_without_imports).
    Imports are lines that start with 'import ' and end with ';'.
    """
    imports: list[str] = []
    lines = text.split('\n')
    kept_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import ') and stripped.endswith(';'):
            imports.append(stripped)
        else:
            kept_lines.append(line)
    return imports, '\n'.join(kept_lines)


# ---------------------------------------------------------------------------
# JSX body extractor
# ---------------------------------------------------------------------------

# Matches the full-component wrapper shape produced by Next.js blocks:
#
#   export default function NAME() {
#     return (
#       <jsx>...</jsx>
#     );
#   }
#
# Captured group 1 is the inner JSX expression only.
_EXPORT_DEFAULT_FUNCTION_RE = re.compile(
    r'^\s*export\s+default\s+function\s+\w+\s*\(\s*\)\s*\{\s*return\s*\(\s*(.*?)\s*\)\s*;?\s*\}\s*$',
    re.DOTALL,
)


def _extract_jsx_body(source: str) -> str:
    """Strip the 'export default function NAME() { return (...); }' wrapper.

    If the pattern is found, returns only the captured JSX expression.
    If not found (e.g. bare JSX templates in tests), returns source unchanged.
    """
    m = _EXPORT_DEFAULT_FUNCTION_RE.match(source)
    if m:
        return m.group(1)
    return source


# Matches a "use client" / 'use client' directive (with optional semicolon).
_USE_CLIENT_RE = re.compile(r'''["']use client["'];?''')


def _normalize_section_source(source: str) -> str:
    """Return source with a single ``"use client";`` directive on line 1 iff the
    block declared one anywhere; otherwise return the stripped source unchanged.

    A ``"use client"`` directive is only valid as the first statement of a
    module, so when a block author (or the motion pass) includes it, we must
    guarantee it lands on line 1 — above the imports.
    """
    stripped = source.strip()
    if not _USE_CLIENT_RE.search(stripped):
        return stripped
    without = _USE_CLIENT_RE.sub("", stripped).strip()
    return '"use client";\n\n' + without


# ---------------------------------------------------------------------------
# page.tsx builder
# ---------------------------------------------------------------------------

_PAGE_TEMPLATE = """\
{imports}
{sections}
export default function Page() {{
  return (
    <main>
{section_tags}
    </main>
  );
}}
"""


def _build_page_tsx(rendered_blocks: list[tuple[str, str]]) -> str:
    """Build the page.tsx content from a list of (block_id, rendered_body) tuples.

    Each block body becomes a `Section{i:02d}` arrow component.
    All import statements are deduped and hoisted to the top.
    """
    all_imports: list[str] = []
    section_components: list[str] = []
    section_names: list[str] = []

    for i, (block_id, body) in enumerate(rendered_blocks):
        imports, clean_body = _extract_imports(body)
        for imp in imports:
            if imp not in all_imports:
                all_imports.append(imp)

        # Strip 'export default function NAME() { return (...); }' wrapper if present.
        # Real bakery blocks are full Next.js components; we only want the JSX body.
        clean_body = _extract_jsx_body(clean_body.strip())

        # Remove leading/trailing blank lines from the JSX body
        clean_body = clean_body.strip()

        section_name = f"Section{i:02d}"
        section_names.append(section_name)

        component = f"const {section_name} = () => (\n{clean_body}\n);\n"
        section_components.append(component)

    imports_block = '\n'.join(all_imports)
    sections_block = '\n'.join(section_components)
    section_tags_block = '\n'.join(f'      <{name} />' for name in section_names)

    return _PAGE_TEMPLATE.format(
        imports=imports_block,
        sections=sections_block,
        section_tags=section_tags_block,
    )


# ---------------------------------------------------------------------------
# Scaffolding writer
# ---------------------------------------------------------------------------

_PACKAGE_JSON = """\
{
  "name": "pebble-v2-site",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.41",
    "tailwindcss": "^3.4.10",
    "typescript": "^5.5.4"
  }
}
"""

_NEXT_CONFIG_MJS = """\
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.pexels.com' },
      { protocol: 'https', hostname: 'picsum.photos' },
      { protocol: 'https', hostname: 'fastly.picsum.photos' },
    ],
  },
};

export default nextConfig;
"""

_TSCONFIG_JSON = """\
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
"""

_TAILWIND_CONFIG_TS = """\
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
};

export default config;
"""

_POSTCSS_CONFIG_MJS = """\
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
"""

_APP_LAYOUT_TSX = """\
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pebble",
  description: "Built with Pebble",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
"""

_APP_GLOBALS_CSS = """\
@tailwind base;
@tailwind components;
@tailwind utilities;
"""


def _write_scaffolding(out_dir: Path) -> None:
    """Write the 7 scaffolding files needed for a runnable Next.js 14 project.

    Safe to call on an already-scaffolded directory — existing files are
    overwritten with the canonical versions.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    app_dir = out_dir / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "package.json").write_text(_PACKAGE_JSON, encoding="utf-8")
    (out_dir / "next.config.mjs").write_text(_NEXT_CONFIG_MJS, encoding="utf-8")
    (out_dir / "tsconfig.json").write_text(_TSCONFIG_JSON, encoding="utf-8")
    (out_dir / "tailwind.config.ts").write_text(_TAILWIND_CONFIG_TS, encoding="utf-8")
    (out_dir / "postcss.config.mjs").write_text(_POSTCSS_CONFIG_MJS, encoding="utf-8")
    (app_dir / "layout.tsx").write_text(_APP_LAYOUT_TSX, encoding="utf-8")
    (app_dir / "globals.css").write_text(_APP_GLOBALS_CSS, encoding="utf-8")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compile_site(
    *,
    registry: BlockRegistry,
    block_picks: list[dict],
    palette: dict[str, str],
    out_dir: Path,
) -> None:
    """Compile block_picks into a Next.js project at out_dir.

    Parameters
    ----------
    registry:
        Loaded BlockRegistry to look up templates from.
    block_picks:
        List of dicts with keys ``block_id`` and ``slot_values``.
    palette:
        Mapping of palette token names to CSS values (e.g. {"bg": "stone-50"}).
    out_dir:
        Directory to write the generated project into. Will be created if absent.
    """
    rendered_blocks: list[tuple[str, str]] = []

    for pick in block_picks:
        block_id = pick["block_id"]
        slot_values = pick.get("slot_values", {})

        block = registry[block_id]
        template = block.template_source

        rendered = _render_block(template, slot_values=slot_values, palette=palette)

        # Check for unfilled placeholders
        remaining = _PLACEHOLDER_RE.findall(rendered)
        if remaining:
            raise ValueError(
                f"unfilled placeholder(s) in {block_id}: {sorted(set(remaining))}"
            )

        rendered_blocks.append((block_id, rendered))

    # Build the page.tsx
    page_tsx = _build_page_tsx(rendered_blocks)

    # Write output
    app_dir = out_dir / "app"
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / "page.tsx").write_text(page_tsx, encoding="utf-8")

    # Write scaffolding (package.json, next.config.mjs, tsconfig.json,
    # tailwind.config.ts, postcss.config.mjs, app/layout.tsx, app/globals.css)
    _write_scaffolding(out_dir)
