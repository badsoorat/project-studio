<!--
  Change Request — plan §6.
  Fill in every section. PRs missing the 5-stage block are rejected at T1.
-->

## Summary

One-line description of what this PR changes.

## Stage 1 — Motivation

Why this change now? Link the upstream request file under
`upgrade-system/requests/` if one exists.

## Stage 2 — Scope

- **Atoms affected:** (list atom IDs from `upgrade-system/architecture/atom-map.yaml`)
- **Surfaces touched:** skill / upgrade-system / both
- **Change-caution level:** low / medium / high (from each affected atom's spec)

## Stage 3 — Scenarios (author: scenario-agent)

- [ ] Scenarios committed RED before implementation began
- [ ] +3 scenarios per affected atom for behavior changes (plan §6)
- [ ] Peer-reviewed by `eval-lead`

Scenario files:
- upgrade-system/scenarios/...

## Stage 4 — Implementation (author: implementation-agent)

- [ ] Lands scenarios green
- [ ] No scenario file edited by this author (plan §7 structural guard)
- [ ] Atom sign-off by `skill-architect`

## Stage 5 — Analysis (author: skill-architect)

Required block. Answers:

1. What invariants were affected?
2. What prior-version compat fixtures were added or updated?
3. Any follow-ups deferred?

## Gate checklist

- [ ] T1 lint green
- [ ] T2 structural green
- [ ] T3 behavioral green for affected atoms
- [ ] T4 integration green
- [ ] T5 compat green (REQUIRED if `change-caution: high`)
- [ ] ADR updated or new ADR filed if an invariant shifted
- [ ] Ledger row added in `.project-studio/ledger.md` if a decision was ratified
