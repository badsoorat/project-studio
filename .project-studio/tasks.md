# Project Studio — Live Task Checklist

**Project:** `project-studio` upgrade system (meta-project)
**Current phase:** F2 — Atom enumeration (entered 2026-04-22 14:36 Z)
**Session of record:** Session 2 — 2026-04-22
**Plan reference:** [`UPGRADE-SYSTEM-PLAN.md`](../UPGRADE-SYSTEM-PLAN.md) §11

This file is the canonical checklist for the current phase. Each phase's
exit criteria come directly from plan §11. Items marked `[x]` are done,
`[~]` are in progress, `[ ]` are pending.

---

## F0 — Dependency verification  ✅ complete

- [x] All hard deps from plan §15.1 verified present in session
- [x] All persona-expertise deps from §15.2 verified present
- [x] All lens-library deps from §15.3 verified present
- [x] Environment probe of sandbox recorded (python, git, gh, pypdf, etc.)
- [x] Output written to `.project-studio/dependencies.yaml`
- [x] `outcome.f0_status: pass` recorded; F1 clearance granted

Artifacts: [`dependencies.yaml`](./dependencies.yaml)

---

<details>
<summary>F1 — Scaffold ✅ exited 2026-04-22 14:35 Z</summary>

Plan §11 exit criteria:

1. T1+T2 green on `main` after baseline import — **deferred to host-side SETUP.md (F1.7); not blocking F2 entry per plan §11**
2. `.project-studio/` present with team announced — **complete**
3. `resume project` works in a fresh session — **complete (validated session 2)**

### F1.1 — `.project-studio/` state directory

- [x] `state.md` — phase pointer, version awareness, surface map, roster
- [x] `team.yaml` — 5 main personas + 2 sub-agents, loadouts, writes_to, memory paths
- [x] `dependencies.yaml` — produced by F0
- [x] `tasks.md` — this file
- [x] `journal.md` — append-only event log (seeded, includes F1-exit + F2-enter)
- [x] `ledger.md` — decisions ledger seeded with ADR-0001 (superseded by 0002) and ADR-0002 (ratified); defect-0001 + defect-0002 recorded
- [x] `persona-memory/` — seven empty per-persona directories created

### F1.2 — `skill/` — v3.1.0 baseline import

Source: `/sessions/confident-kind-fermi/mnt/.claude/skills/project-studio/` (read-only mount of the installed skill)
Destination: `skill/` (working tree — edit target for F2+)

- [x] `skill/SKILL.md` — baseline from installed v3.1.0
- [x] `skill/VERSION` — single-line `3.1.0-baseline`
- [x] `skill/protocol/` — boot.md *(hotfixed 2026-04-22 14:25 Z, defect-0001+0002)*, resume.md, invariants.md
- [x] `skill/references/` — all reference files
- [x] `skill/templates/` — all template files
- [x] `skill/scripts/` — init_project.py + any others
- [x] `skill/evals/xref_check.py` — existing lint from upstream (will be lifted under `upgrade-system/evals/` in F3)
- [x] `skill/sub-skills/upgrade-workspace/` — empty directory with README stub (atom §2.3.9 delivers the contents in later phases)

### F1.3 — `upgrade-system/` meta-project tree

- [x] `upgrade-system/architecture/atoms/_template.md` — atom spec template
- [x] `upgrade-system/architecture/atom-map.yaml` — stub (F2 populates it)
- [x] `upgrade-system/schemas/scenario.schema.yaml` — stub (F3 finalizes)
- [x] `upgrade-system/schemas/atom-spec.schema.yaml` — stub (F3 finalizes)
- [x] `upgrade-system/evals/runner.py` — skeleton that loads tiered suites
- [x] `upgrade-system/evals/tiers/{T1-lint,T2-structural,T3-behavioral,T4-integration,T5-compat}/.gitkeep`
- [x] `upgrade-system/scenarios/.gitkeep`
- [x] `upgrade-system/migrations/.gitkeep`
- [x] `upgrade-system/provenance/features/.gitkeep`
- [x] `upgrade-system/requests/.gitkeep`
- [x] `upgrade-system/decisions/.gitkeep`
- [x] `upgrade-system/fixtures/.gitkeep`

### F1.4 — Decision records

- [x] `upgrade-system/decisions/ADR-0001-multi-module-considered.md` — records the briefly-considered multi-module mode and why it was rejected (plan §1.4, §14.3)
- [x] `upgrade-system/decisions/ADR-0002-dogfood-with-rails.md` — ratifies single-project + version-awareness + pinned orchestrator (plan §1.3, §1.4.5, §1.4.6)

### F1.5 — CI + GitHub plumbing

*Note: bash mount couldn't see `.github/` in session 2; verified via file-tool Reads that all 9 files do persist on Windows host (see journal 2026-04-22 14:30 Z).*

- [x] `.github/workflows/t1-lint.yml`
- [x] `.github/workflows/t2-structural.yml`
- [x] `.github/workflows/t3-behavioral.yml`
- [x] `.github/workflows/t4-integration.yml`
- [x] `.github/workflows/t5-compat.yml`
- [x] `.github/workflows/release-track-a.yml` — builds `project-studio-v<x.y.z>.skill`
- [x] `.github/workflows/release-track-b.yml` — builds `upgrade-workspace-v<a.b.c>.skill`
- [x] `.github/pull_request_template.md` — Change Request sections (§6)
- [x] `.github/ISSUE_TEMPLATE/change-request.md` — stage-5 capture

### F1.6 — Root docs

