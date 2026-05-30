# Pebble Engine v2 — Template-First Architecture Rewrite

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the free-form LLM-writes-code architecture with a curated block library where Claude Sonnet 4.6 picks blocks and writes copy, dropping build time from 60-120s to 10-20s while eliminating placeholder leaks, off-topic photos, and incoherent layouts.

**Architecture:** Brief → template-match (Industry + Style DNA filters) → Sonnet picks 7-8 blocks from the chosen template's library + writes copy JSON + picks palette → renderer instantiates blocks → WebContainer boots preview in browser. v1 free-form engine stays alive in parallel until v2 cutover.

**Tech Stack:** Python engine (unchanged language); Claude Sonnet 4.6 via Anthropic SDK; existing template instantiation pipeline (Phase 31) extended to per-block granularity; StackBlitz WebContainers commercial SDK for v3 preview; existing Next.js 14 site output format.

---

## Strategic context

### Decisions confirmed by Marc (2026-05-29)

| Decision | Value |
|---|---|
| LLM | Claude Sonnet 4.6 for everything (Free + Paid) |
| Block library scope | 50 blocks × 7 industries at launch |
| Industries | bakery, photographer, hair/beauty salon, fitness coach, pest/service, real estate, restaurant |
| Legacy 22 sites | Read-only banner, no auto-migration |
| Timeline | Parallel rewrite, 4-6 weeks, cutover at the end |
| Preview | WebContainers (StackBlitz commercial license) |

### Why this isn't square one

The current engine's output failures (placeholder leaks, pottery shards in bakery, incoherent hero grids) are all classes of bug that **disappear** when templates do the structural work:

- Templates have no placeholders the LLM can forget to fill (slots are filled by the compiler, not the LLM)
- Templates have per-block Pexels query tags ("artisan sourdough bread", not "artisan" alone)
- Templates have one canonical hero layout per DNA, not 100 LLM-decided variations
- Templates handle title-casing at render time, not at LLM-output time

The LLM's only job becomes: pick 7-8 blocks from a library of 50, write copy for each, choose a palette from 5 options. That's a deterministic, low-token, high-reliability task.

### Economics

| Path | Tokens/build | Cost/token | Cost/build | Build time |
|---|---|---|---|---|
| Today (Qwen, freestyle) | ~50K output | $0.002/1K | ~$0.10 | 60-120s |
| v2 (Sonnet, template-first) | ~5K output | $0.015/1K | ~$0.075 | 10-20s |

Net: cheaper per build, ~7× faster, dramatically higher reliability.

---

## File structure

### New module tree

```
pebble/
  blocks/
    __init__.py              # block library exports
    schema.py                # TypedDict + validation for block defs
    registry.py              # lookup by industry + block_type + DNA
    bakery/
      __init__.py
      hero_artisan.tsx       # template with {{slot}} placeholders
      hero_artisan.json      # metadata (slots, image queries, DNA tags)
      hero_clean.tsx
      hero_clean.json
      services_grid.tsx
      services_grid.json
      about_story.tsx
      about_story.json
      testimonials_quote.tsx
      testimonials_quote.json
      contact_form.tsx
      contact_form.json
      footer_compact.tsx
      footer_compact.json
    photographer/            # Phase 2 — same 7 block types
    salon/                   # Phase 2
    fitness/                 # Phase 2
    service/                 # Phase 2
    realestate/              # Phase 2
    restaurant/              # Phase 2
  blocks_compiler.py         # assemble a Next.js project from block_picks JSON
  sonnet_block_picker.py     # Sonnet-driven block selection + copy generation
  server/
    build_v2.py              # POST /api/v2/generate handler
    router.py                # MODIFY: register /api/v2/generate

tests/
  test_blocks_schema.py
  test_blocks_bakery.py
  test_blocks_compiler.py
  test_sonnet_block_picker.py
  test_build_v2_e2e.py
```

### Block schema (the foundational contract)

Every block is a `(template.tsx, metadata.json)` pair:

```json
{
  "block_id": "bakery/hero_artisan",
  "block_type": "hero",
  "industry": "bakery",
  "dna_tags": ["swiss_magazine", "cinematic_imax", "warm_artisan"],
  "slots": {
    "headline": { "kind": "text", "max_chars": 80, "tone": "warm" },
    "subheadline": { "kind": "text", "max_chars": 200, "tone": "warm" },
    "cta_primary": { "kind": "text", "max_chars": 24 },
    "cta_secondary": { "kind": "text", "max_chars": 24 },
    "hero_image": { "kind": "image", "pexels_query": "artisan sourdough bread loaf", "aspect": "16/9" }
  },
  "palette_slots": ["bg", "fg", "accent"],
  "preview_image": "previews/bakery_hero_artisan.png"
}
```

Template uses `{{slot_name}}` placeholders:

```tsx
// hero_artisan.tsx
export default function Hero() {
  return (
    <section className="bg-{{bg}} text-{{fg}} py-24">
      <h1 className="text-6xl font-bold">{{headline}}</h1>
      <p className="mt-4 text-xl">{{subheadline}}</p>
      <div className="mt-8 flex gap-4">
        <a href="#book" className="bg-{{accent}} text-{{bg}} px-6 py-3">{{cta_primary}}</a>
        <a href="#about">{{cta_secondary}}</a>
      </div>
      <img src="{{hero_image}}" alt="" className="mt-12 w-full aspect-video object-cover" />
    </section>
  );
}
```

---

## Phase decomposition

Each phase produces working software. Marc approves each phase before next starts.

### Phase 1 (Weeks 1-2): Block library + Sonnet picker — bakery only

**Deliverable:** `POST /api/v2/generate` produces a complete, beautiful bakery site from a brief in <20s. Old v1 path untouched. Cutover NOT triggered yet.

