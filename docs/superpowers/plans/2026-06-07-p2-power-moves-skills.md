# P2 — Curated "Power Moves" (Skills) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (inline) to implement task-by-task. Steps use `- [ ]`.

**Goal:** Give owners a small library of one-click "power moves" (SEO check, make it accessible, write my About page, holiday sale mode, refresh the look) that run as curated, trigger-matchable instruction packs — capability without prompt-engineering.

**Architecture:** Each power move is a `SKILL.md` (YAML frontmatter: id, label, description, triggers, billable + markdown instruction body) under `pebble/power_moves/`. A loader (`pebble/power_moves.py`) parses + caches them and exposes `list_skills() / get_skill(id) / match_skill(text)`. Execution reuses the existing refine machinery: `pebble/server/refine.py` merges the registry into its LLM-refinement path, so `POST /api/refine {refinement_id: "<skill>"}` runs the skill's instruction (snapshot → LLM edit → apply → bill) with zero new execution code. A `GET /api/skills` lists them for the UI; a v3 "Power moves" slide-over invokes them.

**Tech Stack:** Python stdlib (no YAML dep — parse simple frontmatter), existing refine LLM path, Next.js 14 v3.

**Why this shape:** DRY — refine already snapshots, calls the LLM, parses `<pebble-file>` blocks, applies, and spends credits. Power moves are just additional curated instructions, so we add a registry and a thin merge, not a parallel runner.

---

## File Structure
- Create: `pebble/power_moves.py` — loader/registry (frontmatter parse, list/get/match). No YAML dep.
- Create: `pebble/power_moves/seo_check.md`, `make_it_accessible.md`, `write_about_page.md`, `holiday_sale.md`, `refresh_look.md` — the 5 launch skills.
- Modify: `pebble/server/refine.py` — merge registry instructions into the LLM-refinement lookup so refine runs them (billable, snapshotted). Knowledge block (P1) already prepends — skills inherit that for free.
- Create: `pebble/server/skills_api.py` — `GET /api/skills` (public list for the UI).
- Modify: `pebble/server/router.py` — route `GET /api/skills`.
- Create: `ui/v3/components/workspace/power-moves-button.tsx` — top-bar button + slide-over listing skills; each runs `refine(slug, id)`.
- Modify: `ui/v3/lib/api.ts` — `listSkills()`.
- Modify: `ui/v3/components/workspace-shell.tsx` — mount the button in the edit-phase top-bar row (next to Business info).
- Test: `tests/test_power_moves.py`, `tests/test_skills_api.py`, extend `tests/test_refine_llm.py`.

---

## Task 1: power_moves loader + registry (TDD)
**Files:** Create `pebble/power_moves.py`, `tests/test_power_moves.py`; create one real skill `pebble/power_moves/seo_check.md` for the test to load.

- [ ] **Step 1: Failing tests**
```python
# tests/test_power_moves.py
from pebble import power_moves as pm

def test_lists_at_least_one_skill():
    skills = pm.list_skills()
    assert any(s["id"] == "seo_check" for s in skills)

def test_get_skill_returns_frontmatter_and_body():
    s = pm.get_skill("seo_check")
    assert s and s["label"] and s["description"]
    assert isinstance(s["triggers"], list) and s["triggers"]
    assert "instruction" in s and len(s["instruction"]) > 50
    assert isinstance(s["billable"], bool)

def test_get_unknown_returns_none():
    assert pm.get_skill("nope") is None

def test_match_skill_by_trigger_phrase():
    assert pm.match_skill("can you check my SEO please") is not None
    assert pm.match_skill("xyzzy nothing matches") is None

def test_list_skills_is_ui_safe():
    # list payload must NOT include the full instruction (kept server-side)
    s = pm.list_skills()[0]
    assert "instruction" not in s
    assert {"id", "label", "description"} <= set(s)
```

- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3: Implement** `pebble/power_moves.py`:
```python
"""Curated 'power moves' — reusable, trigger-matchable instruction packs
the engine runs through the existing refine path. Each lives as a SKILL.md
(frontmatter + markdown body) under pebble/power_moves/."""
from __future__ import annotations
import functools
from pathlib import Path
from typing import Any, Optional

_DIR = Path(__file__).resolve().parent / "power_moves"

def _parse(md: str) -> dict[str, Any]:
    fm: dict[str, Any] = {}
    body = md
    if md.startswith("---"):
        _, raw, body = md.split("---", 2)
        for line in raw.strip().splitlines():
            if ":" not in line:
                continue
            k, _, v = line.partition(":")
            k, v = k.strip(), v.strip()
            if k == "triggers":
                fm[k] = [t.strip().lower() for t in v.split(",") if t.strip()]
            elif k == "billable":
                fm[k] = v.lower() in ("true", "yes", "1")
            else:
                fm[k] = v
    fm.setdefault("triggers", [])
    fm.setdefault("billable", True)
    fm["instruction"] = body.strip()
    return fm

@functools.lru_cache(maxsize=1)
def _load_all() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not _DIR.exists():
        return out
    for f in sorted(_DIR.glob("*.md")):
        try:
            d = _parse(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        sid = (d.get("id") or f.stem).strip()
        d["id"] = sid
        out[sid] = d
    return out

def get_skill(skill_id: str) -> Optional[dict[str, Any]]:
    return _load_all().get((skill_id or "").strip())

def list_skills() -> list[dict[str, Any]]:
    # UI-safe: omit the instruction body
    return [
        {"id": s["id"], "label": s.get("label", s["id"]),
         "description": s.get("description", ""), "billable": s.get("billable", True)}
        for s in _load_all().values()
    ]

def match_skill(text: str) -> Optional[dict[str, Any]]:
    low = (text or "").lower()
    for s in _load_all().values():
        if any(t and t in low for t in s.get("triggers", [])):
            return s
    return None

def instructions_by_id() -> dict[str, str]:
    """For refine integration: {skill_id: instruction}."""
    return {sid: s["instruction"] for sid, s in _load_all().items()}
```
Create `pebble/power_moves/seo_check.md`:
```markdown
---
id: seo_check
label: Run an SEO check
description: Tighten titles, meta descriptions, headings, and alt text for search.
triggers: seo, check my seo, seo audit, search ranking, meta description
billable: true
---
Improve this site's on-page SEO without changing its visual design or layout.
For every page: ensure a unique, specific <title> and meta description (via the
App Router `metadata` export), exactly one <h1>, descriptive alt text on images,
and semantic heading order. Use the business's real location and services in the
copy where natural. Do NOT invent reviews, ratings, or facts. Output only the
changed files as <pebble-file> blocks.
```

- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5: Commit** — `feat(power-moves): SKILL.md registry + loader + seo_check`

---

## Task 2: author the remaining 4 skills
**Files:** Create `make_it_accessible.md`, `write_about_page.md`, `holiday_sale.md`, `refresh_look.md`.

- [ ] **Step 1:** Write each `SKILL.md` (frontmatter + instruction) following the seo_check shape. Each instruction MUST end with "Output only the changed files as `<pebble-file>` blocks." and forbid invented facts. Content:
  - `make_it_accessible` (triggers: accessibility, a11y, wcag, screen reader, aria): add aria-labels, focus-visible rings, color-contrast fixes, alt text, keyboard nav — no visual redesign.
  - `write_about_page` (triggers: about page, write my about, our story): write a warm, specific About page from the business knowledge + services; placeholders for any unknown facts.
  - `holiday_sale` (triggers: sale, promo, holiday, discount, special offer): add a tasteful, dismissible promo banner + a CTA; use a [PROMO DETAILS] placeholder if none given.
  - `refresh_look` (triggers: refresh the look, redesign, make it modern, new style): restyle within the existing structure/DNA — spacing, type scale, accents — without breaking layout or inventing content.
- [ ] **Step 2:** Add a test to `tests/test_power_moves.py` asserting all 5 ids load and every instruction contains "pebble-file".
- [ ] **Step 3:** Run → PASS.
- [ ] **Step 4: Commit** — `feat(power-moves): 4 more launch skills (a11y, about, sale, refresh)`

---

## Task 3: run power moves through refine (TDD)
**Files:** Modify `pebble/server/refine.py`; extend `tests/test_refine_llm.py`.

