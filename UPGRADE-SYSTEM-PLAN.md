# Upgrade System Plan v1.0

**Status:** draft, awaiting final approval
**Target repo:** `C:\Users\rajee\Desktop\Work\Badsoorat\project-studio` → public GitHub
**Authoring date:** 2026-04-22
**Supersedes:** `UPGRADE-PROJECT-PLAN.md` (prior rough scaffold)

This document is the authoritative plan for how the `project-studio` skill evolves over time. It defines the repo layout, the rules for making changes, the evaluation regime, and the phased path to full operation. Every section below is a ratified decision unless explicitly marked open.

---

## 0. Purpose and non-goals

**Purpose.** Establish a disciplined, version-controlled, eval-gated process for improving the `project-studio` skill so that quality never regresses, every change is provable, and the skill stays useful to downstream projects already using it.

**Non-goals.**

- Not a product roadmap. This plan governs *how* changes happen, not *which* features come next.
- Not a spec for the skill itself. The skill's source lives under `skill/`; its behavior is described there.
- Not a replacement for good judgment. The rules below exist to catch systematic failures; they don't replace thoughtful review.

---

## 1. Architecture overview

### 1.1 Two surfaces, one repo

The repo hosts two related but separable surfaces:

- **`skill/`** — the `project-studio` skill source of truth. Ships to end users as a `.skill` bundle.
- **`upgrade-system/`** — the meta-project: atom specs, evals, migrations, scenarios, provenance, change requests, decisions.

End users care about `skill/`. Contributors work in both. Downstream-project maintainers consume the `upgrade-workspace` sub-skill, which lives under `skill/sub-skills/` and is released on both Track A (bundled) and Track B (standalone).

### 1.2 Two release tracks

| Track | Tag pattern | Asset | Frequency |
|---|---|---|---|
| **A — the skill** | `v<x.y.z>` | `project-studio-v<x.y.z>.skill` + `.sha256` + `CHANGES.md` + `FEATURE-PROVENANCE-MANIFEST.pdf` | Rolling, tied to accepted changes |
| **B — upgrade-workspace** | `upgrade-system-v<a.b.c>` | `upgrade-workspace-v<a.b.c>.skill` | Independent; shipped when the upgrade tool itself changes |

Both tracks ship via GitHub Releases on the same repo. Users discover the latest via the Releases page.

### 1.3 Dogfood model with safety rails

The upgrade system is run inside project-studio itself. Team = { chief-of-staff, skill-architect, eval-lead, release-manager, downstream-compat-lead }.

Hard rule: **the version that runs the session is the installed, last-known-good version; the version being edited is the working tree.** If the working tree breaks, we fall back to the installed version to fix it. A `--no-studio` mode exists for the first 30 minutes of any session in case project-studio itself is the bug.

ADR-0001 (previously "no meta-recursion") is superseded by ADR-0002 which adopts this dogfood-with-rails model.

### 1.4 Project-studio workspace mode — monorepo setup

This is the single most important scaffolding decision and it is ratified here so no future session re-litigates it.

**Decision:** project-studio runs this repo in **single-project mode**. Not multi-module.

#### 1.4.1 Why not multi-module

Project-studio's multi-module mode treats each module folder as an isolated work surface with its own persona boundary, its own state, and its own context envelope. Modules deliberately cannot reach across the wall — that is the feature, not a bug. Multi-module exists for projects where `module-a/` and `module-b/` are genuinely different concerns that should not entangle.

If this repo were configured multi-module, `skill/` and `upgrade-system/` would become peer modules. The consequence is fatal to the design in §1.1–§1.3:

- The upgrade-system cannot inspect, critique, migrate, or evaluate `skill/` because the wall hides it
- `skill-architect` cannot edit atom specs in `upgrade-system/` while also editing SKILL.md in `skill/` within the same session
- `eval-lead` cannot run T3/T4/T5 against `skill/` from `upgrade-system/evals/` because the runner is on the wrong side of a module wall
- Scenarios in `upgrade-system/scenarios/` would have no authorized way to observe the atom they target
- Dogfooding (§1.3) becomes impossible: the upgrade system is supposed to *improve* the skill, which requires reading and writing both surfaces

Multi-module is the correct mode for "two independent products in one repo." This repo is not that. It is one product (`skill/`) and its own reflexive construction yard (`upgrade-system/`). They are **two surfaces of one project**, which is exactly what single-project mode is for.

#### 1.4.2 Repo setup — single-project monorepo

The repo is a single git repo, single project-studio project, with two first-class directories:

- `skill/` — Track A source, shipped as a `.skill` bundle
- `upgrade-system/` — Track B source + all meta-project artifacts (atoms, evals, scenarios, migrations, provenance, requests, decisions, fixtures, schemas)

Both directories are in the same git history, merged through the same `main` branch, gated by the same CI. They are `surfaces`, not `modules`. The word "monorepo" here means "one git repo with two cooperating surfaces," not "a multi-module polyrepo emulation."

#### 1.4.3 State directory placement

The project-studio state directory lives at the **repo root**:

```
project-studio/
├── .project-studio/             ← project-studio state, at repo root
│   ├── state.md                 ← chief-of-staff narrative + current phase
│   ├── team.yaml                ← persona roster (chief-of-staff + 5 specialists)
│   ├── tasks.md                 ← live task list, fed by F2–F6 and Change Requests
│   ├── journal.md               ← append-only session journal
│   ├── ledger.md                ← decisions ledger (links to upgrade-system/decisions/)
│   └── persona-memory/          ← per-persona scratch + carryover notes
├── skill/                       ← surface A (edited by team)
└── upgrade-system/              ← surface B (edited by team)
```

`.project-studio/` is **not** under `skill/` (that would leak coordination state into the shipped bundle) and **not** under `upgrade-system/` (that would privilege one surface over the other). At the root, it is a peer to both surfaces, which matches the fact that the team operates across both.

`.cowork/` — if project-studio chooses to use it — also lives at the repo root.

#### 1.4.4 Persona-to-surface access rules

All five personas in the team (chief-of-staff, skill-architect, eval-lead, release-manager, downstream-compat-lead) plus both dedicated sub-agents (scenario-agent, implementation-agent) have **read-and-write access to both `skill/` and `upgrade-system/`**. There is no module wall to negotiate. The persona roles in §14.4 determine *who leads* on which kind of work, not *who is allowed to touch* which directory.

What personas do **not** touch:

- **The installed skill path.** The version running the session is read-only from the team's perspective. Only the release pipeline (F5, and later cycles) updates what's installed, and only after `ship.tag` succeeds.
- **`dist/`.** Built artifacts are CI-produced and gitignored. Personas produce source; the release workflow produces `dist/`.
- **CI-generated files.** Logs, coverage reports, eval transcripts emitted during CI runs are artifacts, not sources. Personas read them; they don't hand-edit them.
- **`.project-studio/persona-memory/<other-persona>/`.** Each persona writes its own memory; cross-persona reads are allowed, cross-persona writes are not.

There is no parent-bus / outbox mechanism because there is no child module to coordinate with. Cross-surface coordination happens through `.project-studio/state.md` and `.project-studio/tasks.md`, owned by chief-of-staff.

#### 1.4.5 Meta-recursion safety rails — operationalized

The dogfood-with-rails model from §1.3 concretely means:

- **Runtime-of-record:** the installed `project-studio` skill (v3.1.0 until F5 ships v3.2.0) is the skill that actually runs the session. Changes to `skill/SKILL.md` in the working tree are **not** picked up by the currently-running session.
- **Edit target:** `skill/` in the working tree. Team edits it freely.
- **Propagation:** changes in `skill/` only affect sessions *after* F5 ships the new version and the user re-installs it. The current session is immune to half-finished edits.
- **Breakage isolation:** if the team breaks `skill/SKILL.md` mid-session, the session itself keeps working because it's running the installed version. Recovery is: fix the working tree, run evals, ship, re-install.
- **Escape hatch:** `--no-studio` mode (atom 103 `session.no-studio-mode`) boots a session without invoking project-studio at all. Used only when project-studio itself is the suspected bug.
- **Version awareness:** chief-of-staff announces at session start: *"Running installed v3.1.0, working tree at sha <short> (target v3.2.0)."* This is how every session reminds itself that the two versions are not the same thing.

