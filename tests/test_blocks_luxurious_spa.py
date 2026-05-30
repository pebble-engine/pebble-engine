"""Tests for the luxurious-spa vibe block set (7 blocks).

Covers: registry load, block_type, required slots, slot kinds,
pexels_query_template presence, palette_slots, vibe_tags, and
key template placeholder presence.
"""
from pathlib import Path
from pebble.blocks.registry import BlockRegistry

LIBRARY_ROOT = Path(__file__).parent.parent / "pebble" / "blocks"


def test_hero_serene_luxe_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/hero_serene_luxe" in reg
    block = reg["library/hero_serene_luxe"]
    assert block.metadata.block_type == "hero"
    # Required slots
    for slot in ("eyebrow", "headline", "subheadline", "cta_primary", "cta_secondary", "hero_image"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    # hero_image is an image slot with a pexels query
    assert block.metadata.slots["hero_image"].kind == "image"
    assert block.metadata.slots["hero_image"].pexels_query_template is not None
    assert "industry_scene" in block.metadata.slots["hero_image"].pexels_query_template
    # Template has the placeholders
    assert "{{headline}}" in block.template_source
    assert "{{hero_image}}" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "{{cta_primary}}" in block.template_source
    # Palette and vibe
    assert block.metadata.palette_slots
    assert "luxurious" in block.metadata.vibe_tags
    assert "serene" in block.metadata.vibe_tags


def test_services_menu_luxe_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/services_menu_luxe" in reg
    block = reg["library/services_menu_luxe"]
    assert block.metadata.block_type == "services"
    for slot in ("eyebrow", "headline", "services"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["services"].kind == "list"
    assert block.metadata.slots["services"].pexels_query_template is not None
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    assert "services_list_start" in block.template_source
    assert block.metadata.palette_slots
    assert "luxurious" in block.metadata.vibe_tags
    assert "elegant" in block.metadata.vibe_tags


def test_about_ethos_luxe_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/about_ethos_luxe" in reg
    block = reg["library/about_ethos_luxe"]
    assert block.metadata.block_type == "about"
    for slot in ("eyebrow", "headline", "story_paragraphs", "portrait_image", "signature"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["portrait_image"].kind == "image"
    assert block.metadata.slots["portrait_image"].pexels_query_template is not None
    assert "founder_role" in block.metadata.slots["portrait_image"].pexels_query_template
    assert block.metadata.slots["story_paragraphs"].kind == "list"
    assert "{{signature}}" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "story_paragraphs_list_start" in block.template_source
    assert block.metadata.palette_slots
    assert "luxurious" in block.metadata.vibe_tags
    assert "serene" in block.metadata.vibe_tags


def test_testimonials_whisper_luxe_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/testimonials_whisper_luxe" in reg
    block = reg["library/testimonials_whisper_luxe"]
    assert block.metadata.block_type == "testimonials"
    for slot in ("quote", "attribution", "role", "headshot_image"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["headshot_image"].kind == "image"
    assert block.metadata.slots["headshot_image"].pexels_query_template is not None
    # Pexels query should reference portrait / soft light
    pq = block.metadata.slots["headshot_image"].pexels_query_template.lower()
    assert "portrait" in pq or "soft" in pq
    assert "{{quote}}" in block.template_source
    assert "{{attribution}}" in block.template_source
    assert "{{role}}" in block.template_source
    assert block.metadata.palette_slots
    assert "luxurious" in block.metadata.vibe_tags
    assert "muted" in block.metadata.vibe_tags


def test_pricing_tiers_luxe_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/pricing_tiers_luxe" in reg
    block = reg["library/pricing_tiers_luxe"]
    assert block.metadata.block_type == "pricing"
    for slot in ("eyebrow", "headline", "tiers"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["tiers"].kind == "list"
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    assert "tiers_list_start" in block.template_source
    assert block.metadata.palette_slots
    assert "luxurious" in block.metadata.vibe_tags
    assert "elegant" in block.metadata.vibe_tags


def test_contact_appointment_luxe_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/contact_appointment_luxe" in reg
    block = reg["library/contact_appointment_luxe"]
    assert block.metadata.block_type == "contact"
    for slot in ("eyebrow", "headline", "form_intro", "address", "hours_text", "phone", "email", "form_slug"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    # Form action must use the form_slug placeholder
    assert "/api/forms/{{form_slug}}" in block.template_source
    assert "{{address}}" in block.template_source
    assert "{{hours_text}}" in block.template_source
    assert "{{phone}}" in block.template_source
    assert "{{email}}" in block.template_source
    assert block.metadata.palette_slots
    assert "luxurious" in block.metadata.vibe_tags
    assert "serene" in block.metadata.vibe_tags


def test_footer_signature_luxe_loads():
    reg = BlockRegistry.load(LIBRARY_ROOT)
    assert "library/footer_signature_luxe" in reg
    block = reg["library/footer_signature_luxe"]
    assert block.metadata.block_type == "footer"
    for slot in ("business_name", "tagline", "year", "links"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["links"].kind == "list"
    assert "{{business_name}}" in block.template_source
    assert "{{year}}" in block.template_source
    assert "links_list_start" in block.template_source
    assert block.metadata.palette_slots
    assert "luxurious" in block.metadata.vibe_tags
    assert "muted" in block.metadata.vibe_tags
