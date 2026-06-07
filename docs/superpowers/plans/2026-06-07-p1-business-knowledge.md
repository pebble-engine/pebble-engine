# P1 — "About your business" (Business Knowledge) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every Pebble user a durable "about your business" context (per-project + per-account) that is injected into every build, template-instantiation, and refine — so the AI stops re-guessing and respects the owner's standing facts/voice on every edit.

**Architecture:** A small pure module `pebble/knowledge.py` stores/merges knowledge (per-project in `brief.json["business_knowledge"]`; per-account in `output/.users/<uid>/knowledge.txt`) and renders a `knowledge_block` string. That block is injected into the three LLM entry points (full build prompt, content-swap prompt, refine prompt). Owner-gated GET/PUT endpoints + a v3 "Tell Pebble about your business" field manage it. Anti-slop still governs facts — knowledge is *instructions/standing facts the owner supplied*, never fabrication.

**Tech Stack:** Python stdlib HTTP server (`pebble_engine.py`, `pebble/server/*`), str.format prompt template, Supabase-gated auth (`require_project_owner`, `resolve_user_id`), Next.js 14 v3 frontend.

**Scope note:** This is the first of four subsystems (P1–P4). P2 (curated Skills), P3 (brand kit), P4 (save-as-template) get their own plans after P1 ships working.

---

## File Structure

- Create: `pebble/knowledge.py` — load/save/merge knowledge + render `knowledge_block`.
- Create: `tests/test_knowledge.py` — unit tests for the pure functions.
- Modify: `pebble_engine.py` — `build_prompt(...)` gains a `knowledge_block` kwarg + `{knowledge_block}` in the rendered template; `run_build` (in `pebble/server/build.py`) computes + passes it.
- Modify: `skills/prompt_template.md` — add a `{knowledge_block}` slot near the top override region (after the language block / before the brief). str.format — NO single braces.
- Modify: `pebble/server/templates_api.py` — `_build_content_swap_prompt` injects project+account knowledge into the brief section.
- Modify: `pebble/server/refine.py` — prepend `knowledge_block` to the LLM `user_prompt`.
- Create: `pebble/server/knowledge_api.py` — GET/PUT `/api/projects/<slug>/knowledge` (project) + GET/PUT `/api/account/knowledge` (account default). Owner/auth-gated.
- Modify: `pebble/server/router.py` — route the 4 endpoints.
- Modify: `ui/v3/lib/api.ts` — `getProjectKnowledge/saveProjectKnowledge/getAccountKnowledge/saveAccountKnowledge`.
- Create: `ui/v3/components/workspace/business-knowledge-card.tsx` — the "Tell Pebble about your business" textarea card.
- Modify: wire the card into the workspace (exact host file chosen at execution after reading `ui/v3/components/workspace/`).
- Test: `tests/test_knowledge_api.py`, `tests/test_prompt_knowledge_injection.py`.

---

## Task 1: knowledge module (pure core)

**Files:**
- Create: `pebble/knowledge.py`
- Test: `tests/test_knowledge.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_knowledge.py
from pebble import knowledge as k

def test_project_knowledge_reads_brief_field():
    assert k.project_knowledge({"business_knowledge": "We close Sundays."}) == "We close Sundays."

def test_project_knowledge_blank_when_absent():
    assert k.project_knowledge({}) == ""

def test_knowledge_block_empty_when_no_knowledge():
    assert k.render_knowledge_block(project="", account="") == ""

def test_knowledge_block_includes_both_scopes_labeled():
    out = k.render_knowledge_block(project="Closed Sundays.", account="Brand voice: warm.")
    assert "ABOUT THIS BUSINESS" in out
    assert "Closed Sundays." in out
    assert "Brand voice: warm." in out

def test_knowledge_block_truncates_overlong_input():
    out = k.render_knowledge_block(project="x" * 10000, account="")
    assert len(out) <= k.MAX_BLOCK_CHARS + 200  # block + header overhead

def test_sanitize_strips_braces_for_strformat_safety():
    # build_prompt renders via str.format — knowledge must not inject { }
    assert "{" not in k.render_knowledge_block(project="a {b} c", account="")
    assert "}" not in k.render_knowledge_block(project="a {b} c", account="")
```

