# Workspace Preview-First Layout Restructure
**Date:** 2026-05-23
**Branch:** phase56a-for-squitopest
**Status:** Ready for implementation

---

## 1. Before / After

### Before (current)

```
+------------------------------------------------------------------+
| TopNav: Pebble. | Project Name | New | Templates | Help | Auth   |
|                           (right slot: Add section | History | Publish) |
+--------+-----------------------------------------+--------------+
| Left   |                                         |              |
| Rail   |    Preview iframe (p-6 padded)          | Launch Setup |
| 240px  |    with fake browser chrome             | 320px panel  |
|        |    + desktop/mobile toggle              |              |
| Home   |                                         | Build Integ. |
| All    |                                         | checklist    |
| Templ  |                                         |              |
| Integ  |                                         | setup_needs  |
| Comm   |                                         | item list    |
|        |                                         |              |
| Fav    |                                         | [Go Live]    |
| Recent |                                         |              |
|        +-----------------------------------------+              |
|        | Fixed bottom chips bar (centered between left+right    |
| Footer | rail via CSS vars):                                    |
|        |   hint label | SuggestionChips | REFINE_CHIPS pill     |
|        |   AI chat bar                                          |
+--------+--------------------------------------------------------+
         (right rail swaps to VisualEditorPanel when element clicked)
```

### After (target)

```
+------------------------------------------------------------------+
| TopNav: Pebble. | Project Name | New | Templates | Help | Auth   |
|                           (right slot: Add section | History | Publish) |
+--------+---------------------------------------------------------+
| Left   |                                                         |
| Rail   |         FULL-BLEED PREVIEW IFRAME                      |
| 240px  |         No padding, no fake browser chrome             |
|        |         URL bar + device toggle stay (inside iframe    |
| [Chat] |         chrome strip — just moved up to top of iframe) |
| button |                                                         |
|        |         (Visual editor panel slides in from RIGHT      |
| Home   |          when element clicked — 320px, same as today   |
| All    |          but no longer competing with LaunchSetup       |
| Templ  |          for space)                                     |
| Integ  |                                                         |
| Comm   |                                                         |
|        |                                                         |
| Fav    |                                                         |
| Rec    |                                                         |
|        |                                                         |
| ──     |                                                         |
| Setup  |                                                         |
| [✓] 1  |                                                         |
| [✓] 2  |                                                         |
| [ ] 3  |                                                         |
| [ ] 4  |                                                         |
|        |                                                         |
| Footer |                                                         |
+--------+---------------------------------------------------------+
         Refinement chips: collapsed pill anchored bottom-left of
         preview area; hovers over preview edge, not center.
```

---

## 2. File-by-File Changes

### 2.1 `ui/v3/components/workspace/dashboard-sidebar.tsx`

**What changes:** Add two sections to the existing sidebar markup.

**Section A — Pebble Chatbot button** (new, above the primary nav, below the workspace label):
- A single button styled like a `NavLink` but with a distinct speech-bubble or sparkle icon and label "Ask Pebble".
- `onClick` fires `window.postMessage({ type: "pebble-chat-open" }, "*")` so the workspace shell can intercept it and open a chat panel without prop-drilling.
- Alternatively: open `/help` with a chat anchor, or trigger a future `ChatPanel` via a shared context. For now, the postMessage approach keeps the sidebar zero-prop dependency.

**Section B — Launch Setup checklist** (new, below the Recents section, above the footer):
- A new `<LaunchSetupRail>` component (see §3.1) rendered inside the sidebar.
- Receives `plan` via a new `onNeedsPlan` callback OR via a React context (see §4 — recommendation below).
- Collapsed by default with a section header "Launch Setup" + item count badge. Expands inline (no drawer).
- Each item is a single row: checkbox glyph + label only. NO notes field, NO dependency graph, NO status badges other than a color-coded dot.

**What does NOT change:** The primary nav rows (Home, All designs, Templates, Integrations, Community), Favorites, Recents, the footer, and the Upgrade/Usage widgets.

**Complexity:** Medium (sidebar data plumbing is the tricky part)

---

### 2.2 `ui/v3/components/phases/edit-phase.tsx`

This file has the most deletions.

**Remove:**
- The entire `LaunchSetupPanel` function and its JSX in the `<AnimatePresence>` right-rail swap block (lines 581-601 and 673-775).
- The `publishable` state variable and the `setPublishable` call from `onResult` (they were only used by `LaunchSetupPanel`).
- The `BuildIntegrityChecklist` import (no longer needed here).
- The `--right-rail-w` CSS custom property reference from the chips bar `style` attribute (line 511). Remove the `, right: 'var(--right-rail-w, 320px)'` part — the chips bar should now extend to the right edge of the preview.