#### 1.4.6 First-time setup vs subsequent sessions

**Session 1 (scaffold session):**
User invokes `/project-studio` with the scaffold-and-execute-F1 prompt (see §11 F1 and §14.5). Project-studio creates `.project-studio/`, seeds the team, reads this plan, seeds the task list for F1, and executes F1.

**Sessions 2+ (resume sessions):**
User invokes `/project-studio` with `resume project`. Project-studio reads `.project-studio/state.md`, rehydrates the team, reads the phase pointer, and announces the current state.

`resume project` does not work before session 1 has completed F1 — there is nothing to resume to. This is a one-way door; once F1 creates `.project-studio/`, all future sessions use `resume`.

#### 1.4.7 Git workflow integration

The persona team operates inside the git workflow defined in §8.2:

- Day-to-day work commits to `develop` or to `feature/skill-<slug>` / `feature/upgrade-<slug>` branches
- PRs target `main` with full T1–T5 gating per §8.3
- Release stabilization happens on `release/skill-v<x.y.z>` or `release/upgrade-system-v<a.b.c>` branches
- `gstack-team:ship` drives the merge-to-`main` + release-tag flow (§14.4 release-manager)
- `gstack-team:review` runs on PRs before human review
- `gstack-team:land-and-deploy` is not applicable here (no Vercel deploy target); the equivalent is the GitHub Release publish step in the Track A / Track B workflows

Personas never bypass PRs. Every merge to `main` is gated, even chief-of-staff's own commits.

#### 1.4.8 Sub-skill (upgrade-workspace) workflow inside single-project mode

`upgrade-workspace` is a sub-skill, not a sub-module. It lives at:

- **Source:** `skill/sub-skills/upgrade-workspace/` — edited directly by the team (primarily release-manager and downstream-compat-lead)
- **Scenarios:** `upgrade-system/scenarios/upgrade-workspace/` — authored by scenario-agent like any other atom area
- **Evals:** the T5 runner exercises it against fixtures in `upgrade-system/fixtures/`
- **Release:** bundled inside Track A's `.skill`, and also published standalone as Track B

There is no wall between `skill/sub-skills/upgrade-workspace/` and the rest of `skill/`. It is part of the same surface. Track B exists for release-packaging convenience, not for code-isolation.

#### 1.4.9 Summary of ratified setup decisions

| # | Decision | Value |
|---|---|---|
| 1 | project-studio mode | single-project |
| 2 | `.project-studio/` location | repo root |
| 3 | Module walls between surfaces | none — `skill/` and `upgrade-system/` are peers |
| 4 | Persona access to `skill/` | read + write, all personas |
| 5 | Persona access to `upgrade-system/` | read + write, all personas |
| 6 | Installed-skill path | read-only from team's perspective |
| 7 | `dist/` | CI-produced, gitignored, not hand-edited |
| 8 | Parent bus / outbox | N/A — no child module |
| 9 | Runtime-of-record | installed v3.1.0 until F5 ships v3.2.0 |
| 10 | Edit target | working tree under `skill/` and `upgrade-system/` |
| 11 | Session 1 entry | `/project-studio` + scaffold-and-execute-F1 prompt |
| 12 | Session 2+ entry | `/project-studio` + `resume project` |
| 13 | Release flow | `gstack-team:ship` into `main`; GitHub Release publishes Track A/B |

### 1.5 Required skill and plugin bundle (prerequisites)

Project-studio is the orchestrator, not a monolith. It coordinates a team of personas whose *expertise* comes from other skills in the Anthropic skills library and the `gstack-team` plugin. Without these, the personas cannot do their work and the eval regime cannot run.

The exhaustive list with rationale per persona lives in **§15 Skill dependency inventory**. This section is the at-a-glance summary. F0 (§11) enforces these are present before F1 starts.

**Hard dependencies** (session will refuse to proceed if missing):

| Bucket | Item | Purpose |
|---|---|---|
| Orchestrator | `anthropic-skills:project-studio` | This skill. The chief-of-staff runtime. |
| Plugin | `gstack-team` | Engineering discipline: ship, review, retro, plan-reviews, QA, canary, freeze/guard, context save/restore, investigate, careful, make-pdf |
| Skill authoring | `anthropic-skills:skill-creator` | Editing SKILL.md and sub-skills |
| Reasoning | `anthropic-skills:context-engineering-kit` | Structured reasoning + multi-agent patterns |
| Reasoning | `anthropic-skills:superpowers` | Software dev framework with planning, testing, execution |
| Reference | `anthropic-skills:code-guide` | Claude Code CLI / Agent SDK / API reference |
| Document production | `anthropic-skills:pdf` | Provenance PDFs (Track A release asset) |
| Document production | `anthropic-skills:docx` | Spec docs, reports |
| Product management | `product-management:*` (9 skills) | Change Requests, sprint planning, retros, stakeholder updates |

**Persona-expertise dependencies** (recommended for the personas to operate at full fidelity): see §15 for the per-persona breakdown. Short version: `clean-code`, `clean-architecture`, `refactoring-patterns`, `pragmatic-programmer`, `software-design-philosophy`, `domain-driven-design`, `release-it`, `ddia-systems`, `system-design`, `webapp-testing`, `mobile-responsive-testing`, `c-framework`, `mom-test`, `doc-coauthoring`, `yc-sv-development-framework`, plus the design-review skills (`emil-design-eng`, `refactoring-ui`, `design-everyday-things`, `ux-heuristics`, `top-design`).

**Environment dependencies**:

- Cowork mode with a workspace folder mounted at `C:\Users\rajee\Desktop\Work\Badsoorat\project-studio`
- Python ≥ 3.11 (for eval runner)
- `git` + GitHub CLI (`gh`) or equivalent
- Working `mcp__workspace__bash` for scripting

**Dependency manifest.** F0 writes the resolved list to `.project-studio/dependencies.yaml` so every future session can verify the environment before proceeding. On resume, chief-of-staff re-checks the manifest against what's currently available and halts if a hard dep disappeared.

---

## 2. Atom architecture

### 2.1 Definition

An **atom** has one observable behavior, one success criterion, and one failure surface. If describing what it does needs the word "and," it splits further.

Each atom owns:
- A 1-page spec at `upgrade-system/architecture/atoms/<atom>.md`
- A node in the dependency graph at `upgrade-system/architecture/atom-map.yaml`
- A scenario directory at `upgrade-system/scenarios/<atom>/`
- A minimum of 10 scenarios spanning 6 categories (set in the Foundation Sprint; ongoing +3 per touching change)

### 2.2 Scenario categories per atom

Every atom is stress-tested along six axes:

1. **Happy path** — canonical successful invocation
2. **Alternate paths** — valid but non-default branches
3. **Failure modes** — known ways the atom breaks
4. **Adversarial** — hostile or malformed inputs
5. **Concurrency** — race conditions, interleavings
6. **Backwards-compat** — behavior against prior version fixtures

### 2.3 Atom inventory (103 total)

Each atom also inherits scenario axes: `mode` ∈ { new, resume, import }, `scale` ∈ { light, standard, rigorous }, `surface` ∈ { single-project, multi-project }, `host-state` ∈ { clean, dirty, corrupt, wrong-version }. These are scenario dimensions, not separate atoms.

#### 2.3.1 Pre-boot / detection (11 atoms)