- [ ] **Step 2: Run, verify FAIL** — `python -m pytest tests/test_knowledge.py -q` → FAIL (module missing).

- [ ] **Step 3: Implement**

```python
# pebble/knowledge.py
"""Durable per-project + per-account 'about your business' context.

Injected into every build / template-instantiation / refine so the AI
respects the owner's standing facts and voice without being re-told.
NOT facts to fabricate — anti-slop still governs invented data.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

MAX_BLOCK_CHARS = 4000  # keep prompt lean; trim pathological input

def project_knowledge(brief: dict[str, Any]) -> str:
    v = (brief or {}).get("business_knowledge")
    return v.strip() if isinstance(v, str) else ""

def _account_path(output_dir: Path, uid: str) -> Path:
    return output_dir / ".users" / uid / "knowledge.txt"

def load_account_knowledge(output_dir: Path, uid: str) -> str:
    if not uid:
        return ""
    p = _account_path(Path(output_dir), uid)
    try:
        return p.read_text(encoding="utf-8").strip() if p.exists() else ""
    except Exception:
        return ""

def save_account_knowledge(output_dir: Path, uid: str, text: str) -> None:
    p = _account_path(Path(output_dir), uid)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text((text or "").strip()[:MAX_BLOCK_CHARS], encoding="utf-8")

def _sanitize(s: str) -> str:
    # str.format safety: literal braces in the build template would break .format
    return (s or "").replace("{", "(").replace("}", ")")

def render_knowledge_block(project: str, account: str) -> str:
    project = _sanitize((project or "").strip())[:MAX_BLOCK_CHARS]
    account = _sanitize((account or "").strip())[:MAX_BLOCK_CHARS]
    if not project and not account:
        return ""
    parts = ["## ABOUT THIS BUSINESS (owner-provided — honor on every page; never contradict)"]
    if account:
        parts.append("Account-wide preferences:\n" + account)
    if project:
        parts.append("This project specifically:\n" + project)
    return "\n\n".join(parts)
```

- [ ] **Step 4: Run, verify PASS** — `python -m pytest tests/test_knowledge.py -q`.

- [ ] **Step 5: Commit** — `git add pebble/knowledge.py tests/test_knowledge.py && git commit -m "feat(knowledge): durable business-knowledge module (P1 core)"`

---

## Task 2: inject into the full build prompt

**Files:**
- Modify: `skills/prompt_template.md` (add `{knowledge_block}` slot — near the top, after the language/override region, before `# Customer brief`-style sections). NO single braces in surrounding additions.
- Modify: `pebble_engine.py` `build_prompt` — add `knowledge_block: str = ""` param; pass `knowledge_block=knowledge_block` into `PROMPT_TEMPLATE.format(...)` (the call ~line 1266).
- Modify: `pebble/server/build.py` `run_build` — compute the block from brief + account uid and pass it to `build_prompt`.
- Test: `tests/test_prompt_knowledge_injection.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_prompt_knowledge_injection.py
import pebble_engine as pe

def test_template_has_knowledge_slot():
    assert "{knowledge_block}" in pe.PROMPT_TEMPLATE

def test_build_prompt_injects_knowledge():
    out = pe.build_prompt({"industry": "pest control"}, "", [], knowledge_block="OWNER SAYS: closed Sundays.")
    assert "closed Sundays" in out

def test_build_prompt_blank_knowledge_renders_clean():
    out = pe.build_prompt({"industry": "pest control"}, "", [])
    assert "{knowledge_block}" not in out  # placeholder consumed even when empty
```

- [ ] **Step 2: Run, verify FAIL.**

