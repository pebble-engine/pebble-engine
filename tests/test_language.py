"""Tests for ``pebble.language`` — auto-detection + prompt-block emission.

Detection is heuristic so the threshold is "doesn't drift on realistic
free-text briefs." For each supported language we feed a representative
paragraph (the kind of thing a real small business owner would type into
``extra_context`` or ``notes_freeform``) and assert the right code falls
out.

The English path is the dominant case — a brief with no signal must
default to English without crashing.
"""
from __future__ import annotations

import pytest

from pebble.language import (
    LANGUAGES,
    detect_language,
    language_block,
    language_codes,
    language_display,
)


# ---- Registry sanity -----------------------------------------------------

def test_every_language_has_required_fields():
    for code, entry in LANGUAGES.items():
        assert isinstance(code, str) and code
        for required in ("english_name", "native_name", "html_lang", "sample"):
            assert entry.get(required), f"{code!r} missing {required}"


def test_language_codes_sorted():
    codes = language_codes()
    assert codes == sorted(codes)
    assert "en" in codes
    assert len(codes) >= 10  # bug-proof against accidental deletion


def test_language_display_fallback():
    """Unknown codes degrade to English so callers always get a usable dict."""
    out = language_display("xx-not-real")
    assert out == LANGUAGES["en"]


# ---- Detection: explicit override ----------------------------------------

def test_explicit_underscore_language_wins():
    """``_language`` on the brief beats heuristic detection."""
    brief = {"_language": "fr", "extra_context": "We are a yoga studio in Brooklyn."}
    assert detect_language(brief) == "fr"


def test_explicit_language_alias_also_honored():
    """``language`` (without underscore) is also accepted — both keys come
    from different code paths and we want both to do the same thing."""
    brief = {"language": "de", "extra_context": "yoga studio"}
    assert detect_language(brief) == "de"


def test_explicit_language_with_regional_subtag_reduces():
    """`es-MX` reduces to `es` — we keep the dialect out of the engine path.
    The HTML lang attribute is set from LANGUAGES['es']['html_lang']."""
    brief = {"_language": "es-MX"}
    assert detect_language(brief) == "es"


def test_unknown_explicit_language_degrades_to_english():
    """A bogus override doesn't force the prompt into 'lang=xx' country."""
    brief = {"_language": "xx-fake", "extra_context": "We bake bread."}
    assert detect_language(brief) == "en"


# ---- Detection: script-based (immediate giveaways) -----------------------

def test_detects_japanese_from_kana():
    brief = {
        "extra_context": "私たちは東京の小さなパン屋です。毎朝、自家製のサワードウを焼いています。"
    }
    assert detect_language(brief) == "ja"


def test_detects_chinese_from_han():
    brief = {
        "extra_context": "我们是一家位于上海的精品咖啡馆。每天提供新鲜烘焙的咖啡和手工糕点。"
    }
    assert detect_language(brief) == "zh"


def test_detects_korean_from_hangul():
    brief = {
        "extra_context": "서울 강남에 위치한 작은 디자인 스튜디오입니다. 브랜드 아이덴티티를 전문으로 합니다."
    }
    assert detect_language(brief) == "ko"


def test_detects_arabic():
    brief = {
        "extra_context": "نحن مطعم عائلي صغير في دبي نقدم المأكولات اللبنانية التقليدية والمشاوي الطازجة."
    }
    assert detect_language(brief) == "ar"


def test_detects_hebrew():
    brief = {
        "extra_context": "אנחנו סטודיו קטן ליוגה בתל אביב. שיעורים בוקר וערב, מתאים לכל הרמות."
    }
    assert detect_language(brief) == "he"


def test_detects_russian_vs_ukrainian():
    """Cyrillic with Ukrainian-specific letters should map to Ukrainian
    instead of Russian."""
    russian = {"extra_context": "Мы — небольшая семейная пекарня в Москве, выпекаем свежий хлеб каждое утро."}
    ukrainian = {"extra_context": "Ми — невелика сімейна пекарня в Києві, випікаємо свіжий хліб щоранку."}
    assert detect_language(russian) == "ru"
    assert detect_language(ukrainian) == "uk"


def test_detects_hindi_devanagari():
    brief = {
        "extra_context": "हम मुंबई में एक छोटा सा कैफे चलाते हैं। हम स्थानीय व्यंजन और ताज़ी कॉफ़ी परोसते हैं।"
    }
    assert detect_language(brief) == "hi"


# ---- Detection: function-word (Latin scripts) ----------------------------

def test_detects_spanish_from_function_words():
    brief = {
        "extra_context": (
            "Somos una panadería familiar en el barrio de Polanco. "
            "Hacemos el pan con harinas locales y nuestra masa madre tiene más de cinco años. "
            "Nos especializamos en panes artesanales y pasteles tradicionales."
        )
    }
    assert detect_language(brief) == "es"


