"""Inspiration-from-URL — extract DESIGN DNA from a user-pasted site.

Sibling of :mod:`pebble.migrate`. Migrate pulls *business facts* (name,
type, contact info) so a switching user doesn't re-type their content;
inspire pulls *aesthetic facts* (palette, typography, vibe) so a user
who likes the look of a site can pre-seed a Pebble build's style
direction. Different intent, different output shape.

Both endpoints fetch arbitrary user-supplied URLs, so this module also
hardens the fetch:

- Block ``file://``, ``ftp://``, ``data:``, etc. — http(s) only.
- Block private IPv4 ranges (RFC 1918), loopback, link-local, and the
  cloud-metadata IP 169.254.169.254. SSRF defense — without this, a
  malicious URL could probe the engine's internal network or read
  AWS/GCP/Azure metadata via the IMDS endpoint.
- Cap response size, content-type, and timeout.

The output (:class:`InspirationExtract`) maps cleanly onto a partial
brief the v3 questionnaire can pre-fill, *plus* a suggested DNA card
ID (matched against :mod:`style_dna`) so the live DNA preview can show
the user "your style direction starts here" before generation.
"""
from __future__ import annotations

import ipaddress
import re
import socket
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass, field, asdict
from html.parser import HTMLParser
from typing import Optional


# ---- Color and font extraction -------------------------------------------

_HEX_COLOR_RE = re.compile(r"#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\b")
_RGB_COLOR_RE = re.compile(
    r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)",
    re.IGNORECASE,
)
_FONT_FAMILY_RE = re.compile(
    r"font-family\s*:\s*([^;}\n]+)",
    re.IGNORECASE,
)

# Common font categorisations for vibe detection.
_SERIF_FAMILIES = {
    "georgia", "times", "times new roman", "garamond", "cormorant",
    "playfair", "merriweather", "lora", "fraunces", "spectral", "newsreader",
    "source serif", "roboto slab", "noto serif", "libre baskerville",
}
_MONO_FAMILIES = {
    "monaco", "menlo", "consolas", "courier", "courier new", "ibm plex mono",
    "geist mono", "jetbrains mono", "fira code", "source code", "iosevka",
    "space mono",
}


def _normalize_hex(raw: str) -> Optional[str]:
    """Return a lowercase 6-digit ``#RRGGBB`` or ``None`` if unparseable."""
    raw = raw.lstrip("#")
    if len(raw) == 3:
        raw = "".join(c * 2 for c in raw)
    if len(raw) != 6:
        return None
    try:
        int(raw, 16)
    except ValueError:
        return None
    return "#" + raw.lower()


def _rgb_to_hex(r: int, g: int, b: int) -> Optional[str]:
    if not all(0 <= v <= 255 for v in (r, g, b)):
        return None
    return f"#{r:02x}{g:02x}{b:02x}"


def _extract_colors(text: str) -> list[str]:
    """Pull every hex / rgb color out of CSS-bearing text. Returns
    duplicates preserved — caller does frequency analysis."""
    out: list[str] = []
    for m in _HEX_COLOR_RE.findall(text):
        norm = _normalize_hex(m)
        if norm:
            out.append(norm)
    for r, g, b in _RGB_COLOR_RE.findall(text):
        try:
            hx = _rgb_to_hex(int(r), int(g), int(b))
        except ValueError:
            continue
        if hx:
            out.append(hx)
    return out


def _extract_fonts(text: str) -> list[str]:
    """Pull font-family values out of CSS. Returns the FIRST family in
    each declaration (the primary; fallbacks are decorative)."""
    out: list[str] = []
    for decl in _FONT_FAMILY_RE.findall(text):
        # decl is something like:  "Inter", "Helvetica Neue", sans-serif
        first = decl.split(",", 1)[0].strip().strip("'\"").strip()
        if first and first.lower() not in {"inherit", "initial", "unset"}:
            out.append(first)
    return out


