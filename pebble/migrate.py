"""Site migration — pull semantic facts from an existing public URL so
the user can switch to Pebble without re-typing everything.

The entry point is :func:`extract_from_url`, which:

1. Fetches the URL via :mod:`pebble.url_fetch`'s SSRF-hardened path
   (private-IP block, multi-record DNS check, manual redirect following,
   IP pinning to defeat DNS rebinding).
2. Parses with the stdlib :mod:`html.parser` — no external deps, no
   selenium, no Playwright.
3. Walks the DOM tree collecting structured facts: title, meta
   description, OpenGraph tags, every heading (h1-h3), nav link text,
   contact info (phone via regex, mailto links), image hosts, dominant
   inline-style colors, and a rough text body for industry inference.
4. Maps the result into a partial :class:`Brief` shape the engine's
   intake already understands.

The implementation is intentionally heuristic — best-effort extraction,
no scraping arms race. Sites that block bots or hide everything behind
client-side rendering will return a thin extraction with whatever we
could find. We never raise; the caller always gets a dict.

Why this matters: Base44's "Migrate from another platform" entry was
the single most explicit acquisition path I saw in the competitor
audit. Pebble's version of the same UX needs to be Pebble-honest —
we don't pretend to clone the site, we extract facts that pre-fill
the existing intake.
"""
from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field, asdict
from html.parser import HTMLParser
from typing import Optional

from pebble.url_fetch import safe_fetch_html as _fetch_url


# ---- HTML parsing ---------------------------------------------------------

_PHONE_RE = re.compile(r"""
    (?:\+?1[\s.-]?)?              # optional country code
    \(?\d{3}\)?[\s.-]?           # area
    \d{3}[\s.-]?\d{4}            # local
""", re.VERBOSE)

_HEX_COLOR_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")

# Industry hints — same shape as ui/v3/lib/state.ts but kept inline so
# the engine can run independently. Order matters: first match wins.
_INDUSTRY_HINTS: list[tuple[str, str]] = [
    ("bakery", "bakery"), ("restaurant", "restaurant"),
    ("coffee", "cafe"), ("café", "cafe"), ("cafe", "cafe"),
    ("dentist", "dentist"), ("dental", "dentist"),
    ("yoga", "yoga_studio"), ("pilates", "yoga_studio"),
    ("plumb", "plumbing"), ("plumber", "plumbing"),
    ("hvac", "hvac"), ("heating and air", "hvac"), ("air conditioning", "hvac"),
    ("law firm", "law_firm"), ("attorney", "law_firm"), ("lawyer", "law_firm"),
    ("real estate", "real_estate"), ("realtor", "real_estate"),
    ("photograph", "photography"),
    ("therapist", "therapist"), ("counsel", "therapist"),
    ("hair salon", "hair_salon"), ("haircut", "hair_salon"),
    ("barber", "barbershop"),
    ("spa ", "spa"), ("massage", "spa"),
    ("gym", "gym"), ("fitness", "gym"), ("crossfit", "gym"),
    ("pet groom", "pet_grooming"), ("dog wash", "pet_grooming"),
    ("clean", "cleaning_service"), ("janitorial", "cleaning_service"),
    ("landscap", "landscaping"), ("lawn care", "landscaping"),
    ("construction", "construction"), ("contractor", "construction"),
    ("consult", "consultant"),
    ("agency", "agency"), ("studio", "agency"),
    ("jewel", "jeweler"),
    ("auto repair", "auto_repair"), ("mechanic", "auto_repair"),
    ("bakery", "bakery"),
]


@dataclass
class MigrationExtract:
    """The structured facts we pulled from a URL. Pre-filled into the
    Brief on the intake step. Empty fields just mean we couldn't find
    that thing — never a sign of an error."""
    url: str
    final_url: str = ""              # after redirects
    title: str = ""
    meta_description: str = ""
    og_title: str = ""
    og_description: str = ""
    headings: list[str] = field(default_factory=list)        # h1+h2 concatenated, deduped
    nav_links: list[str] = field(default_factory=list)       # nav anchor text
    phone: str = ""
    emails: list[str] = field(default_factory=list)
    image_count: int = 0
    image_hosts: list[str] = field(default_factory=list)     # unique hostnames
    color_hints: list[str] = field(default_factory=list)     # unique hex colors found in style/class
    text_sample: str = ""             # plain-text body up to ~1000 chars
    business_name_guess: str = ""
    business_type_guess: str = ""
    error: Optional[str] = None       # human-readable error if any
    raw_bytes: int = 0                # size of the fetched HTML

    def to_dict(self) -> dict:
        return asdict(self)

    def to_brief_partial(self) -> dict:
        """Map this extraction onto fields the engine's Brief understands."""
        return {
            "business_name":  self.business_name_guess or self.title,
            "business_type":  self.business_type_guess,
            "extra_context":  self._compose_context(),
            "_migrated_from": self.final_url or self.url,
        }

    def _compose_context(self) -> str:
        """Build a brief.extra_context paragraph the LLM can use."""
        bits: list[str] = []
        if self.title or self.og_title:
            bits.append(f"Existing site title: {self.og_title or self.title}.")
        desc = self.og_description or self.meta_description
        if desc:
            bits.append(f"Existing description: {desc}.")
        if self.phone:
            bits.append(f"Phone visible on site: {self.phone}.")
        if self.emails:
            bits.append(f"Contact emails: {', '.join(self.emails[:3])}.")
        if self.headings:
            top = "; ".join(self.headings[:4])
            bits.append(f"Top headings: {top}.")
        return " ".join(bits)