- [x] `README.md` — splash with users-vs-contributors split (plan §16.4)
- [x] `CONTRIBUTING.md` — workflow summary, Change Request stages
- [x] `CHANGELOG.md` — seeded with `v3.1.0-baseline` entry
- [x] `LICENSE` — MIT (matching upstream project-studio license)
- [x] `.gitignore` — `dist/`, `.cowork/`, persona scratch, eval artifacts

### F1.7 — Git + baseline tag  ✅ closed 2026-04-22 15:12 Z

*Executed host-side via `SETUP.md` Steps 1-5. F1.7 was not a gate on F2 entry, but has now been retired so there is no dangling deferred work.*

- [x] `git init -b main` in working tree (broken `.git/` husk removed first)
- [x] Initial commit of the scaffold — `f595811` (98 files)
- [x] Tag `v3.1.0-baseline` on initial commit — tag object `6e782b5`
- [x] **Human action:** GitHub repo `badsoorat/project-studio` created (public, via `gh repo create`)
- [x] **Human action:** `origin` HTTPS remote added; `main` + tags pushed; follow-up cleanup commit `f9227c5` (stray `boot.md.tmp`) landed
- [x] **Human action:** branch protection on `main` applied per **[ADR-0003](../upgrade-system/decisions/ADR-0003-branch-protection-solo-deviation.md)** (relaxed solo-dogfood variant: 5 T-tier checks required, 1 approval, `enforce_admins: false`; must revert to plan §8.2 at v3.2.0 release)

</details>

---

## F2 — Atom enumeration  ⏳ in progress (entered 2026-04-22 14:36 Z)

Plan §11 exit criteria:

- All 103 atoms enumerated with spec files under `upgrade-system/architecture/atoms/`
- Every atom has: `id`, `surface`, `change-caution`, `invariants[]`, `owner-persona`, `related-atoms[]`, `scenarios[]` placeholder
- `upgrade-system/architecture/atom-map.yaml` links atoms to source lines in `skill/` baseline
- Per-atom sign-off by `skill-architect`

**Gate before any atom spec is written:** Tier-1 plan-critique (Invariant #20) must run on the F2 approach. Four lenses spawned in parallel on the next user turn:
- [ ] `gstack-team:plan-ceo-review`
- [ ] `gstack-team:plan-eng-review`
- [ ] `gstack-team:plan-design-review`
- [ ] `gstack-team:plan-devex-review`

After consolidation + user approval, proceed with the F2 worksheet below.

### F2 worksheet

- [ ] F2.1 — Enumerate Tier-0 pre-boot atoms (§2.3.1) — includes defect-0001 resolution (which boot.md copy is authoritative?)
- [ ] F2.2 — Setup & resume atoms (§2.3.2, §2.3.3)
- [ ] F2.3 — Update & critique atoms (§2.3.4, §2.3.5) — **§2.3.15 multi-project carries change-caution:high**
- [ ] F2.4 — Ship/retro/context atoms (§2.3.6-8)
- [ ] F2.5 — Upgrade-workspace sub-skill atom (§2.3.9)
- [ ] F2.6 — Degraded-mode + meta-session atoms (§2.3.10, §2.3.11)
- [ ] F2.7 — References library atoms — includes defect-0002 resolution (add `PATTERN:reflexion-check` to `references/patterns.md` OR rewrite the boot.md xref)
- [ ] F2.8 — Link atoms to baseline source lines in `atom-map.yaml`

---

## F3 — Scenario authoring  🔜

Plan §11 exit criteria:

- Every atom has at least one behavioral scenario committed RED
- Schemas finalized in `upgrade-system/schemas/`
- `scenario-agent` authored; `eval-lead` peer-reviewed
- T3 suite runs (red, as expected)

Seed:

- [ ] F3.1 — Finalize scenario schema
- [ ] F3.2 — Author T3 scenarios for each atom (scenario-agent)
- [ ] F3.3 — Peer review (eval-lead)
- [ ] F3.4 — Finalize T4 integration scenarios
- [ ] F3.5 — Finalize T5 compat fixtures (downstream-compat-lead)

---

## F4 — Eval runner + CI wiring  🔜

- [ ] F4.1 — Flesh out `upgrade-system/evals/runner.py`
- [ ] F4.2 — Wire T1-T5 tiers into workflows (from F1.5 stubs)
- [ ] F4.3 — T5 compat harness loads prior-version fixtures
- [ ] F4.4 — Branch protection confirmed enforcing all 5 tiers

---

## F5 — Implementation (scenarios → green)  🔜

- [ ] F5.1 — For each Change Request: spawn `scenario-agent` → commit red scenarios → peer review → spawn `implementation-agent` → land green
- [ ] F5.2 — Per-atom sign-off (skill-architect)
- [ ] F5.3 — Release candidate cut: `v3.2.0-rc.1`
- [ ] F5.4 — `gstack-team:cso` security audit
- [ ] F5.5 — `gstack-team:ship` to production; Track A publish

---

## F6 — Track B (upgrade-workspace) publish  🔜

- [ ] F6.1 — Cut `upgrade-workspace-v0.1.0.skill` from `skill/sub-skills/upgrade-workspace/`
- [ ] F6.2 — Track B release workflow run
- [ ] F6.3 — Downstream dogfood on a prior-version pilot workspace
- [ ] F6.4 — Retro (`gstack-team:retro`) — close out the upgrade-system meta-project

---

## How this file is maintained

- CoS updates checkboxes at turn boundaries, never mid-task.
- When a phase exits, the completed phase's block is collapsed behind a
  `<details>` tag (not deleted).
- Seed tasks for future phases are intentionally non-specific. They are
  fleshed out by the persona owning the relevant phase at phase start.
- This file lives alongside — not inside — `journal.md` and `ledger.md`.
  Tasks describe *what*; journal is *when*; ledger is *why*.