- [ ] **Step 3: Implement** — (a) in `skills/prompt_template.md` add a line in the top override region: `{knowledge_block}` on its own line (renders empty string when none). (b) in `build_prompt` add the param + `knowledge_block=knowledge_block` to the `.format(...)`. (c) in `run_build`, before calling `build_prompt`, compute:

```python
from pebble import knowledge as _k
_acct = _k.load_account_knowledge(OUTPUT_DIR, caller_uid or "")
_kb = _k.render_knowledge_block(_k.project_knowledge(brief), _acct)
# ...build_prompt(..., knowledge_block=_kb)
```

- [ ] **Step 4: Run, verify PASS** (also run `python -c "import pebble_engine"` smoke + the existing `tests/test_prompt_copy_craft.py::test_template_still_renders_via_str_format`-style render check by formatting with all keys incl. `knowledge_block`).

- [ ] **Step 5: Commit** — `feat(knowledge): inject business knowledge into full build prompt`

---

## Task 3: inject into content-swap (template instantiation)

**Files:**
- Modify: `pebble/server/templates_api.py` `_build_content_swap_prompt` (add knowledge to the `# Customer brief` section, read from `brief.get("business_knowledge")`; account-level merged by caller `run_instantiate_template`).
- Test: extend `tests/test_templates_api.py`.

- [ ] **Step 1: Failing test**

```python
def test_content_swap_prompt_includes_business_knowledge():
    p = templates_api._build_content_swap_prompt(
        "service_pro", "export const X=1;",
        {"business_name": "T", "business_knowledge": "We only serve commercial clients."},
    )
    assert "commercial clients" in p
    assert "ABOUT THIS BUSINESS" in p
```

- [ ] **Step 2: Run, verify FAIL.**
- [ ] **Step 3: Implement** — in `_build_content_swap_prompt`, after the brief block, append `render_knowledge_block(project_knowledge(brief), brief.get("_account_knowledge",""))`. In `run_instantiate_template`, stamp `brief["_account_knowledge"] = load_account_knowledge(OUTPUT_DIR, caller_uid)` before calling.
- [ ] **Step 4: Run, verify PASS.**
- [ ] **Step 5: Commit** — `feat(knowledge): inject business knowledge into content-swap prompt`

---

## Task 4: inject into refine

**Files:**
- Modify: `pebble/server/refine.py` (~line 230, prepend the knowledge block to `user_prompt` for LLM refinements).
- Test: extend `tests/test_refine_llm.py`.

- [ ] **Step 1: Failing test** — assert that when a project's `brief.json` has `business_knowledge`, the constructed refine `user_prompt` contains it. (Use the existing refine test harness/fixtures in `tests/test_refine_llm.py`; mirror its setup.)
- [ ] **Step 2: Run, verify FAIL.**
- [ ] **Step 3: Implement** — load brief + account knowledge in `run_refine`, build the block, prepend to `user_prompt`.
- [ ] **Step 4: Run, verify PASS.**
- [ ] **Step 5: Commit** — `feat(knowledge): refines respect business knowledge`

---

## Task 5: API endpoints (project + account knowledge)

**Files:**
- Create: `pebble/server/knowledge_api.py`
- Modify: `pebble/server/router.py`
- Test: `tests/test_knowledge_api.py`

- [ ] **Step 1: Failing tests** — using the project's handler-mock pattern (see `tests/test_publish.py` for the FakeHandler style): GET project knowledge returns `{slug, knowledge}`; PUT writes `brief["business_knowledge"]` (snapshot first via `snapshot_site`); owner-gated (401/403 paths); GET/PUT account knowledge round-trips via `save/load_account_knowledge`.
- [ ] **Step 2: Run, verify FAIL.**
- [ ] **Step 3: Implement** `knowledge_api.py`:
  - `run_get_project_knowledge(handler, slug)` — `require_project_owner`; read `brief.json`; return `{slug, knowledge: project_knowledge(brief)}`.
  - `run_put_project_knowledge(handler, slug)` — owner-gated; read body `{knowledge}`; `snapshot_site(slug, reason="edit-knowledge")`; set `brief["business_knowledge"]=text[:MAX_BLOCK_CHARS]`; write brief.json; 200.
  - `run_get_account_knowledge(handler)` / `run_put_account_knowledge(handler)` — `resolve_user_id`; load/save via module.
  Routes in `router.py`: GET/PUT `/api/projects/<slug>/knowledge`, GET/PUT `/api/account/knowledge`.
