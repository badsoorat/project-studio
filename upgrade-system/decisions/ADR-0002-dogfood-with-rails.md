# ADR-0002 — Dogfood-with-rails: single-project mode with version awareness

**Status:** ratified
**Phase:** F0
**Date:** 2026-04-22
**Author:** chief-of-staff (session 1)
**Supersedes:** [ADR-0001](./ADR-0001-multi-module-considered.md)

## Context

The upgrade-system is a meta-project whose **purpose** is to add safe
upgrade discipline to `project-studio`. It must do two things that are
in tension:

1. Use `project-studio` as its own orchestrator (dogfood), because any
   orchestration tool we would otherwise reach for is weaker than the
   one we already have.
2. Not accidentally break `project-studio` while it is in use as the
   orchestrator.

The naive approach — simply editing the installed skill on-disk while
a session is running — fails because the running session has the
*old* skill's text cached in its context window. Edits to `skill/`
in the working tree would produce inconsistent behavior mid-session.

## Decision

**We ratify a single-project, dogfood-with-rails architecture:**

1. **Single project, two surfaces.** `skill/` and `upgrade-system/`
   are peer surfaces in one git history. The working tree directory
   IS the project. No module wall.

2. **Pinned orchestrator.** The session is always driven by the
   **installed** v3.1.0 `anthropic-skills:project-studio` — NOT by
   the `skill/` directory in the working tree. The working tree is
   the **edit target**, not the runtime.

3. **Version awareness.** CoS announces both version identities at
   every session start:
   - *Runtime-of-record:* `project-studio` v3.1.0 (installed)
   - *Edit target:* working tree, shipping v3.2.0 at F5

4. **Ship-then-reinstall.** Changes to `skill/` in the working tree
   are NOT picked up by the running session. They ship via the F5
   release process (Track A `.skill` build + publish) and take effect
   only after the user re-installs and starts a fresh session.

5. **Team structure.** 5 main personas + 2 dedicated sub-agents
   (scenario-agent, implementation-agent). All main personas are
   cross-surface. Sub-agents carry strict read/write guards that
   prevent the same sub-agent from authoring both scenarios and
   implementation for the same Change Request (plan §7 structural
   guard).

6. **Safety rails for the dogfood:**
   - 5-tier eval regime (T1 lint, T2 structural, T3 per-atom
     behavioral, T4 integration, T5 backwards-compat) gated in CI on
     `main`.
   - 103-atom architecture (§2.3) with explicit `change_caution`
     labels; §2.3.15 multi-project atoms carry `change_caution: high`.
   - Two release tracks (Track A = skill, Track B = upgrade-workspace
     sub-skill) with distinct publishing workflows.
   - Scenario-first discipline: scenarios commit red before
     implementation commits green.

## Consequences

**Positive:**

- One CI, one git history, one CoS — no meta-session coordination cost.
- Every main persona has the cross-surface authority they need (e.g.,
  `skill-architect` authors SKILL.md AND upgrade-system provenance;
  `release-manager` owns BOTH tracks).
- The pinned-orchestrator rule eliminates the mid-session self-edit
  failure mode without giving up dogfood.
- The 5-tier regime provides the blast-radius control that the
  multi-module wall was meant to provide, but enforced via evals
  rather than via directory boundaries.

**Negative:**

- Developers must remember that editing `skill/` does not affect the
  running session. This is mitigated by CoS's version-awareness boot
  announcement.
- The F5 release step is mandatory before any in-tree skill change
  takes effect in future sessions.

## Alternatives

- **Multi-module:** see ADR-0001. Rejected.
- **Two separate repos:** rejected — splits the atom-to-code
  traceability that §2.3 and the atom map depend on.
- **Edit the installed skill directly:** rejected — see Context above.

## Dissent

None recorded at ratification time. Dissent is append-only — if any
persona later objects, they append here and in `journal.md` as a
`dissent` event.

## References

- Plan: `UPGRADE-SYSTEM-PLAN.md` §1.3 (dogfood-with-rails), §1.4
  (mode ratification), §1.4.5 (version awareness), §1.4.6
  (change-caution labels).
- Team: `.project-studio/team.yaml`
- State: `.project-studio/state.md`
- Ledger: `.project-studio/ledger.md` #0002