def test_detects_french_from_function_words():
    brief = {
        "extra_context": (
            "Nous sommes une boulangerie familiale dans le 11ème arrondissement. "
            "Notre équipe travaille avec des farines bio et des fermentations longues. "
            "Tous nos pains et viennoiseries sont faits sur place chaque matin."
        )
    }
    assert detect_language(brief) == "fr"


def test_detects_german_from_function_words():
    brief = {
        "extra_context": (
            "Wir sind eine Familienbäckerei in Berlin Kreuzberg. "
            "Unsere Brote sind aus Bio-Mehl und unsere Sauerteig-Kultur ist über zehn Jahre alt. "
            "Das Team arbeitet jeden Morgen früh, damit das Brot zur Öffnungszeit fertig ist."
        )
    }
    assert detect_language(brief) == "de"


def test_detects_italian_from_function_words():
    brief = {
        "extra_context": (
            "Siamo una piccola panetteria di famiglia nel cuore di Trastevere. "
            "Il nostro pane è fatto con farine biologiche e la nostra pasta madre è di nostra produzione. "
            "Lavoriamo con amore e tradizione per offrirvi il meglio."
        )
    }
    assert detect_language(brief) == "it"


def test_detects_portuguese_from_function_words():
    brief = {
        "extra_context": (
            "Somos uma padaria familiar no centro de Lisboa. "
            "Os nossos pães são feitos com farinhas portuguesas e a nossa massa mãe tem mais de oito anos. "
            "Todos os dias trabalhamos para oferecer o melhor pão tradicional."
        )
    }
    assert detect_language(brief) == "pt"


def test_detects_dutch_from_function_words():
    brief = {
        "extra_context": (
            "Wij zijn een kleine familiebakkerij in het centrum van Amsterdam. "
            "Onze broden worden elke ochtend vers gebakken met lokaal meel. "
            "Wij werken met natuurlijke gisten en lange fermentatietijden."
        )
    }
    assert detect_language(brief) == "nl"


# ---- Defaults + edge cases -----------------------------------------------

def test_defaults_to_english_on_empty_brief():
    assert detect_language({}) == "en"
    assert detect_language({"extra_context": ""}) == "en"


def test_defaults_to_english_on_short_brief():
    """Less than six tokens of free text — refuse to guess, return en."""
    brief = {"extra_context": "Yoga studio"}
    assert detect_language(brief) == "en"


def test_defaults_to_english_on_ambiguous_input():
    """A brief that's mostly business-name + technical terms shouldn't
    confidently pick a non-English language. The 'margin over runner-up'
    rule in _word_signal handles this."""
    brief = {"extra_context": "ACME Industries. Booking, payment, SEO, CRM."}
    assert detect_language(brief) == "en"


def test_business_name_alone_does_not_force_a_language():
    """A Japanese brand name in a US business shouldn't flip the whole site
    to Japanese. The script-signal threshold is high enough (3 chars) that
    a brand-name with one kanji passes through to English."""
    brief = {"business_name": "Yamamoto Bagels"}
    assert detect_language(brief) == "en"


def test_corpus_includes_multiple_brief_fields():
    """Detection should consume extra_context + notes_freeform + services
    so the user has multiple paths to provide a language signal."""
    brief = {
        "business_name": "Acme",
        "extra_context": "",
        "notes_freeform": (
            "Por favor escribe el contenido en español. "
            "Tenemos clientes locales y queremos que se sientan cómodos. "
            "Nuestra empresa lleva diez años en el barrio."
        ),
        "services_offered": "",
    }
    assert detect_language(brief) == "es"


# ---- language_block emission --------------------------------------------

def test_english_returns_empty_block():
    """English is default — we don't waste prompt budget on a language
    instruction the LLM defaults to anyway."""
    assert language_block("en") == ""


def test_non_english_block_names_target_language():
    block = language_block("es")
    assert "Spanish" in block
    assert "Español" in block
    assert 'lang="es"' in block
    # The sample line confirms idiomatic tone
    assert LANGUAGES["es"]["sample"] in block


def test_block_mentions_html_lang_attribute():
    """Critical instruction — the foundation eval enforces <html lang>."""
    block = language_block("ja")
    assert 'lang="ja"' in block


def test_block_for_chinese_uses_correct_html_lang_subtag():
    """Chinese maps to lang=zh-Hans (simplified) because that's what the
    LANGUAGES registry says — script subtags matter to screen readers."""
    block = language_block("zh")
    assert 'lang="zh-Hans"' in block


def test_unknown_code_falls_back_safely():
    """``language_block`` mirrors ``language_display``'s fallback: bogus
    code returns the English block (which is empty)."""
    assert language_block("xx-fake") == ""


def test_block_explicitly_covers_a11y_strings():
    """The LLM has a tendency to leave aria-label in English. The prompt
    must mention this verbatim or the regression will show up live."""
    block = language_block("fr")
    assert "aria" in block.lower() or "accessibility" in block.lower()
    assert "alt text" in block.lower() or "alt" in block.lower()