def _hex_brightness(hex_color: str) -> float:
    """Perceived brightness 0..1 (per ITU-R BT.601). Used to pick which
    extracted color is "background-y" (light) vs. "type-y" (dark)."""
    raw = hex_color.lstrip("#")
    if len(raw) != 6:
        return 0.5
    try:
        r, g, b = int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
    except ValueError:
        return 0.5
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def _classify_palette(colors: list[str]) -> dict:
    """Pick a primary/accent/background trio from a frequency-counted
    list of hex colors. Heuristic, not perfect — best-effort. The most
    common bright color becomes the background, the most common dark
    color becomes the type/primary, and the most saturated remaining
    color becomes the accent.
    """
    if not colors:
        return {"primary": "", "accent": "", "background": "", "all": []}

    counts = Counter(colors)
    # Dedup-with-counts, sorted by frequency desc then alphabetic.
    ordered = [c for c, _ in counts.most_common()]

    # Background: most common color with brightness >= 0.7
    background = next(
        (c for c in ordered if _hex_brightness(c) >= 0.7),
        "",
    )
    # Primary text/ink: most common color with brightness <= 0.25
    primary = next(
        (c for c in ordered if _hex_brightness(c) <= 0.25),
        "",
    )
    # Accent: highest-saturation color that isn't already chosen, in the
    # mid-brightness band (0.25..0.75) — that's where brand colors live.
    def _saturation(hx: str) -> float:
        raw = hx.lstrip("#")
        if len(raw) != 6:
            return 0.0
        r, g, b = int(raw[0:2], 16) / 255, int(raw[2:4], 16) / 255, int(raw[4:6], 16) / 255
        mx, mn = max(r, g, b), min(r, g, b)
        return 0.0 if mx == 0 else (mx - mn) / mx

    accent_candidates = [
        c for c in ordered
        if c not in {background, primary} and 0.15 < _hex_brightness(c) < 0.85
    ]
    accent_candidates.sort(key=_saturation, reverse=True)
    accent = accent_candidates[0] if accent_candidates else ""

    return {
        "primary":    primary,
        "accent":     accent,
        "background": background,
        "all":        ordered[:12],
    }


# ---- HTML parsing --------------------------------------------------------

@dataclass
class InspirationExtract:
    """Aesthetic signals pulled from a public URL.

    Empty fields just mean we couldn't find that thing — never an error.
    The ``error`` field is set only when the fetch / parse itself failed.
    """
    url: str
    final_url: str = ""
    error: Optional[str] = None
    raw_bytes: int = 0
    title: str = ""
    headline: str = ""             # first <h1> we saw
    subheading: str = ""           # first <h2> or <p> right after
    palette: dict = field(default_factory=dict)
    typography: dict = field(default_factory=dict)
    vibe: dict = field(default_factory=dict)
    suggested_dna: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_brief_partial(self) -> dict:
        """Map onto fields the v3 questionnaire pre-fills. Conservative —
        we only pre-seed style-direction context, never business facts.
        Use :func:`pebble.migrate.extract_from_url` for those."""
        bits: list[str] = []
        if self.headline:
            bits.append(f"Inspired by a site whose lead reads: \"{self.headline[:140]}\".")
        if self.suggested_dna and self.suggested_dna.get("label"):
            bits.append(
                f"The visual direction leans {self.suggested_dna['label']} "
                f"— {self.suggested_dna.get('reason', '')}."
            )
        descriptors = (self.vibe or {}).get("descriptors") or []
        if descriptors:
            bits.append(f"Mood signals: {', '.join(descriptors)}.")
        return {
            "extra_context":     " ".join(bits).strip(),
            "_inspired_by":      self.final_url or self.url,
            "_inspire_dna_hint": (self.suggested_dna or {}).get("id") or "",
        }


