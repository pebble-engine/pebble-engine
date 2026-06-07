# Lovable "Customization" deep-dive → how Pebble should implement (2026-06-07)

Studied every section of Lovable's settings, focused on the **Customization** group
(Knowledge, Skills, Templates, Design systems) — the "teach your project / teach your AI"
features. Marc's question: *is this real LLM customization, or a front for easier prompting?*

## The honest answer to "is it real LLM work or just prompting?"
**It's structured prompt context — NOT fine-tuning.** And that's the correct, frontier way to
do it. Neither Lovable nor anyone serious fine-tunes a model per customer (cost, staleness, no
quality win over good context). The durable customization is two layers:
1. **Knowledge** = persistent *custom instructions* injected into the model's context on every run.
2. **Skills** = modular, *trigger-activated instruction documents* loaded only when relevant.

The "magic" isn't a smarter model — it's **giving the same model durable memory (Knowledge) and
on-demand expertise (Skills) without bloating every prompt.** Marc's instinct is right: it's a
front for better prompting. But that front IS the state of the art for reliable agents.

**The kicker for us:** Lovable's Skills are *literally the Anthropic Agent Skills system*
(`SKILL.md` + frontmatter + trigger phrases + "/" invocation + auto-activation + GitHub import).
**Pebble already runs on Claude Code, which has this exact system natively.** We are uniquely
positioned to expose it — we'd be surfacing a capability we already have under the hood.

---

## What each Customization feature actually is

### 1. Knowledge  (`/settings/knowledge`)
- "Custom instructions that apply across all projects in your workspace" + per-project.
- Examples Lovable gives: coding style/naming, preferred libraries/patterns, behavioral rules
  (tone, language, formatting).
- **Mechanism:** a persistent text blob prepended to the LLM context for every generation.
  Two scopes: workspace-wide and per-project. This is "ChatGPT custom instructions" for builds.

### 2. Skills  (`/settings/skills`)  ← the deep one
- "Reusable instructions your agents apply… so the agent gets it right without being told twice."
- Author by *describing in chat* or *importing from GitHub/URL*. Invoke with **"/"** or let it
  **auto-activate when the task matches the trigger.** Shareable across the team.
- Lovable ships built-ins, each with explicit trigger phrases:
  - `accessibility` — a11y audit + fixes (triggers: "check accessibility", "WCAG", "aria labels"…)
  - `redesign` — visual redesign of existing UI
  - `seo-review` — SEO audit → results panel
  - `skill-creator` — guides authoring well-structured `SKILL.md` files (frontmatter, triggers)
  - `video-creator` — programmatic animated videos
- **Mechanism = Anthropic Agent Skills.** Each skill is a `SKILL.md`: name + description +
  trigger conditions in frontmatter, instructions in the body. The agent reads the lightweight
  descriptions, and only loads a skill's full body when its trigger matches the user's request —
  so context stays lean but capability is deep. Identical to the `superpowers`/skill system this
  very engine is built on.

### 3. Templates  (Business tier)
- "Reuse projects as workspace templates… new builds begin from a consistent base."
- = save a finished project as a reusable starting point. **Pebble already has this** (examples +
  templates that clone instantly).

### 4. Design systems  (Enterprise tier)
- "Promote any project to a design system so every new build inherits your components and tokens."
- = a shared component/token library. **Pebble's Style DNA is the analog** (palette/fonts/voice),
  though ours is engine-picked, not user-pinned.

(Other settings groups are standard SaaS: Account/Devices, Plans & credits, Cloud & AI balance,
People/Groups/Identity[SSO], Git, Workspace domains, Privacy/Security/Audit logs — mostly
team/enterprise plumbing, low relevance to Pebble's solo-SMB user.)

---

## How Pebble should implement this (prioritized)

Guiding principle: **Lovable exposes these to technical teams who will author SKILL.md and write
rules. Pebble's user is a non-technical SMB owner who never will.** So we take the same powerful
mechanisms but wrap them as *guided capture* and *one-click curated packs*, not config IDEs.

### ⭐ P1 — "About your business" (= Knowledge). Highest ROI, easiest.
A persistent, per-project + per-account field injected into every build AND refine prompt.
- **User-facing framing (NOT "custom instructions"):** "Tell Pebble about your business" —
  a friendly guided capture: hours, service area, brand voice (pick: warm / no-nonsense / premium),
  things to always include (phone, license #), things to never say.
- **Why it wins:** durable memory. Today every refine/rebuild re-guesses; with this, the owner
  says it once and every edit respects it. Directly serves "everything explained, editable later."
- **Implementation:** new `knowledge` field on the project (+ account-level default). Inject it
  into the build prompt (alongside `intent_block`/`no_slop_block` in pebble_engine.build_prompt)
  and into `pebble/server/refine.py` LLM refinements + the content-swap prompt
  (`_build_content_swap_prompt`). ~1 day. Anti-slop still applies (it's instructions, not facts to
  fabricate).

### ⭐ P2 — Curated "Power moves" (= Skills), Pebble-authored, one-click.
A small library of trigger-activated instruction packs the user invokes from chat or a button —
NOT a build-your-own-skill editor.
- **Launch set:** `/seo-check`, `/make-it-accessible`, `/write-my-about-page`,
  `/add-online-booking`, `/holiday-sale-mode`, `/refresh-the-look` (redesign), `/add-testimonials`
  (guides them to paste real reviews — ties into tonight's honesty work).
- **Why it wins:** deepens the AI's capability per task without bloating the base prompt, and it's
  a capability we ALREADY have (Claude Code Agent Skills). Each is a `SKILL.md` Pebble maintains;
  the user just clicks. This is "going deeper on the LLM" honestly.
- **Implementation:** author skills as `SKILL.md` under the engine; the engine matches the user's
  request/`/command` to a skill and injects its body into the relevant build/refine call. Pebble
  is literally built on the system that does this — reuse it. ~2-4 days for the framework + 3-5
  launch skills. Curated-only at launch (no user authoring → keeps it non-technical).

### P3 — "My brand kit" (= Design systems, lite). Medium.
Let a returning/multi-site owner pin a personal brand (colors, fonts, logo, voice) that all their
builds inherit — a user-pinned extension of Style DNA. Good for the "I have 3 locations" owner.

### P4 — "Save as a starting point" (= Templates). Low (we mostly have it).
Let an owner reuse one of their own sites as a base for the next. Nice for agencies/multi-site;
low priority for single-site owners.

## Strategic takeaway
- **Don't fine-tune.** The right investment is Knowledge (durable context) + Skills (modular
  expertise) — exactly what Lovable did, and exactly what our Claude-Code foundation gives us
  cheaply.
- **Our differentiation:** Lovable ships a *power-user config surface*. We should ship the same
  depth as *guided capture + one-click packs* — so a plumber gets the benefit without ever seeing
  "SKILL.md", a trigger phrase, or a rules editor. Same engine, non-technical wrapper.
- **Sequencing:** P1 ("About your business") first — biggest UX win, lowest effort, and it makes
  every other AI feature (refine, skills) sharper because the model finally has durable context.
