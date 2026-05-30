"""Tests for the appetizing-rich vibe block library (7 blocks).

Pattern mirrors tests/test_blocks_library.py.
"""
from pathlib import Path
from pebble.blocks.registry import BlockRegistry

LIBRARY_ROOT = Path(__file__).parent.parent / "pebble" / "blocks"


def test_hero_plate_appetizing_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/hero_plate_appetizing" in reg
    block = reg["library/hero_plate_appetizing"]
    assert block.metadata.block_type == "hero"
    assert "{{headline}}" in block.template_source
    assert "{{hero_image}}" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "{{cta_primary}}" in block.template_source
    assert block.metadata.slots["hero_image"].kind == "image"
    assert block.metadata.slots["hero_image"].pexels_query_template is not None
    assert "warm" in block.metadata.slots["hero_image"].pexels_query_template
    assert "appetizing" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_menu_grid_appetizing_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/menu_grid_appetizing" in reg
    block = reg["library/menu_grid_appetizing"]
    assert block.metadata.block_type == "services"
    assert "services" in block.metadata.slots
    assert block.metadata.slots["services"].kind == "list"
    assert "eyebrow" in block.metadata.slots
    assert "headline" in block.metadata.slots
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    assert "services_list_start" in block.template_source
    assert "{{services[].title}}" in block.template_source
    assert "{{services[].body}}" in block.template_source
    assert "{{services[].price}}" in block.template_source
    assert "appetizing" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_about_kitchen_appetizing_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/about_kitchen_appetizing" in reg
    block = reg["library/about_kitchen_appetizing"]
    assert block.metadata.block_type == "about"
    assert "portrait_image" in block.metadata.slots
    assert block.metadata.slots["portrait_image"].kind == "image"
    assert block.metadata.slots["portrait_image"].pexels_query_template is not None
    assert "chef" in block.metadata.slots["portrait_image"].pexels_query_template.lower()
    assert "story_paragraphs" in block.metadata.slots
    assert block.metadata.slots["story_paragraphs"].kind == "list"
    assert "story_paragraphs_list_start" in block.template_source
    assert "{{signature}}" in block.template_source
    assert "appetizing" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_testimonials_review_appetizing_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/testimonials_review_appetizing" in reg
    block = reg["library/testimonials_review_appetizing"]
    assert block.metadata.block_type == "testimonials"
    assert "quote" in block.metadata.slots
    assert "attribution" in block.metadata.slots
    assert "role" in block.metadata.slots
    assert "headshot_image" in block.metadata.slots
    assert block.metadata.slots["headshot_image"].kind == "image"
    assert block.metadata.slots["headshot_image"].pexels_query_template is not None
    assert "smiling" in block.metadata.slots["headshot_image"].pexels_query_template.lower()
    assert "{{quote}}" in block.template_source
    assert "{{attribution}}" in block.template_source
    assert "appetizing" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_pricing_prixfixe_appetizing_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/pricing_prixfixe_appetizing" in reg
    block = reg["library/pricing_prixfixe_appetizing"]
    assert block.metadata.block_type == "pricing"
    assert "tiers" in block.metadata.slots
    assert block.metadata.slots["tiers"].kind == "list"
    assert "eyebrow" in block.metadata.slots
    assert "headline" in block.metadata.slots
    assert "tiers_list_start" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "{{tiers[].name}}" in block.template_source
    assert "{{tiers[].price}}" in block.template_source
    assert "tiers[].features_list_start" in block.template_source
    assert "appetizing" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_contact_reservation_appetizing_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/contact_reservation_appetizing" in reg
    block = reg["library/contact_reservation_appetizing"]
    assert block.metadata.block_type == "contact"
    assert "form_slug" in block.metadata.slots
    assert "address" in block.metadata.slots
    assert "hours_text" in block.metadata.slots
    assert "phone" in block.metadata.slots
    assert "email" in block.metadata.slots
    assert "/api/forms/{{form_slug}}" in block.template_source
    assert "{{address}}" in block.template_source
    assert "{{hours_text}}" in block.template_source
    assert "appetizing" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_footer_warm_appetizing_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/footer_warm_appetizing" in reg
    block = reg["library/footer_warm_appetizing"]
    assert block.metadata.block_type == "footer"
    assert "links" in block.metadata.slots
    assert block.metadata.slots["links"].kind == "list"
    assert "business_name" in block.metadata.slots
    assert "year" in block.metadata.slots
    assert "tagline" in block.metadata.slots
    assert "links_list_start" in block.template_source
    assert "{{business_name}}" in block.template_source
    assert "{{year}}" in block.template_source
    assert "{{tagline}}" in block.template_source
    assert "appetizing" in block.metadata.vibe_tags
    assert block.metadata.palette_slots