class _Extractor(HTMLParser):
    """Walks the DOM collecting aesthetic facts."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.headline = ""
        self.subheading = ""
        self._capture_tag: Optional[str] = None
        self._capture_buf: list[str] = []
        self._inline_css: list[str] = []
        self._inline_styles: list[str] = []
        self._in_style = False
        self._in_script = False
        self._stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        self._stack.append(tag)
        if tag == "script":
            self._in_script = True
            return
        if tag == "style":
            self._in_style = True
            self._capture_buf = []
            return
        if tag == "title":
            self._capture_tag = "title"
            self._capture_buf = []
        elif tag == "h1" and not self.headline:
            self._capture_tag = "h1"
            self._capture_buf = []
        elif tag in ("h2", "p") and self.headline and not self.subheading:
            self._capture_tag = tag
            self._capture_buf = []

        # Inline style attribute → CSS we can mine.
        style = a.get("style", "")
        if style:
            self._inline_styles.append(style)

    def handle_endtag(self, tag: str) -> None:
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()
        if tag == "script":
            self._in_script = False
            return
        if tag == "style":
            self._inline_css.append("".join(self._capture_buf))
            self._in_style = False
            self._capture_buf = []
            return
        if tag == self._capture_tag:
            text = " ".join(self._capture_buf).strip()
            text = re.sub(r"\s+", " ", text)[:240]
            if tag == "title":
                self.title = text
            elif tag == "h1":
                self.headline = text
            elif tag in ("h2", "p"):
                if text and len(text) > 8:  # skip stub paragraphs
                    self.subheading = text
            self._capture_tag = None
            self._capture_buf = []

    def handle_data(self, data: str) -> None:
        if self._in_script:
            return
        if self._in_style:
            self._capture_buf.append(data)
            return
        if self._capture_tag:
            self._capture_buf.append(data)

    def all_css_text(self) -> str:
        """Concatenate every CSS-bearing string on the page. Used by the
        color and font extractors."""
        return "\n".join(self._inline_css + self._inline_styles)


# ---- Vibe + DNA matching --------------------------------------------------

def _derive_vibe(palette: dict, fonts: dict) -> dict:
    """Distill a few high-level descriptors from the palette + fonts.
    These feed both the suggested-DNA matcher and the brief.extra_context
    line the v3 UI shows the user."""
    bg_brightness = _hex_brightness(palette.get("background") or "#ffffff")
    is_dark = bg_brightness < 0.4
    color_count = len(palette.get("all") or [])
    is_minimal = color_count <= 4
    is_maximal = color_count >= 9

    descriptors: list[str] = []
    descriptors.append("dark" if is_dark else "light")
    descriptors.append("minimal" if is_minimal else ("maximal" if is_maximal else "balanced"))

    display_lower = (fonts.get("display") or "").lower()
    if any(s in display_lower for s in _SERIF_FAMILIES):
        descriptors.append("serif")
    elif any(s in display_lower for s in _MONO_FAMILIES):
        descriptors.append("mono")
    elif display_lower:
        descriptors.append("sans")

    return {
        "is_dark":      is_dark,
        "is_minimal":   is_minimal,
        "color_count":  color_count,
        "descriptors":  descriptors,
    }


def _suggest_dna(palette: dict, fonts: dict, vibe: dict) -> dict:
    """Pick the closest DNA card from style_dna.DNA_CARDS based on the
    extracted vibe. Returns a dict with id/label/score/reason. Never
    raises — falls back to the default 'swiss_magazine' if the DNA
    module isn't importable."""
    try:
        from style_dna import DNA_CARDS
    except Exception:
        return {"id": "", "label": "", "score": 0.0, "reason": "DNA module unavailable"}

    is_dark = vibe.get("is_dark", False)
    is_minimal = vibe.get("is_minimal", True)
    descriptors = set(vibe.get("descriptors") or [])

    # Heuristic scoring: each DNA card gets points for matching axes.
    # Tuned from the palette_posture text in style_dna.py — not perfect,
    # but explainable. The "reason" field surfaces what we matched on.
    scores: list[tuple[float, dict, list[str]]] = []
    for card in DNA_CARDS:
        score = 0.0
        why: list[str] = []
        posture = (card.get("palette_posture") or "").lower()
        feel = (card.get("feel") or "").lower()
        display_font = (card.get("display_font") or "").lower()

        card_is_dark = ("black" in posture or "#000" in posture or "dark" in posture
                        or "phosphor" in posture or "neon" in posture)
        if is_dark == card_is_dark:
            score += 1.5
            why.append("dark page" if is_dark else "light page")

        card_is_serif = any(s in display_font for s in _SERIF_FAMILIES)
        card_is_mono = any(s in display_font for s in _MONO_FAMILIES)
        if "serif" in descriptors and card_is_serif:
            score += 2.0
            why.append("serif display")
        elif "mono" in descriptors and card_is_mono:
            score += 2.0
            why.append("mono display")
        elif ("sans" in descriptors and not card_is_serif and not card_is_mono):
            score += 1.0

        if is_minimal and ("minimal" in feel or "quiet" in feel or "editorial" in feel):
            score += 1.0
            why.append("minimal posture")
        if not is_minimal and ("maximal" in feel or "max" in card.get("id", "")):
            score += 1.0
            why.append("maximal posture")

        scores.append((score, card, why))

    scores.sort(key=lambda t: t[0], reverse=True)
    best_score, best_card, best_why = scores[0]
    return {
        "id":     best_card.get("id", ""),
        "label":  best_card.get("label", ""),
        "score":  round(best_score, 2),
        "reason": ", ".join(best_why) if best_why else "default match",
    }


# ---- Safe URL fetch (SSRF-hardened) --------------------------------------

_USER_AGENT = "PebbleBot/1.0 (+https://getpebble.net; inspiration extractor)"
_MAX_BYTES = 2 * 1024 * 1024  # 2 MB
_TIMEOUT = 10.0

# Hosts we refuse to resolve, even if the URL looks public. The cloud
# metadata IP is the one the cloud-provider IMDS endpoint listens on;
# without this an attacker could read EC2 instance credentials via SSRF.
_BLOCKED_HOSTNAMES = {"localhost"}


def _is_private_or_loopback(ip_str: str) -> bool:
    """True for any IP we should refuse to fetch from. Includes RFC 1918
    private ranges, loopback, link-local, multicast, reserved, and the
    169.254.169.254 cloud-metadata IP (which is link-local but worth
    naming explicitly because it's the SSRF target everyone forgets).
    """
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # unparseable → treat as suspicious, refuse
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_reserved
        or addr.is_unspecified
    )