1. `boot.detect-cowork-mount`
2. `boot.detect-session-continuity`
3. `boot.detect-installed-version`
4. `boot.detect-existing-state`
5. `boot.detect-state-integrity`
6. `boot.detect-mcp-inventory`
7. `boot.detect-installed-skills`
8. `boot.detect-version-drift`
9. `boot.classify-mode`
10. `boot.route`
11. `boot.announce`
12. `boot.error-handle` *(merged from 4 prior error atoms)*

#### 2.3.2 Setup — intent & metadata (6 atoms)

13. `setup.intent-confirm`
14. `setup.scale-pick`
15. `setup.surface-pick`
16. `setup.project-identity` *(merged: name, scope, deliverable-types, sensitivity)*
17. `setup.goals` *(merged: objectives, milestones, success-criteria)*
18. `setup.context` *(merged: constraints, stakeholders)*

#### 2.3.3 Setup — team formation (9 atoms)

19. `setup.team-recommend`
20. `setup.team-confirm`
21. `setup.persona-load`
22. `setup.persona-boundaries`
23. `setup.persona-handshake`
24. `setup.persona-conflict-detect`
25. `setup.persona-dissent-surface`
26. `setup.chief-of-staff-contract`
27. `setup.escalation-paths`

#### 2.3.4 Setup — connector / severity resolution (6 atoms)

28. `severity.inventory`
29. `severity.classify`
30. `severity.resolve` *(merged: critical-check, recommended-warn, optional-note)*
31. `severity.remediation-suggest`
32. `severity.connector-test`
33. `severity.multi-instance-handle`

#### 2.3.5 Setup — invariant bootstrap (8 atoms)

34. `invariant.load`
35. `invariant.display`
36. `invariant.user-confirm`
37. `invariant.project-specific-add`
38. `invariant.conflict-detect`
39. `invariant.preflight`
40. `invariant.runtime-check`
41. `invariant.violation-handle`

#### 2.3.6 Setup — state directory creation (7 atoms)

42. `setup.cowork-init`
43. `setup.project-studio-init`
44. `setup.journal-init`
45. `setup.ledger-init`
46. `setup.provenance-init`
47. `setup.git-init-suggest`
48. `setup.first-commit`

#### 2.3.7 Setup — import & migration (9 atoms)

49. `import.source-detect`
50. `import.diff`
51. `import.user-approve`
52. `import.apply`
53. `migration.chain-plan`
54. `migration.dry-run`
55. `migration.apply`
56. `migration.rollback`
57. `migration.post-validate`

#### 2.3.8 Setup — kickoff (5 atoms)

58. `setup.first-agenda`
59. `setup.priorities-rank`
60. `setup.actions-assign`
61. `setup.initial-retro-placeholder`
62. `setup.exit-to-work`

#### 2.3.9 Resume (7 atoms)

63. `resume.state-load`
64. `resume.integrity-check`
65. `resume.staleness-report`
66. `resume.persona-rehydrate`
67. `resume.in-flight-items-surface`
68. `resume.pending-migrations-surface`
69. `resume.announce`

#### 2.3.10 Update cycle (5 atoms)

70. `update.capture`
71. `update.validate`
72. `update.atomic-write`
73. `update.journal-append`
74. `update.ledger-record`

#### 2.3.11 Critique / review (7 atoms)

75. `critique.round-robin`
76. `critique.dissent-capture`
77. `critique.consensus-form` *(merged with reconcile)*
78. `tier1.ceo`
79. `tier1.eng`
80. `tier1.design`
81. `tier1.devex`

#### 2.3.12 Ship pipeline (5 atoms)

82. `ship.preflight`
83. `ship.critique`
84. `ship.tag`
85. `ship.propagate`
86. `ship.rollback`

#### 2.3.13 Retro (3 atoms)

87. `retro.milestone-detect`
88. `retro.capture` *(merged with invoke)*
89. `retro.action-to-intake`

#### 2.3.14 Context & continuity (4 atoms)

90. `context.save` *(merged with checkpoint)*
91. `context.restore`
92. `context.diff`
93. `context.handoff`

#### 2.3.15 Multi-project surface (5 atoms) — **change-caution: high**

94. `multi.project-registry`
95. `multi.project-switch`
96. `multi.cross-project-rules`
97. `multi.isolation-check`
98. `multi.aggregate-view`

Any *behavior* change on these atoms requires all 4 Tier-1 lenses (not the default 2). Scenario authorship for existing behavior requires the normal 2.

#### 2.3.16 Degraded-mode fallback (4 atoms)

99. `degraded.detect`
100. `degraded.fallback`
101. `degraded.notify`
102. `degraded.recovery`

#### 2.3.17 Meta-session support (1 atom)

103. `session.no-studio-mode` — bootstrap session without invoking project-studio itself (for when project-studio is suspected broken)

### 2.4 Dependency graph

`upgrade-system/architecture/atom-map.yaml` declares directed edges between atoms. Edges determine **blast radius**: if atom X is touched by a change, every atom downstream of X is in blast radius and its scenarios must run as part of the PR gate.

---

## 3. Eval taxonomy — 5 tiers, all in CI

Per the ratified "safest option, no compromise" policy, all tiers run on every PR. T4 and T5 are slow; that cost is accepted.

| Tier | What it covers | Triggered by | Target runtime |
|---|---|---|---|
| **T1 Lint** | File hygiene, YAML validity, markdown structure, trailing whitespace | every commit (pre-commit hook + CI) | < 30 s |
| **T2 Structural** | Cross-refs resolve, version consistency, invariant sequence, namespace, placeholder resolution, atom-spec schema | every PR | < 2 min |
| **T3 Per-atom behavioral** | Run each touched atom against its scenarios; diff output against expected | every PR touching that atom; full set on release | 5–15 min |
| **T4 Integration** | Multi-atom flows (setup→update→retro, boot→resume→update, import→migrate→resume), simulated transcripts | every PR | 10–20 min |
| **T5 Backwards-compat** | Run migrations against synthetic workspace fixtures from last 3 versions | every PR touching `skill/` or `upgrade-system/migrations/`; always on release candidates | 10–15 min |

Full-regression runtime on release candidates: ~45 min. Accepted.

---

## 4. Scenario schema

Every scenario is one YAML file at `upgrade-system/scenarios/<atom>/<scenario-slug>.yaml`:

```yaml
id: <atom>/<slug>
atom: <atom-name>
tier: T3            # T3|T4|T5
category: happy-path | alt-path | failure | adversarial | concurrency | compat
mode: new | resume | import | any
scale: light | standard | rigorous | any
surface: single-project | multi-project | any
host_state: clean | dirty | corrupt | wrong-version | any
inputs:
  <input-name>: <value or fixture-path>
expected_behavior:
  - emits: "<substring or regex>"
  - halts: true | false
  - writes: [<path>, ...]
  - preserves: [<path>, ...]
assertions:
  - log_contains: "<text>"
  - exit_code: <int>
  - file_exists: <path>
  - file_equals: [<path>, <fixture>]
provenance:
  added_in: <version>
  added_by: <persona>
  related_requests: [<request-id>]
```

---

## 5. Change Request intake — questionnaire → analysis → triage

### 5.1 Intake channels

Five funnels, all produce a `requests/<yyyy-mm-dd>-<slug>.md`:

1. **User proposal** — you say "propose feature X"
2. **Retro outcome** — retro action flagged `propose`
3. **Eval regression** — CI failure on `main` auto-files
4. **Downstream report** — upgrade-workspace error or end-user bug
5. **Incident** — production-class bug, fast-lane

### 5.2 Stage 1 — Intent

Single question: change type ∈ { `add`, `improve`, `remove`, `fix`, `refactor` }.

### 5.3 Stage 2 — Scope (branches per intent)

