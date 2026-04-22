# Scale Modes

Three scales match the size of the project. Smaller projects deserve less ceremony. Bigger projects need more discipline.

**v3.1 rule (Invariants #8 + #20):** Scale controls depth and cadence, not the **presence** of plan-critique. Tier-1 plan-critique (four lenses via `gstack-team:plan-*-review`) runs at every scale, including light. Scale decides whether the four lenses run as four separate specialist spawns (standard / heavy) or as one condensed single-pass specialist spawn (light). Scale cannot waive critique.

---

## §light — Light (up to ~3 days, solo or small scope, one focused task)

**Example prompts that indicate light mode:**
- "Write a landing page today"
- "Help me draft a blog post this afternoon"
- "Fix these 3 bugs before EOD"
- "Quick research summary on topic X"

### Team composition
- Chief of Staff (required)
- 1 primary specialist (the single most relevant role)
- Optional: 1 critic/devil's-advocate persona

### Setup flow — skip these steps
- Step 5 (connectors/plugins) — run **only the critical tier** (workspace bash, `gstack-team` plugin); skip recommended and optional tiers unless explicitly asked
- Step 6 (setup review) — skip entirely
- Scheduled retros (part of Step 5d) — skip the calendar cadence; still run a condensed retro at milestone completion per Invariant #22
- Formal registers — use a single `notes.md` instead of 4 registers
- **Graphify — skip entirely.** Light projects are usually sub-100-LOC or single-file; there is no cross-file structure to graph and the skill-loading overhead exceeds the context savings. CoS does not spawn graphify-equipped specialists at light scale.

### gstack-team skills at light scale

Enabled at light:
- `gstack-team:context-save` / `gstack-team:context-restore` — still run at session boundaries
- `gstack-team:plan-ceo-review` + `gstack-team:plan-eng-review` + `gstack-team:plan-design-review` + `gstack-team:plan-devex-review` — condensed into ONE specialist spawn applying all four lenses in a single pass (per Invariant #8 exception). Never skipped.
- `gstack-team:make-pdf` — still the default export for user-facing deliverables (Invariant #24)
- `gstack-team:freeze` / `:guard` / `:unfreeze` — available on request, not auto-enabled
- `gstack-team:careful` — not auto-loaded; user may request

Deferred at light (loaded only on explicit request):
- `gstack-team:review`, `:cso`, `:investigate`, `:qa`, `:design-review` — the project is usually too small to warrant these at standard depth; user may explicitly request for a specific turn
- `gstack-team:ship`, `:canary`, `:land-and-deploy` — light projects usually do not run formal deploy flows
- `gstack-team:retro` — condensed retro via inline template, not the full skill

### Per-turn workflow — simplifications
- **Use `protocol/boot-light.md` instead of `boot.md`** — compact checklist, same safety guarantees, ~60% fewer tokens per turn
- Still log every prompt
- Still strict propose-then-yes gate
- Still run the pre-write-checklist (PATTERN:pre-write-checklist) before every write
- Critic persona activates only on big decisions (scope, direction)
- Checkpoints: one at init, one at done
- **Post-compaction:** use boot-light.md for the tiered resume (CLAUDE.md + log tail + roadmap only), not the full 12-step resume

### Plan-critique at light scale (mandatory)

Even at light scale, every implementation plan runs through all four plan-critique lenses. The condensed form:

1. CoS spawns ONE specialist with the four `gstack-team:plan-*-review` skills listed in order.
2. The specialist applies each lens in sequence in a single pass, returning findings per-lens.
3. CoS consolidates and presents to the user per PATTERN:plan-critique-sequence.

A light-scale plan-critique should complete in under ~600 words across all four lenses combined. If a lens flags a blocker, the plan does not execute until the blocker resolves — same rule as standard / heavy. See `references/patterns.md` PATTERN:plan-critique-sequence for the exact shape.

### When light graduates to standard
If the project grows past ~3 days, or adds a second domain (e.g., "actually let's also do a demo video"), pause and ask: *"This is growing — want to upgrade to standard scale?"*

---

## Standard (1 day to 1 month, real project)

**Example prompts:**
- "Build a marketing site over 2 weeks"
- "Research customer pain points and deliver a report by end of month"
- "Plan and execute a product launch campaign"
- "Redesign our onboarding flow"

### Team composition
- Chief of Staff (required)
- 3-5 specialists from an archetype (full team)

### Setup flow
All 7 steps. Don't skip. Step 5 runs all three connector tiers (critical / recommended / optional) per Invariant #21 and `references/connectors.md` §severity-tiers.

### Per-turn workflow
Full workflow from `references/workflow.md`. `gstack-team:careful` becomes the default critique stance — specialists apply careful-mode reasoning to every structural decision without needing explicit activation.

### gstack-team skills at standard scale

All `gstack-team:*` skills are on the table. Typical loadouts:
- Code-heavy specialists pair `graphify` + one of `gstack-team:review` / `:cso` / `:investigate` / `:qa` / `:design-review` — see `references/invokable-skills.md`
- Plan-critique runs th