- [ ] **Step 1: Failing test** — mirror `test_friendlier_uses_llm_and_writes_returned_files`: seed a site, set FakeLLMClient, `run_refine({slug, refinement_id: "seo_check"})` → 200, `kind=="llm"`, file written, and `client.calls[0]["user"]` contains text from the seo_check instruction (e.g. "on-page SEO").
- [ ] **Step 2:** Run → FAIL (unknown refinement).
- [ ] **Step 3: Implement** — in `refine.py`, build the LLM-refinement instruction lookup as `{**_LLM_REFINE_PROMPTS, **power_moves.instructions_by_id()}` and the `LLM_REFINEMENTS` set as its keys, so a power-move id resolves to its instruction and flows through the existing snapshot → LLM → apply → bill path. (P1's knowledge block already prepends in `_run_llm_refinement`, so power moves honor business knowledge automatically.)
- [ ] **Step 4:** Run → PASS (+ existing refine tests still green).
- [ ] **Step 5: Commit** — `feat(power-moves): run skills through the refine path`

---

## Task 4: GET /api/skills (TDD)
**Files:** Create `pebble/server/skills_api.py`; modify `pebble/server/router.py`; create `tests/test_skills_api.py`.

- [ ] **Step 1: Failing test** — FakeHandler GET → 200 `{skills: [...]}`, each item has id/label/description, NO instruction field.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3: Implement** `run_list_skills(handler)` → `handler._json(200, {"skills": power_moves.list_skills()})` (public; no secrets). Route `GET /api/skills` in `route_get`.
- [ ] **Step 4:** Run → PASS + `from pebble.server import router` import smoke.
- [ ] **Step 5: Commit** — `feat(power-moves): GET /api/skills list endpoint`

---

## Task 5: v3 "Power moves" slide-over
**Files:** Modify `ui/v3/lib/api.ts` (`listSkills`); create `ui/v3/components/workspace/power-moves-button.tsx`; modify `ui/v3/components/workspace-shell.tsx`.

- [ ] **Step 1:** `listSkills(): Promise<{skills: {id,label,description,billable}[]}>` → `getJSON("/api/skills")`.
- [ ] **Step 2:** `PowerMovesButton({slug})`: top-bar button (Sparkles icon) → slide-over (mirror BusinessInfoButton) listing skills as rows (label + description + "credits" tag when billable). Clicking a row calls `refine(slug, id)`, shows a per-row running/done state + a toast on success/failure, closes on done.
- [ ] **Step 3:** Mount `{build?.slug && <PowerMovesButton slug={build.slug} />}` in the edit-phase top-bar row next to BusinessInfoButton; import it.
- [ ] **Step 4:** `cd ui/v3 && npx tsc --noEmit` clean; `npm run build` passes.
- [ ] **Step 5: Commit** — `feat(v3): 'Power moves' slide-over (one-click curated skills)`

---

## Task 6: end-to-end verification
- [ ] Restart engine (picks up new Python). `GET /api/skills` returns 5. Run a real `POST /api/refine {slug, refinement_id:"seo_check"}` against an instantiated test site → confirm it applies SEO edits + spends/sims billing. Full `pytest` (expect only the 24 pre-existing failures). v3 build green.

---

## Self-Review
- **Spec coverage:** registry+loader (T1), 5 skills (T1–T2), execution via refine (T3), list API (T4), UI (T5), verify (T6). ✓
- **DRY:** reuses refine's snapshot/LLM/apply/billing; no parallel runner. ✓
- **No new fabrication risk:** every skill instruction forbids invented facts + ends with the `<pebble-file>` contract; P1 anti-slop + knowledge still apply. ✓
- **Naming consistency:** `power_moves.py`, `list_skills/get_skill/match_skill/instructions_by_id`, refinement_id == skill id throughout. ✓
- **UI-safe list:** `list_skills()` omits instruction bodies (T1 test pins it). ✓

## Note on future "import skills from GitHub" (Lovable parity)
The `SKILL.md` format here is deliberately the Anthropic Agent-Skills shape, so a later P (user/community-imported skills) can drop files into `pebble/power_moves/` (or a per-user dir) with no loader changes. Out of scope for P2 (curated-only at launch keeps it non-technical).
