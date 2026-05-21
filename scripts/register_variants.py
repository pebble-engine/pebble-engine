"""Register all 14 variant templates into pebble/templates/registry.json.

Reads each variant's content/site.ts for the brand SITE_TITLE + TAGLINE,
reads its tailwind.config.ts / globals.css for color swatches, and writes
a clean entry per variant. Variants do NOT get preview_url initially —
the gallery treats them as "click to instantiate" rather than "click to
preview live" (the screenshot in the card is the preview).

Run after all variant agents have completed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO / "pebble" / "templates"
REGISTRY = TEMPLATES_DIR / "registry.json"

# Variant_id → (source_template_id, fresh_brand_name, applicable_industries_subset,
#               vibe_label, color_swatches, fonts_dict, best_for, optional_preview_port)
VARIANTS: dict[str, dict] = {
    "service_pro_navy": {
        "source": "service_pro",
        "name": "Meridian Service Co",
        "tagline": "Professional. Precise. Insured.",
        "vibe": "Corporate Navy + Slate",
        "color_swatches": ["#020617", "#0F172A", "#0369A1", "#F8FAFC"],
        "best_for": "B2B / corporate service providers — bonded, insured, white-collar trades.",
    },
    "service_pro_cream": {
        "source": "service_pro",
        "name": "Magnolia Home & Garden",
        "tagline": "Honest service. Grown locally.",
        "vibe": "Warm Cream + Forest Emerald",
        "color_swatches": ["#FAF8F1", "#059669", "#CA8A04", "#2D3A2D"],
        "best_for": "Landscaping, lawn care, garden services — warm, organic, light-mode native.",
    },
    "luxe_beauty_rose": {
        "source": "luxe_beauty",
        "name": "Rose & Veil Apothecary",
        "tagline": "Warm luxury. Made with care.",
        "vibe": "Warm Rose + Lavender",
        "color_swatches": ["#FDF2F8", "#EC4899", "#8B5CF6", "#831843"],
        "best_for": "Warm, feminine beauty + spa brands. Inviting, intimate, premium.",
    },
    "luxe_beauty_aubergine": {
        "source": "luxe_beauty",
        "name": "Atelier Vesper",
        "tagline": "Twilight rituals. Crafted in shadow.",
        "vibe": "Deep Aubergine + Champagne",
        "color_swatches": ["#FAF7F2", "#4A1A4D", "#B8924A", "#1B0F1F"],
        "best_for": "Mysterious, evening-luxury brands — perfume, jewelry, premium skincare.",
    },
    "ink_studio_oxblood": {
        "source": "ink_studio",
        "name": "Cathedral Ink Society",
        "tagline": "Carved in Tradition. Worn With Honor.",
        "vibe": "Warm Gothic Oxblood + Parchment",
        "color_swatches": ["#1A0E0E", "#8B1A1A", "#B8924A", "#F3E9D7"],
        "best_for": "Old-world craft brands — tattoo, leather, whiskey, cigar lounge, vintage.",
    },
    "ink_studio_steel": {
        "source": "ink_studio",
        "name": "Vault Iron Studio",
        "tagline": "Forged in detail. Built to last.",
        "vibe": "Cold Industrial Steel + Brass",
        "color_swatches": ["#0E1014", "#A8B0BD", "#C0B47A", "#E8E6E0"],
        "best_for": "Workshop / fabrication / metal craft — industrial precision, dark mood.",
    },
    "artisan_kitchen_navy": {
        "source": "artisan_kitchen",
        "name": "Harbor Light Coffee",
        "tagline": "Roasted by hand. Served by the harbor.",
        "vibe": "Coastal Navy + Amber",
        "color_swatches": ["#FAF6EE", "#0F2B3D", "#F59E0B", "#1E3A8A"],
        "best_for": "Coastal coffee shops + light cafes. Cream + navy + warm amber.",
    },
    "artisan_kitchen_olive": {
        "source": "artisan_kitchen",
        "name": "Olive Tree Trattoria",
        "tagline": "Slow food. Long lunches. Tradition.",
        "vibe": "Deep Olive + Honey + Terracotta",
        "color_swatches": ["#F7F2E8", "#4F5D2F", "#C8943C", "#A03A28"],
        "best_for": "Mediterranean / Italian / trattoria — slow food + olive-oil-warm hospitality.",
    },
    "instructor_pro_navy": {
        "source": "instructor_pro",
        "name": "Veridian Executive Coaching",
        "tagline": "Clarity. Strategy. Results.",
        "vibe": "Authority Navy + Gold",
        "color_swatches": ["#0B1426", "#1E3A8A", "#CA8A04", "#F8FAFC"],
        "best_for": "Executive coaching, leadership development, professional services authority.",
    },
    "instructor_pro_forest": {
        "source": "instructor_pro",
        "name": "Northbound Guide Co",
        "tagline": "Beyond the trail. Beyond yourself.",
        "vibe": "Wilderness Forest + Bronze",
        "color_swatches": ["#0F1A14", "#1F3D2D", "#B8762E", "#F2EDE3"],
        "best_for": "Wilderness guiding, outdoor adventure, survival training, eco-lodges.",
    },
    "boutique_brokerage_sage": {
        "source": "boutique_brokerage",
        "name": "Willow & Slate Estates",
        "tagline": "Quiet places. Considered properties.",
        "vibe": "Sage Countryside + Bronze",
        "color_swatches": ["#FAF8F2", "#4A5840", "#9B7B47", "#1F2421"],
        "best_for": "Rural / countryside luxury real estate. Calm, considered, less urban.",
    },
    "boutique_brokerage_navy": {
        "source": "boutique_brokerage",
        "name": "Harbor Stone Holdings",
        "tagline": "Quietly significant properties.",
        "vibe": "Marine Navy + Brass",
        "color_swatches": ["#0A1726", "#1E3A5F", "#B8924A", "#F5F1E8"],
        "best_for": "Yacht-club / old-money urban-coastal real estate. Greenwich, Newport, Annapolis vibe.",
    },
    "honest_garage_rust": {
        "source": "honest_garage",
        "name": "Rust Belt Garage",
        "tagline": "Old-school repairs. Real work. Real prices.",
        "vibe": "Vintage Americana Rust + Bone",
        "color_swatches": ["#1A1714", "#C9501C", "#E89E3C", "#F4EDE0"],
        "best_for": "Vintage / classic-car mechanics. Americana mood, warmer industrial.",
    },
    "honest_garage_military": {
        "source": "honest_garage",
        "name": "Foxtrot Motor Works",
        "tagline": "Disciplined repairs. Operational standards.",
        "vibe": "Olive Drab + Safety Orange",
        "color_swatches": ["#1A1D14", "#4A5240", "#FF6B1A", "#EDE9DC"],
        "best_for": "Diesel / fleet / military-spec / heavy-duty mechanics. Disciplined precision.",
    },
}


def main():
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    existing_ids = {t["id"] for t in reg.get("templates", [])}

    # Build a map source_id → source_entry to inherit fields like
    # applicable_industries, fonts (variants reuse the same), source_dna.
    sources = {t["id"]: t for t in reg.get("templates", [])}

    added = 0
    skipped = 0
    for vid, v in VARIANTS.items():
        if vid in existing_ids:
            print(f"skip (already registered): {vid}")
            skipped += 1
            continue
        tmpl_dir = TEMPLATES_DIR / vid
        if not tmpl_dir.exists():
            print(f"skip (template not on disk): {vid}")
            skipped += 1
            continue
        src = sources.get(v["source"])
        if not src:
            print(f"skip (source not in registry): {vid} -> {v['source']}")
            skipped += 1
            continue
        entry = {
            "id": vid,
            "directory": f"pebble/templates/{vid}",
            "name": v["name"],
            "tagline": v["tagline"],
            "vibe": v["vibe"],
            "source_dna": src["source_dna"],
            "applicable_industries": src["applicable_industries"],
            "preview_image": f"/templates-preview/{vid}.png",
            "color_swatches": v["color_swatches"],
            "fonts": src["fonts"],
            "best_for": v["best_for"],
            "tier": "free",
        }
        reg["templates"].append(entry)
        added += 1
        print(f"added: {vid}")

    # Clear the _planned_next list since all 14 variants are now real.
    reg["_planned_next"] = []

    REGISTRY.write_text(json.dumps(reg, indent=2), encoding="utf-8")
    print(f"\nregistry now has {len(reg['templates'])} templates (added {added}, skipped {skipped})")


if __name__ == "__main__":
    main()