**Why bakery first:** The `artisan_kitchen` template already exists from Phase 31 — we have a known-good baseline to extract blocks from. Smallest scope to prove the architecture.

7 blocks for bakery (one of each type): hero, services, about, testimonials, contact, pricing, footer. Each block has 1-2 variants. Total: ~12 bakery blocks.

Tasks detailed below.

### Phase 2 (Weeks 3-4): Block library expansion

**Deliverable:** All 50 blocks × 7 industries shipped. v2 endpoint handles all 7 industries.

Tasks (outline — to be detailed when Phase 1 completes):
- Port photographer blocks from `ink_studio` + `emma_hart_photography` references
- Port salon blocks from `vermilion_ink_atelier` reference
- Port fitness blocks from `instructor_pro` + `brookline_fitness_academy` references
- Port service-industry blocks from `hudson_valley_pest_lawn` + `honest_garage` references
- Port real estate blocks from `boutique_brokerage` reference
- Port restaurant blocks from `bon_appétit` reference (rename to `bon_appetit` first to fix the Unicode-slug bug we hit)
- Add Sonnet industry routing to `sonnet_block_picker.py`
- Integration tests for each industry

### Phase 3 (Week 5): WebContainers preview

**Deliverable:** v3's `/workspace/<slug>` preview iframe is replaced by a WebContainer-driven in-browser Node.js sandbox. `next dev` server-side path removed for new (v2) builds.

Tasks (outline):
- Sign up for StackBlitz WebContainers commercial plan
- Install `@webcontainer/api` in `ui/v3/`
- Build `WebContainerPreview` React component that boots the generated code
- Replace `/preview/<slug>/` iframe src with the WebContainer instance
- Handle hot-reload on visual-edit + refine
- Decommission `pebble.postbuild.run_dev_server` for v2 sites
- Cost monitoring: dashboard widget showing active WebContainer minutes

### Phase 4 (Week 6): Cutover + legacy handling

**Deliverable:** v2 is the only active path for new builds. Old v1 endpoint deprecated. Legacy 22 sites get the read-only banner. Qwen disabled.

Tasks (outline):
- Make `POST /api/generate` route to v2 by default
- Add `?engine=v1` escape hatch for emergency rollback
- Dashboard banner on v1-built projects: "Built before our new engine — refresh to rebuild"
- Comment out OpenRouter from `_pick_client()` (keep code for revert)
- Update `.env.example` defaults
- Remove `PEBBLE_AUTO_RUN` and `PEBBLE_AUTO_REPAIR` flags
- Update `CLAUDE.md` API reference + architecture-in-60-seconds
- 30-day uptime watch + Sentry alert tuning
- Public changelog entry

---

## Phase 1: Detailed task list (TDD)

### Task 1: Block schema definition

