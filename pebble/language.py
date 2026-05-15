"""Multi-language support — detection + prompt block.

Pebble auto-detects the target language from the brief's free-text
fields (extra_context, notes_freeform, business_name). If the user
has explicitly set ``_language`` on the brief, that override wins.

The LLM is excellent at writing in any language given clear
instructions, so the prompt template's job is to:

1. State the target language explicitly at the TOP of the prompt
   (override-priority framing — same posture as the DNA block).
2. Set the canonical BCP 47 code in ``<html lang="...">``.
3. Confirm in the Output checklist that EVERY copy string —
   headings, nav, CTAs, form labels, footer, alt text — uses the
   target language. The LLM has a tendency to drift back into
   English at low-attention boilerplate (placeholders, accessibility
   labels); the prompt addresses that directly.

This module never calls the LLM. Detection is heuristic — Unicode
script ranges first (Japanese/Chinese/Korean/Arabic/Hebrew/Russian
are immediate giveaways), then a small Latin-script function-word
list. Defaults to English when ambiguous.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Optional


# ---- Supported language registry -----------------------------------------

# BCP 47 code → (English name, Native name, instruction sample).
# Native names are what we show to the user; instruction samples appear
# in the prompt so the LLM has a per-language micro-anchor for "yes,
# this is what 'continue in this language' looks like in practice."
LANGUAGES: dict[str, dict] = {
    "en": {
        "english_name": "English",
        "native_name":  "English",
        "html_lang":    "en",
        "sample":       "Welcome — your trusted local team.",
    },
    "es": {
        "english_name": "Spanish",
        "native_name":  "Español",
        "html_lang":    "es",
        "sample":       "Bienvenido — tu equipo local de confianza.",
    },
    "fr": {
        "english_name": "French",
        "native_name":  "Français",
        "html_lang":    "fr",
        "sample":       "Bienvenue — votre équipe locale de confiance.",
    },
    "de": {
        "english_name": "German",
        "native_name":  "Deutsch",
        "html_lang":    "de",
        "sample":       "Willkommen — Ihr lokales Team Ihres Vertrauens.",
    },
    "it": {
        "english_name": "Italian",
        "native_name":  "Italiano",
        "html_lang":    "it",
        "sample":       "Benvenuto — il tuo team locale di fiducia.",
    },
    "pt": {
        "english_name": "Portuguese",
        "native_name":  "Português",
        "html_lang":    "pt",
        "sample":       "Bem-vindo — sua equipe local de confiança.",
    },
    "nl": {
        "english_name": "Dutch",
        "native_name":  "Nederlands",
        "html_lang":    "nl",
        "sample":       "Welkom — uw lokale team dat u kunt vertrouwen.",
    },
    "pl": {
        "english_name": "Polish",
        "native_name":  "Polski",
        "html_lang":    "pl",
        "sample":       "Witamy — twój lokalny zespół, któremu możesz zaufać.",
    },
    "sv": {
        "english_name": "Swedish",
        "native_name":  "Svenska",
        "html_lang":    "sv",
        "sample":       "Välkommen — ditt lokala team du kan lita på.",
    },
    "tr": {
        "english_name": "Turkish",
        "native_name":  "Türkçe",
        "html_lang":    "tr",
        "sample":       "Hoş geldiniz — güvenebileceğiniz yerel ekibiniz.",
    },
    "ja": {
        "english_name": "Japanese",
        "native_name":  "日本語",
        "html_lang":    "ja",
        "sample":       "ようこそ — 信頼できる地元のチーム。",
    },
    "ko": {
        "english_name": "Korean",
        "native_name":  "한국어",
        "html_lang":    "ko",
        "sample":       "환영합니다 — 신뢰할 수 있는 현지 팀.",
    },
    "zh": {
        "english_name": "Chinese (Simplified)",
        "native_name":  "中文",
        "html_lang":    "zh-Hans",
        "sample":       "欢迎 — 您值得信赖的本地团队。",
    },
    "ar": {
        "english_name": "Arabic",
        "native_name":  "العربية",
        "html_lang":    "ar",
        "sample":       "أهلاً بك — فريقك المحلي الموثوق به.",
    },
    "he": {
        "english_name": "Hebrew",
        "native_name":  "עברית",
        "html_lang":    "he",
        "sample":       "ברוכים הבאים — הצוות המקומי שלכם שאפשר לסמוך עליו.",
    },
    "ru": {
        "english_name": "Russian",
        "native_name":  "Русский",
        "html_lang":    "ru",
        "sample":       "Добро пожаловать — ваша надёжная местная команда.",
    },
    "uk": {
        "english_name": "Ukrainian",
        "native_name":  "Українська",
        "html_lang":    "uk",
        "sample":       "Ласкаво просимо — ваша надійна місцева команда.",
    },
    "id": {
        "english_name": "Indonesian",
        "native_name":  "Bahasa Indonesia",
        "html_lang":    "id",
        "sample":       "Selamat datang — tim lokal yang dapat Anda percayai.",
    },
    "vi": {
        "english_name": "Vietnamese",
        "native_name":  "Tiếng Việt",
        "html_lang":    "vi",
        "sample":       "Chào mừng — đội ngũ địa phương đáng tin cậy của bạn.",
    },
    "hi": {
        "english_name": "Hindi",
        "native_name":  "हिन्दी",
        "html_lang":    "hi",
        "sample":       "स्वागत है — आपकी विश्वसनीय स्थानीय टीम।",
    },
}


def language_codes() -> list[str]:
    """Sorted list of supported BCP 47 codes — useful for the v3 picker."""
    return sorted(LANGUAGES.keys())


def language_display(code: str) -> dict:
    """Return the LANGUAGES entry for ``code``, or English as a fallback.
    The returned dict is read-only by convention — don't mutate."""
    return LANGUAGES.get(code) or LANGUAGES["en"]


