# Workspace Motion Polish — Hand-off (2026-05-15)

This document is for Marc to verify the motion-polish work shipped in
the workspace-motion-polish branch via manual browser testing.

## TL;DR

7 commits shipped + 1 spec commit + 1 plan commit. ~809 pytest passing.
Plain-Node verifiers exit 0. View Transitions API path covered for
Chrome / Edge / Safari; Firefox + older browsers use the AnimatePresence
fallback.

## Commits in this round

```bash
git log --oneline ba98ef8..HEAD
```

(Spec: ba98ef8 · Plan: e7c8106 · Task 1: 6a2e431 + d5c68c4 (follow-up) ·
Task 2: 0b1c45f + 501f151 (follow-up) · Task 3: 3d2f1bf + 3040afb
(follow-up) · Task 4: 154197d · Task 5: e7999dd · Task 6: bbb62a3 ·
Task 7: this commit.)

## Run the v3 dev server

```bash
cd C:\Users\marci\pebble-engine\ui\v3
npm install         # if you haven't already
npm run dev
```

Engine should also be running for previews to work:

```bash
# In a separate terminal, from C:\Users\marci\pebble-engine
python pebble_engine.py
```

Open: http://localhost:3001

## Manual testing checklist

Run through each item in Chrome (or Edge / Safari) and then in Firefox
to verify both the native View Transitions path and the AnimatePresence
fallback feel right.

### Phase navigation

- [ ] Land on `/` (welcome). The big hero text fades in cinematically.
- [ ] Type a project idea and hit send. Watch the welcome → /workspace
      transition.
  - Chrome / Edge / Safari: native View Transitions morph — TopNav and
    Rail visibly slide/fade into place.
  - Firefox: framer-motion AnimatePresence fade. Slightly different
    but still smooth.
- [ ] In the workspace, click rail items: Idea → Plan → Draft → Design
      → Publish. The active highlight (the `bg-primary/15` block behind
      the label) should SLIDE between rail items, not fade.
- [ ] Click back to Idea. Highlight slides back. TopNav stays in place
      (does NOT remount or flash).

### Build narration

- [ ] Enter the idea phase, finish the chip questionnaire, generate
      the plan, then hit Generate. Build screen entrance should stagger:
      droplet → headline → subhead → checklist → live feed.
- [ ] Live feed lines should fade up individually (not instant pop).
- [ ] On completion, the final checklist step pulses (scale up + glow)
      before the design phase fades in.

### Reduced motion

- [ ] Enable OS-level "Reduce motion" preference:
  - macOS: System Settings → Accessibility → Display → Reduce motion ON
  - Windows: Settings → Accessibility → Visual effects → Animation
    effects OFF
- [ ] Refresh /. Re-run any phase transition.
- [ ] All motion should now be instant. The shell stops sliding the
      rail width; phase content swaps without fade.
- [ ] Active-step glow on draft phase should be disabled (the CSS is
      gated on `@media (prefers-reduced-motion: no-preference)`).

### Direct hash hits

- [ ] Visit `http://localhost:3001/workspace#phase=plan` cold (after
      generating a build). Should land directly on the plan phase, no
      flash of design.
- [ ] Reload `/workspace#phase=design` mid-session. Should resume on
      the design phase if a build exists, or bounce to welcome if not.

### Back / forward

- [ ] Browser back from design → plan → idea → welcome. Phase changes
      should animate.
- [ ] Browser forward through the same path. Same animations.

### Window resize

- [ ] Resize the window during a phase transition. No layout glitches,
      no flickering.

### Accessibility

- [ ] On the welcome screen, press Tab. Focus should NOT pass through
      the (collapsed) Build Plan rail. The rail aside is `inert` while
      hidden.

## Known pre-existing flake

`tests/test_auth.py::test_revoke_all_falls_back_when_index_missing`
intermittently fails in the full test suite due to test-ordering
sensitivity. It passes in isolation. NOT introduced by this round of
work; flagged in the Task 5 review and confirmed pre-existing on
parent `154197d`. Worth fixing in a separate session.

## If anything looks wrong

- Capture a screenshot, paste the URL, and tell Claude which phase
  you were in. Include the browser + OS in case the issue is View
  Transitions-specific.
- The spec is at `docs/superpowers/specs/2026-05-15-workspace-motion-
  polish-design.md` — reference it for "this is supposed to do X."

## Files changed

11 v3 files modified + 4 new lib/test files + 1 spec + 1 plan + 1
hand-off doc. Detailed in the commit log.

## What's next (round 2)

Per the spec's "Honest scoping notes" section:

1. Typography pass — font sizes, weights, line heights, letter
   spacing across the v3 design system.
2. Component-level micro-interactions — every clickable element gets
   a refined hover/active/focus treatment.
3. Density / spacing audit.
4. Project-name layoutId morph from welcome hero → TopNav (deferred
   from round 1 because the semantic match isn't clean).
5. Consolidate phaseEnter + phaseExit into a single phaseVariants
   object with hidden/visible/exit keys (architectural cleanup
   noted in Task 3 code review).
6. Apply withReducedMotion() consumer-side wherever variants are
   used in the shell (project-wide reduced-motion pass).

Estimated scope: ~6-8 hours of focused work.
