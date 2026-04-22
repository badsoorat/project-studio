# Changelog

All notable changes to this project are documented here. This project
ships two release tracks with independent version lines:

- **Track A** — `project-studio-v<x.y.z>.skill`
- **Track B** — `upgrade-workspace-v<a.b.c>.skill`

---

## [Unreleased]

### In progress (F1 — Scaffold)

- Scaffold `.project-studio/` coordination state.
- Import `skill/` v3.1.0 baseline from installed skill.
- Lay down `upgrade-system/` meta-project tree.
- Stub 7 CI workflows (T1-T5 + 2 release tracks).
- Record ADR-0001 (multi-module considered) and ADR-0002
  (dogfood-with-rails, ratified).

---

## [v3.1.0-baseline] — 2026-04-22

### Imported

- `skill/` contents = verbatim copy of installed `project-studio` v3.1.0
  (51 files: SKILL.md, protocol/, references/, templates/, scripts/,
  evals/, CHANGES.md, EVAL-REPORT.md).
- `skill/VERSION` = `3.1.0-baseline` to mark the import point.

### Notes

- This tag (`v3.1.0-baseline`) marks the beginning of the upgrade-system
  meta-project. It is NOT a new release of the skill — the installed
  runtime-of-record remains v3.1.0.
- First new release of the skill will be `v3.2.0` at the end of F5.