# ---- Script-based detection (immediate giveaways) ------------------------

# Each entry: (lang_code, predicate_on_char) — predicate returns True if
# the character belongs to that script's primary Unicode range.
def _is_japanese(c: str) -> bool:
    o = ord(c)
    # Hiragana 3040..309F, Katakana 30A0..30FF, Half-width Katakana FF66..FF9F
    return (0x3040 <= o <= 0x309F) or (0x30A0 <= o <= 0x30FF) or (0xFF66 <= o <= 0xFF9F)


def _is_korean(c: str) -> bool:
    o = ord(c)
    # Hangul syllables AC00..D7AF, Hangul Jamo 1100..11FF
    return (0xAC00 <= o <= 0xD7AF) or (0x1100 <= o <= 0x11FF)


def _is_chinese_han(c: str) -> bool:
    o = ord(c)
    # CJK Unified Ideographs 4E00..9FFF
    return 0x4E00 <= o <= 0x9FFF


def _is_arabic(c: str) -> bool:
    o = ord(c)
    return 0x0600 <= o <= 0x06FF


def _is_hebrew(c: str) -> bool:
    o = ord(c)
    return 0x0590 <= o <= 0x05FF


def _is_cyrillic(c: str) -> bool:
    o = ord(c)
    return 0x0400 <= o <= 0x04FF


def _is_devanagari(c: str) -> bool:
    o = ord(c)
    return 0x0900 <= o <= 0x097F


def _script_signal(text: str) -> Optional[str]:
    """Detect language by Unicode script when the signal is unambiguous.
    Returns a BCP 47 code or None to fall through to function-word
    detection."""
    counts = {
        "ja": 0,
        "ko": 0,
        "zh": 0,
        "ar": 0,
        "he": 0,
        "cyrillic": 0,
        "hi": 0,
    }
    for c in text:
        if _is_japanese(c):
            counts["ja"] += 1
        elif _is_korean(c):
            counts["ko"] += 1
        elif _is_chinese_han(c):
            counts["zh"] += 1
        elif _is_arabic(c):
            counts["ar"] += 1
        elif _is_hebrew(c):
            counts["he"] += 1
        elif _is_cyrillic(c):
            counts["cyrillic"] += 1
        elif _is_devanagari(c):
            counts["hi"] += 1

    # Need a meaningful run of the script to call it — a single emoji or
    # one stray Han character shouldn't tip the detector. Threshold of 3
    # rejects accidental hits while still firing on short business names.
    JP_THRESHOLD = 3
    if counts["ja"] >= JP_THRESHOLD:
        # Hiragana/Katakana present → almost certainly Japanese, even if
        # the page also has Han characters (which Japanese borrows).
        return "ja"
    if counts["ko"] >= JP_THRESHOLD:
        return "ko"
    # Han without kana → Chinese (Japanese rarely uses ONLY Han).
    if counts["zh"] >= JP_THRESHOLD and counts["ja"] == 0:
        return "zh"
    if counts["ar"] >= JP_THRESHOLD:
        return "ar"
    if counts["he"] >= JP_THRESHOLD:
        return "he"
    if counts["hi"] >= JP_THRESHOLD:
        return "hi"
    if counts["cyrillic"] >= JP_THRESHOLD:
        # Russian vs. Ukrainian disambiguation — Ukrainian uses 'і', 'ї', 'є', 'ґ';
        # Russian doesn't.
        if any(c in text for c in "іїєґ"):
            return "uk"
        return "ru"
    return None