**ADD**
- 2a. Feature name + one-sentence description
- 2b. Why project-studio needs this
- 2c. Runtime trigger (user command / lifecycle event / another atom)
- 2d. Success criteria
- 2e. New atoms vs. extend existing
- 2f. Workspace state format change? (y/n)
- 2g. **Dependency-map draft** — sketch the atom graph delta (new nodes, new edges) *(required for ADD)*

**IMPROVE**
- 2a. Affected atoms (pick from registry)
- 2b. What's inadequate (evidence required)
- 2c. Better-version behavior
- 2d. Refinement vs. reshape
- 2e. Invariant change? (y/n)

**REMOVE**
- 2a. Atoms going away
- 2b. Why no longer needed
- 2c. Replacement (if any)
- 2d. Deprecation path (one-version warning, then remove — default)
- 2e. Migration script impact

**FIX**
- 2a. Scenario that failed (or should exist)
- 2b. Expected vs. actual
- 2c. Root-cause hypothesis
- 2d. New scenario needed, or existing one now exposes the bug

**REFACTOR**
- 2a. Atoms restructured
- 2b. Behavior-invariant confirmed (required yes)
- 2c. Why now

### 5.4 Stage 3 — External skill usage

For each external skill involved:
- Skill name
- Role it plays
- **Integration mode** (pick one):
  - `direct-reference` — hard dep, halts if missing
  - `optional-reference` — graceful degradation
  - `rebuild-in` — copy logic, no external dep
  - `vendor-wrap` — pinned fork as sub-skill
- Rationale for mode
- Compatibility range
- Fallback behavior if missing/broken

### 5.5 Stage 4 — Impact

- Atoms touched (from 2a and 3b)
- Blast radius (auto-computed from atom-map.yaml, user reviews)
- Existing scenarios expected to change
- New scenarios estimated (≥ 3 per affected atom unless behavior-invariant)
- Downstream workspace impact? Migration required?

### 5.6 Stage 5 — Analysis block (skill-architect persona auto-generates)

Appended to the request:

1. Is this really an improvement? (for/against, with evidence)
2. Integration-mode defensibility
3. Improvement mechanism — how project-studio behaves better
4. Risks — regressions, invariant conflicts, downstream breakage
5. Constraints — timeline, deps, compatibility
6. Estimated version bump (patch/minor/major + rationale)
7. Atom churn (N new / M modified / K deleted)
8. Scenario churn + blast-radius list
9. Owner persona recommendation
10. Tier-1 lenses required (≥ 2 default; all 4 if touching A.15 multi-project)
11. Dependency on open requests
12. Open questions for triage

### 5.7 Stage 6 — Triage

Chief-of-staff + skill-architect session. Verdict ∈ { `accept`, `defer`, `reject`, `reframe` }. All four logged. Accept → owner assigned, branch created, Tier-1 critique scheduled.

---

## 6. Scenario-first development ritual

1. Scenarios land before code.
2. Change-type classifier determines scenario requirement:
   - **Behavior change** → hard rule: +3 scenarios per affected atom, no waiver
   - **Behavior-invariant refactor** → no new scenarios required; existing scenarios must stay green as proof of invariance
   - **Doc-only** → no scenario requirement; T1+T2 only
3. Scenarios committed as "red" state — eval runner reports "N new, all failing, expected"
4. Implementation commits turn them green
5. PR template surfaces `atoms_touched`, `scenarios_added`, `scenarios_modified`, `scenarios_deleted`; CI refuses merge if totals don't reconcile with change-type classification
6. Scenario peer review: `eval-lead` + one rotating persona, before implementation starts

---

## 7. Agent model — three roles, two dedicated sub-agents

**Chief-of-staff** — the main session. Coordinates, captures dissent, runs eval gates, owns the triage verdict and the PR merge decision.

**`scenario-agent`** (dedicated sub-agent) — reads Change Request + atom specs (not implementation). Authors scenarios, submits for peer review, commits the red state. Cannot see implementation code during authorship.

**`implementation-agent`** (dedicated sub-agent) — reads Change Request + atom specs + committed scenarios. Writes implementation to turn scenarios green. Cannot modify scenarios except via explicit `scenario-revision` follow-up commit, which re-triggers scenario review.

Why two agents: same agent writing both code and scenarios drifts toward scenarios that mirror the code. Separation is a structural guard against circular validation.

---

## 8. Git workflow and repo structure

### 8.1 Directory layout

```
project-studio/                         ← public GitHub repo
├── skill/                              ← the shipped skill (Track A source)
│   ├── SKILL.md
│   ├── VERSION
│   ├── protocol/
│   ├── references/
│   ├── templates/
│   ├── scripts/
│   └── sub-skills/
│       └── upgrade-workspace/          ← bundled in Track A; also Track B source
├── upgrade-system/                     ← the meta-project
│   ├── architecture/
│   │   ├── atoms/                      ← 103 atom specs, 1 md per atom
│   │   └── atom-map.yaml               ← dependency graph
│   ├── evals/
│   │   ├── runner.py
│   │   └── tiers/
│   │       ├── T1-lint/
│   │       ├── T2-structural/
│   │       ├── T3-behavioral/
│   │       ├── T4-integration/
│   │       └── T5-compat/
│   ├── scenarios/                      ← per-atom scenario files
│   ├── migrations/                     ← v<from>-to-v<to> manifests + scripts
│   ├── provenance/
│   │   └── features/                   ← 5-field manifests
│   ├── requests/                       ← Change Requests
│   ├── decisions/                      ← ADRs
│   ├── fixtures/                       ← T5 compat fixtures (synthetic workspaces)
│   └── schemas/                        ← YAML schemas for scenarios, atom specs, manifests
├── dist/                               ← built artifacts (gitignored, CI-produced)
├── docs/
│   ├── users/                          ← install, use, changelog
│   └── contributors/                   ← atom specs guide, scenario schema, PR guide
├── .github/
│   ├── workflows/
│   │   ├── t1-lint.yml
│   │   ├── t2-structural.yml
│   │   ├── t3-behavioral.yml
│   │   ├── t4-integration.yml
│   │   ├── t5-compat.yml
│   │   ├── release-track-a.yml
│   │   └── release-track-b.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
├── README.md                           ← splash: users vs. contributors
├── CHANGELOG.md                        ← skill changelog
├── UPGRADE-SYSTEM-PLAN.md              ← this document
├── CONTRIBUTING.md
└── LICENSE
```

### 8.2 Branches

- `main` — protected. Both tracks merge here via PR. CI must be green. No direct push.
- `develop` — integration branch for in-flight work.
- `feature/skill-<slug>` — changes to `skill/` (+ scenario additions)
- `feature/upgrade-<slug>` — changes to `upgrade-system/` only
- `release/skill-v<x.y.z>` — skill release stabilization
- `release/upgrade-system-v<a.b.c>` — upgrade-system release stabilization
- `hotfix/<issue>` — from the last `main` tag

### 8.3 CI gating by path

- PR touches `skill/` → T1 + T2 + T3 (affected + blast radius) + T4 (affecting flows) + T5 (if migration-bearing) + plan-critique from 2 Tier-1 lenses (4 if A.15)
- PR touches `upgrade-system/` only → T1 + T2 + atom-spec meta-lint + 1 lens review
- PR touches both → strictest of the two
- Release PR into `main` → full T1–T5 across entire atom set + T5 across last 3 versions + upgrade-workspace dry-run against all registered fixtures

### 8.4 Release assets

**Track A release (`v<x.y.z>`):**
- `project-studio-v<x.y.z>.skill` (zip bundle)
- `project-studio-v<x.y.z>.sha256`
- `CHANGES-v<x.y.z>.md`
- `FEATURE-PROVENANCE-MANIFEST-v<x.y.z>.pdf`
- `MIGRATION-v<prev>-to-v<x.y.z>.yaml`

**Track B release (`upgrade-system-v<a.b.c>`):**
- `upgrade-workspace-v<a.b.c>.skill`
- `upgrade-workspace-v<a.b.c>.sha256`
- `CHANGES-upgrade-system-v<a.b.c>.md`

