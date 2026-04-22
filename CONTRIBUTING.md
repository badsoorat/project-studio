# Contributing to project-studio

Thank you for contributing. This repo ships a Claude skill that runs in
other people's sessions — the bar for changes is high, and we keep it
high with the **5-stage Change Request** flow plus the **5-tier eval**
regime.

Read [`UPGRADE-SYSTEM-PLAN.md`](./UPGRADE-SYSTEM-PLAN.md) before you
open anything non-trivial.

---

## The short version

1. Open an issue using the **Change Request** template. Describe the
   problem, expected scope, and acceptance criteria.
2. A main persona (listed in `.project-studio/team.yaml`) claims the
   request and opens a feature branch.
3. A **scenario-agent** sub-agent authors behavioral scenarios in
   `upgrade-system/scenarios/` and commits them RED. No implementation
   yet.
4. **eval-lead** peer-reviews the scenarios.
5. A **implementation-agent** sub-agent writes the implementation that
   turns those scenarios green. **Different sub-agent** from the one
   that authored the scenarios — this is a structural guard in
   `.project-studio/team.yaml`.
6. **skill-architect** signs off per affected atom.
7. CI runs all five tiers. Branch protection on `main` requires all
   five to pass plus two reviewer approvals.
8. **release-manager** picks up merged work and cuts Track A / Track B
   releases.

## The 5 stages on a PR

Every PR MUST include the 5-stage block from the PR template:

1. Motivation — why now
2. Scope — atoms and surfaces affected + change-caution
3. Scenarios — written first, committed red
4. Implementation — turns scenarios green
5. Analysis — invariants, compat fixtures, follow-ups

Stage 5 is authored by `skill-architect` and is a hard requirement —
it is not optional for any PR that touches `skill/` or an atom spec.

## The 5-tier eval regime

| Tier | What | Blocking? |
|---|---|---|
| T1 | Lint, schema conformance, xref check | yes |
| T2 | Structural — atom ↔ spec ↔ scenario coherence | yes |
| T3 | Per-atom behavioral (scenario runs) | yes for affected atoms |
| T4 | Integration (cross-atom flows) | yes if any atom touched |
| T5 | Backwards-compat (prior-version fixtures) | required for `change-caution: high` |

Run locally:

```bash
python upgrade-system/evals/runner.py --tier all
python upgrade-system/evals/runner.py --tier T3 --atom atom-017-classifier
```

## What NOT to change outside the Change Request flow

- `skill/protocol/invariants.md` — invariants only shift via a new ADR
  in `upgrade-system/decisions/`.
- `.project-studio/team.yaml` — persona scopes, loadouts, and guardrails
  are ratified via an ADR.
- `upgrade-system/schemas/` — schema shifts are `change-caution: high`.

## Running the session

Open the repo in a Claude Code session or Cowork session. The skill is
the installed v3.1.0 orchestrator — the working tree is your edit
target, not your runtime. See ADR-0002 for the dogfood-with-rails
rationale.

## Code of conduct

Be kind. Dissent is captured append-only in `.project-studio/journal.md`
and ADRs — there is always a place to register disagreement. Nothing
gets rolled back silently.