# ---- Function-word detection (Latin scripts) -----------------------------

# Each entry: per-language set of high-frequency function words. We
# tokenize the input on word boundaries (Unicode-aware), lowercase,
# and count overlaps. The language with the highest match-count wins
# IF it clears a minimum threshold; otherwise default to English.
_FUNCTION_WORDS: dict[str, frozenset[str]] = {
    "en": frozenset({"the", "and", "for", "with", "you", "your", "our", "we", "are", "is", "of", "in", "on", "to", "this", "that"}),
    "es": frozenset({"el", "la", "los", "las", "de", "que", "en", "para", "con", "nuestro", "nuestra", "nuestros", "nuestras", "es", "un", "una", "su", "sus", "se", "le", "te", "del"}),
    "fr": frozenset({"le", "la", "les", "de", "des", "du", "et", "pour", "avec", "votre", "notre", "nos", "vos", "est", "un", "une", "ce", "cette", "ces", "que", "qui", "vous"}),
    "de": frozenset({"der", "die", "das", "und", "für", "mit", "ihre", "unsere", "ist", "ein", "eine", "wir", "sie", "von", "zu", "den", "dem", "des", "auf"}),
    "it": frozenset({"il", "la", "lo", "i", "gli", "le", "e", "di", "del", "della", "per", "con", "nostro", "nostra", "nostri", "nostre", "vostro", "vostra", "è", "un", "una"}),
    "pt": frozenset({"o", "a", "os", "as", "e", "de", "do", "da", "dos", "das", "para", "com", "nosso", "nossa", "seu", "sua", "é", "um", "uma", "que", "em", "no", "na"}),
    "nl": frozenset({"de", "het", "een", "en", "voor", "met", "onze", "uw", "wij", "is", "van", "in", "op", "te", "dat", "die", "naar", "bij"}),
    "pl": frozenset({"i", "w", "na", "z", "do", "od", "dla", "nasze", "nasz", "naszej", "twój", "twoja", "jest", "są", "się", "który", "która"}),
    "sv": frozenset({"och", "för", "med", "din", "ditt", "dina", "vår", "vårt", "våra", "är", "vi", "ni", "han", "hon", "den", "det", "att", "som", "av"}),
    "tr": frozenset({"ve", "bir", "için", "ile", "size", "bizim", "sizin", "olan", "var", "yok", "şu", "bu", "bunlar", "şunlar"}),
    "id": frozenset({"dan", "untuk", "dengan", "yang", "anda", "kami", "kita", "saya", "ini", "itu", "adalah", "akan", "atau"}),
    "vi": frozenset({"và", "của", "cho", "với", "bạn", "chúng tôi", "là", "này", "đó", "có", "không", "để"}),
}