**Modify — chips bar repositioning:**
- Change the chips bar from `fixed bottom-6` centered between both rails to a **left-anchored floating panel** pinned to the bottom-left of the preview area.
- New CSS: `fixed bottom-6 left-[calc(var(--left-rail-w,240px)+16px)]` — i.e., 16px right-offset from where the left rail ends.
- The chips bar should NOT span full width. Cap it at `max-w-max` so it's a compact pill-cluster that stays in the bottom-left corner rather than stretching across the full preview.
- The AI chat bar stays as a separate element, also bottom-left anchored, stacked directly above the chips nav row (already the case today).

**Modify — VisualEditorPanel behavior:**
- `VisualEditorPanel` currently renders inside the same `<AnimatePresence>` that swapped with `LaunchSetupPanel`. Without the LaunchSetupPanel, the right rail now only ever renders `VisualEditorPanel` (when `selected !== null`).
- Adjust: make `VisualEditorPanel` an absolute overlay that slides in from the right edge of the preview iframe area (not from the right edge of the viewport). Use `absolute` positioning within the `<main>` container rather than a flex child. This way it appears as a floating side panel over the preview, not consuming its own layout column.
- Add a semi-transparent backdrop (`bg-charcoal/20`) behind it so the panel feels layered rather than embedded.
- Keep the panel width at 320px. Keep all existing controls (text, font-size, color, image-swap) unchanged.