---

## 9. Downstream upgrade protocol (`upgrade-workspace` sub-skill)

Runs in pull mode, inside a session within a project that already uses project-studio.

1. **Detect** installed skill version + workspace state format version
2. **Load** migration chain from locally bundled manifest, or fetch from Track A/B release
3. **Dry-run** against workspace state, compute diff
4. **Present** each change to the user: *what / why / impact*, choose `apply` / `skip` / `defer`
5. **Apply** atomically (mktemp → write → mv), record in `.cowork/upgrade-journal.md`
6. **Post-validate** schema + invariants + resume-readiness
7. **Rollback** path: revert journal entry + restore backup

Critically: migrations are declared at the **atom level** in the manifest, not at the file level. When an atom's state shape changes, the migration operates on all state writes from that atom across the workspace.

---

## 10. Recurring workflows

- **Per commit** — T1 via pre-commit hook, locally
- **Per PR** — T1 + T2 + T3 (touched atoms) + T4 (affecting flows) + T5 (if migration-bearing) + plan-critique
- **Per release candidate** — full T1–T5 + T5 across last 3 versions + upgrade-workspace dry-run against all fixtures
- **Post-release (72 h)** — canary window, collect pilot reports, hotfix-ready
- **Every milestone** — retro via `gstack-team:retro`; retro actions become intake candidates
- **Monthly** — architecture review: does the atom graph still reflect reality? ADRs if drift detected
- **Quarterly** — deep audit: 10% scenario sample for quality, all open waivers audited, fixture list refreshed

---

## 11. Foundation phases — one-time setup

The recurring workflow cannot run until these phases complete. F0–F6 are sequenced; no phase starts before the prior phase exits.

### F0. Dependency install and verification (pre-flight)

**Goal:** every hard dependency listed in §1.5 and §15 is installed and callable from the session.

- Install the `gstack-team` plugin from its source marketplace
- Install or confirm each hard-dep skill listed in §1.5
- Install or confirm each persona-expertise skill listed in §15 (per persona)
- Install or confirm Python ≥ 3.11, `git`, `gh`, the Python libs `pypdf`, `reportlab`, `pyyaml`, `jsonschema`
- Confirm `mcp__workspace__bash` works end-to-end in the mounted workspace
- Confirm Cowork directory access to `C:\Users\rajee\Desktop\Work\Badsoorat\project-studio`
- Run the `list_skills` MCP tool and assert each expected skill is listed under the expected qualified name
- Write the resolved inventory to `.project-studio/dependencies.yaml` — schema in §15.4
- A missing hard dep halts F0. A missing persona-expertise skill raises a *warning* (team can operate in reduced-capability mode for that persona, with reduced fidelity noted in the decision ledger).

**Exit:** `.project-studio/dependencies.yaml` present, all hard deps green, any persona-expertise gaps logged.

### F1. Git and infrastructure

**Goal:** working repo, CI, templates, and project-studio workspace all in place.

**Project-studio workspace initialization (per §1.4):**

- Confirm single-project mode (not multi-module) at session start
- Create `.project-studio/` at the repo root with:
  - `state.md` — session-1 narrative, phase pointer set to `F1`
  - `team.yaml` — roster: chief-of-staff, skill-architect, eval-lead, release-manager, downstream-compat-lead (+ scenario-agent, implementation-agent as sub-agents)
  - `tasks.md` — the F1 checklist below, plus seeded placeholders for F2–F6
  - `journal.md` — empty append-only log
  - `ledger.md` — empty decisions ledger, cross-links to `upgrade-system/decisions/`
  - `persona-memory/<persona>/` directories, one per persona
- Record ADR-0002 (dogfood-with-rails, supersedes ADR-0001) in `upgrade-system/decisions/`

**Git and repo scaffolding:**

- Initialize git at `C:\Users\rajee\Desktop\Work\Badsoorat\project-studio`
- Create public GitHub repo, push initial commit
- Branch protection on `main` (no direct push, require green CI, require review)
- `develop` branch created
- `.gitignore` includes `dist/`, eval artifacts, persona scratch

**Directory and schema scaffolding:**

- `skill/` populated with v3.1.0 baseline (imported, not edited)
- `upgrade-system/architecture/atoms/_template.md` — atom-spec template
- `upgrade-system/schemas/scenario.schema.yaml` — scenario YAML schema
- `upgrade-system/schemas/atom-spec.schema.yaml` — atom-spec YAML schema
- `upgrade-system/architecture/atom-map.yaml` — empty stub with schema header
- Empty directories (with `.gitkeep`): `scenarios/`, `migrations/`, `provenance/features/`, `requests/`, `decisions/`, `fixtures/`

**Eval runner and CI:**

- Eval runner skeleton (Python) with all 5 tier stubs at `upgrade-system/evals/runner.py`
- CI workflows active for T1 + T2; T3–T5 stubbed, activated as scenarios come online
- Release workflows `release-track-a.yml` and `release-track-b.yml` stubbed

**Documentation and templates:**

- `README.md` splash (users vs. contributors), `CONTRIBUTING.md`, `LICENSE`
- PR template + issue templates in `.github/`
- Link from `README.md` to this plan

**Baseline tag:**

- First tag: `v3.1.0-baseline` (the existing shipped skill, imported into `skill/`)

**Exit:** T1+T2 green on `main` after baseline import; `.project-studio/` present with the team announced; `resume project` works in a fresh session.

### F2. Atom enumeration

**Goal:** 103-atom list (or revised) locked, each with a full spec.

- Review and finalize the atom list from §2.3
- Write 1-page spec per atom: purpose, preconditions, postconditions, observable outputs, failure modes, dependency list, related invariants
- Skill-architect persona signs off per atom
- Build `upgrade-system/architecture/atom-map.yaml` with full dependency graph
- Blast-radius computation script working against the map

**Exit:** atom-spec meta-lint green; every atom has a spec; atom-map.yaml validates.

### F3. Scenario Foundation Sprint

**Goal:** ≥ 10 scenarios per atom across 6 categories.

- Per-atom session: scenario-agent authors, skill-architect + eval-lead peer-review
- Scenarios written against spec, not against current behavior (important: this surfaces latent bugs)
- Parallelizable across independent atoms
- Budget: 103 atoms × ~75 min ≈ 130 hours sequential; with parallel sessions, targeting 6–8 calendar weeks of focused work

**Exit:** T3 green on baseline SKILL.md; every atom has ≥ 10 scenarios.

### F4. Integration and compat backfill

**Goal:** T4 flow coverage + T5 compat fixtures.

- Flow scenarios authored for end-to-end paths (setup→update→retro, boot→resume→update, import→migrate→resume, etc.)
- T5 synthetic fixtures built for v3.0 and v3.1 workspace state shapes
- `upgrade-workspace` sub-skill built against fixtures
- Migrations authored retroactively for v3.0→v3.1 and v3.1→v3.2-baseline

**Exit:** T4+T5 green on release-candidate branch.

### F5. Baseline release — v3.2.0

**Goal:** first version shipped under the full regime.

- No new features; the delta is purely the upgrade-system infrastructure
- Full T1–T5 green
- `upgrade-workspace` dry-run clean against synthetic fixtures
- Release-manager signs off (you)
- Tag `v3.2.0`; Track A assets published; Track B `upgrade-workspace-v1.0.0` released

**Exit:** public GitHub Release for both tracks.

### F6. Normal operation

**Goal:** intake queue opens, feature work begins.

- All rules in §12 in full force
- Change Requests accepted via §5 funnels
- All eval tiers run per §10 cadence

---

## 12. Rules (consolidated)

1. **Every change bumps the version.** Feature → minor, fix → patch, breaking workspace format → major. Doc-only may batch.