def _resolve_safely(host: str) -> Optional[str]:
    """DNS-resolve ``host`` and return the first IP IF it's a public
    address; return ``None`` if all resolved IPs are private/loopback,
    if the hostname is in the blocklist, or if resolution fails. The
    caller must use the returned IP (or the original host with the IP
    pinned) to defeat DNS-rebinding — for now we just block on resolve.
    """
    if not host or host.lower() in _BLOCKED_HOSTNAMES:
        return None
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (socket.gaierror, OSError, UnicodeError):
        return None
    for info in infos:
        ip = info[4][0]
        if _is_private_or_loopback(ip):
            return None
    return infos[0][4][0] if infos else None


def _fetch_url_safe(url: str) -> tuple[str, str, int, Optional[str]]:
    """Same return shape as migrate._fetch_url, plus SSRF blocking.
    Returns (final_url, body, byte_count, error). Never raises."""
    if not isinstance(url, str) or not url.strip():
        return "", "", 0, "url is required"
    url = url.strip()
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return url, "", 0, f"unsupported scheme: {parsed.scheme}"
    if not parsed.hostname:
        return url, "", 0, "url has no host"
    if _resolve_safely(parsed.hostname) is None:
        return url, "", 0, "host resolves to a private or blocked address"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent":      _USER_AGENT,
            "Accept":          "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            # Re-validate the FINAL URL after redirects — a 30x could
            # have bounced us to an internal address.
            final_url = resp.geturl()
            final_parsed = urllib.parse.urlparse(final_url)
            if final_parsed.hostname and _resolve_safely(final_parsed.hostname) is None:
                return final_url, "", 0, "redirected to a private or blocked address"

            ct = resp.headers.get("Content-Type", "").lower()
            if "html" not in ct and "xml" not in ct and ct.strip() != "":
                return final_url, "", 0, f"non-HTML content type: {ct}"
            raw = resp.read(_MAX_BYTES + 1)
            if len(raw) > _MAX_BYTES:
                return final_url, "", len(raw), f"page exceeds {_MAX_BYTES // (1024*1024)} MB"
            charset = "utf-8"
            for part in ct.split(";"):
                part = part.strip().lower()
                if part.startswith("charset="):
                    charset = part.split("=", 1)[1].strip()
                    break
            try:
                text = raw.decode(charset, errors="replace")
            except LookupError:
                text = raw.decode("utf-8", errors="replace")
            return final_url, text, len(raw), None
    except urllib.error.HTTPError as e:
        return url, "", 0, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return url, "", 0, f"network error: {e.reason}"
    except socket.timeout:
        return url, "", 0, "timeout"
    except Exception as e:
        return url, "", 0, f"{type(e).__name__}: {e}"


# ---- Public API -----------------------------------------------------------

def extract_inspiration(url: str) -> InspirationExtract:
    """Fetch and analyse a public URL for aesthetic signals. Always
    returns an :class:`InspirationExtract`; the ``error`` field is set
    if anything went wrong, with empty palette/typography/vibe."""
    final_url, body, n, err = _fetch_url_safe(url)
    if err:
        return InspirationExtract(
            url=url, final_url=final_url, error=err, raw_bytes=n,
        )

    parser = _Extractor()
    try:
        parser.feed(body)
    except Exception as e:
        return InspirationExtract(
            url=url, final_url=final_url, error=f"parse error: {type(e).__name__}: {e}",
            raw_bytes=n,
        )

    css_text = parser.all_css_text()
    colors = _extract_colors(css_text)
    fonts = _extract_fonts(css_text)

    palette = _classify_palette(colors)
    font_counts = Counter(fonts)
    primary_font = font_counts.most_common(1)[0][0] if font_counts else ""
    # Display font heuristic: the font on h1/h2 — but we don't trace it
    # back from headings reliably without a full CSS engine. As a proxy,
    # pick the SECOND most common (often display vs. body), falling back
    # to the most common when there's only one.
    display_font = (
        font_counts.most_common(2)[1][0]
        if len(font_counts) >= 2 else primary_font
    )
    typography = {
        "display":      display_font,
        "body":         primary_font,
        "all_families": [f for f, _ in font_counts.most_common(8)],
    }

    vibe = _derive_vibe(palette, typography)
    suggested = _suggest_dna(palette, typography, vibe)

    return InspirationExtract(
        url=url,
        final_url=final_url or url,
        raw_bytes=n,
        title=parser.title,
        headline=parser.headline,
        subheading=parser.subheading,
        palette=palette,
        typography=typography,
        vibe=vibe,
        suggested_dna=suggested,
    )


__all__ = ["InspirationExtract", "extract_inspiration"]
