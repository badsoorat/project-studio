# Project Studio — Decisions Ledger

Index of material decisions made during this meta-project. The ledger
is a **pointer table** — full ADR content lives in
`upgrade-system/decisions/ADR-NNNN-<slug>.md`. This file exists so that
future sessions can find decisions without scanning the full ADR
directory.

Columns:

- **#** — ADR number (monotonic)
- **Title** — short slug
- **Status** — proposed / ratified / superseded / deprecated
- **Phase** — phase during which the decision was made
- **Link** — relative path to the ADR file
- **Supersedes / Superseded-by** — cross-links

---

| #    | Title                               | Status     | Phase | Link                                                           | Supersedes / Superseded-by |
|------|-------------------------------------|------------|-------|----------------------------------------------------------------|----------------------------|
| 0001 | Multi-module mode considered                   | superseded | F0    | [ADR-0001](../upgrade-system/decisions/ADR-0001-multi-module-considered.md)                  | superseded-by ADR-0002     |
| 0002 | Dogfood-with-rails (single-project)            | ratified   | F0    | [ADR-0002](../upgrade-system/decisions/ADR-0002-dogfood-with-rails.md)                        | supersedes ADR-0001        |
| 0003 | Branch-protection solo-dogfood deviation       | ratified (temporary) | F1.7 | [ADR-0003](../upgrade-system/decisions/ADR-0003-branch-protection-solo-deviation.md) | revert at v3.2.0 release   |

---

## Defects found in v3.1.0 baseline

Discovered during F1 import of the installed v3.1.0 skill into `skill/`.
These are findings against the baseline, **not** against the working-tree
edits. Each will be re-examined during F2 atom enumeration to decide
whether to fold the repair into an atom spec or leave as a non-issue.

| id          | File                             | Summary                                                          | Phase found | Status in working tree |
|-------------|----------------------------------|------------------------------------------------------------------|-------------|------------------------|
| defect-0001 | `skill/protocol/boot.md`         | Installed v3.1.0 copy in sandbox mount (`/sessions/.../.claude/skills/project-studio/protocol/boot.md`) is truncated at L71 mid-sentence in step 6 of the Per-Turn Checklist. The Windows skills-plugin copy (authoritative) is 115 lines. Divergence between the two installed copies is itself a finding. | F1          | Working tree restored to 115-line authoritative content via F1 hotfix (see journal 2026-04-22 14:20 Z). |
| defect-0002 | `skill/protocol/boot.md` (L115)  | Authoritative Windows-plugin v3.1.0 source ends line 115 mid-word at `"for the ca"`. The dangling reference into `references/patterns.md §PATTERN:reflexion-check` is also missing from `patterns.md` (grep-confirmed). | F1          | Closed in working tree to `"for the canonical form."` — minimal textual repair. The dangling xref remains an open F2 finding to resolve by either (a) adding the pattern to `patterns.md` or (b) rewriting the boot-file reference. |
| defect-0003 | Toolchain — PowerShell 5.1 + `gh api` | First `PUT` of branch-protection rule sent an em-dash (U+2014) literal inside a PowerShell here-string. PS's cp850 I/O code page encoded it as `0xE2` and GitHub's API accepted the mangled name `"T1 ? lint"` silently — a rule was created but referenced check context names that would never report. | F1.7 | Resolved by re-PUT with `\u2014` JSON escapes (ASCII-only on the wire). Verified correct via `jq '.contexts[0] \| explode'` returning code-point 8212. Future `gh api` calls from PowerShell that include non-ASCII MUST use `\uXXXX` escapes or UTF-8-encoded `--input file`. |

---

## Adding a new decision

1. Append a row above with the next ADR number.
2. Create the ADR file at `upgrade-system/decisions/ADR-NNNN-<slug>.md`
   using the ADR skeleton (Context, Decision, Consequences, Alternatives,
   Dissent, References).
3. Record a `decision` event in `journal.md` pointing at the row.
4. If this decision supersedes a prior one, update BOTH rows'
   Supersedes / Superseded-by columns.
5. Never mutate a row's `Status` from `ratified` to `proposed`. If a
   ratified decision needs revisiting, open a new ADR that supersedes
   it — history is append-only.