2. **Change-type classifier gates scenario requirements:**
   - Behavior change → +3 scenarios per affected atom, hard rule
   - Behavior-invariant refactor → existing scenarios must stay green
   - Doc-only → T1+T2 only

3. **No PR without:** (a) atom delta declared, (b) scenario delta meeting change-type rule, (c) T1+T2+T3+T4 green, (d) T5 green if migration-bearing, (e) CHANGELOG entry, (f) provenance entry, (g) ≥ 2 Tier-1 lenses signed off (≥ 4 if touching A.15 multi-project atoms).

4. **No release without:** T1–T5 all green, T5 compat across last 3 versions, upgrade-workspace dry-run clean against all registered fixtures, release-manager sign-off.

5. **Scenario-first discipline.** Scenarios land in red state before implementation lands in green. Enforced by CI via commit ordering check.

6. **Dedicated sub-agents.** `scenario-agent` and `implementation-agent` run as separate contexts. No single agent writes both scenarios and implementation for the same Change Request.

7. **Dogfood with safety rails.** Installed version runs sessions; working tree is edit target. `--no-studio` mode available when project-studio itself is suspect.

8. **No soft-delete.** Removed features get one deprecated version with warning, then removal with migration.

9. **Skill-of-record per edit type:**
   - SKILL.md prose edits → `skill-creator` + `context-engineering-kit`
   - Eval harness code → `code-guide` + `superpowers`
   - PDF/docx exports → `gstack-team:make-pdf` / `anthropic-skills:pdf` / `docx`
   - Session ceremonies (retros, sprint planning) → `product-management:*`
   - Plan critique → `gstack-team:plan-{ceo,eng,design,devex}-review`

10. **Multi-project atoms (§2.3.15) are change-caution: high.** Behavior changes require all 4 Tier-1 lenses; read-only scenario authorship uses default 2.

11. **Rolling release cadence.** Ship when ready, not on a calendar. No feature-rush, no scheduled pressure.

12. **Public repo.** All work visible.

13. **You (kr.rajeev.design@gmail.com) are the release-approver for now.** A persona-committee vote may be introduced later under its own Change Request.

---

## 13. Open questions remaining

Just one, and it's non-blocking:

- **Real-world pilot workspaces** — when you accumulate other projects that use project-studio, register them as T5 targets. Until then, T5 runs against synthetic fixtures in `upgrade-system/fixtures/`. No action required for scaffold.

---

## 14. Appendix

### 14.1 Feature Provenance entry format

```yaml
id: <date>-<slug>
origin: user-proposal | retro-action | eval-regression | downstream-report | incident
rationale: >
  One sentence.
atoms_touched: [<atom>, ...]
scenarios_added: [<scenario-id>, ...]
introduced_in: <version>
```

### 14.2 Scenario categories recap

- `happy-path` — canonical success (1 per atom minimum)
- `alt-path` — valid non-default branches (2 minimum)
- `failure` — known break modes (3 minimum)
- `adversarial` — hostile/malformed inputs (2 minimum)
- `concurrency` — races and interleavings (1 minimum)
- `compat` — prior-version fixtures (1 minimum)

### 14.3 Eval tier summary

| Tier | Covers | Trigger | Time |
|---|---|---|---|
| T1 | Lint, YAML, markdown | every commit | < 30 s |
| T2 | Cross-refs, version, invariant seq | every PR | < 2 min |
| T3 | Per-atom behavioral | PR touching atom + release | 5–15 min |
| T4 | Integration flows | every PR | 10–20 min |
| T5 | Backwards-compat | PR touching skill/ or migrations + release | 10–15 min |

### 14.4 Persona → skill mapping

| Persona | Primary skills used |
|---|---|
| chief-of-staff | project-studio core |
| skill-architect | skill-creator, context-engineering-kit, anthropic-skills:pdf |
| eval-lead | superpowers, code-guide |
| release-manager | gstack-team:ship, gstack-team:canary, gstack-team:make-pdf |
| downstream-compat-lead | gstack-team:qa |
| scenario-agent (sub-agent) | context-engineering-kit |
| implementation-agent (sub-agent) | code-guide, superpowers |

### 14.5 Session continuity

This plan is designed to survive session resets. Single-project mode (§1.4) makes continuity concrete.

**First-time setup prompt (session 1):**

> *"Scaffold this project per `UPGRADE-SYSTEM-PLAN.md` using /project-studio in single-project mode. Execute Foundation phase F1."*

This creates `.project-studio/` at the repo root and seeds the team + task list.

**Resume prompt (session 2+):**

> *"/project-studio — resume project."*

On resume, project-studio must:

1. Load `.project-studio/state.md` (coordination state at repo root, not under any surface)
2. Load `.project-studio/team.yaml` and rehydrate the persona team
3. Load `.project-studio/tasks.md` to recover the phase pointer and open work items
4. Read this `UPGRADE-SYSTEM-PLAN.md` to refresh rules
5. Read `upgrade-system/decisions/` for any ADRs added since last session
6. Detect runtime-of-record vs working-tree version (§1.4.5) and announce both
7. Report current phase, open tasks, and recommended next action — chief-of-staff speaks first

**Resume integrity checks:**

- `.project-studio/` exists at repo root (otherwise: refuse resume, direct user to F1 scaffold)
- `UPGRADE-SYSTEM-PLAN.md` is readable (otherwise: halt, plan is the source of truth)
- `.project-studio/dependencies.yaml` matches what's installed now (otherwise: warn on persona gaps, halt on hard-dep gaps — see §15.4)
- Installed project-studio version matches or exceeds the version that last wrote `state.md` (otherwise: warn about version drift; do not auto-migrate in resume)
- Git working tree status is reported to the user before any action is taken

---

## 15. Skill dependency inventory

This section enumerates every skill and plugin the project-studio team depends on, grouped by purpose. It is the source for `.project-studio/dependencies.yaml`. It is ratified — changes require a Change Request (§5).

### 15.1 Hard dependencies

The session refuses to start F1 if any of these are missing.

#### 15.1.1 Orchestration

| Qualified name | Why required |
|---|---|
| `anthropic-skills:project-studio` | The orchestrator itself. Provides chief-of-staff runtime, persona loading, state directory management, multi-persona workflow. |

#### 15.1.2 `gstack-team` plugin

The plugin ships as one unit; the listed sub-skills are all installed when the plugin is installed. Every one is referenced by at least one workflow in this plan.

| Sub-skill | Used for |
|---|---|
| `gstack-team:ship` | Release-manager's merge-to-`main` + release-tag flow (§8.2, §12 rule 4) |
| `gstack-team:review` | PR-review gate (§8.3, §12 rule 3) |
| `gstack-team:retro` | Milestone retros (§10, atom A.13) |
| `gstack-team:make-pdf` | `FEATURE-PROVENANCE-MANIFEST-v<x.y.z>.pdf` (§8.4) |
| `gstack-team:plan-ceo-review` | Tier-1 CEO lens (§2.3.11 atom 78, §12 rule 3) |
| `gstack-team:plan-eng-review` | Tier-1 Eng lens (atom 79) |
| `gstack-team:plan-design-review` | Tier-1 Design lens (atom 80) |
| `gstack-team:plan-devex-review` | Tier-1 DevEx lens (atom 81) |
| `gstack-team:qa` | Downstream-compat-lead's QA runs (§14.4) |
| `gstack-team:canary` | Progressive rollout (§10 post-release 72h window) |
| `gstack-team:investigate` | Root-cause analysis for failed evals or downstream reports |
| `gstack-team:careful` | Raise the bar on production-critical changes (A.15 multi-project atoms) |
| `gstack-team:freeze` / `gstack-team:guard` / `gstack-team:unfreeze` | Scope-drift protection mid-session |
| `gstack-team:context-save` / `gstack-team:context-restore` | Session checkpoints (atoms A.14 context) |
| `gstack-team:autoplan` | Planning before Change Requests |
| `gstack-team:learn` | Onboarding-mode when reading unfamiliar code |
| `gstack-team:office-hours` | Product interrogation for ADD-type Change Requests |
| `gstack-team:browse` | Live-URL smoke checks (rare — for docs site if added) |
| `gstack-team:design-review` | Visual/UX review of docs site or diagrams |
| `gstack-team:design-consultation` | Design-system work (only if we add one) |
| `gstack-team:cso` | Security audit before cutting Track A/B release |
| `gstack-team:land-and-deploy` | If a deploy target ever exists; currently N/A |

