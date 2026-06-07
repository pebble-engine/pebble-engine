# P4 — Save-as-template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a signed-in owner save any finished project as a personal, reusable template, then spin up new projects from it (clone + optional content-swap).

**Architecture:** A new per-account store at `output/.users/<uid>/templates/` mirrors the curated-template pattern from `pebble/server/templates_api.py`: each saved template is a self-contained copy of a project's `site/` directory (immune to later edits/deletes of the source). "Using" a personal template copies it to a fresh `output/<slug>/site/` and, if the copy contains `content/site.ts` (template-instantiated projects), runs the same focused content-swap LLM call; otherwise it's a plain structural clone (full-generated projects) the owner edits via refine/visual-edit. All endpoints are owner-gated.

**Tech Stack:** Python stdlib (pathlib, shutil, json), existing `pebble.security` auth, existing `templates_api` content-swap helpers, Next.js v3 (`lib/api.ts` + components).

---

### Task 1: `pebble/personal_templates.py` core module

**Files:**
- Create: `pebble/personal_templates.py`
- Test: `tests/test_personal_templates.py`

Storage: `output/.users/<uid>/templates/registry.json` =
`{"schema_version":"1.0","templates":[{id,label,source_slug,created_at,file_count,has_content_ts}]}`.
Template files: `output/.users/<uid>/templates/<id>/site/...`.

- [ ] **Step 1:** Write `tests/test_personal_templates.py` covering: save copies files + returns entry; `has_content_ts` true when source has `content/site.ts`, false otherwise; id is slugified + collision-suffixed; list returns saved entries; get returns one / None; delete removes dir + entry; node_modules/.next excluded; empty/blank label rejected (ValueError); label capped.
- [ ] **Step 2:** Run `python -m pytest tests/test_personal_templates.py -q` → FAIL (module missing).
- [ ] **Step 3:** Implement module:
  - `MAX_LABEL = 80`, `_SKIP = {"node_modules",".next",".turbo","dist","build"}`
  - `_store(output_dir, uid) -> Path`, `_registry_path(...)`, `_read_registry`, `_write_registry`
  - `_safe_id(label, existing) -> str` (slugify a-z0-9-, fallback "template", numeric `-2` suffix on collision; no randomness)
  - `_copy_site(src, dst) -> int` (rglob, skip `_SKIP` parts + dirs)
  - `list_personal_templates(output_dir, uid) -> list[dict]`
  - `get_personal_template(output_dir, uid, template_id) -> dict | None`
  - `template_site_dir(output_dir, uid, template_id) -> Path`
  - `save_personal_template(output_dir, uid, source_site_dir, label, source_slug="") -> dict` (validate label, build id, copy, detect content/site.ts, upsert registry, return entry)
  - `delete_personal_template(output_dir, uid, template_id) -> bool`
- [ ] **Step 4:** Run tests → PASS.
- [ ] **Step 5:** Commit `feat(p4): personal-templates store module`.

### Task 2: API layer `pebble/server/personal_templates_api.py`

**Files:**
- Create: `pebble/server/personal_templates_api.py`
- Test: `tests/test_personal_templates_api.py`

- [ ] **Step 1:** Write tests with a fake handler: list unauthed → 401; save unauthed → 401; save with non-owner slug → 403 (via require_project_owner); save happy path → 200 + entry; use unauthed → 401; use unknown id → 404; delete unauthed → 401. (Patch `_engine().OUTPUT_DIR` to a tmp dir and stub `resolve_user_id`/owner like the brand_kit_api / knowledge_api tests do.)
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement:
  - `run_list_personal_templates(handler)` — `resolve_user_id` else 401; `{"templates": list_personal_templates(...)}`.
  - `run_save_personal_template(handler)` — read body `{slug,label}`; `uid = require_project_owner(handler, slug)` (writes its own error); if None return; site_dir = OUTPUT_DIR/slug/site; 404 if missing; `save_personal_template(...)`; 400 on ValueError (bad label); 200 `{"template": entry, "ok": True}`.
  - `run_use_personal_template(handler, template_id)` — `resolve_user_id` else 401; body `{brief}`; `get_personal_template` else 404; copy `template_site_dir` → new slug `site/` (reuse slug derivation + auto-suffix from templates_api; import its helpers); if `content/site.ts` exists → run content-swap (reuse `_build_content_swap_prompt`/`_extract_typescript_block`/`_validate_swapped_site_ts` + LLM as in `run_instantiate_template`), fold `_account_knowledge`; else skip swap; patch next.config; stamp brief.json (`_personal_template_id`) + build_meta.json (`provider:"personal-template"`, `billable:False`); 200 `{slug,...}`.
  - `run_delete_personal_template(handler, template_id)` — auth else 401; `delete_personal_template`; 200 `{"ok":True}` / 404.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat(p4): personal-templates API endpoints`.

### Task 3: Routes

**Files:** Modify `pebble/server/router.py` (GET, POST, DELETE blocks)

- [ ] **Step 1:** GET `/api/account/templates` → `run_list_personal_templates`.
- [ ] **Step 2:** POST `/api/account/templates` → `run_save_personal_template`; POST `/api/account/templates/<id>/use` (endswith `/use`) → `run_use_personal_template(handler, id)`.
- [ ] **Step 3:** DELETE `/api/account/templates/<id>` → `run_delete_personal_template`.
- [ ] **Step 4:** Restart engine; curl: GET unauthed 401, save unauthed 401, use unauthed 401.
- [ ] **Step 5:** Commit `feat(p4): route personal-template endpoints`.

### Task 4: v3 api.ts + Save-as-template button + Your-templates section

**Files:**
- Modify: `ui/v3/lib/api.ts`
- Create: `ui/v3/components/workspace/save-template-button.tsx`
- Modify: `ui/v3/components/workspace-shell.tsx` (add button to design-phase rightSlot)
- Modify: `ui/v3/app/templates/page.tsx` ("Your templates" section + Use + delete)

- [ ] **Step 1:** api.ts: `PersonalTemplate` type + `listPersonalTemplates()`, `savePersonalTemplate(slug,label)`, `usePersonalTemplate(id,brief)`, `deletePersonalTemplate(id)`.
- [ ] **Step 2:** `SaveTemplateButton` (Bookmark icon; prompt for label via small inline dialog; calls savePersonalTemplate; toast/inline success). Mount in workspace top bar next to BusinessInfoButton.
- [ ] **Step 3:** templates page: load `listPersonalTemplates()`; render a "Your templates" grid above the tier tabs when non-empty; each card has Use (creates project via usePersonalTemplate→route to /workspace/<slug>) + a trash button (deletePersonalTemplate→refresh).
- [ ] **Step 4:** `npx tsc --noEmit` + `npm run build` → clean.
- [ ] **Step 5:** Commit `feat(v3): save-as-template + your-templates gallery (P4)`.

### Task 5: Verify + finish

- [ ] Restart engine; full `python -m pytest -q` (only the known network-DNS failures remain).
- [ ] v3 `npm run build` clean.
- [ ] Commit any residue; summarize for Marc.