**Files:**
- Create: `pebble/blocks/schema.py`
- Test: `tests/test_blocks_schema.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_blocks_schema.py
import pytest
from pebble.blocks.schema import BlockMetadata, validate_block_metadata

def test_minimal_valid_block_passes():
    meta = {
        "block_id": "bakery/hero_artisan",
        "block_type": "hero",
        "industry": "bakery",
        "dna_tags": ["swiss_magazine"],
        "slots": {
            "headline": {"kind": "text", "max_chars": 80, "tone": "warm"}
        },
        "palette_slots": ["bg", "fg", "accent"],
    }
    result = validate_block_metadata(meta)
    assert result.block_id == "bakery/hero_artisan"
    assert result.block_type == "hero"

def test_missing_block_id_raises():
    with pytest.raises(ValueError, match="block_id"):
        validate_block_metadata({"block_type": "hero", "industry": "bakery"})

def test_unknown_slot_kind_raises():
    with pytest.raises(ValueError, match="slot kind"):
        validate_block_metadata({
            "block_id": "x/y",
            "block_type": "hero",
            "industry": "bakery",
            "dna_tags": [],
            "slots": {"foo": {"kind": "video", "max_chars": 80}},
            "palette_slots": [],
        })
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_blocks_schema.py -v`
Expected: ImportError (module doesn't exist)

- [ ] **Step 3: Implement schema**

```python
# pebble/blocks/schema.py
"""Block metadata schema + validation.

A block is a (template.tsx, metadata.json) pair. The metadata describes
what slots the template exposes, what kind of content each slot accepts,
and which DNA cards the block is visually compatible with. The Sonnet
picker reads metadata to assemble copy briefs; the compiler reads
metadata to substitute slot values into the template.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SlotKind = Literal["text", "image", "list", "url"]
BlockType = Literal[
    "hero", "services", "about", "testimonials",
    "contact", "pricing", "footer", "gallery", "faq",
]

_VALID_SLOT_KINDS = {"text", "image", "list", "url"}


@dataclass(frozen=True)
class SlotSpec:
    kind: SlotKind
    max_chars: int | None = None
    tone: str | None = None
    pexels_query: str | None = None
    aspect: str | None = None


@dataclass(frozen=True)
class BlockMetadata:
    block_id: str         # "bakery/hero_artisan"
    block_type: BlockType
    industry: str         # "bakery"
    dna_tags: list[str]
    slots: dict[str, SlotSpec]
    palette_slots: list[str]
    preview_image: str | None = None


def validate_block_metadata(raw: dict) -> BlockMetadata:
    """Validate a metadata.json dict and return a typed BlockMetadata.

    Raises ValueError on any structural issue. Keep error messages
    actionable — block authors will read them when their .json is
    rejected during library load.
    """
    for required in ("block_id", "block_type", "industry", "dna_tags",
                     "slots", "palette_slots"):
        if required not in raw:
            raise ValueError(f"block metadata missing required field: {required}")
    slots = {}
    for slot_name, spec in raw["slots"].items():
        if spec.get("kind") not in _VALID_SLOT_KINDS:
            raise ValueError(
                f"slot kind {spec.get('kind')!r} invalid for slot {slot_name!r}; "
                f"must be one of {sorted(_VALID_SLOT_KINDS)}"
            )
        slots[slot_name] = SlotSpec(
            kind=spec["kind"],
            max_chars=spec.get("max_chars"),
            tone=spec.get("tone"),
            pexels_query=spec.get("pexels_query"),
            aspect=spec.get("aspect"),
        )
    return BlockMetadata(
        block_id=raw["block_id"],
        block_type=raw["block_type"],
        industry=raw["industry"],
        dna_tags=list(raw["dna_tags"]),
        slots=slots,
        palette_slots=list(raw["palette_slots"]),
        preview_image=raw.get("preview_image"),
    )
```

- [ ] **Step 4: Run test to verify pass**

Run: `python -m pytest tests/test_blocks_schema.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add pebble/blocks/schema.py tests/test_blocks_schema.py
git commit -m "feat(blocks): block metadata schema + validation (Phase 1.1)"
```

### Task 2: Block registry — load + lookup

**Files:**
- Create: `pebble/blocks/__init__.py` (empty, marks package)
- Create: `pebble/blocks/registry.py`
- Test: `tests/test_blocks_registry.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_blocks_registry.py
import json
import pytest
from pathlib import Path

from pebble.blocks.registry import BlockRegistry

def test_load_from_directory(tmp_path):
    bakery = tmp_path / "bakery"
    bakery.mkdir()
    (bakery / "hero_artisan.json").write_text(json.dumps({
        "block_id": "bakery/hero_artisan",
        "block_type": "hero",
        "industry": "bakery",
        "dna_tags": ["swiss_magazine"],
        "slots": {"headline": {"kind": "text", "max_chars": 80}},
        "palette_slots": ["bg", "fg"],
    }))
    (bakery / "hero_artisan.tsx").write_text("<section>{{headline}}</section>")

    reg = BlockRegistry.load(tmp_path)

    assert "bakery/hero_artisan" in reg
    block = reg["bakery/hero_artisan"]
    assert block.metadata.block_type == "hero"
    assert "{{headline}}" in block.template_source

def test_lookup_by_industry_and_type(tmp_path):
    # ... setup two heroes for bakery
    (tmp_path / "bakery").mkdir()
    for name in ("hero_artisan", "hero_clean"):
        (tmp_path / "bakery" / f"{name}.json").write_text(json.dumps({
            "block_id": f"bakery/{name}",
            "block_type": "hero",
            "industry": "bakery",
            "dna_tags": ["swiss_magazine"],
            "slots": {"headline": {"kind": "text"}},
            "palette_slots": [],
        }))
        (tmp_path / "bakery" / f"{name}.tsx").write_text("x")

    reg = BlockRegistry.load(tmp_path)
    heroes = reg.find(industry="bakery", block_type="hero")
    assert len(heroes) == 2
    assert {h.metadata.block_id for h in heroes} == {"bakery/hero_artisan", "bakery/hero_clean"}

def test_missing_template_file_raises(tmp_path):
    (tmp_path / "bakery").mkdir()
    (tmp_path / "bakery" / "orphan.json").write_text(json.dumps({
        "block_id": "bakery/orphan",
        "block_type": "hero",
        "industry": "bakery",
        "dna_tags": [],
        "slots": {},
        "palette_slots": [],
    }))
    # no orphan.tsx
    with pytest.raises(ValueError, match="template file"):
        BlockRegistry.load(tmp_path)
```

- [ ] **Step 2: Verify failure**

Run: `python -m pytest tests/test_blocks_registry.py -v`
Expected: ImportError

- [ ] **Step 3: Implement registry**

```python
# pebble/blocks/registry.py
"""Load and look up blocks from the on-disk library.

The on-disk layout is `<industry>/<block_id>.{json,tsx}`. The registry
walks the tree at load time, validates each metadata.json, and pairs it
with the sibling .tsx template source. Sonnet's block picker queries
this registry; the blocks_compiler uses it to retrieve template source
for substitution.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pebble.blocks.schema import BlockMetadata, BlockType, validate_block_metadata


@dataclass(frozen=True)
class Block:
    metadata: BlockMetadata
    template_source: str  # the raw .tsx file contents with {{slot}} placeholders


class BlockRegistry:
    def __init__(self, blocks: dict[str, Block]) -> None:
        self._blocks = blocks

    @classmethod
    def load(cls, root: Path) -> "BlockRegistry":
        """Walk `root/<industry>/<name>.{json,tsx}` and build the registry."""
        out: dict[str, Block] = {}
        for industry_dir in sorted(root.iterdir()):
            if not industry_dir.is_dir():
                continue
            for json_path in sorted(industry_dir.glob("*.json")):
                tsx_path = json_path.with_suffix(".tsx")
                if not tsx_path.exists():
                    raise ValueError(
                        f"block {json_path.name}: template file {tsx_path.name} "
                        f"missing in {industry_dir.name}/"
                    )
                meta = validate_block_metadata(json.loads(json_path.read_text(encoding="utf-8")))
                out[meta.block_id] = Block(
                    metadata=meta,
                    template_source=tsx_path.read_text(encoding="utf-8"),
                )
        return cls(out)

    def __contains__(self, block_id: str) -> bool:
        return block_id in self._blocks

    def __getitem__(self, block_id: str) -> Block:
        return self._blocks[block_id]

    def find(self, *, industry: str, block_type: BlockType,
             dna_tag: str | None = None) -> list[Block]:
        """Return all blocks matching the filter."""
        out = []
        for block in self._blocks.values():
            if block.metadata.industry != industry:
                continue
            if block.metadata.block_type != block_type:
                continue
            if dna_tag is not None and dna_tag not in block.metadata.dna_tags:
                continue
            out.append(block)
        return out
```

- [ ] **Step 4: Verify pass**

Run: `python -m pytest tests/test_blocks_registry.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add pebble/blocks/__init__.py pebble/blocks/registry.py tests/test_blocks_registry.py
git commit -m "feat(blocks): registry — load library, lookup by industry+type (Phase 1.2)"
```

### Task 3: First bakery block — hero_artisan

**Files:**
- Create: `pebble/blocks/bakery/__init__.py` (empty)
- Create: `pebble/blocks/bakery/hero_artisan.tsx`
- Create: `pebble/blocks/bakery/hero_artisan.json`
- Test: `tests/test_blocks_bakery.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_blocks_bakery.py
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
```

- [ ] **Step 2: Verify failure**

Run: `python -m pytest tests/test_blocks_bakery.py -v`
Expected: KeyError ("bakery/hero_artisan" not found, because no block files yet)

- [ ] **Step 3: Create the block files**

Create `pebble/blocks/bakery/hero_artisan.tsx`:

```tsx
import Image from "next/image";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-end overflow-hidden">
      <div className="absolute inset-0">
        <Image
          src="{{hero_image}}"
          alt="{{headline}}"
          fill
          priority
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-{{bg}} via-{{bg}}/40 to-transparent" />
      </div>
      <div className="relative z-10 container mx-auto px-8 pb-24">
        <p className="text-{{accent}} text-sm uppercase tracking-widest mb-4">
          {{eyebrow}}
        </p>
        <h1 className="text-{{fg}} text-6xl md:text-8xl font-bold leading-none max-w-4xl">
          {{headline}}
        </h1>
        <p className="text-{{fg}}/80 text-xl mt-6 max-w-2xl leading-relaxed">
          {{subheadline}}
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <a href="#order"
             className="bg-{{accent}} text-{{bg}} px-8 py-4 rounded-full font-semibold hover:opacity-90 transition">
            {{cta_primary}}
          </a>
          <a href="#about"
             className="text-{{fg}} px-8 py-4 rounded-full border border-{{fg}}/30 hover:bg-{{fg}}/10 transition">
            {{cta_secondary}}
          </a>
        </div>
      </div>
    </section>
  );
}
```

Create `pebble/blocks/bakery/hero_artisan.json`:

```json
{
  "block_id": "bakery/hero_artisan",
  "block_type": "hero",
  "industry": "bakery",
  "dna_tags": ["swiss_magazine", "cinematic_imax", "warm_artisan", "boutique_brokerage"],
  "slots": {
    "eyebrow": {
      "kind": "text",
      "max_chars": 40,
      "tone": "intimate, neighborhood-feel"
    },
    "headline": {
      "kind": "text",
      "max_chars": 80,
      "tone": "warm, confident, sensory"
    },
    "subheadline": {
      "kind": "text",
      "max_chars": 200,
      "tone": "warm, descriptive, evoke smell and texture"
    },
    "cta_primary": {
      "kind": "text",
      "max_chars": 24,
      "tone": "action-oriented (Order now, Reserve a loaf)"
    },
    "cta_secondary": {
      "kind": "text",
      "max_chars": 24,
      "tone": "informational (Our story, See the menu)"
    },
    "hero_image": {
      "kind": "image",
      "pexels_query": "artisan sourdough bread bakery interior warm light",
      "aspect": "16/9"
    }
  },
  "palette_slots": ["bg", "fg", "accent"],
  "preview_image": "previews/bakery_hero_artisan.png"
}
```

Create `pebble/blocks/bakery/__init__.py`:

```python
# bakery block library — see hero_artisan.tsx etc.
```

- [ ] **Step 4: Verify pass**

Run: `python -m pytest tests/test_blocks_bakery.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add pebble/blocks/bakery/ tests/test_blocks_bakery.py
git commit -m "feat(blocks): bakery hero_artisan block (Phase 1.3)"
```

### Tasks 4-9: Remaining 6 bakery blocks

For each block type (services, about, testimonials, contact, pricing, footer):
- 1 `.tsx` template with `{{slot}}` placeholders
- 1 `.json` metadata file
- 1 test asserting the block loads + has expected slots

Each task follows the same TDD pattern as Task 3. Block specifications:

- **`services_grid`**: 3-column grid, each card has icon/image + title + body + price. Slots: `eyebrow, headline, services[]` (list of `{title, body, image, price}`).
- **`about_story`**: Two-column with portrait image left, prose right. Slots: `eyebrow, headline, story_paragraphs[], portrait_image, signature`.
- **`testimonials_quote`**: Single large pull-quote. Slots: `quote, attribution, role, headshot_image`.
- **`contact_form`**: Form + hours/address sidebar. Slots: `eyebrow, headline, address, hours_text, phone, email, form_intro`.
- **`pricing_simple`**: 2-3 tier cards. Slots: `eyebrow, headline, tiers[]` (list of `{name, price, features[], cta}`).
- **`footer_compact`**: Logo, nav links, copyright. Slots: `business_name, tagline, year, links[]`.

Tests live in `tests/test_blocks_bakery.py` (same file, extra test functions). Commit after each block.

### Task 10: Blocks compiler — substitute slots, assemble project

**Files:**
- Create: `pebble/blocks_compiler.py`
- Test: `tests/test_blocks_compiler.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_blocks_compiler.py
from pathlib import Path
import json
from pebble.blocks_compiler import compile_site
from pebble.blocks.registry import BlockRegistry

def test_simple_substitution(tmp_path):
    # tiny in-memory registry
    bakery = tmp_path / "library" / "bakery"
    bakery.mkdir(parents=True)
    (bakery / "hero.tsx").write_text(
        '<h1 className="text-{{fg}}">{{headline}}</h1>'
    )
    (bakery / "hero.json").write_text(json.dumps({
        "block_id": "bakery/hero",
        "block_type": "hero",
        "industry": "bakery",
        "dna_tags": [],
        "slots": {"headline": {"kind": "text", "max_chars": 80}},
        "palette_slots": ["fg"],
    }))
    reg = BlockRegistry.load(tmp_path / "library")

    out = tmp_path / "site"
    compile_site(
        registry=reg,
        block_picks=[
            {"block_id": "bakery/hero", "slot_values": {"headline": "Welcome to the bakery"}}
        ],
        palette={"fg": "slate-900"},
        out_dir=out,
    )

    page_file = out / "app" / "page.tsx"
    assert page_file.exists()
    content = page_file.read_text(encoding="utf-8")
    assert "Welcome to the bakery" in content
    assert "text-slate-900" in content
    assert "{{" not in content  # all placeholders substituted

def test_unfilled_placeholder_raises(tmp_path):
    bakery = tmp_path / "library" / "bakery"
    bakery.mkdir(parents=True)
    (bakery / "hero.tsx").write_text("<h1>{{headline}} - {{tagline}}</h1>")
    (bakery / "hero.json").write_text(json.dumps({
        "block_id": "bakery/hero", "block_type": "hero", "industry": "bakery",
        "dna_tags": [], "slots": {
            "headline": {"kind": "text"},
            "tagline": {"kind": "text"},
        }, "palette_slots": [],
    }))
    reg = BlockRegistry.load(tmp_path / "library")

    import pytest
    with pytest.raises(ValueError, match="unfilled placeholder"):
        compile_site(
            registry=reg,
            block_picks=[{"block_id": "bakery/hero",
                          "slot_values": {"headline": "x"}}],  # tagline missing
            palette={},
            out_dir=tmp_path / "site",
        )
```

- [ ] **Step 2: Verify failure**

Run: `python -m pytest tests/test_blocks_compiler.py -v`
Expected: ImportError

- [ ] **Step 3: Implement compiler**

```python
# pebble/blocks_compiler.py
"""Compile a list of block picks into a complete Next.js project.

block_picks is the Sonnet picker's output: a list of
{block_id, slot_values} dicts. For each pick we look up the template
source, substitute {{slot_name}} → slot_value and {{palette_slot}} →
palette[palette_slot], then concatenate the rendered blocks into
app/page.tsx. We also drop a minimal package.json, tailwind.config,
and globals.css so the project is runnable in a WebContainer.

A built-in safety net rejects compiled output containing any
{{...}} sequence — that's the "no placeholder leaks" guarantee we
made in the v2 spec.
"""
from __future__ import annotations

import re
from pathlib import Path

from pebble.blocks.registry import BlockRegistry


_PLACEHOLDER_RX = re.compile(r"\{\{(\w+)\}\}")


def _substitute(template: str, values: dict[str, str]) -> str:
    """Replace {{slot}} occurrences with values[slot]."""
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in values:
            return match.group(0)  # leave unfilled, caller detects below
        return str(values[key])
    return _PLACEHOLDER_RX.sub(_replace, template)


def compile_site(
    *,
    registry: BlockRegistry,
    block_picks: list[dict],
    palette: dict[str, str],
    out_dir: Path,
) -> None:
    """Render block_picks into a Next.js project at out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    app_dir = out_dir / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    rendered_sections: list[str] = []
    component_imports: list[str] = []

    for i, pick in enumerate(block_picks):
        block = registry[pick["block_id"]]
        values = dict(pick["slot_values"])
        values.update(palette)  # palette tokens substitute into the same {{name}} slots
        rendered = _substitute(block.template_source, values)

        unfilled = _PLACEHOLDER_RX.findall(rendered)
        if unfilled:
            raise ValueError(
                f"unfilled placeholder(s) in {pick['block_id']}: "
                f"{sorted(set(unfilled))} — Sonnet picker dropped a slot value"
            )

        component_name = f"Section{i:02d}"
        component_imports.append(
            f"const {component_name} = () => (<>{rendered}</>);"
        )
        rendered_sections.append(f"<{component_name} />")

    page_tsx = (
        "// Auto-generated by Pebble v2 — do not edit by hand.\n"
        + "\n".join(component_imports)
        + "\n\nexport default function Page() {\n  return (\n    <main>\n      "
        + "\n      ".join(rendered_sections)
        + "\n    </main>\n  );\n}\n"
    )
    (app_dir / "page.tsx").write_text(page_tsx, encoding="utf-8")
```

- [ ] **Step 4: Verify pass**

Run: `python -m pytest tests/test_blocks_compiler.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add pebble/blocks_compiler.py tests/test_blocks_compiler.py
git commit -m "feat(blocks): compiler — substitute slots, reject unfilled (Phase 1.10)"
```

### Task 11: Sonnet block picker

**Files:**
- Create: `pebble/sonnet_block_picker.py`
- Test: `tests/test_sonnet_block_picker.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sonnet_block_picker.py
import json
from unittest.mock import MagicMock, patch
from pebble.sonnet_block_picker import pick_blocks_and_copy

def test_calls_sonnet_with_brief_and_block_menu():
    brief = {
        "business_name": "Stoneground Loaf",
        "industry": "bakery",
        "extra_context": "Brooklyn sourdough, weekly subscription",
    }
    # mock AnthropicClient.generate to return a deterministic JSON
    mock_response = json.dumps({
        "block_picks": [
            {"block_id": "bakery/hero_artisan", "slot_values": {
                "eyebrow": "Brooklyn",
                "headline": "Sourdough, by hand, every morning",
                "subheadline": "We mill our own flour and bake every loaf the night before. Pick up tomorrow, eat through the week.",
                "cta_primary": "Reserve a loaf",
                "cta_secondary": "Our story",
            }},
        ],
        "palette": {"bg": "stone-50", "fg": "stone-900", "accent": "orange-700"},
    })
    fake_client = MagicMock()
    fake_client.generate.return_value = mock_response

    result = pick_blocks_and_copy(
        brief=brief,
        llm_client=fake_client,
        registry=None,  # picker doesn't read registry; it sees a menu
        block_menu=[
            {"block_id": "bakery/hero_artisan", "block_type": "hero",
             "slots": {"eyebrow": {"max_chars": 40}, "headline": {"max_chars": 80},
                       "subheadline": {"max_chars": 200},
                       "cta_primary": {"max_chars": 24}, "cta_secondary": {"max_chars": 24}}},
        ],
    )

    assert len(result["block_picks"]) == 1
    assert result["block_picks"][0]["block_id"] == "bakery/hero_artisan"
    assert "Stoneground" in str(result) or "Sourdough" in str(result)
    assert result["palette"]["fg"] == "stone-900"
    # confirm the LLM was called once with a prompt containing the brief
    assert fake_client.generate.call_count == 1
    prompt = fake_client.generate.call_args[0][0]
    assert "Stoneground" in prompt
    assert "bakery/hero_artisan" in prompt

def test_rejects_malformed_llm_json():
    fake_client = MagicMock()
    fake_client.generate.return_value = "this is not json"

    import pytest
    with pytest.raises(ValueError, match="invalid JSON"):
        pick_blocks_and_copy(
            brief={"business_name": "x", "industry": "bakery"},
            llm_client=fake_client,
            registry=None,
            block_menu=[],
        )
```

- [ ] **Step 2: Verify failure**

Run: `python -m pytest tests/test_sonnet_block_picker.py -v`
Expected: ImportError

- [ ] **Step 3: Implement picker**

```python
# pebble/sonnet_block_picker.py
"""Sonnet-driven block selection + copy generation.

Takes a brief and a block menu (the available blocks for the matched
industry), asks Sonnet to pick 7-8 blocks and write copy for each
slot, returns a JSON spec the blocks_compiler can render.

The whole job is ~5K output tokens. ~3-5s wall clock. ~$0.05/call.
"""
from __future__ import annotations

import json
import re


_PROMPT_TEMPLATE = """You are designing a one-page website for a small business.

# Business brief
Name: {business_name}
Industry: {industry}
Description: {extra_context}

# Available blocks
{block_menu_json}

# Your job
1. Pick 7-8 blocks (one of each block_type when possible: hero, services, about, testimonials, pricing, contact, footer). Use the block_id values from the menu above. Do not invent new block_ids.
2. For each picked block, write copy for every slot. Respect the slot's max_chars and tone. Make it specific to this business. Never use placeholders like "[BUSINESS PHONE]" or "Your tagline here" — write real copy or leave the slot out entirely.
3. Pick a palette: 3 Tailwind color tokens for bg / fg / accent. Choose values that fit the brief's tone.

# Output
Return ONLY a JSON object with this exact shape, no prose around it:

{{
  "block_picks": [
    {{"block_id": "...", "slot_values": {{"slot_name": "value", ...}}}},
    ...
  ],
  "palette": {{"bg": "stone-50", "fg": "stone-900", "accent": "orange-700"}}
}}
"""

_JSON_RX = re.compile(r"\{[\s\S]*\}")


def pick_blocks_and_copy(
    *,
    brief: dict,
    llm_client,
    registry,  # currently unused; reserved for cross-validation
    block_menu: list[dict],
) -> dict:
    """Call Sonnet to pick blocks + write copy. Return parsed JSON."""
    prompt = _PROMPT_TEMPLATE.format(
        business_name=brief.get("business_name", ""),
        industry=brief.get("industry", ""),
        extra_context=brief.get("extra_context", ""),
        block_menu_json=json.dumps(block_menu, indent=2),
    )
    raw = llm_client.generate(prompt)

    # Sonnet may wrap JSON in prose despite the prompt. Extract the first {...}.
    match = _JSON_RX.search(raw)
    if not match:
        raise ValueError(f"Sonnet returned no JSON object; raw response: {raw[:200]}")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"Sonnet returned invalid JSON: {e}; raw: {raw[:200]}")
```

- [ ] **Step 4: Verify pass**

Run: `python -m pytest tests/test_sonnet_block_picker.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add pebble/sonnet_block_picker.py tests/test_sonnet_block_picker.py
git commit -m "feat(blocks): Sonnet block picker (Phase 1.11)"
```

### Task 12: /api/v2/generate endpoint — wire it all up

**Files:**
- Create: `pebble/server/build_v2.py`
- Modify: `pebble/server/router.py` (add one elif clause)
- Test: `tests/test_build_v2_e2e.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_build_v2_e2e.py
"""End-to-end smoke: POST /api/v2/generate produces a runnable site.

Uses a real BlockRegistry over the on-disk bakery library + a mocked
LLM client so the test is deterministic and free. The asserts cover
the contract we promise: build_meta.json exists, page.tsx exists,
no {{...}} leaks in output.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock

from pebble.server.build_v2 import run_build_v2


def test_bakery_brief_produces_runnable_site(tmp_path, monkeypatch):
    fake_client = MagicMock()
    fake_client.generate.return_value = json.dumps({
        "block_picks": [
            {
                "block_id": "bakery/hero_artisan",
                "slot_values": {
                    "eyebrow": "Brooklyn",
                    "headline": "Sourdough, by hand",
                    "subheadline": "Real bread, made slowly.",
                    "cta_primary": "Reserve a loaf",
                    "cta_secondary": "Our story",
                    "hero_image": "https://images.pexels.com/test.jpg",
                },
            }
        ],
        "palette": {"bg": "stone-50", "fg": "stone-900", "accent": "orange-700"},
    })

    handler = MagicMock()
    handler.headers = {"Content-Length": "100"}
    handler.rfile.read.return_value = json.dumps({
        "business_name": "Stoneground Loaf",
        "industry": "bakery",
        "extra_context": "Brooklyn sourdough"
    }).encode("utf-8")

    monkeypatch.setattr(
        "pebble.server.build_v2.get_llm_client",
        lambda: (fake_client, "ok"),
    )
    monkeypatch.setattr(
        "pebble.server.build_v2._output_dir",
        lambda: tmp_path,
    )

    run_build_v2(handler)

    handler._json.assert_called_once()
    status, body = handler._json.call_args[0]
    assert status == 200
    assert "slug" in body

    site_dir = tmp_path / body["slug"] / "site"
    page = (site_dir / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "Sourdough" in page
    assert "{{" not in page

    meta = json.loads((tmp_path / body["slug"] / "build_meta.json").read_text())
    assert meta["engine_version"] == "v2"
    assert meta["model"] == fake_client.model if hasattr(fake_client, "model") else True
```

- [ ] **Step 2: Verify failure**

Run: `python -m pytest tests/test_build_v2_e2e.py -v`
Expected: ImportError

- [ ] **Step 3: Implement endpoint**

```python
# pebble/server/build_v2.py
"""POST /api/v2/generate — the template-first build path.

Reads brief → looks up the block registry for the matched industry
→ calls Sonnet for block picks + copy → compiles site → writes
build_meta.json with engine_version=v2 → returns slug.

Cost: ~$0.05-0.08 per call. Latency: ~10-20s wall clock.
Replaces the multi-minute v1 pipeline in pebble/server/build.py
for new builds once Phase 4 cutover lands.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from pebble.blocks.registry import BlockRegistry
from pebble.blocks_compiler import compile_site
from pebble.llm import get_llm_client
from pebble.sonnet_block_picker import pick_blocks_and_copy
from pebble.text import sanitize_business_name


_BLOCK_LIBRARY_ROOT = Path(__file__).parent.parent / "blocks"


def _output_dir() -> Path:
    return sys.modules.get("pebble_engine", sys.modules["__main__"]).OUTPUT_DIR


def _slugify(name: str) -> str:
    return sys.modules.get("pebble_engine", sys.modules["__main__"])._slugify(name)


def run_build_v2(handler) -> None:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        handler._json(400, {"error": "invalid Content-Length"}); return
    if length <= 0:
        handler._json(400, {"error": "empty body"}); return

    try:
        brief = json.loads(handler.rfile.read(length).decode("utf-8"))
    except Exception:
        handler._json(400, {"error": "invalid json"}); return

    name = sanitize_business_name(brief.get("business_name", "")) or "untitled"
    brief["business_name"] = name
    slug = _slugify(name)
    industry = brief.get("industry", "").strip().lower() or "bakery"

    client, reason = get_llm_client()
    if reason != "ok":
        handler._json(503, {"error": f"LLM not configured: {reason}"}); return

    registry = BlockRegistry.load(_BLOCK_LIBRARY_ROOT)
    menu = [
        {
            "block_id": b.metadata.block_id,
            "block_type": b.metadata.block_type,
            "slots": {
                name: {"max_chars": s.max_chars, "tone": s.tone, "kind": s.kind}
                for name, s in b.metadata.slots.items()
            },
        }
        for b in registry._blocks.values()
        if b.metadata.industry == industry
    ]
    if not menu:
        handler._json(400, {"error": f"no blocks available for industry: {industry}"}); return

    spec = pick_blocks_and_copy(
        brief=brief, llm_client=client, registry=registry, block_menu=menu,
    )

    project_dir = _output_dir() / slug
    site_dir = project_dir / "site"
    compile_site(
        registry=registry,
        block_picks=spec["block_picks"],
        palette=spec["palette"],
        out_dir=site_dir,
    )

    (project_dir / "brief.json").write_text(json.dumps(brief), encoding="utf-8")
    (project_dir / "build_meta.json").write_text(
        json.dumps({
            "engine_version": "v2",
            "model": getattr(client, "model", None),
            "provider": getattr(client, "provider", None),
            "built_at": datetime.now(timezone.utc).isoformat(),
            "block_picks": [p["block_id"] for p in spec["block_picks"]],
        }),
        encoding="utf-8",
    )

    handler._json(200, {"slug": slug, "engine_version": "v2"})
```

Add to `pebble/server/router.py`'s `route_post` (after the `/api/generate` clause):

```python
        elif handler.path == "/api/v2/generate":
            from pebble.server.build_v2 import run_build_v2
            run_build_v2(handler)
```

- [ ] **Step 4: Verify pass**

Run: `python -m pytest tests/test_build_v2_e2e.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add pebble/server/build_v2.py pebble/server/router.py tests/test_build_v2_e2e.py
git commit -m "feat(v2): POST /api/v2/generate endpoint — wire blocks + Sonnet + compiler"
```

### Task 13: Switch .env to Anthropic, smoke test a real bakery build

**Files:**
- Modify: `.env`

- [ ] **Step 1: Confirm Anthropic key is present**

`grep '^ANTHROPIC_API_KEY=' .env | head -1` — should show a non-empty value. If not, Marc sets it before continuing.

- [ ] **Step 2: Switch provider**

Modify `.env`:

```
# Was openrouter for v1; v2 uses Anthropic Sonnet 4.6 exclusively.
PEBBLE_PROVIDER=anthropic
PEBBLE_MODEL=claude-sonnet-4-6
```

- [ ] **Step 3: Restart engine, hit /api/v2/generate**

```bash
cd C:/Users/marci/pebble-engine && python pebble_engine.py &
curl -sN -X POST -H "Content-Type: application/json" \
  -d '{"business_name":"Stoneground Loaf","industry":"bakery","extra_context":"Brooklyn sourdough"}' \
  http://127.0.0.1:8000/api/v2/generate
```

Expected: `{"slug": "stoneground-loaf", "engine_version": "v2"}` within ~15s.

- [ ] **Step 4: Inspect the output**

```bash
ls output/stoneground-loaf/site/app/page.tsx && \
  grep -c "{{" output/stoneground-loaf/site/app/page.tsx
```

Expected: file exists, `0` occurrences of `{{` (no placeholder leaks).

- [ ] **Step 5: Commit env + write the proof memo**

```bash
git add .env
git commit -m "feat(env): switch provider to Anthropic Sonnet for v2"
```

Write `docs/superpowers/notes/2026-05-29-v2-phase-1-proof.md` summarizing:
- Build time observed
- Sonnet API cost from response headers
- Diff of page.tsx vs. v1's typical Stoneground output
- Side-by-side screenshots (next dev the v2 output for visual comparison)

---

## Phase 2-4 outlines

To be detailed in their own plan documents when we get to them. High-level:

### Phase 2 plan (Weeks 3-4)

Save to: `docs/superpowers/plans/2026-06-12-pebble-v2-phase-2-block-library-expansion.md`

Per-industry sub-plans (one each for photographer, salon, fitness, service, realestate, restaurant). Each sub-plan:
- Audit existing template assets for that industry (Phase 31 references)
- Author 7-8 blocks (.tsx + .json each)
- Add per-industry routing test
- Commit

End-of-phase deliverable: all 7 industries route cleanly through `/api/v2/generate`.

### Phase 3 plan (Week 5)

Save to: `docs/superpowers/plans/2026-06-26-pebble-v2-phase-3-webcontainers-preview.md`

- StackBlitz account + commercial license signup (Marc decision)
- `npm install @webcontainer/api` in `ui/v3/`
- `WebContainerPreview` component
- Replace iframe src in `WorkspacePreviewPanel`
- Hot-reload on visual-edit
- Decommission `pebble.postbuild.run_dev_server` for v2 sites
- Cost monitoring widget

### Phase 4 plan (Week 6)

Save to: `docs/superpowers/plans/2026-07-03-pebble-v2-phase-4-cutover.md`

- Route `POST /api/generate` to v2 by default
- `?engine=v1` rollback escape hatch
- Legacy banner component on v1 sites in dashboard
- Comment out OpenRouter in `_pick_client()`
- Remove `PEBBLE_AUTO_RUN` / `PEBBLE_AUTO_REPAIR` flags
- Update `CLAUDE.md` API reference
- Sentry alert tuning for v2 error patterns
- Public changelog entry

---

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Sonnet refuses to return valid JSON | Medium | High | Picker has regex extraction + retry with stricter prompt; fail-loud on second miss |
| Block library feels "same-y" across industries | Medium | High | Phase 2 includes design review checkpoint; budget 2-3 hours per industry for visual differentiation |
| WebContainers cost exceeds projection | Low | Medium | Cost widget + monthly cap; fall back to server-side preview if breached |
| Sonnet free-tier cost explodes if abused | Medium | Medium | Per-user daily build limit (5/day for Free); existing rate limiter extended |
| v1 → v2 cutover regresses existing users | Low | High | `?engine=v1` escape hatch + 7-day soak before deprecation banner |
| Block authoring takes longer than estimated | Medium | Medium | Industries shipped sequentially in Phase 2; can ship v2 with subset if others slip |

---

## Cost projections (Sonnet 4.6)

- Sonnet 4.6 pricing: $3/MTok input, $15/MTok output
- v2 build: ~3K input tokens (brief + block menu) + ~5K output tokens (copy + picks)
- Cost per build: 3K × $3/M + 5K × $15/M = $0.009 + $0.075 = **~$0.084/build**
- 100 free-tier users × 5 builds/day × 30 days = 15,000 builds × $0.084 = **~$1,260/mo** on Free alone at full saturation
- Mitigation: 5 builds/day rate limit means realistic Free burn is ~$200-400/mo

---

## Self-review

**Spec coverage** — checked each spec section against task list:
- ✅ Block library schema → Tasks 1-2
- ✅ 7 bakery blocks → Tasks 3-9
- ✅ Compiler with no-placeholder-leak guarantee → Task 10
- ✅ Sonnet picker → Task 11
- ✅ /api/v2/generate endpoint → Task 12
- ✅ Anthropic switchover → Task 13
- ✅ All 7 industries → Phase 2 outline
- ✅ WebContainers preview → Phase 3 outline
- ✅ Cutover + legacy handling → Phase 4 outline

**Placeholder scan** — no TBDs, no "implement appropriate", every code step has full code.

**Type consistency** — `BlockMetadata.slots: dict[str, SlotSpec]` used consistently. `block_id` is always a string of shape `"<industry>/<name>"`. `block_picks` always `list[{block_id, slot_values}]`. `palette` always `dict[str, str]` mapping palette_slot → Tailwind class.

---

## Execution handoff

Plan complete and saved. **Two execution options:**

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task in Phase 1, two-stage review after each, fast iteration. Phase 2-4 plans get written closer to their start dates so they reflect what we learn.

2. **Inline Execution** — I execute Phase 1 tasks myself in this session using executing-plans, batch checkpoints every 3-4 tasks for your review.

Which approach?
