# project-studio upgrade system

Meta-project for shipping safe upgrades to the
[`anthropic-skills:project-studio`](https://github.com/anthropic-skills/project-studio)
skill.

This repository holds two peer surfaces in one git history:

- **`skill/`** — the source of the shipped `project-studio` skill
  (Track A release artifact).
- **`upgrade-system/`** — the meta-project tools: atoms, schemas,
  scenarios, evals, migrations, provenance, decisions.

Plus shared coordination state in `.project-studio/` (team roster,
phase tracker, journal, ledger).

---

## For users of the skill

You don't need to clone this repo. Install the skill via its published
`.skill` bundle — see the [releases page] once releases begin.

For documentation on the skill itself, read `skill/SKILL.md`.

[releases page]: https://github.com/badsoorat/project-studio/releases

---

## For contributors

### Prerequisites

- Python **≥3.11** (the eval runner depends on it)
- `git` ≥2.34
- `gh` (GitHub CLI) for the release workflows
- `anthropic-skills:project-studio` v3.1.0+ installed in your Claude
  client — this is what drives your working sessions on this repo

### Getting started

```bash
# Clone
git clone git@github.com:badsoorat/project-studio.git
cd project-studio

# Install eval runner deps
python -m pip install -r upgrade-system/evals/requirements.txt 2>/dev/null || \
  pip install pyyaml jsonschema

# Sanity-check the scaffold — all five tiers are stubs that pass cleanly
# in F1; F4 brings them online.
python upgrade-system/evals/runner.py --tier all
```

### Opening a session

```
/project-studio — resume project
```

The Chief of Staff will announce the version of record (installed
v3.1.0), the edit target (working tree), and the current phase from
`.project-studio/state.md`.

### Contributing a change

Every merge-bound change goes through the 5-stage Change Request flow
(plan §6). Use the **Change Request** issue template to start one; the
PR template enforces stages.

### Repo tour

```
UPGRADE-SYSTEM-PLAN.md    ← the plan of record (read this first)
.project-studio/          ← coordination state (team, phases, journal, ledger)
skill/                    ← the shipped skill — Track A
upgrade-system/           ← meta-project — Track B sub-skill, atoms, evals, decisions
.github/workflows/        ← 5-tier CI + both release tracks
docs/                     ← additional onboarding (users/ and contributors/)
```

---

## License

MIT. See [LICENSE](./LICENSE).