#### 15.1.3 Core skill authoring

| Skill | Used for |
|---|---|
| `anthropic-skills:skill-creator` | Editing `skill/SKILL.md`, creating/maintaining sub-skills (§14.4 skill-architect) |
| `anthropic-skills:context-engineering-kit` | Structured reasoning patterns, multi-agent hand-offs, scenario-agent authorship |
| `anthropic-skills:superpowers` | Planning → testing → execution discipline for implementation-agent |
| `anthropic-skills:code-guide` | Authoritative Claude Code CLI / Agent SDK / Claude API reference for eval-lead and implementation-agent |

#### 15.1.4 Document production

| Skill | Used for |
|---|---|
| `anthropic-skills:pdf` | `FEATURE-PROVENANCE-MANIFEST-v<x.y.z>.pdf` generation; parsing provenance from prior releases |
| `anthropic-skills:docx` | Internal proposal docs, formal specs, retros if exported |
| `anthropic-skills:xlsx` | Atom-inventory exports, eval-matrix spreadsheets |
| `anthropic-skills:pptx` | Milestone readouts when requested |

#### 15.1.5 Product-management ceremonies

The plugin's 9 skills are all used across the workflow:

| Skill | Used for |
|---|---|
| `product-management:write-spec` | Stage-5 analysis block on Change Requests (§5.6) |
| `product-management:brainstorm` | Stage-2 ADD scope exploration (§5.3) |
| `product-management:product-brainstorming` | Pre-intake ideation |
| `product-management:sprint-planning` | F1–F6 phase planning, ongoing sprint ceremonies |
| `product-management:metrics-review` | Eval trend reviews, quarterly audits (§10) |
| `product-management:stakeholder-update` | Release notes, CHANGELOG narrative (§8.4) |
| `product-management:roadmap-update` | After accepted Change Requests |
| `product-management:synthesize-research` | Retro synthesis across multiple sessions |
| `product-management:competitive-brief` | If we ever compare project-studio to alternatives |

### 15.2 Persona-expertise dependencies

These are the library skills each persona should load when operating. Missing these does not halt the session; the persona simply loses that expertise lens.

#### 15.2.1 chief-of-staff

- `anthropic-skills:project-studio` (home base)
- `gstack-team:autoplan`, `gstack-team:context-save`, `gstack-team:context-restore`, `gstack-team:careful`, `gstack-team:retro`
- `product-management:brainstorm`, `product-management:write-spec`, `product-management:stakeholder-update`
- `anthropic-skills:doc-coauthoring` — for writing this plan and its successors

#### 15.2.2 skill-architect

- `anthropic-skills:skill-creator` (primary)
- `anthropic-skills:context-engineering-kit`
- `anthropic-skills:doc-coauthoring` — structured doc workflow
- `anthropic-skills:clean-architecture` — for reasoning about atom boundaries
- `anthropic-skills:domain-driven-design` — bounded contexts, atom modeling
- `anthropic-skills:software-design-philosophy` — complexity management in atom design
- `anthropic-skills:pragmatic-programmer` — meta-principles for skill design
- `anthropic-skills:pdf` — provenance docs

#### 15.2.3 eval-lead

- `anthropic-skills:superpowers` (primary)
- `anthropic-skills:code-guide`
- `anthropic-skills:clean-code` — eval harness code quality
- `anthropic-skills:refactoring-patterns`
- `anthropic-skills:pragmatic-programmer`
- `anthropic-skills:ddia-systems` — data-shape evals (scenario state fixtures)
- `anthropic-skills:release-it` — fault-tolerance patterns for eval runner
- `anthropic-skills:c-framework` — contractual mode for eval rigor
- `gstack-team:review` — PR review tooling

#### 15.2.4 release-manager

- `gstack-team:ship` (primary)
- `gstack-team:canary`
- `gstack-team:make-pdf`
- `gstack-team:land-and-deploy` (future use)
- `gstack-team:cso` — security audit before release
- `anthropic-skills:release-it` — release-engineering patterns
- `anthropic-skills:code-guide`
- `anthropic-skills:pdf` — provenance PDF generation

#### 15.2.5 downstream-compat-lead

- `gstack-team:qa` (primary)
- `gstack-team:investigate`
- `gstack-team:browse` — if smoke-testing live URLs
- `anthropic-skills:webapp-testing` — Playwright-driven checks
- `anthropic-skills:mobile-responsive-testing` — if mobile surfaces appear
- `anthropic-skills:code-guide` — understanding downstream workspace shapes

#### 15.2.6 scenario-agent (sub-agent)

- `anthropic-skills:context-engineering-kit` (primary)
- `anthropic-skills:superpowers` — structured scenario authorship
- `anthropic-skills:c-framework` — contractual thinking prevents leaky scenarios
- `anthropic-skills:mom-test` — writing scenarios that don't lead the implementation
- `anthropic-skills:clean-code` — scenario YAML quality

#### 15.2.7 implementation-agent (sub-agent)

- `anthropic-skills:code-guide` (primary)
- `anthropic-skills:superpowers`
- `anthropic-skills:clean-code`
- `anthropic-skills:refactoring-patterns`
- `anthropic-skills:clean-architecture`
- `anthropic-skills:pragmatic-programmer`
- `anthropic-skills:software-design-philosophy`

### 15.3 Plan-review lens skills

The Tier-1 plan-review atoms (§2.3.11) invoke these lenses. The `gstack-team:plan-*-review` sub-skills wrap them, but each lens also loads library skills to sharpen its critique.

| Lens | Library skills loaded |
|---|---|
| plan-ceo-review | `product-management:brainstorm`, `yc-sv-development-framework`, `yc-startup-fundamentals` |
| plan-eng-review | `system-design`, `ddia-systems`, `release-it`, `clean-architecture`, `software-design-philosophy` |
| plan-design-review | `design-everyday-things`, `ux-heuristics`, `refactoring-ui`, `emil-design-eng`, `top-design`, `microinteractions` |
| plan-devex-review | `code-guide`, `clean-code`, `pragmatic-programmer`, `refactoring-patterns` |

### 15.4 `dependencies.yaml` schema

Written by F0 to `.project-studio/dependencies.yaml`. Checked by every `resume project` invocation.

```yaml
version: 1
resolved_on: <ISO-8601 timestamp>
cowork_session: <session-id or "n/a">

hard_deps:
  - name: anthropic-skills:project-studio
    status: present | missing
    version_seen: <string or null>
  - name: gstack-team
    kind: plugin
    status: present | missing
    sub_skills_present: [<list>]
    sub_skills_missing: [<list>]
  # ... one entry per row in §15.1

persona_deps:
  chief-of-staff:
    - name: <skill>
      status: present | missing
  skill-architect: [...]
  eval-lead: [...]
  release-manager: [...]
  downstream-compat-lead: [...]
  scenario-agent: [...]
  implementation-agent: [...]

environment:
  python: <version or null>
  git: <version or null>
  gh: <version or null>
  bash_mcp: present | missing
  cowork_directory: <absolute path or null>
  pypdf: <version or null>
  reportlab: <version or null>

gaps:
  hard:    []   # list of missing hard deps — non-empty = session halts
  persona: []   # list of {persona, skill} pairs — non-empty = warnings only
  env:     []   # list of missing env items — evaluated per item severity
```

