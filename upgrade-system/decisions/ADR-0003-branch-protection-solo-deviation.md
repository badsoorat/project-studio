# ADR-0003 — Branch-protection relaxation for the solo dogfood window

**Status:** ratified (temporary deviation)
**Phase:** F1.7 closeout (post-F1 exit, pre-F2 atom writes)
**Date:** 2026-04-22
**Author:** chief-of-staff (session 2)
**Relates to:** plan §8.2 (release-time branch protection spec)

## Context

Plan §8.2 specifies the production branch-protection rule for `main`:

- All 5 T-tier status checks required (`T1 — lint`, `T2 — structural`,
  `T3 — behavioral`, `T4 — integration`, `T5 — compat`).
- `required_approving_review_count: 2`.
- `enforce_admins: true`.

Those values are correct for a published v3.2.0 skill.

For the F2-F5 dogfood window, the project is a **solo contributor
authoring with sub-agents**. There is no second human reviewer
available, and `enforce_admins: true` would prevent the sole
contributor from bypassing the 2-approval gate. Applying §8.2 verbatim
now would produce a deadlock on the first Change Request PR, blocking
all F2-F5 progress until a second reviewer account is introduced.

Plan §11 is a phase-progression gate, not a release gate — nothing in
§11 requires §8.2's *final* values to be active during F2-F5. §8.2 is
scoped to "released product safety."

## Decision

**Branch protection on `main` is set to relaxed parameters during the
F2-F5 solo dogfood window, and reverted to plan §8.2 values at the
v3.2.0 release cut.**

Relaxed parameters (applied 2026-04-22 via `gh api ... PUT`):

| Parameter | Plan §8.2 | Relaxed (F2-F5) |
|---|---|---|
| `required_status_checks.contexts` | T1-T5 | T1-T5 (unchanged) |
| `required_status_checks.strict` | true | true (unchanged) |
| `required_pull_request_reviews.required_approving_review_count` | 2 | **1** |
| `enforce_admins` | true | **false** |
| `required_pull_request_reviews.dismiss_stale_reviews` | — | true |
| `allow_force_pushes` | false | false (unchanged) |
| `allow_deletions` | false | false (unchanged) |

The 5 T-tier check names were verified as U+2014 em-dash via
`jq '.contexts[0] | explode'` returning code-point 8212 after a
first PUT attempt mangled them through PowerShell's cp850 encoding
(see ledger defect-0003).

## Revert criteria

This deviation **MUST** be reverted before the v3.2.0 release tag is
pushed. Revert is part of the F5 release checklist:

1. Re-apply §8.2 values:
   `required_approving_review_count: 2`, `enforce_admins: true`.
2. Confirm by re-reading the rule via `gh api`.
3. Log the revert in `journal.md` as event type `decision` and
   update the status line of this ADR from "ratified (temporary
   deviation)" to "superseded by §8.2 revert".
4. Release-manager signs off on the revert before `v3.2.0` is tagged.

If additional human reviewers join before F5 (e.g., a second
contributor with merge rights on `badsoorat/project-studio`), the
deviation may be reverted earlier — it is not required to wait for
the release cut.

## Consequences

**Positive:**

- Unblocks F2-F5 Change Request flow for solo operation.
- Preserves the 5-tier status-check gate (the highest-value part of
  §8.2 — no merge without green CI).
- Explicit revert criteria prevent drift from the §8.2 target.

**Negative:**

- `enforce_admins: false` means the sole admin can bypass protection
  in an emergency. Mitigation: every admin-bypass merge MUST be
  logged as a `decision` event in `journal.md` with a link to the PR
  and a reason — giving the post-hoc auditability that §8.2 would
  have enforced structurally.
- Single approval means sub-agent outputs get only one human review.
  Mitigation: the scenario-agent / implementation-agent split (plan
  §7, §14.4) provides structural peer review; the sole human is
  reviewing the *merge*, not the *authoring*.

## Alternatives

- **(A) §8.2 verbatim + admin override per-merge.** Rejected — admin
  override requires `enforce_admins: false`, which is effectively
  this ADR anyway, but without explicit documentation.
- **(C) §8.2 verbatim, pair with a second reviewer account.**
  Rejected for now — the second account doesn't exist and would be
  administrative overhead to create and maintain. Not ruled out as a
  future improvement.
- **No branch protection during dogfood.** Rejected — loses the T-tier
  CI gate, which is the whole point of having §8 in the first place.

## Dissent

None recorded at ratification time.

## References

- Plan: `UPGRADE-SYSTEM-PLAN.md` §8.2 (release-time branch protection).
- SETUP.md Step 4 (the superseded command that §8.2 would have us run).
- Ledger: defect-0003 (PowerShell cp850 em-dash mangling, resolved
  via `\u2014` JSON escape on second PUT).
- Journal: 2026-04-22 entries covering F1.7 closeout.
