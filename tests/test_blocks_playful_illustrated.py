"""Tests for the playful-illustrated vibe block library (7 blocks)."""
from pathlib import Path
from pebble.blocks.registry import BlockRegistry

LIBRARY_ROOT = Path(__file__).parent.parent / "pebble" / "blocks"


def test_hero_bright_playful_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/hero_bright_playful" in reg
    block = reg["library/hero_bright_playful"]
    assert block.metadata.block_type == "hero"
    # Required slots present
    for slot in ("eyebrow", "headline", "subheadline", "cta_primary", "cta_secondary", "hero_image"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    # hero_image is an image slot with a Pexels query
    assert block.metadata.slots["hero_image"].kind == "image"
    assert block.metadata.slots["hero_image"].pexels_query_template is not None
    assert "bright" in block.metadata.slots["hero_image"].pexels_query_template.lower()
    # Template uses the slots
    assert "{{headline}}" in block.template_source
    assert "{{hero_image}}" in block.template_source
    assert "{{cta_primary}}" in block.template_source
    # Vibe tags
    assert "playful" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_services_cards_playful_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/services_cards_playful" in reg
    block = reg["library/services_cards_playful"]
    assert block.metadata.block_type == "services"
    # Required slots
    for slot in ("eyebrow", "headline", "services"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["services"].kind == "list"
    # Template uses list markers
    assert "services_list_start" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    # Vibe tags
    assert "playful" in block.metadata.vibe_tags
    assert "vibrant" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_about_origin_playful_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/about_origin_playful" in reg
    block = reg["library/about_origin_playful"]
    assert block.metadata.block_type == "about"
    # Required slots
    for slot in ("eyebrow", "headline", "story_paragraphs", "portrait_image", "signature"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["portrait_image"].kind == "image"
    assert block.metadata.slots["portrait_image"].pexels_query_template is not None
    assert "smiling" in block.metadata.slots["portrait_image"].pexels_query_template.lower()
    assert block.metadata.slots["story_paragraphs"].kind == "list"
    # Template
    assert "{{signature}}" in block.template_source
    assert "story_paragraphs_list_start" in block.template_source
    # Vibe tags
    assert "playful" in block.metadata.vibe_tags
    assert "friendly" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_testimonials_kids_playful_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/testimonials_kids_playful" in reg
    block = reg["library/testimonials_kids_playful"]
    assert block.metadata.block_type == "testimonials"
    # Required slots
    for slot in ("quote", "attribution", "role", "headshot_image"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["headshot_image"].kind == "image"
    assert block.metadata.slots["headshot_image"].pexels_query_template is not None
    assert "smiling" in block.metadata.slots["headshot_image"].pexels_query_template.lower()
    # Template
    assert "{{quote}}" in block.template_source
    assert "{{attribution}}" in block.template_source
    assert "{{role}}" in block.template_source
    # Vibe tags
    assert "playful" in block.metadata.vibe_tags
    assert "joyful" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_pricing_tiers_playful_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/pricing_tiers_playful" in reg
    block = reg["library/pricing_tiers_playful"]
    assert block.metadata.block_type == "pricing"
    # Required slots
    for slot in ("eyebrow", "headline", "tiers"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["tiers"].kind == "list"
    # Template uses list markers and slots
    assert "tiers_list_start" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    # Vibe tags
    assert "playful" in block.metadata.vibe_tags
    assert "friendly" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_contact_friendly_playful_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/contact_friendly_playful" in reg
    block = reg["library/contact_friendly_playful"]
    assert block.metadata.block_type == "contact"
    # Required slots
    for slot in ("eyebrow", "headline", "form_intro", "address", "hours_text", "phone", "email", "form_slug"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    # Form action must use form_slug
    assert "/api/forms/{{form_slug}}" in block.template_source
    assert "{{address}}" in block.template_source
    assert "{{hours_text}}" in block.template_source
    assert "{{phone}}" in block.template_source
    assert "{{email}}" in block.template_source
    # Vibe tags
    assert "playful" in block.metadata.vibe_tags
    assert "friendly" in block.metadata.vibe_tags
    assert block.metadata.palette_slots


def test_footer_pop_playful_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/footer_pop_playful" in reg
    block = reg["library/footer_pop_playful"]
    assert block.metadata.block_type == "footer"
    # Required slots
    for slot in ("business_name", "tagline", "year", "links"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["links"].kind == "list"
    # Template
    assert "links_list_start" in block.template_source
    assert "{{business_name}}" in block.template_source
    assert "{{year}}" in block.template_source
    assert "{{tagline}}" in block.template_source
    # Vibe tags
    assert "playful" in block.metadata.vibe_tags
    assert "vibrant" in block.metadata.vibe_tags
    assert block.metadata.palette_slots
