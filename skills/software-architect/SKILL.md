---
name: software-architect
description: Plan, review, and evolve software architectures through an explicit artifact-driven workflow. Use when Codex needs to turn a product or engineering brief into architecture drivers, current-state analysis, option tradeoffs, target architecture, integration boundaries, migration steps, risks, and validation criteria. Especially useful for backend platforms, fullstack systems, service decomposition, event-driven designs, scaling plans, architecture reviews, and major refactors where `mesh-flow` should enforce review and validation before recommendations are finalized, without introducing repo-specific side effects into the task-time flow.
_agensi: "36e86c53-09d1-43b5-afd6-2c8490ff5526"
---

# Software Architect

## Overview

Turn an architecture problem into explicit artifacts instead of jumping straight to a final diagram. Use `project.yaml` as the task-time orchestration source of truth so option generation, review, validation, and summary polish happen in a fixed order. Use `project.maintenance.yaml` only when maintainers need to review the skill itself, validate public packaging, or record durable wiki updates.

## Workflow

1. Clarify the architecture problem.
   - Identify the business goal, core user flows, constraints, and success criteria.
   - Separate functional requirements from non-functional requirements.
   - Classify whether the task is primarily a backend platform, SaaS product, or agent system design problem when that changes the option space.
2. Identify architecture drivers.
   - Make scale, latency, consistency, security, operability, and cost tradeoffs explicit.
   - Refuse to hide missing assumptions inside a recommendation.
3. Map the current state.
   - Record services, modules, databases, queues, integrations, trust boundaries, and bottlenecks.
   - Keep unknowns visible.
4. Generate and compare options.
   - Produce at least two viable options when the problem is open.
   - Compare them against the same driver set instead of mixing criteria.
5. Draft the target architecture.
   - Recommend one option with clear component boundaries, data flow, risks, and migration steps.
   - Keep the recommendation implementable, not aspirational.
6. Review and validate before finalizing.
   - Use the mesh-flow review and validation gates in `project.yaml`.
   - Validate the architecture result against the brief, drivers, current state, and output contract, not against the skill scaffold.
7. Prepare the outward-facing summary only when needed.
   - Draft a faithful human-facing summary from the validated recommendation before any rewrite step.
   - Use `ai-smell-detector` only as triage for that summary draft.
   - Allow pass-through or trivial cleanup when the smell score is low.
   - Use `humanize-writing` only on the outward-facing summary draft, not on the technical artifacts.
8. Maintain the skill separately.
   - Use `project.maintenance.yaml` only for skill review, public packaging checks, building a release-candidate `.skill` archive, and optional wiki recording.
   - Do not let normal architecture runs write repo wiki state.

## Output Contract

Default sections for the final architecture artifact:

- `Problem Frame`
- `Architecture Drivers`
- `Current State`
- `Candidate Options`
- `Recommended Architecture`
- `Component Boundaries`
- `Data Flow`
- `Reliability / Scale / Security Notes`
- `Migration Plan`
- `Risks`
- `Open Questions`

## Core Rules

- Prefer explicit tradeoffs over confident but unsupported recommendations.
- Prefer the smallest architecture that satisfies the real drivers.
- Keep current-state observations separate from target-state recommendations.
- Treat hidden coupling, unclear ownership, and migration gaps as design defects.
- Do not let summary polish change technical meaning.
- Let low-smell summaries pass through with only minimal cleanup.
- Keep task-time architecture work free of repo-specific wiki side effects.
- Use the maintenance flow, not the task-time flow, for public packaging checks and optional wiki recording.
- Require explicit approval before maintainer-side wiki recording.
