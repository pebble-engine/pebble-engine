"""Tests for the editorial-minimal vibe block library."""
from pathlib import Path
from pebble.blocks.registry import BlockRegistry

LIBRARY_ROOT = Path(__file__).parent.parent / "pebble" / "blocks"

_EDITORIAL_VIBE = "editorial"


def _reg() -> BlockRegistry:
    return BlockRegistry.load(LIBRARY_ROOT)


# ---------------------------------------------------------------------------
# hero_fullbleed_editorial
# ---------------------------------------------------------------------------

def test_hero_fullbleed_editorial_loads():
    reg = _reg()
    assert "library/hero_fullbleed_editorial" in reg
    block = reg["library/hero_fullbleed_editorial"]
    assert block.metadata.block_type == "hero"
    assert "{{headline}}" in block.template_source
    assert "{{hero_image}}" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "{{cta_primary}}" in block.template_source
    assert block.metadata.slots["hero_image"].kind == "image"
    assert block.metadata.slots["hero_image"].pexels_query_template is not None
    assert "editorial" in block.metadata.slots["hero_image"].pexels_query_template
    assert _EDITORIAL_VIBE in block.metadata.vibe_tags
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# services_grid_editorial
# ---------------------------------------------------------------------------

def test_services_grid_editorial_loads():
    reg = _reg()
    assert "library/services_grid_editorial" in reg
    block = reg["library/services_grid_editorial"]
    assert block.metadata.block_type == "services"
    assert "services" in block.metadata.slots
    assert block.metadata.slots["services"].kind == "list"
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    assert "services_list_start" in block.template_source
    assert _EDITORIAL_VIBE in block.metadata.vibe_tags
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# about_statement_editorial
# ---------------------------------------------------------------------------

def test_about_statement_editorial_loads():
    reg = _reg()
    assert "library/about_statement_editorial" in reg
    block = reg["library/about_statement_editorial"]
    assert block.metadata.block_type == "about"
    assert "portrait_image" in block.metadata.slots
    assert block.metadata.slots["portrait_image"].kind == "image"
    assert block.metadata.slots["portrait_image"].pexels_query_template is not None
    assert "story_paragraphs" in block.metadata.slots
    assert block.metadata.slots["story_paragraphs"].kind == "list"
    assert "{{signature}}" in block.template_source
    assert "story_paragraphs_list_start" in block.template_source
    assert _EDITORIAL_VIBE in block.metadata.vibe_tags
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# testimonials_press_editorial
# ---------------------------------------------------------------------------

def test_testimonials_press_editorial_loads():
    reg = _reg()
    assert "library/testimonials_press_editorial" in reg
    block = reg["library/testimonials_press_editorial"]
    assert block.metadata.block_type == "testimonials"
    assert "quote" in block.metadata.slots
    assert "attribution" in block.metadata.slots
    assert "role" in block.metadata.slots
    assert "headshot_image" in block.metadata.slots
    assert block.metadata.slots["headshot_image"].kind == "image"
    assert "{{quote}}" in block.template_source
    assert "{{attribution}}" in block.template_source
    assert _EDITORIAL_VIBE in block.metadata.vibe_tags
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# pricing_tiers_editorial
# ---------------------------------------------------------------------------

def test_pricing_tiers_editorial_loads():
    reg = _reg()
    assert "library/pricing_tiers_editorial" in reg
    block = reg["library/pricing_tiers_editorial"]
    assert block.metadata.block_type == "pricing"
    assert "tiers" in block.metadata.slots
    assert block.metadata.slots["tiers"].kind == "list"
    assert "eyebrow" in block.metadata.slots
    assert "headline" in block.metadata.slots
    assert "tiers_list_start" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    assert _EDITORIAL_VIBE in block.metadata.vibe_tags
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# contact_inquiry_editorial
# ---------------------------------------------------------------------------

def test_contact_inquiry_editorial_loads():
    reg = _reg()
    assert "library/contact_inquiry_editorial" in reg
    block = reg["library/contact_inquiry_editorial"]
    assert block.metadata.block_type == "contact"
    assert "form_slug" in block.metadata.slots
    assert "address" in block.metadata.slots
    assert "hours_text" in block.metadata.slots
    assert "phone" in block.metadata.slots
    assert "email" in block.metadata.slots
    assert "/api/forms/{{form_slug}}" in block.template_source
    assert "{{address}}" in block.template_source
    assert "{{hours_text}}" in block.template_source
    assert _EDITORIAL_VIBE in block.metadata.vibe_tags
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# footer_minimal_editorial
# ---------------------------------------------------------------------------

def test_footer_minimal_editorial_loads():
    reg = _reg()
    assert "library/footer_minimal_editorial" in reg
    block = reg["library/footer_minimal_editorial"]
    assert block.metadata.block_type == "footer"
    assert "links" in block.metadata.slots
    assert block.metadata.slots["links"].kind == "list"
    assert "business_name" in block.metadata.slots
    assert "year" in block.metadata.slots
    assert "links_list_start" in block.template_source
    assert "{{business_name}}" in block.template_source
    assert "{{year}}" in block.template_source
    assert _EDITORIAL_VIBE in block.metadata.vibe_tags
    assert block.metadata.palette_slots