class _Extractor(HTMLParser):
    """Walks the DOM and accumulates facts into a MigrationExtract."""
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.out = MigrationExtract(url=base_url)
        self._stack: list[str] = []
        self._capture_buf: list[str] = []
        self._capture_tag: Optional[str] = None
        self._in_nav = False
        self._image_hosts: set[str] = set()
        self._color_set: set[str] = set()
        self._heading_set: set[str] = set()
        self._nav_link_buf = ""
        self._capturing_nav_link = False
        self._text_buf: list[str] = []
        self._in_script_or_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]):
        a = {k.lower(): (v or "") for k, v in attrs}
        self._stack.append(tag)
        if tag in ("script", "style"):
            self._in_script_or_style = True
            return

        if tag == "title":
            self._capture_tag = "title"; self._capture_buf = []
        elif tag == "meta":
            name = a.get("name", "").lower()
            prop = a.get("property", "").lower()
            content = a.get("content", "")
            if name == "description" and not self.out.meta_description:
                self.out.meta_description = content.strip()[:300]
            elif prop == "og:title" and not self.out.og_title:
                self.out.og_title = content.strip()[:200]
            elif prop == "og:description" and not self.out.og_description:
                self.out.og_description = content.strip()[:300]
            elif prop == "og:site_name" and not self.out.business_name_guess:
                self.out.business_name_guess = content.strip()[:120]
        elif tag in ("h1", "h2", "h3"):
            self._capture_tag = tag; self._capture_buf = []
        elif tag == "nav":
            self._in_nav = True
        elif tag == "a" and self._in_nav:
            self._capturing_nav_link = True; self._nav_link_buf = ""
        elif tag == "a":
            href = a.get("href", "")
            if href.startswith("mailto:"):
                addr = href[len("mailto:"):].split("?", 1)[0].strip()
                if addr and addr not in self.out.emails and len(self.out.emails) < 5:
                    self.out.emails.append(addr)
        elif tag == "img":
            self.out.image_count += 1
            src = a.get("src", "")
            if src:
                try:
                    host = urllib.parse.urlparse(src).netloc
                    if host: self._image_hosts.add(host)
                except Exception: pass

        # Inline style colors — captures brand palette hints
        style = a.get("style", "")
        if style:
            for m in _HEX_COLOR_RE.findall(style):
                self._color_set.add(m.lower())

    def handle_endtag(self, tag: str):
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()
        if tag in ("script", "style"):
            self._in_script_or_style = False
            return
        if tag == self._capture_tag:
            text = " ".join(self._capture_buf).strip()
            text = re.sub(r"\s+", " ", text)[:200]
            if tag == "title" and not self.out.title:
                self.out.title = text
            elif tag in ("h1", "h2", "h3") and text and text not in self._heading_set:
                self._heading_set.add(text)
                self.out.headings.append(text)
            self._capture_tag = None
        if tag == "nav":
            self._in_nav = False
        if tag == "a" and self._capturing_nav_link:
            label = re.sub(r"\s+", " ", self._nav_link_buf).strip()
            if label and label not in self.out.nav_links and len(self.out.nav_links) < 12:
                self.out.nav_links.append(label[:60])
            self._capturing_nav_link = False
            self._nav_link_buf = ""

    def handle_data(self, data: str):
        if self._in_script_or_style:
            return
        if self._capture_tag:
            self._capture_buf.append(data)
        if self._capturing_nav_link:
            self._nav_link_buf += data
        # General text body sample
        if len(self._text_buf) < 1100:
            stripped = data.strip()
            if stripped:
                self._text_buf.append(stripped)

    def finalize(self):
        text = " ".join(self._text_buf)[:1100]
        text = re.sub(r"\s+", " ", text)
        self.out.text_sample = text[:1000]
        self.out.image_hosts = sorted(self._image_hosts)[:5]
        self.out.color_hints = list(self._color_set)[:8]
        # Phone — scan title + headings + text body
        haystack = " ".join([self.out.title, self.out.meta_description] + self.out.headings + [text])
        m = _PHONE_RE.search(haystack)
        if m:
            self.out.phone = m.group(0).strip()
        # Business name guess priority: og:site_name (already set) > title before " — / | /  -"
        if not self.out.business_name_guess and self.out.title:
            for sep in (" | ", " — ", " - ", " :: "):
                if sep in self.out.title:
                    self.out.business_name_guess = self.out.title.split(sep)[0].strip()
                    break
            if not self.out.business_name_guess:
                self.out.business_name_guess = self.out.title.strip()[:80]
        # Industry guess
        haystack_lower = (self.out.title + " " + " ".join(self.out.headings) + " " + text).lower()
        for needle, key in _INDUSTRY_HINTS:
            if needle in haystack_lower:
                self.out.business_type_guess = key
                break


# ---- Public API -----------------------------------------------------------

def extract_from_url(url: str) -> MigrationExtract:
    """Fetch + extract semantic facts from a public URL. Always returns a
    MigrationExtract; the ``error`` field is set if anything went wrong."""
    final, body, n, err = _fetch_url(url)
    if err:
        out = MigrationExtract(url=url, final_url=final, error=err, raw_bytes=n)
        return out
    parser = _Extractor(base_url=final or url)
    try:
        parser.feed(body)
    except Exception as e:
        parser.out.error = f"parse error: {type(e).__name__}: {e}"
    parser.finalize()
    parser.out.final_url = final or url
    parser.out.raw_bytes = n
    return parser.out


__all__ = ["MigrationExtract", "extract_from_url"]
