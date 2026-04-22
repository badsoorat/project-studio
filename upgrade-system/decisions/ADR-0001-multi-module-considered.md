# ADR-0001 — Multi-module mode considered for the upgrade-system meta-project

**Status:** superseded (by ADR-0002)
**Phase:** F0
**Date:** 2026-04-22
**Author:** chief-of-staff (session 1)

## Context

`project-studio` v3.1.0 supports a v2.4 multi-module "parent" architecture:
a parent directory holding a data-only manifest, a shared communication
layer, a shared state layer, and N module sub-projects that communicate
via inbox/outbox/bus messaging routed by a `sync` command.

At F0 we had to choose a mode for the upgrade-system meta-project itself:

1. **Multi-module** — treat `skill/` and `upgrade-system/` as two
   Project Studio "modules" under a parent, with separate team rosters
   and inbox/outbox routing between them.

2. **Single-project** — both `skill/` and `upgrade-system/` are peer
   surfaces in one working tree, sharing one CoS, one team roster,
   one git history, and one CI.

Option 1 was considered because it mirrors how downstream users often
organize large products, and because the separation between "the thing
being shipped" and "the thing doing the shipping" is real.

## Decision (tentative, superseded before ratification)

The initial lean was toward multi-module, on the grounds that a module
wall would clarify blast radius.

## Consequences explored

Multi-module would have introduced:

- Two separate CoS sessions that would have to coordinate via inbox/outbox
  bus messages — creating a new class of meta-session-coordination bugs
  during the very work intended to harden the skill.
- A duplicate team roster (or a shared-scope roster with per-module
  overrides) for personas that genuinely have cross-surface concerns
  (skill-architect authors BOTH skill text and upgrade-system provenance;
  release-manager owns BOTH tracks).
- Two CI pipelines to keep in lockstep, doubling branch-protection
  bookkeeping.
- A messaging layer whose own correctness is in-scope for this project
  — creating a circular dependency where the upgrade-system depends on
  the inbox/outbox correctness it is trying to verify.

## Why this was superseded

Plan §1.4 considered multi-module and rejected it explicitly. The
rejection reasoning is captured in ADR-0002. In short: the module wall
would add coordination cost for no blast-radius benefit, because every
main persona already has cross-surface write authority by necessity.

## Links

- Superseded by: [ADR-0002](./ADR-0002-dogfood-with-rails.md)
- Plan reference: `UPGRADE-SYSTEM-PLAN.md` §1.4 (mode ratification),
  §14.3 (alternatives considered).
- Ledger row: `.project-studio/ledger.md` #0001