- [ ] **Step 4: Run, verify PASS** + `python -c "from pebble.server import router"` import smoke.
- [ ] **Step 5: Commit** — `feat(knowledge): GET/PUT project + account knowledge endpoints`

---

## Task 6: v3 frontend — "Tell Pebble about your business"

**Files:**
- Modify: `ui/v3/lib/api.ts` (4 fns mirroring existing `getJSON/postJSON` auth helpers).
- Create: `ui/v3/components/workspace/business-knowledge-card.tsx`
- Modify: host file (chosen at execution after reading `ui/v3/components/workspace/` + `ui/v3/app/settings/`).

- [ ] **Step 1:** Read `ui/v3/lib/api.ts` (auth header + getJSON/postJSON pattern) and the workspace/settings layout to pick the host + match conventions. (AGENTS.md: this Next.js has breaking changes — check `node_modules/next/dist/docs/` before writing.)
- [ ] **Step 2:** Add the 4 api.ts functions hitting the Task-5 endpoints (Bearer auth via existing helper).
- [ ] **Step 3:** Build `BusinessKnowledgeCard`: a labeled textarea ("Tell Pebble about your business — hours, service area, brand voice, anything to always include or never say"), debounced save, "Saved ✓" state, char counter to `MAX_BLOCK_CHARS`. Plain-language helper text, NOT "custom instructions".
- [ ] **Step 4:** Mount it (workspace project settings for per-project; account settings for the account default). Manual verify on localhost (engine :8000 + v3 :3001): type knowledge → reload → persists; run a build/refine → confirm the copy reflects it.
- [ ] **Step 5: Commit** — `feat(v3): 'Tell Pebble about your business' knowledge editor`

---

## Task 7: end-to-end localhost verification

- [ ] Boot engine + v3. Set project knowledge ("We never do weekend jobs; tone is no-nonsense; always show license #"). Run a real template instantiation + an LLM refine. Confirm the output honors it. Run full `pytest` (expect prior baseline failures only). Commit nothing new unless fixes needed.

---

## Self-Review notes
- **Spec coverage:** durable per-project + per-account context injected into build (T2), instantiate (T3), refine (T4); managed via API (T5) + UI (T6). ✓
- **str.format safety:** `_sanitize` strips braces (T1) + render smoke (T2) — guards the #1 prompt gotcha. ✓
- **Naming consistency:** `business_knowledge` (brief field), `render_knowledge_block`, `load/save_account_knowledge`, `project_knowledge` used identically across tasks. ✓
- **Anti-slop:** knowledge is owner-provided instructions; the existing anti-slop rules (no invented facts) remain authoritative and are unaffected.

---

## P2–P4 roadmap (separate plans, built after P1 ships)
- **P2 — Curated "Power moves" (Skills):** author 3–5 `SKILL.md` packs (`/seo-check`, `/make-it-accessible`, `/write-my-about-page`, `/holiday-sale-mode`, `/refresh-the-look`); a matcher that injects a skill body into the relevant build/refine call on `/command` or trigger; v3 buttons. Leverages the Claude-Code Agent-Skills system Pebble already runs on. Own plan.
- **P3 — "My brand kit" (design-system lite):** per-account pinned palette/fonts/voice that all the owner's builds inherit (extends Style DNA via `_design_dna_id`-style pin). Own plan.
- **P4 — "Save as a starting point" (templates):** let an owner register one of their finished sites as a personal template for new builds (reuses the instantiate/clone path). Own plan.
