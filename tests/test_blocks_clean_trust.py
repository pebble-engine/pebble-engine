"""Tests for the clean-trust vibe block library.

Seven blocks targeting professional services (dentist, lawyer, financial
advisor, medical practice, consultant, accountant). All assertions mirror
the pattern from test_blocks_library.py.
"""
from pathlib import Path
from pebble.blocks.registry import BlockRegistry

LIBRARY_ROOT = Path(__file__).parent.parent / "pebble" / "blocks"

_CLEAN_TRUST_TAGS = {
    "clean", "trust-building", "professional", "structured", "calm", "authoritative",
}


def _reg() -> BlockRegistry:
    return BlockRegistry.load(LIBRARY_ROOT)


# ---------------------------------------------------------------------------
# hero_focused_clean
# ---------------------------------------------------------------------------

def test_hero_focused_clean_loads():
    reg = _reg()
    assert "library/hero_focused_clean" in reg
    block = reg["library/hero_focused_clean"]
    assert block.metadata.block_type == "hero"
    # Required hero slots
    for slot in ("eyebrow", "headline", "subheadline", "cta_primary", "cta_secondary", "hero_image"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    # Image slot
    assert block.metadata.slots["hero_image"].kind == "image"
    assert block.metadata.slots["hero_image"].pexels_query_template is not None
    assert "clean" in block.metadata.slots["hero_image"].pexels_query_template
    # Template placeholders
    assert "{{headline}}" in block.template_source
    assert "{{hero_image}}" in block.template_source
    assert "{{cta_primary}}" in block.template_source
    # Vibe / palette
    assert len(_CLEAN_TRUST_TAGS & set(block.metadata.vibe_tags)) >= 3
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# services_grid_clean
# ---------------------------------------------------------------------------

def test_services_grid_clean_loads():
    reg = _reg()
    assert "library/services_grid_clean" in reg
    block = reg["library/services_grid_clean"]
    assert block.metadata.block_type == "services"
    for slot in ("eyebrow", "headline", "services"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["services"].kind == "list"
    # List iteration markers
    assert "services_list_start" in block.template_source
    assert "services_list_end" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    assert "{{headline}}" in block.template_source
    # No price slot — clean-trust services don't list prices in the grid card
    assert "price" not in block.metadata.slots
    assert len(_CLEAN_TRUST_TAGS & set(block.metadata.vibe_tags)) >= 3
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# about_team_clean
# ---------------------------------------------------------------------------

def test_about_team_clean_loads():
    reg = _reg()
    assert "library/about_team_clean" in reg
    block = reg["library/about_team_clean"]
    assert block.metadata.block_type == "about"
    for slot in ("eyebrow", "headline", "story_paragraphs", "portrait_image", "signature"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["portrait_image"].kind == "image"
    assert block.metadata.slots["portrait_image"].pexels_query_template is not None
    assert "professional" in block.metadata.slots["portrait_image"].pexels_query_template
    assert block.metadata.slots["story_paragraphs"].kind == "list"
    assert "story_paragraphs_list_start" in block.template_source
    assert "{{signature}}" in block.template_source
    assert len(_CLEAN_TRUST_TAGS & set(block.metadata.vibe_tags)) >= 3
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# testimonials_panel_clean
# ---------------------------------------------------------------------------

def test_testimonials_panel_clean_loads():
    reg = _reg()
    assert "library/testimonials_panel_clean" in reg
    block = reg["library/testimonials_panel_clean"]
    assert block.metadata.block_type == "testimonials"
    for slot in ("quote", "attribution", "role", "headshot_image"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["headshot_image"].kind == "image"
    assert block.metadata.slots["headshot_image"].pexels_query_template is not None
    assert "professional" in block.metadata.slots["headshot_image"].pexels_query_template.lower()
    assert "{{quote}}" in block.template_source
    assert "{{attribution}}" in block.template_source
    assert "{{role}}" in block.template_source
    assert len(_CLEAN_TRUST_TAGS & set(block.metadata.vibe_tags)) >= 3
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# pricing_tiers_clean
# ---------------------------------------------------------------------------

def test_pricing_tiers_clean_loads():
    reg = _reg()
    assert "library/pricing_tiers_clean" in reg
    block = reg["library/pricing_tiers_clean"]
    assert block.metadata.block_type == "pricing"
    for slot in ("eyebrow", "headline", "tiers"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["tiers"].kind == "list"
    assert "tiers_list_start" in block.template_source
    assert "tiers_list_end" in block.template_source
    assert "{{eyebrow}}" in block.template_source
    # Nested features list
    assert "tiers[].features_list_start" in block.template_source
    # rounded-md buttons (authoritative), not rounded-full (warm)
    assert "rounded-md" in block.template_source
    assert "rounded-full" not in block.template_source
    assert len(_CLEAN_TRUST_TAGS & set(block.metadata.vibe_tags)) >= 3
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# contact_split_clean
# ---------------------------------------------------------------------------

def test_contact_split_clean_loads():
    reg = _reg()
    assert "library/contact_split_clean" in reg
    block = reg["library/contact_split_clean"]
    assert block.metadata.block_type == "contact"
    for slot in ("eyebrow", "headline", "form_intro", "address", "hours_text",
                 "phone", "email", "form_slug"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    # Form action
    assert "/api/forms/{{form_slug}}" in block.template_source
    assert "{{address}}" in block.template_source
    assert "{{hours_text}}" in block.template_source
    assert "{{phone}}" in block.template_source
    assert "{{email}}" in block.template_source
    # rounded-md inputs (authoritative)
    assert "rounded-md" in block.template_source
    assert len(_CLEAN_TRUST_TAGS & set(block.metadata.vibe_tags)) >= 3
    assert block.metadata.palette_slots


# ---------------------------------------------------------------------------
# footer_anchored_clean
# ---------------------------------------------------------------------------

def test_footer_anchored_clean_loads():
    reg = _reg()
    assert "library/footer_anchored_clean" in reg
    block = reg["library/footer_anchored_clean"]
    assert block.metadata.block_type == "footer"
    for slot in ("business_name", "tagline", "year", "links"):
        assert slot in block.metadata.slots, f"missing slot: {slot}"
    assert block.metadata.slots["links"].kind == "list"
    assert "links_list_start" in block.template_source
    assert "links_list_end" in block.template_source
    assert "{{business_name}}" in block.template_source
    assert "{{year}}" in block.template_source
    assert len(_CLEAN_TRUST_TAGS & set(block.metadata.vibe_tags)) >= 3
    assert block.metadata.palette_slots