### 15.5 Upgrading dependencies

Adding, removing, or changing a dependency is a Change Request (§5) of intent `add` / `remove` / `improve`. The request must cover:

- Which persona(s) it affects
- Whether it becomes a hard dep or persona-expertise dep
- Integration mode per §5.4
- Fallback behavior if the skill is unavailable
- Migration for existing workspaces running older `dependencies.yaml`

### 15.6 Bundled vs referenced

We do **not** copy the source of dependency skills into this repo. They are referenced by qualified name, loaded at runtime from the user's installed plugin set. This avoids: version drift between our copy and upstream, licensing complications, and the need to mirror updates manually.

The only exception is `skill/sub-skills/upgrade-workspace/` — that's *our* sub-skill, authored in this repo.

---

## 16. Installation and usage guide

This section is the end-user manual. It is duplicated in `docs/users/install.md` at F1 for discoverability; this canonical copy lives in the plan.

### 16.1 Prerequisites

Before installing project-studio, confirm:

| Item | Minimum | Check |
|---|---|---|
| Anthropic Claude client | Cowork mode enabled | You can see the skills picker in your client |
| Operating system | Windows / macOS / Linux | `mcp__workspace__bash` runs |
| Workspace mount | one folder, read-write | The repo-to-be lives there |
| Python | ≥ 3.11 | `python --version` |
| git | any recent | `git --version` |
| GitHub CLI | optional but recommended | `gh --version` |
| Disk space | ≥ 500 MB for repo + artifacts | — |

### 16.2 Install the plugins

Install `gstack-team` first (it provides the engineering discipline layer):

1. Open your Claude client's plugin settings.
2. Install `gstack-team` from its marketplace URL (or from the plugin's `.plugin` file if you were given one).
3. Confirm by running any sub-skill, e.g. invoking `/ship` should surface the `gstack-team:ship` guide.

Install `project-studio` from the Anthropic skills library. If you obtained a `project-studio-v<x.y.z>.skill` bundle from the GitHub Releases page of this repo, install it the same way — open your plugin settings, add the `.skill` bundle.

Install each hard-dep skill listed in §15.1 that is not already present.

### 16.3 Mount a workspace folder

Decide where your repo lives on disk. Example: `C:\Users\rajee\Desktop\Work\Badsoorat\project-studio`.

In Cowork mode, use the "select folder" action to mount that folder into the session. Confirm by listing files via the bash tool; you should see your repo's contents.

### 16.4 First-time scaffold (F0 + F1)

Open a new Cowork session with the folder mounted. Paste this prompt:

> *"Scaffold this project per `UPGRADE-SYSTEM-PLAN.md` using /project-studio in single-project mode. Execute Foundation phase F0, then F1."*

What happens:

1. Project-studio reads this plan.
2. F0 runs: the dependency check writes `.project-studio/dependencies.yaml`. If any hard dep is missing, the session halts with a clear install action for you.
3. F1 runs: `.project-studio/` is created at the repo root, git is initialized, CI workflows are stubbed, the atom-spec template is written, the baseline v3.1.0 is imported into `skill/`, and the first commit is made.
4. The chief-of-staff announces the final state: phase pointer on F2, tasks seeded, team present.

You (the human) then review the commit, push to GitHub, enable branch protection, and end the session.

### 16.5 Subsequent sessions — `resume project`

For every session after the scaffold, the prompt is:

> *"/project-studio — resume project."*

Project-studio:

1. Loads `.project-studio/state.md` and `tasks.md`
2. Verifies `dependencies.yaml` against the current environment (§15.4 gap check)
3. Reports current phase + open tasks
4. Chief-of-staff speaks first, proposes the next action
5. You confirm or redirect

Typical cadences:

- **Scenario authoring session** — you: *"F3 continued. Work on atom `boot.detect-cowork-mount` today."* scenario-agent loads, authors, submits for peer review.
- **Implementation session** — you: *"Implementation-agent, pick up `boot.detect-cowork-mount` — scenarios are red, turn them green."*
- **Retro** — you: *"Milestone retro for F3 week 2."* chief-of-staff runs `gstack-team:retro`.
- **Release** — you: *"Cut v3.2.0 release candidate."* release-manager runs the full T1–T5 battery, then `gstack-team:ship`.

### 16.6 Typical workflows

**Propose a Change Request:**
1. Open a session, `resume project`.
2. You: *"I'd like to propose a change: <brief>."*
3. Chief-of-staff runs intake §5. skill-architect auto-fills the Stage-5 analysis block.
4. Triage at end of session. Accepted requests get a branch and an owner.

**Author scenarios:**
1. scenario-agent reads request + atom specs *only*.
2. Writes scenarios to `upgrade-system/scenarios/<atom>/<slug>.yaml`.
3. eval-lead peer-reviews.
4. Commits to `feature/skill-<slug>` in red state.

**Land the implementation:**
1. implementation-agent reads request + atom specs + committed scenarios.
2. Writes code under `skill/` to turn scenarios green.
3. T1–T5 runs in CI on the feature branch.
4. `gstack-team:review` reviews the diff.
5. 2 Tier-1 lenses sign off (4 if touching A.15 multi-project atoms).
6. PR merges to `develop`; periodically `develop` merges to `main` via release branch.

**Cut a release:**
1. release-manager spins a `release/skill-v<x.y.z>` branch off `develop`.
2. Full T1–T5 regression + `gstack-team:cso` security audit.
3. `gstack-team:make-pdf` produces `FEATURE-PROVENANCE-MANIFEST-v<x.y.z>.pdf`.
4. `gstack-team:ship` merges to `main`, tags, triggers GitHub Release.
5. First 72 h: canary window via `gstack-team:canary` against any pilot workspaces.

### 16.7 Invoking the upgrade-workspace sub-skill (downstream)

If you are a downstream project that already has project-studio state and want to upgrade to a new release, from inside your project's Cowork session:

> *"/project-studio upgrade-workspace — upgrade to v<x.y.z>."*

upgrade-workspace:
1. Detects your installed skill version + workspace state format version
2. Loads the migration chain from the release's bundled manifest
3. Dry-runs, shows you a diff per affected atom's state
4. Asks per-change: apply / skip / defer
5. Applies atomically, records in `.cowork/upgrade-journal.md`
6. Post-validates schema + invariants + resume-readiness

If something goes wrong, the journal entry supports a rollback.

### 16.8 Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Session refuses to start, cites missing skill | F0 dependency gap (hard dep) | Install the named skill/plugin; re-run the scaffold prompt |
| Session starts but a persona is limited | F0 persona-expertise gap | Install the named skill (optional) or accept reduced fidelity, logged in ledger |
| `resume project` halts with "state.md missing" | F1 never ran, or `.project-studio/` got deleted | Re-run the F0+F1 scaffold prompt (non-destructive for `skill/` and `upgrade-system/` contents already committed) |
| `resume project` warns "version drift" | Installed project-studio is older than state.md expects | Upgrade the installed skill; re-run resume |
| CI fails at T5 on a PR | migration-bearing change hasn't been authored | release-manager authors the v<from>→v<to> migration in `upgrade-system/migrations/` |
| `--no-studio` mode needed | project-studio itself is suspect | Open a session *without* invoking `/project-studio`; debug `skill/` via raw file tools; re-try normal mode once fixed |
| Multi-module mode accidentally enabled | Someone configured project-studio wrong | See §1.4. This mode is ratified as forbidden. Re-scaffold in single-project mode. |

### 16.9 Uninstall / archive

The repo is public and portable. To stop using it:

- Archive the GitHub repo (read-only)
- Remove the mounted workspace folder
- Uninstall the project-studio skill and the gstack-team plugin

Downstream projects using older shipped versions are not affected by the archive; their skill bundles are self-contained.

---

**End of plan.**