_WORD_RE = re.compile(r"\b[\w'’-]+\b", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    """Lowercased word tokens, Unicode-aware. Accents preserved (we want
    'también' to lose its 'también' shape so it matches Spanish dicts)."""
    return [m.group(0).lower() for m in _WORD_RE.finditer(text)]


def _word_signal(text: str) -> Optional[str]:
    """Score every supported language by overlap of function words; return
    the best fit if it exceeds a hit threshold. Designed to refuse calls
    on short or ambiguous input — we'd rather default to English than
    guess wrong on three words of marketing copy."""
    tokens = _tokenize(text)
    if len(tokens) < 6:
        # Too little signal — anything could match.
        return None

    scores: dict[str, int] = {code: 0 for code in _FUNCTION_WORDS}
    for tok in tokens:
        for code, vocab in _FUNCTION_WORDS.items():
            if tok in vocab:
                scores[code] += 1

    best_code = max(scores, key=lambda k: scores[k])
    best_score = scores[best_code]
    # Require BOTH absolute minimum (>= 3 hits) AND a margin over runner-up.
    runner_up = max(v for c, v in scores.items() if c != best_code) if len(scores) > 1 else 0
    if best_score < 3:
        return None
    if best_score - runner_up < 1:
        return None
    return best_code


# ---- Public API ----------------------------------------------------------

_BRIEF_TEXT_FIELDS = (
    "extra_context",
    "notes_freeform",
    "services_offered",
    "business_name",
    "audience",
)


def _coalesce_brief_text(brief: dict) -> str:
    """Concatenate the brief's free-text fields into one detection corpus.
    business_name comes last because it's often a brand-name (not a
    language signal) so we don't want it dominating short briefs."""
    parts: list[str] = []
    for key in _BRIEF_TEXT_FIELDS:
        val = brief.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
        elif isinstance(val, list):
            parts.extend(str(v) for v in val if isinstance(v, (str, int, float)))
    return "\n".join(parts)


def detect_language(brief: dict) -> str:
    """Pick the target language for this build.

    Order of precedence:

    1. ``_language`` set explicitly on the brief (BCP 47 code).
    2. ``language`` set explicitly on the brief (alias).
    3. Script-based detection on the concatenated free-text fields.
    4. Function-word detection on the same corpus.
    5. Default: ``"en"``.

    Always returns a code that's in :data:`LANGUAGES`. Unrecognised
    overrides degrade to English to avoid an "lang=xx-foo" attribute
    nobody understands.
    """
    explicit = (brief.get("_language") or brief.get("language") or "").strip().lower()
    if explicit:
        # Accept e.g. "es-MX" by reducing to the primary subtag.
        primary = explicit.split("-", 1)[0]
        if primary in LANGUAGES:
            return primary

    corpus = _coalesce_brief_text(brief)
    if not corpus:
        return "en"

    by_script = _script_signal(corpus)
    if by_script:
        return by_script

    by_words = _word_signal(corpus)
    if by_words:
        return by_words

    return "en"


def language_block(code: str) -> str:
    """Return the markdown block injected at the top of the prompt
    above (or below) the DNA block. Override-priority framing — the
    LLM defers to this when later sections include English placeholder
    copy in the boilerplate."""
    if code == "en" or code not in LANGUAGES:
        # English (or an unknown code we fall back to English on) doesn't
        # need a block — leaving it out also keeps the prompt shorter on
        # the dominant case.
        return ""
    lang = language_display(code)
    return (
        "---\n\n"
        "## LANGUAGE — WRITE EVERY STRING OF COPY IN THIS LANGUAGE\n\n"
        f"**Target language: {lang['english_name']} ({lang['native_name']}, BCP 47 `{code}`).**\n\n"
        f"Set `<html lang=\"{lang['html_lang']}\">` in `app/layout.tsx`. "
        f"Every single user-visible string in the generated site — headings, body, navigation, "
        f"footer, buttons, form labels, placeholders, alt text, page titles, meta descriptions, "
        f"toast messages, error messages — MUST be in {lang['english_name']}. There is NO "
        "exception for accessibility labels, aria attributes, or boilerplate. \n\n"
        f"Sample tone, for calibration: \"{lang['sample']}\"\n\n"
        "Treat industry terms naturally: if a phrase has no idiomatic translation, prefer the "
        "established loan-word over an awkward calque (e.g. \"e-commerce\", \"booking\", \"newsletter\" "
        "in many languages). When the brief itself contains English text (e.g. a brand name), "
        "keep proper nouns and brand names verbatim — everything else translates.\n\n"
        "Do NOT mix languages. Do NOT leave English placeholder strings as comments. "
        f"If this build's industry intel or any later skill block in this prompt has English "
        f"sample copy, treat it as a structural reference only and re-write the strings in "
        f"{lang['english_name']}.\n\n"
        "---\n"
    )
