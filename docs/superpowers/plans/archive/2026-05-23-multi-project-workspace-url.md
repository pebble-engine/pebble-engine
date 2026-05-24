# Multi-Project Workspace URL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve a single workspace per URL — `/workspace/<slug>` deep-links to the right project so refreshes, bookmarks, multi-tab use, and shared URLs all work. Today `/workspace` reads `localStorage.pebble.lastBuild`, which silently mixes projects across tabs and breaks any shared link.

**Architecture:** Add a Next.js dynamic route `app/workspace/[slug]/page.tsx` plus a new engine endpoint `GET /api/projects/<slug>` that returns `{slug, brief, plan, build_meta}`. Refactor `WorkspaceShell` to accept an optional `slug` prop — when present, fetch full project state from the engine; when absent (the `/workspace` no-slug entry), keep existing localStorage behavior for the fresh-build / autostart flow. Update sidebar + dashboard + command palette + templates page to navigate via `/workspace/<slug>` instead of `/workspace` + localStorage stamp.

**Tech Stack:** Python (engine handler), Next.js 16 App Router (dynamic route + useParams), React 19, existing test harness (pytest + node test for v3 helpers).

---

## File Structure

**Engine side (Python):**

- Create: `pebble/server/projects.py:run_get_project_state` — new handler function next to `run_list_projects`. Returns brief + plan + build_meta + slug for one project, owner-gated.
- Modify: `pebble_engine.py` — wire the new endpoint into the URL router. There's an existing dispatch in the worktree; this just adds one route.
- Modify: `tests/test_projects_api.py` — JSON-contract tests for the new handler.
- Modify: `tests/test_http_e2e.py` — auth-gate regression pin (401 anon, 404 missing slug, 200 owner).
- Modify: `CLAUDE.md` — add the new route to the HTTP API reference table.

**v3 frontend side:**

