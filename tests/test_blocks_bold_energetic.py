from pathlib import Path
from pebble.blocks.registry import BlockRegistry

LIBRARY_ROOT = Path(__file__).parent.parent / "pebble" / "blocks"


def test_hero_strike_bold_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/hero_strike_bold" in reg
    block = reg["library/hero_strike_bold"]
    assert block.metadata.block_type == "hero"
    assert "{{headline}}" in block.template_source
    assert "{{hero_image}}" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "{{cta_primary}}" in block.template_source
    assert "{{cta_secondary}}" in block.template_source
    assert block.metadata.slots["hero_image"].kind == "image"
    assert block.metadata.slots["hero_image"].pexels_query_template is not None
    assert "intense" in block.metadata.slots["hero_image"].pexels_query_template
    assert "bold" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_services_grid_bold_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/services_grid_bold" in reg
    block = reg["library/services_grid_bold"]
    assert block.metadata.block_type == "services"
    assert "services" in block.metadata.slots
    assert block.metadata.slots["services"].kind == "list"
    assert "eyebrow" in block.metadata.slots
    assert "headline" in block.metadata.slots
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    assert "services_list_start" in block.template_source
    assert "bold" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_about_origin_bold_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/about_origin_bold" in reg
    block = reg["library/about_origin_bold"]
    assert block.metadata.block_type == "about"
    assert "portrait_image" in block.metadata.slots
    assert block.metadata.slots["portrait_image"].kind == "image"
    assert block.metadata.slots["portrait_image"].pexels_query_template is not None
    assert "intense" in block.metadata.slots["portrait_image"].pexels_query_template
    assert "story_paragraphs" in block.metadata.slots
    assert block.metadata.slots["story_paragraphs"].kind == "list"
    assert "{{signature}}" in block.template_source
    assert "story_paragraphs_list_start" in block.template_source
    assert "bold" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_testimonials_panel_bold_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/testimonials_panel_bold" in reg
    block = reg["library/testimonials_panel_bold"]
    assert block.metadata.block_type == "testimonials"
    assert "quote" in block.metadata.slots
    assert "attribution" in block.metadata.slots
    assert "role" in block.metadata.slots
    assert "headshot_image" in block.metadata.slots
    assert block.metadata.slots["headshot_image"].kind == "image"
    assert "intense" in block.metadata.slots["headshot_image"].pexels_query_template.lower()
    assert "{{quote}}" in block.template_source
    assert "{{attribution}}" in block.template_source
    assert "bold" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_pricing_tiers_bold_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/pricing_tiers_bold" in reg
    block = reg["library/pricing_tiers_bold"]
    assert block.metadata.block_type == "pricing"
    assert "tiers" in block.metadata.slots
    assert block.metadata.slots["tiers"].kind == "list"
    assert "eyebrow" in block.metadata.slots
    assert "headline" in block.metadata.slots
    assert "tiers_list_start" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "bold" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_contact_compact_bold_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/contact_compact_bold" in reg
    block = reg["library/contact_compact_bold"]
    assert block.metadata.block_type == "contact"
    assert "form_slug" in block.metadata.slots
    assert "address" in block.metadata.slots
    assert "hours_text" in block.metadata.slots
    assert "phone" in block.metadata.slots
    assert "email" in block.metadata.slots
    assert "/api/forms/{{form_slug}}" in block.template_source
    assert "{{address}}" in block.template_source
    assert "{{hours_text}}" in block.template_source
    assert "bold" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_footer_anchored_bold_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/footer_anchored_bold" in reg
    block = reg["library/footer_anchored_bold"]
    assert block.metadata.block_type == "footer"
    assert "links" in block.metadata.slots
    assert block.metadata.slots["links"].kind == "list"
    assert "business_name" in block.metadata.slots
    assert "year" in block.metadata.slots
    assert "tagline" in block.metadata.slots
    assert "links_list_start" in block.template_source
    assert "{{business_name}}" in block.template_source
    assert "{{year}}" in block.template_source
    assert "bold" in block.metadata.vibe_tags
    assert block.metadata.palette_slots