**Modify — iframe chrome strip:**
- The existing fake browser chrome bar (with the macOS-style dots, URL pill, and device toggle) is currently inside `<main>` with `p-6` padding on the entire `<main>`. Remove the `p-6` padding from `<main>`. The iframe should fill edge-to-edge.
- Keep the chrome strip (it gives context — the user sees the URL and can switch desktop/mobile). But move it flush to the top of the preview area (it already is, just now there's no outer padding).

**Complexity:** Medium

---

### 2.3 `ui/v3/components/workspace-shell.tsx`

**Changes:**
- Pass `plan` down to `DashboardSidebar` so `LaunchSetupRail` can render it without a fetch.
- Currently `DashboardSidebar` takes no props. Two approaches:
  - **Preferred:** Add an optional `plan?: PebblePlan | null` prop to `DashboardSidebar` and thread it from `WorkspaceShell` where `phase === "design"`.
  - Alternative: use a React context (overkill for one prop; keep it simple).
- The `--right-rail-w` CSS variable should be removed from wherever it is declared (currently set to `320px` via the `style` attribute on the chips bar). After this change there is no right rail to account for.
- The `--left-rail-w` CSS variable can stay — the chips bar uses it to avoid overlapping the sidebar.

**Complexity:** Small

---

### 2.4 `ui/v3/components/workspace/dashboard-sidebar.tsx` — prop update

Update the function signature:

```tsx
export function DashboardSidebar({ plan }: { plan?: PebblePlan | null } = {})
```

Import `PebblePlan` from `@/lib/state`. Render `<LaunchSetupRail plan={plan} />` between the Recents section and the footer `mt-auto` block.

**Complexity:** Small

---

### 2.5 New file: `ui/v3/components/workspace/launch-setup-rail.tsx`

New component extracted from `LaunchSetupPanel` in `edit-phase.tsx`. Key differences:

- No "Go Live" button (that button belongs in the TopNav's Publish slot, which already exists).
- No `BuildIntegrityChecklist` (remove — integrity checks are redundant here; the user can trigger a publish from the top nav which can re-run checks at that point).
- No dependency graph prose ("Unlocks after: Hosting + Pages").
- Tight list: just a `[✓]` or `[ ]` glyph + the item label per row.
- A section header "Launch Setup" with an item-count badge (`N items remaining`).
- Collapsible: clicking the header toggles an `isExpanded` boolean. Default: collapsed when all items are "auto", expanded otherwise — so new users always see it open.
- Items displayed: only the "keep" subset (see §5 below).

**Complexity:** Small

---

## 3. Component Decomposition

### 3.1 `LaunchSetupRail` (new, `ui/v3/components/workspace/launch-setup-rail.tsx`)

```
Props:
  plan: PebblePlan | null
  className?: string

State:
  isExpanded: boolean (default: false if all auto, true otherwise)

Renders:
  <section>
    <button onClick toggle>
      Launch Setup
      <span>{pendingCount} remaining</span>
      <ChevronDown (rotates when expanded) />
    </button>
    {isExpanded && (
      <ul>
        {KEPT_ITEMS.map(item => (
          <li>
            {item.status === "auto" ? <Check /> : <Circle />}
            {item.label}
          </li>
        ))}
      </ul>
    )}
  </section>
```

No network calls. Pure display from the `plan` prop.

### 3.2 `PebbleChatbotButton` (new inline in `dashboard-sidebar.tsx`, no separate file needed)

A single `<button>` with a `MessageSquare` (or `Bot`) icon and the label "Ask Pebble". Placed as the first item after the workspace label, before the primary nav items. Styling: same `NavLink` shape but with a distinct bg tint (e.g., `bg-primary/10`). Action: emit a custom event or postMessage to open a future chat panel. For now: `onClick={() => alert("Pebble chat coming soon!")}` as a placeholder — the important thing is that the button is present and styled.

### 3.3 `VisualEditorPanel` — overlay mode (modification, no new file)

The panel stays in `edit-phase.tsx` but its CSS positioning changes from being a sibling flex item (right rail) to an `absolute`-positioned overlay inside `<main>`. No API changes.

---

## 4. Refinement Chips + Iterate Input: Recommendation

**Recommendation: Bottom-left floating dock, anchored to the left rail edge.**

Rationale:
- The user's primary goal is to see the site. Chips crossing the preview horizontally (current behavior) pull visual attention from the content they're evaluating.
- A bottom-left dock keeps controls close to the left rail navigation — the user's eye naturally looks left for controls. The right side of the preview stays completely clear.
- "Hover to reveal" (an alternative) would hide controls that aren't discoverable — bad for Marc's target audience (non-technical users who benefit from visible affordances).
- A right-edge collapsible dock (another alternative) would still consume preview real-estate when open and would conflict with the VisualEditorPanel overlay.

**Specific layout:**

```
Bottom-left corner of the preview area:
  [ 🧠 Make it friendlier ] [ 🎨 Palette shift ] ... (chips pill)
  [ ✨ Simpler ] [ 📅 Add booking ]
  [ 💬 Ask a change... "Make it friendlier"  → ]  (chat bar)
  [ + Add section ] [ Testimonials ] [ Pricing ] [ FAQ ] (suggestion chips)
```

The entire cluster is `fixed` positioned at `bottom-6 left-[calc(240px+16px)]` (respecting the left-rail width via the CSS variable). It does NOT span to the right — it is left-anchored and `max-w-fit`. This keeps the right 60%+ of the preview completely unobstructed.

For the hint text line ("✨ Style tweaks are free — click an element..."), move it inside the chips dock as a small `type.caption` line at the top, not a centered banner across the full width.

---

## 5. Launch Setup Keep / Drop List

From the 14 items in `_LAUNCH_SETUP_TEMPLATE` (`pebble/plan.py`):

| Item ID | Label | Keep in rail? | Reason |
|---|---|---|---|
| `project_name` | Project name | **DROP** | Marc explicitly said drop. Already editable in the TopNav. |
| `website_address` | Website address | Keep | Meaningful to the user. |
| `hosting` | Hosting | **DROP** | Marc explicitly said drop. Goes in Settings. |
| `business_email` | Business email | **DROP** | Marc explicitly said drop. Goes in Settings. |
| `logo_photos` | Logo & photos | Keep | User-actionable, clearly understandable. |
| `pages` | Pages | Keep | Reassuring to see "auto-done". |
| `forms` | Forms | Keep | Contact form status matters to users. |
| `booking` | Booking | Keep | Visible goal for service businesses. |
| `payments` | Payments | Keep | Clearly understandable. |
| `seo_basics` | SEO basics | Keep | Important and auto-done — a confidence signal. |
| `analytics` | Analytics | Keep | Users want to know if tracking is set up. |
| `language_region` | Language & region | Keep (optionally) | Low priority — can be hidden behind "show more". |
| `accessibility` | Accessibility | Keep | Auto-done confidence signal. |
| `publish` | Publish | Keep | The goal — make it prominent. |

**Rail item order (suggested):** Pages → Forms → SEO basics → Accessibility → Logo & photos → Website address → Booking → Payments → Analytics → Publish
(Auto-done items first so the user sees green checks immediately, then the actionable ones.)

The three dropped items (`project_name`, `hosting`, `business_email`) should eventually live in a Settings page (linked from the sidebar footer or from a gear icon in the TopNav). No Settings page is in scope for this plan.

---

## 6. Migration Risks

### 6.1 Visual Edit Bridge (`PEBBLE_VISUAL_EDIT_BRIDGE`)

**Risk level: Low.**

The bridge is injected server-side by the engine into every `/preview/<slug>/` HTML response (`pebble_engine.py`). It posts `pebble-select` messages to `window.parent`. The `EditPhase` component listens for these via `window.addEventListener("message", onMessage)`.

This listener is not affected by the layout change. The only change is that `VisualEditorPanel` switches from a flex sibling to an `absolute` overlay. The postMessage flow is unchanged.

**Verify after implementation:** Click an element in the iframe; confirm the editor panel appears as a right-edge overlay without disrupting the full-bleed preview layout.

### 6.2 Fixed-position chips bar CSS variable (`--right-rail-w`)

**Risk level: Low.**

The chips bar currently sets `right: var(--right-rail-w, 320px)` to avoid the LaunchSetupPanel. After removing the right rail, this variable must be removed or set to `0`. If it's declared anywhere else (e.g., a CSS file or a `globals.css` custom property), grep for it and clean up.

### 6.3 `publishable` state in `EditPhase` / `BuildIntegrityChecklist`

**Risk level: Low.**

The `publishable` state variable (`const [publishable, setPublishable] = useState<boolean | null>(null)`) was used only by `LaunchSetupPanel` to show a pre-publish warning and conditionally disable the Go Live button. When `LaunchSetupPanel` is removed, `publishable` state and its `onResult` callback become dead code. Remove both cleanly to avoid a stale-state footgun.

The `BuildIntegrityChecklist` component itself (`build-integrity-checklist.tsx`) should NOT be deleted — it may be reused on the Publish phase. Just remove its import and usage from `edit-phase.tsx`.

### 6.4 E2E tests

**Risk level: Low.**

Check `tests/test_http_e2e.py` and any Playwright tests for assertions on:
- The right-rail 320px panel (LaunchSetupPanel)
- The centered chips bar width or position

None of the 15 HTTP e2e tests are UI-position-aware (they test the engine API, not CSS layout), so no test breakage is expected. If Playwright screenshot tests exist and compare pixel-level layout, those will need snapshot updates.

### 6.5 Published-subdomain mode

**Risk level: None.**

The full-bleed preview change only affects the Pebble workspace at `localhost:3001` (and `pebbleapp.ai`). The published customer site on `*.pebbleapp.ai` or a custom domain is served directly by the engine's `/preview/<slug>/` endpoint — completely separate from the workspace shell layout. No changes needed.

### 6.6 `DashboardSidebar` prop change (shared component)

**Risk level: Low.**

`DashboardSidebar` is currently used on `/dashboard`, `/workspace`, and other pages. Adding an optional `plan?: PebblePlan | null` prop with a default of `null` is backwards-compatible — all other call-sites omit the prop and the `LaunchSetupRail` simply renders nothing when `plan` is null (or is hidden entirely for non-design phases).

### 6.7 Sidebar scroll overflow

**Risk level: Medium.**

The sidebar currently has `min-h-[calc(100vh-4rem)]` and scrolls its own content via natural document flow. Adding `LaunchSetupRail` below Recents may push the footer upgrade widget off-screen on short viewports (e.g., 768px height). The sidebar should get `overflow-y-auto` with a `flex flex-col` + `flex-1` on the scrollable middle section so the footer always stays pinned at the bottom. This is a pre-existing issue that this change makes more likely to surface.

---

## 7. Complexity Estimates

| Task | File(s) | Complexity |
|---|---|---|
| Remove `LaunchSetupPanel` from `edit-phase.tsx` | `edit-phase.tsx` | Small |
| Remove `BuildIntegrityChecklist` import + `publishable` state | `edit-phase.tsx` | Small |
| Convert `VisualEditorPanel` to absolute overlay | `edit-phase.tsx` | Small |
| Remove outer `p-6` from `<main>`, keep inner chrome strip | `edit-phase.tsx` | Small |
| Reposition chips bar to bottom-left anchored dock | `edit-phase.tsx` | Medium |
| Remove `--right-rail-w` CSS var from chips bar `style` | `edit-phase.tsx` | Small |
| Create `LaunchSetupRail` component | `launch-setup-rail.tsx` (new) | Small |
| Add `PebbleChatbotButton` inline in sidebar | `dashboard-sidebar.tsx` | Small |
| Add `LaunchSetupRail` to sidebar, add `plan` prop | `dashboard-sidebar.tsx` | Small |
| Thread `plan` prop from `WorkspaceShell` to `DashboardSidebar` | `workspace-shell.tsx` | Small |
| Fix sidebar scroll overflow (flex layout) | `dashboard-sidebar.tsx` | Small |
| Verify visual-edit bridge still works end-to-end | Manual QA | Small |
| Grep + remove `--right-rail-w` from any CSS files | Repo-wide | Small |

**Total estimated complexity: Medium.** All individual tasks are Small; the medium rating reflects the number of coordinated touch-points across files.

**Suggested implementation order:**
1. Create `launch-setup-rail.tsx` (zero dependencies)
2. Modify `dashboard-sidebar.tsx` (add button + rail + plan prop + overflow fix)
3. Modify `workspace-shell.tsx` (thread plan prop)
4. Modify `edit-phase.tsx` (remove LaunchSetupPanel, convert VisualEditorPanel, reposition chips bar)
5. Manual QA: verify visual-edit bridge, chips bar positioning, sidebar scroll on a 768px window