- Create: `ui/v3/app/workspace/[slug]/page.tsx` — dynamic-segment page. Reads `params.slug`, renders `<WorkspaceShell slug={...} />`.
- Modify: `ui/v3/components/workspace-shell.tsx` — accept optional `slug?: string` prop. When slug is provided, fetch project state via `/api/projects/<slug>` on mount and populate brief/plan/build state. When absent, keep existing localStorage-based behavior.
- Modify: `ui/v3/lib/api.ts` — add `fetchProjectState(slug)` helper that wraps the new GET endpoint.
- Modify: `ui/v3/app/workspace/page.tsx` — pass no slug prop (it's the fresh-build entry). One-line change to keep TS happy.
- Modify: `ui/v3/components/workspace/dashboard-sidebar.tsx` — `ProjectLink` navigates to `/workspace/${slug}` instead of `/workspace` + localStorage stamp. Drop the `setLastBuild()` call (the new fetch covers it).
- Modify: `ui/v3/app/dashboard/page.tsx` — `openProject` does the same.
- Modify: `ui/v3/components/command-palette.tsx` — same pattern.
- Modify: `ui/v3/app/templates/page.tsx` — already uses `?slug=X` query-param style; convert to `/workspace/${slug}`.

**NOT touched (intentionally):**
- `ui/v3/components/auth-provider.tsx` — OAuth callbacks land on `/workspace` (no slug); user picks a project from sidebar after.
- `ui/v3/app/reset/page.tsx`, `app/signup/page.tsx`, `app/error.tsx`, `app/not-found.tsx`, `app/migrate/page.tsx` — these all redirect TO `/workspace` as a generic "go home" destination. That's still correct.
- `ui/v3/lib/safe-redirect.test.mjs` — tests the safeRedirect helper with `/workspace` as fallback. The new `/workspace/<slug>` URLs ALSO pass safeRedirect because they start with `/`.
- Middleware (`ui/v3/lib/supabase/middleware.ts`) — `PROTECTED_PREFIXES` already covers `/workspace/*` because the check is `path.startsWith(prefix + "/")`. No middleware change needed.

---

## Task 1: Engine endpoint `GET /api/projects/<slug>` — tests first

**Files:**
- Modify: `tests/test_projects_api.py` (add ~3 tests at end)
- Modify: `pebble/server/projects.py` (add `run_get_project_state` function)
- Modify: `pebble_engine.py` (wire the route)

- [ ] **Step 1: Add failing test for empty-slug behavior**

Append to `tests/test_projects_api.py`:

```python
# ---- /api/projects/<slug> (single-project state) -----------------------------

def test_get_project_state_returns_brief_plan_meta(fake_output):
    """The new GET /api/projects/<slug> bundles everything a workspace
    needs to resume a project: slug + brief + plan + build_meta."""
    slug = "good-co"
    (fake_output / slug).mkdir()
    (fake_output / slug / "brief.json").write_text(json.dumps({
        "business_name": "Good Co",
        "business_type": "bakery",
        "_design_dna": "swiss_magazine",
    }), encoding="utf-8")
    (fake_output / slug / "plan.json").write_text(json.dumps({
        "name": "Good Co",
        "audience": "local",
    }), encoding="utf-8")
    (fake_output / slug / "build_meta.json").write_text(json.dumps({
        "built_at": "2026-05-14T12:00:00",
        "model": "qwen/qwen3.6-plus",
    }), encoding="utf-8")
    _seed_site(fake_output, slug, {"app/page.tsx": "x"})

    h = FakeHandler()
    projects.run_get_project_state(h, slug)
    assert h.status == 200
    body = h.json_body
    assert body["slug"] == slug
    assert body["brief"]["business_name"] == "Good Co"
    assert body["plan"]["name"] == "Good Co"
    assert body["build_meta"]["built_at"] == "2026-05-14T12:00:00"


def test_get_project_state_404_for_unknown(fake_output):
    h = FakeHandler()
    projects.run_get_project_state(h, "does-not-exist")
    assert h.status == 404


def test_get_project_state_handles_missing_plan_gracefully(fake_output):
    """Some old projects don't have plan.json yet. Return null for plan
    rather than 500."""
    slug = "ancient"
    (fake_output / slug).mkdir()
    (fake_output / slug / "brief.json").write_text(json.dumps({"business_name": "Ancient"}))
    _seed_site(fake_output, slug, {"app/page.tsx": "x"})

    h = FakeHandler()
    projects.run_get_project_state(h, slug)
    assert h.status == 200
    assert h.json_body["plan"] is None
    assert h.json_body["build_meta"] is None  # also missing
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_projects_api.py::test_get_project_state_returns_brief_plan_meta tests/test_projects_api.py::test_get_project_state_404_for_unknown tests/test_projects_api.py::test_get_project_state_handles_missing_plan_gracefully -v`

Expected: 3 FAILED with `AttributeError: module 'pebble.server.projects' has no attribute 'run_get_project_state'`

- [ ] **Step 3: Implement the handler**

Add to `pebble/server/projects.py` after `run_get_history`:

```python
# --------- GET /api/projects/<slug> -----------------------------------------

def run_get_project_state(handler, slug: str) -> None:
    """Return the full state of a project: slug + brief + plan + build_meta.

    Used by the v3 workspace shell to populate state when a user opens
    a project via /workspace/<slug>. Missing plan / build_meta are
    returned as null (old projects predate them).

    Auth: gated through require_project_owner. The full project state
    includes the brief (business name, design DNA, customer answers)
    which is sensitive enough to keep behind ownership.
    """
    if require_project_owner(handler, slug) is None:
        return

    project_dir = _output_dir() / slug

    def _read_optional(name: str):
        p = project_dir / name
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    handler._json(200, {
        "slug":       slug,
        "brief":      _read_optional("brief.json") or {},
        "plan":       _read_optional("plan.json"),
        "build_meta": _read_optional("build_meta.json"),
    })
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_projects_api.py -v -k "get_project_state"`

Expected: 3 PASSED

- [ ] **Step 5: Wire the route in `pebble_engine.py`**

Find the existing dispatch for `/api/projects/<slug>/history` in `pebble_engine.py` (search for `run_get_history`). Add a sibling case for the bare `/api/projects/<slug>` GET — right after the history wiring. The exact location to find:

```bash
grep -n "run_get_history\|run_toggle_star" pebble_engine.py | head -5
```

Add the route handler dispatch next to those. Pattern (look at how the existing slug-routed GETs are wired and follow the same pattern; do NOT make up new dispatch syntax). The general shape:

```python
# Existing pattern in pebble_engine.py — add a case for the bare slug GET
if path_parts == ["api", "projects", slug]:  # exact 3-part match
    from pebble.server.projects import run_get_project_state
    return run_get_project_state(self, slug)
```

- [ ] **Step 6: Add HTTP e2e auth-gate regression pin**

Append to `tests/test_http_e2e.py` (next to the other `/api/projects/<slug>/*` e2e tests):

```python
def test_get_project_state_401_when_signed_out(engine_server):
    """Auth-gate regression pin — the brief contains design DNA, customer
    answers, etc. Anon callers must 401."""
    out = engine_server["output"]
    _seed_project(out, "good-co", {"app/page.tsx": "x"})
    status, _ = _get(engine_server["base"], "/api/projects/good-co")
    assert status == 401


def test_get_project_state_200_for_signed_in_owner(engine_server):
    cookie = _signin(engine_server["base"], "u@example.com", "valid-password")
    out = engine_server["output"]
    _seed_project(out, "good-co", {"app/page.tsx": "x"},
                  brief={"business_name": "Good Co"})
    status, body = _get_with_cookie(engine_server["base"], "/api/projects/good-co", cookie=cookie)
    assert status == 200
    assert body["slug"] == "good-co"
    assert body["brief"]["business_name"] == "Good Co"
```

- [ ] **Step 7: Run full test suite to confirm zero regressions**

Run: `python -m pytest -q`

Expected: PASS — all previously-passing tests still pass, 5 new tests added (3 unit + 2 e2e).

- [ ] **Step 8: Commit**

```bash
git add tests/test_projects_api.py tests/test_http_e2e.py pebble/server/projects.py pebble_engine.py
git commit -m "feat(engine): GET /api/projects/<slug> — bundled project state for workspace deep-links"
```

---

## Task 2: v3 client helper `fetchProjectState(slug)`

**Files:**
- Modify: `ui/v3/lib/api.ts` (add ~12 lines)

- [ ] **Step 1: Add the helper**

In `ui/v3/lib/api.ts`, add after the existing `listProjects` export (around line 295). Use grep to find the exact spot:

```bash
grep -n "export async function listProjects" "ui/v3/lib/api.ts"
```

Add after that function:

```typescript
// ---------- /api/projects/<slug> (single-project state) ---------------------

export type ProjectState = {
  slug:       string;
  brief:      Record<string, unknown>;
  plan:       PebblePlan | null;
  build_meta: Record<string, unknown> | null;
};

/** Fetch the full state of one project — brief + plan + build_meta.
 *  Used by /workspace/<slug> dynamic route to populate the shell on
 *  mount without depending on localStorage. */
export async function fetchProjectState(slug: string): Promise<ProjectState> {
  return getJSON(`/api/projects/${encodeURIComponent(slug)}`);
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `cd ui/v3 && npx tsc --noEmit`

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add ui/v3/lib/api.ts
git commit -m "feat(v3): fetchProjectState helper for the new GET /api/projects/<slug> endpoint"
```

---

## Task 3: Workspace dynamic route + shell prop

**Files:**
- Create: `ui/v3/app/workspace/[slug]/page.tsx`
- Modify: `ui/v3/components/workspace-shell.tsx` (accept slug prop, fetch on mount when present)

- [ ] **Step 1: Create the dynamic route page**

Write `ui/v3/app/workspace/[slug]/page.tsx`:

```tsx
"use client";

import { use } from "react";
import { WorkspaceShell } from "@/components/workspace-shell";

/**
 * /workspace/<slug> — open an existing project by slug.
 *
 * Next.js 16 App Router passes route params as a Promise — `use()`
 * unwraps it synchronously inside a client component. Then we hand
 * the slug to the shell, which fetches the project state via the
 * /api/projects/<slug> endpoint.
 *
 * Sibling /workspace (no slug) still handles the fresh-build entry —
 * see app/workspace/page.tsx.
 */
export default function WorkspaceSlugPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  return <WorkspaceShell slug={slug} />;
}
```

- [ ] **Step 2: Modify the shell to accept the prop**

In `ui/v3/components/workspace-shell.tsx`, change the function signature. Find the line:

```bash
grep -n "export function WorkspaceShell" "ui/v3/components/workspace-shell.tsx"
```

Update the signature from `export function WorkspaceShell()` to `export function WorkspaceShell({ slug: slugProp }: { slug?: string } = {})`. The shell's existing state already has a "build" object with a `slug` field — the prop is a HINT for the initial load, then localStorage takes over.

The minimal addition inside the component (place right after the existing `useEffect` that loads brief/build/plan from localStorage — search for `getLastBuild()` in the file to find the right spot):

```typescript
  // When the URL provides a slug (we're at /workspace/<slug>), fetch
  // the full project state from the engine. This replaces the
  // stale-localStorage problem where opening a project from the
  // sidebar inherited the previous project's brief/plan.
  useEffect(() => {
    if (!slugProp) return;
    // Skip if localStorage already matches (avoid the round-trip when
    // the user navigated FROM the sidebar, which already stamped state).
    const cached = getLastBuild();
    if (cached?.slug === slugProp && getBrief()?.business_name) return;

    void (async () => {
      try {
        const state = await fetchProjectState(slugProp);
        // Hydrate the same three localStorage keys the legacy flow
        // populates — keeps every downstream consumer working.
        setBrief(state.brief as Brief);
        if (state.plan) setPlan(state.plan);
        setLastBuild({
          slug:        state.slug,
          preview_url: `/preview/${state.slug}/`,
          saved_to:    `output/${state.slug}/`,
          file_count:  0,  // unknown without a separate fetch; UI handles 0
        });
        // Force a re-render with the fresh data
        setBuild(getLastBuild());
        setBriefState(getBrief());
        setPlanState(getPlan());
      } catch (e) {
        console.error("[workspace] failed to load project state:", e);
        // Fall back to /dashboard so the user sees a clear bounce
        // instead of a half-loaded shell
        router.push("/dashboard");
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slugProp]);
```

NOTE: the exact state setter names (`setBriefState` vs `setBrief`, etc) depend on the existing component. Before writing the effect, read `workspace-shell.tsx` lines 80-160 to see the actual state hook names. Match them.

- [ ] **Step 3: Add the import for `fetchProjectState`**

Top of `workspace-shell.tsx`, in the `@/lib/api` import block, add `fetchProjectState`. Find the import line:

```bash
grep -n 'from "@/lib/api"' "ui/v3/components/workspace-shell.tsx"
```

Insert `fetchProjectState` into the existing destructure.

- [ ] **Step 4: TypeScript check**

Run: `cd ui/v3 && npx tsc --noEmit`

Expected: No errors.

- [ ] **Step 5: Restart the v3 dev server + smoke-test deep-linking**

```bash
# Stop any running v3 dev server, then:
cd ui/v3 && npm run dev
```

In a browser, navigate to `http://localhost:3001/workspace/coffee-shop-in-oakland` (or whatever slug exists in `output/`). The workspace shell should render with that project's brief/plan populated in design phase. A bare `http://localhost:3001/workspace` should still work for the fresh-build flow.

- [ ] **Step 6: Commit**

```bash
git add ui/v3/app/workspace/[slug]/page.tsx ui/v3/components/workspace-shell.tsx
git commit -m "feat(v3): /workspace/<slug> dynamic route + shell fetches project state on mount"
```

---

## Task 4: Route sidebar / dashboard / cmd-palette via /workspace/<slug>

**Files:**
- Modify: `ui/v3/components/workspace/dashboard-sidebar.tsx`
- Modify: `ui/v3/app/dashboard/page.tsx`
- Modify: `ui/v3/components/command-palette.tsx`
- Modify: `ui/v3/app/templates/page.tsx`

- [ ] **Step 1: Update sidebar ProjectLink**

In `ui/v3/components/workspace/dashboard-sidebar.tsx`, find `ProjectLink` (around line 311). Replace the `open` function:

```typescript
  function open(e: React.MouseEvent) {
    e.preventDefault();
    // /workspace/<slug> is now self-sufficient — the shell fetches the
    // brief + plan from the engine. We no longer need to stamp
    // localStorage here (the shell does it after the fetch lands).
    router.push(`/workspace/${encodeURIComponent(project.slug)}`);
  }
```

And update the `<a href="/workspace">` to `<a href={`/workspace/${encodeURIComponent(project.slug)}`}>`. Keep `onClick={open}` for the `e.preventDefault()` + smooth client-side navigation.

Remove the `setLastBuild` import if it's no longer used in this file.

- [ ] **Step 2: Update dashboard openProject**

In `ui/v3/app/dashboard/page.tsx`, find `function openProject(p: ProjectSummary)` (around line 93). Simplify to:

```typescript
  function openProject(p: ProjectSummary) {
    router.push(`/workspace/${encodeURIComponent(p.slug)}`);
  }
```

Remove the `setLastBuild` import if no longer used.

- [ ] **Step 3: Update command-palette**

In `ui/v3/components/command-palette.tsx`, find the `run:` callback for `open-${p.slug}` items (around line 99). Replace with:

```typescript
        run: () => {
          router.push(`/workspace/${encodeURIComponent(p.slug)}`);
        },
```

Remove the `setLastBuild` import if no longer used.

- [ ] **Step 4: Update templates page**

In `ui/v3/app/templates/page.tsx`, find `router.push(\`/workspace?slug=...\`)` (around line 481). Replace with:

```typescript
      router.push(`/workspace/${encodeURIComponent(res.slug)}`);
```

- [ ] **Step 5: TypeScript check + dev-server smoke**

```bash
cd ui/v3 && npx tsc --noEmit
```

Expected: No errors.

Restart `npm run dev`, then in a browser:
1. Go to `/dashboard`. Click any project. URL should change to `/workspace/<slug>`. Project should load correctly.
2. Open Cmd-K palette, type a project name, hit Enter. Same expected URL + load.
3. Sidebar: click a different project. URL updates, shell re-fetches.

- [ ] **Step 6: Commit**

```bash
git add ui/v3/components/workspace/dashboard-sidebar.tsx ui/v3/app/dashboard/page.tsx ui/v3/components/command-palette.tsx ui/v3/app/templates/page.tsx
git commit -m "feat(v3): navigate via /workspace/<slug> from sidebar, dashboard, cmd-palette, templates"
```

---

## Task 5: Update CLAUDE.md HTTP API reference + commit

**Files:**
- Modify: `CLAUDE.md` (one row in the HTTP API table)

- [ ] **Step 1: Add the route to the API table**

Find the "Project management (owner-gated)" table in `CLAUDE.md` (search for `/api/projects/<slug>/history`). Add a new row right above the history entry:

```markdown
| GET | `/api/projects/<slug>` | — | **Bundled project state** (slug + brief + plan + build_meta) for the v3 workspace `/workspace/<slug>` deep-link route. Owner-gated. |
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(CLAUDE.md): add /api/projects/<slug> route to API reference"
```

---

## Task 6: Push the branch

- [ ] **Step 1: Push**

```bash
git push squitopest phase56a-for-squitopest
git push origin phase56a-for-squitopest
```

Expected output: `<old-sha>..<new-sha>  phase56a-for-squitopest -> phase56a-for-squitopest` for each remote.

---

## Self-Review (pre-execution checklist)

**Spec coverage:**
- Multi-project URL routing ✓ (Task 3 creates the dynamic route)
- Engine endpoint for project state ✓ (Task 1)
- Sidebar + dashboard + cmd-palette + templates updates ✓ (Task 4)
- Backward compat for `/workspace` (no slug) ✓ (existing page.tsx untouched; only the dynamic route is new)
- Auth gating on the new endpoint ✓ (Task 1 uses `require_project_owner`)
- TypeScript compilation gates ✓ (Tasks 2, 3, 4)
- Smoke tests at each phase ✓ (Tasks 3 step 5, Task 4 step 5)
- CLAUDE.md API reference update ✓ (Task 5)
- Branch pushed ✓ (Task 6)

**Placeholder scan:** None — every step has exact code or exact command.

**Type consistency:**
- `ProjectState` type defined in Task 2, used in Task 3 ✓
- `fetchProjectState(slug)` signature consistent across Tasks 2 + 3 ✓
- `slug` param name consistent ✓

**Edge case I'm flagging in advance (not blocking):**
- The shell's existing localStorage-based `getBrief()`/`getPlan()` will be stale on `/workspace/<slug>` until the fetch completes. The user sees the PREVIOUS project's state for ~200ms while the new fetch lands. Acceptable for v1; could mitigate with a loading state in v2.
- `file_count: 0` in the synthesized lastBuild is a known UI hint — the dashboard cards show file count, but the workspace shell doesn't display it prominently, so the 0 value isn't visible to the user.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-23-multi-project-workspace-url.md`. Two execution options:**

1. **Subagent-Driven** (recommended for this plan) — I dispatch a fresh subagent per task, review between tasks, faster iteration through the 6 tasks.

2. **Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints for review.

**Which approach?**
