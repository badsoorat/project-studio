# Project Studio — Session State

**Project:** `project-studio` upgrade system (meta-project)
**Repo root:** `C:\Users\rajee\Desktop\Work\Badsoorat\project-studio`
**Plan:** [`UPGRADE-SYSTEM-PLAN.md`](../UPGRADE-SYSTEM-PLAN.md) (v1.0, 2026-04-22)
**Mode:** single-project (ratified in plan §1.4 — multi-module is explicitly forbidden)
**Phase pointer:** `F2 — Atom enumeration` (entered 2026-04-22 14:36 Z)
**Previous phase:** `F1 — Scaffold` (exited 2026-04-22 14:35 Z; F1.7 git steps deferred to host-side `SETUP.md`, not blocking per plan §11)
**Session of record:** Session 2 — F1 cleanup + F2 entry
**Session date:** 2026-04-22

---

## Version awareness (plan §1.4.5)

- **Runtime-of-record:** `anthropic-skills:project-studio` **v3.1.0** (installed skill driving this session)
- **Edit target:** working tree under `skill/` and `upgrade-system/`
- **Target version to ship:** `v3.2.0` (released at end of F5)
- **Working-tree commit:** set at first commit (see `journal.md`)

Chief-of-staff must announce both version identities at each session start. Changes to `skill/` in the working tree are **not** picked up by this running session — they ship via F5, then the user re-installs.

---

## Surfaces (plan §1.1, §1.4.2)

- **`skill/`** — the shipped `project-studio` skill source. Track A.
- **`upgrade-system/`** — meta-project: atoms, evals, scenarios, migrations, provenance, requests, decisions. Track B.
- **`.project-studio/`** — this directory. Coordination state only. Not under either surface.
- **`.cowork/`** — ephemera (freeze lists, context snapshots, scratch). Git-ignored. Not yet populated.

Both surfaces are peers in one git history, gated by the same CI. All five personas have read + write access to both. No module wall.

---

## Team roster (see `team.yaml`)

| Persona | Scope | Primary skill |
|---|---|---|
| chief-of-staff | cross-surface | `anthropic-skills:project-studio` |
| skill-architect | cross-surface | `anthropic-skills:skill-creator` |
| eval-lead | cross-surface | `anthropic-skills:superpowers` |
| release-manager | cross-surface | `gstack-team:ship` |
| downstream-compat-lead | cross-surface | `gstack-team:qa` |
| scenario-agent (sub-agent) | scenarios only | `anthropic-skills:context-engineering-kit` |
| implementation-agent (sub-agent) | implementation only | `anthropic-skills:code-guide` |

---

## Current phase — F2

Plan §11 F2 entry conditions met: F1 in-tree scaffold complete; `resume project` validated in session 2; F1.7 host-side git steps deferred to `SETUP.md` (not blocking F2 per plan §11).

F2 deliverables in progress — see `tasks.md` for the live checklist.

F2 exit criteria (plan §11):
- All 103 atoms enumerated with spec files under `upgrade-system/architecture/atoms/` — **pending**
- Every atom has: `id`, `surface`, `change-caution`, `invariants[]`, `owner-persona`, `related-atoms[]`, `scenarios[]` placeholder — **pending**
- `upgrade-system/architecture/atom-map.yaml` populated with atom ↔ baseline line mappings — **pending**
- Per-atom sign-off by `skill-architect` — **pending**

**Gate for first atom write:** Tier-1 plan-critique on the F2 approach itself (Invariant #20) — four lenses in parallel on the next user turn: `plan-ceo-review`, `plan-eng-review`, `plan-design-review`, `plan-devex-review`.

---

## Dissent log for this session

None yet. Dissent is captured append-only (plan §6 + project-studio Invariant #3).

---

## Open questions from the plan (§13)

- Real-world pilot workspaces for T5 — deferred; not blocking F2.

## Carried-over findings from F1

- **defect-0001** (boot.md baseline truncation). Two installed v3.1.0 copies diverge — Linux-sandbox mount is 70 lines (truncated), Windows-plugin copy is 115 lines. Working tree restored to 115. Resolve in F2.1 (which is authoritative?).
- **defect-0002** (boot.md L115 + dangling `PATTERN:reflexion-check` xref into `references/patterns.md` which does not define it). Text repaired in working tree; xref still dangles. Resolve in F2.7.
- **Bash-mount blindness for `.github/`.** Windows Cowork mount intermittently hides host-side files from the Linux sandbox. Workaround: file-tool Read/Write. Log in F2 observability pass.
- **F1.7 host-side git** (not a defect — waiting on user to execute `SETUP.md`).

---

## Next action (chief-of-staff's proposal)

On the next user turn, spawn the Tier-1 plan-critique (four lenses
in parallel, Invariant #20) on the F2 atom-enumeration approach.
Consolidate returns, surface any dissent, and present for approval
before any file under `upgrade-system/architecture/atoms/` is created.

Parallel host-side track (user-owned): run `SETUP.md` Steps 1-4 at
any time to close F1.7. This is independent of F2 progression.
