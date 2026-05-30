from pathlib import Path
from pebble.blocks.registry import BlockRegistry

LIBRARY_ROOT = Path(__file__).parent.parent / "pebble" / "blocks"


def test_library_hero_artisan_warm_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/hero_artisan_warm" in reg
    block = reg["library/hero_artisan_warm"]
    assert "{{headline}}" in block.template_source
    assert "{{hero_image}}" in block.template_source
    assert block.metadata.slots["hero_image"].pexels_query_template is not None
    assert "industry_scene" in block.metadata.slots["hero_image"].pexels_query_template


def test_library_services_grid_cards_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/services_grid_cards" in reg
    block = reg["library/services_grid_cards"]
    assert block.metadata.block_type == "services"
    assert "services" in block.metadata.slots
    assert block.metadata.slots["services"].kind == "list"
    assert "eyebrow" in block.metadata.slots
    assert "headline" in block.metadata.slots
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    assert "services_list_start" in block.template_source
    assert block.metadata.palette_slots  # non-empty
    assert "clean" in block.metadata.vibe_tags


def test_library_about_story_portrait_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/about_story_portrait" in reg
    block = reg["library/about_story_portrait"]
    assert block.metadata.block_type == "about"
    assert "portrait_image" in block.metadata.slots
    assert block.metadata.slots["portrait_image"].kind == "image"
    assert block.metadata.slots["portrait_image"].pexels_query_template is not None
    assert "founder_role" in block.metadata.slots["portrait_image"].pexels_query_template
    assert "story_paragraphs" in block.metadata.slots
    assert block.metadata.slots["story_paragraphs"].kind == "list"
    assert "{{signature}}" in block.template_source
    assert block.metadata.palette_slots
    assert "warm" in block.metadata.vibe_tags


def test_library_testimonials_pullquote_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/testimonials_pullquote" in reg
    block = reg["library/testimonials_pullquote"]
    assert block.metadata.block_type == "testimonials"
    assert "quote" in block.metadata.slots
    assert "attribution" in block.metadata.slots
    assert "headshot_image" in block.metadata.slots
    assert block.metadata.slots["headshot_image"].kind == "image"
    assert "smiling" in block.metadata.slots["headshot_image"].pexels_query_template.lower()
    assert "{{quote}}" in block.template_source
    assert "{{attribution}}" in block.template_source
    assert block.metadata.palette_slots
    assert "minimal" in block.metadata.vibe_tags


def test_library_contact_form_sidebar_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/contact_form_sidebar" in reg
    block = reg["library/contact_form_sidebar"]
    assert block.metadata.block_type == "contact"
    assert "form_slug" in block.metadata.slots
    assert "address" in block.metadata.slots
    assert "hours_text" in block.metadata.slots
    # Form action must use form_slug placeholder
    assert "/api/forms/{{form_slug}}" in block.template_source
    assert "{{address}}" in block.template_source
    assert "{{hours_text}}" in block.template_source
    assert block.metadata.palette_slots
    assert "clean" in block.metadata.vibe_tags


def test_library_pricing_tiers_3up_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/pricing_tiers_3up" in reg
    block = reg["library/pricing_tiers_3up"]
    assert block.metadata.block_type == "pricing"
    assert "tiers" in block.metadata.slots
    assert block.metadata.slots["tiers"].kind == "list"
    assert "eyebrow" in block.metadata.slots
    assert "tiers_list_start" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert block.metadata.palette_slots
    assert "structured" in block.metadata.vibe_tags


def test_library_footer_horizontal_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/footer_horizontal" in reg
    block = reg["library/footer_horizontal"]
    assert block.metadata.block_type == "footer"
    assert "links" in block.metadata.slots
    assert block.metadata.slots["links"].kind == "list"
    assert "business_name" in block.metadata.slots
    assert "year" in block.metadata.slots
    assert "links_list_start" in block.template_source
    assert "{{business_name}}" in block.template_source
    assert "{{year}}" in block.template_source
    assert block.metadata.palette_slots
    assert "minimal" in block.metadata.vibe_tags
