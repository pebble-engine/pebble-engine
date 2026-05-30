from pathlib import Path
from pebble.blocks.registry import BlockRegistry

BAKERY_ROOT = Path(__file__).parent.parent / "pebble" / "blocks"

def test_bakery_hero_artisan_loads():
    reg = BlockRegistry.load(BAKERY_ROOT)
    assert "bakery/hero_artisan" in reg
    block = reg["bakery/hero_artisan"]
    assert "{{headline}}" in block.template_source
    assert "{{hero_image}}" in block.template_source
    assert block.metadata.slots["hero_image"].pexels_query is not None
    assert "bread" in block.metadata.slots["hero_image"].pexels_query.lower()


def test_bakery_services_grid_loads():
    reg = BlockRegistry.load(BAKERY_ROOT)
    assert "bakery/services_grid" in reg
    block = reg["bakery/services_grid"]
    assert block.metadata.block_type == "services"
    assert "services" in block.metadata.slots
    assert block.metadata.slots["services"].kind == "list"
    assert "eyebrow" in block.metadata.slots
    assert "headline" in block.metadata.slots
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    assert "services_list_start" in block.template_source
    assert block.metadata.palette_slots  # non-empty


def test_bakery_about_story_loads():
    reg = BlockRegistry.load(BAKERY_ROOT)
    assert "bakery/about_story" in reg
    block = reg["bakery/about_story"]
    assert block.metadata.block_type == "about"
    assert "portrait_image" in block.metadata.slots
    assert block.metadata.slots["portrait_image"].kind == "image"
    assert block.metadata.slots["portrait_image"].pexels_query is not None
    assert "baker" in block.metadata.slots["portrait_image"].pexels_query.lower()
    assert "story_paragraphs" in block.metadata.slots
    assert block.metadata.slots["story_paragraphs"].kind == "list"
    assert "{{signature}}" in block.template_source
    assert block.metadata.palette_slots


def test_bakery_testimonials_quote_loads():
    reg = BlockRegistry.load(BAKERY_ROOT)
    assert "bakery/testimonials_quote" in reg
    block = reg["bakery/testimonials_quote"]
    assert block.metadata.block_type == "testimonials"
    assert "quote" in block.metadata.slots
    assert "attribution" in block.metadata.slots
    assert "headshot_image" in block.metadata.slots
    assert block.metadata.slots["headshot_image"].kind == "image"
    assert "smiling" in block.metadata.slots["headshot_image"].pexels_query.lower()
    assert "{{quote}}" in block.template_source
    assert "{{attribution}}" in block.template_source
    assert block.metadata.palette_slots


def test_bakery_contact_form_loads():
    reg = BlockRegistry.load(BAKERY_ROOT)
    assert "bakery/contact_form" in reg
    block = reg["bakery/contact_form"]
    assert block.metadata.block_type == "contact"
    assert "form_slug" in block.metadata.slots
    assert "address" in block.metadata.slots
    assert "hours_text" in block.metadata.slots
    # Form action must use form_slug placeholder
    assert "/api/forms/{{form_slug}}" in block.template_source
    assert "{{address}}" in block.template_source
    assert "{{hours_text}}" in block.template_source
    assert block.metadata.palette_slots


def test_bakery_pricing_simple_loads():
    reg = BlockRegistry.load(BAKERY_ROOT)
    assert "bakery/pricing_simple" in reg
    block = reg["bakery/pricing_simple"]
    assert block.metadata.block_type == "pricing"
    assert "tiers" in block.metadata.slots
    assert block.metadata.slots["tiers"].kind == "list"
    assert "eyebrow" in block.metadata.slots
    assert "tiers_list_start" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert block.metadata.palette_slots


def test_bakery_footer_compact_loads():
    reg = BlockRegistry.load(BAKERY_ROOT)
    assert "bakery/footer_compact" in reg
    block = reg["bakery/footer_compact"]
    assert block.metadata.block_type == "footer"
    assert "links" in block.metadata.slots
    assert block.metadata.slots["links"].kind == "list"
    assert "business_name" in block.metadata.slots
    assert "year" in block.metadata.slots
    assert "links_list_start" in block.template_source
    assert "{{business_name}}" in block.template_source
    assert "{{year}}" in block.template_source
    assert block.metadata.palette_slots
