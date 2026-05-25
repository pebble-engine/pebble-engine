# tests/test_palette_swap.py
import sys
import os
import tempfile
from pathlib import Path

# Make sure pebble package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


def _write_globals(tmp: Path, content: str) -> Path:
    app_dir = tmp / "app"
    app_dir.mkdir(parents=True, exist_ok=True)
    css = app_dir / "globals.css"
    css.write_text(content, encoding="utf-8")
    return css


CSS_SAMPLE = """\
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --accent: 210 40% 96.1%;
    --radius: 0.5rem;
  }
  .dark {
    --background: 222.2 84% 4.9%;
    --primary: 217.2 91.2% 59.8%;
  }
}
"""


def test_palette_swap_primary_hex():
    from pebble.server.visual_edit import _edit_palette_swap
    with tempfile.TemporaryDirectory() as tmp:
        site_dir = Path(tmp)
        _write_globals(site_dir, CSS_SAMPLE)
        result = _edit_palette_swap(site_dir, {"primary": "#1a3a6b"})
        assert result["files_changed"], "should have changed globals.css"
        css_text = (site_dir / "app" / "globals.css").read_text()
        # The new primary value should appear and the old one should be gone
        assert "221.2 83.2% 53.3%" not in css_text
        assert "--primary:" in css_text


def test_palette_swap_multiple_vars():
    from pebble.server.visual_edit import _edit_palette_swap
    with tempfile.TemporaryDirectory() as tmp:
        site_dir = Path(tmp)
        _write_globals(site_dir, CSS_SAMPLE)
        result = _edit_palette_swap(site_dir, {
            "primary": "#1a3a6b",
            "secondary": "#f5a623",
        })
        assert len(result["files_changed"]) >= 1
        css_text = (site_dir / "app" / "globals.css").read_text()
        # --primary old value should be gone from all occurrences
        assert "221.2 83.2% 53.3%" not in css_text
        # --secondary should now have the new hsl value, not the old one
        # Check that --secondary: no longer has the original value
        import re
        secondary_match = re.search(r"--secondary\s*:\s*([^;]+);", css_text)
        assert secondary_match is not None
        assert secondary_match.group(1).strip() != "210 40% 96.1%"


def test_palette_swap_no_globals_css():
    from pebble.server.visual_edit import _edit_palette_swap
    with tempfile.TemporaryDirectory() as tmp:
        site_dir = Path(tmp)
        # No globals.css — should return gracefully
        result = _edit_palette_swap(site_dir, {"primary": "#1a3a6b"})
        assert result["files_changed"] == []
        assert "error" in result


def test_palette_swap_invalid_hex():
    from pebble.server.visual_edit import _edit_palette_swap
    with tempfile.TemporaryDirectory() as tmp:
        site_dir = Path(tmp)
        _write_globals(site_dir, CSS_SAMPLE)
        result = _edit_palette_swap(site_dir, {"primary": "notahex"})
        assert result.get("error")


def test_palette_swap_empty_palette():
    from pebble.server.visual_edit import _edit_palette_swap
    with tempfile.TemporaryDirectory() as tmp:
        site_dir = Path(tmp)
        _write_globals(site_dir, CSS_SAMPLE)
        result = _edit_palette_swap(site_dir, {})
        assert result["files_changed"] == []
