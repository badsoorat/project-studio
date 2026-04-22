# Project Setup Flow

This is the setup wizard that runs **once** per project to stand up the office team. Follow the sequence strictly — each step depends on outputs from previous steps.

**Flow at a glance:**

- **Step 0** — Module resume detection (auto-triggered, runs before Step 1 asks anything).
- **Step 1** — Scenario + Scale (deterministic 3-question gate that locks A/B/C/D1/D2 + scale).
- **Step 2** — Scenario-specific context gathering. Branches into 2A/2B/2C/2D1/2D2. For parent scenarios (B/D1/D2) this also captures the full module inventory and per-module purposes.
- **Step 2.5** — Context Sort & Cleanup (runs only for D1/D2). Walks the existing tree, classifies files into four tiers, asks for batch approval, moves or hard-deletes accordingly. See `references/classifier-rules.md`.
- **Step 3** — Team Setup. For parent scenarios, splits into Phase 3A (parent-level team) + Phase 3B (per-module teams with a matrix view showing cross-module vs. module-specific personas). Every persona still passes the two-gate approval (body + skills) from `references/persona-schema.md`.
- **Step 4** — Roadmap. Single-tier for A/C, two-tier (parent milestones + module roll-ups) for B/D1/D2.
- **Step 5** — Connectors & Plugins.
- **Step 6** — Setup Review.
- **Step 7** — Build Project (scaffold, write files, including module seeds + communication files + handoff output for parent scenarios).
- **Step 8** — Module Resume Mode spec. Defines what happens when the user opens a new Cowork session inside a module subfolder after parent setup completed. Auto-triggers via Step 0 on the module side.

**Key philosophy shift:** Step 1 is a deterministic 3-question gate that locks the scenario and scale **before** any scenario-specific work begins. Everything downstream specialises by scenario but returns to the same gates (two-gate persona approval, user-approved roadmap, consistency review).

**Folder layout:** All Project Studio files live inside `project-studio/` at the project root. The codebase (if any) lives at the root alongside `project-studio/`. The root `CLAUDE.md` is the sole source of truth — it points to everything inside `project-studio/`.

Use `AskUserQuestion` for all multi-choice decisions (in Cowork mode). In Claude Code CLI where `AskUserQuestion` is unavailable, present options as a numbered list and ask the user to reply with a number or letter. Use TodoWrite to mirror progress visibly.

**Light-scale fast-track:** For light-scale projects (<1 day), compress setup to 3 steps: (1) Name + one-sentence brief + pick 1 specialist from the prompt context, (2) Scaffold via init_project.py or Write tool, (3) Write CLAUDE.md + brief + roadmap and go. Skip Step 5 (connectors) and Step 6 (review). See `references/scale-modes.md` for the full light-scale spec. Light scale forces single-module even if the product is technically multi-module — parent architecture is overkill for <1 day of work.

---

## Step 0 — Module Resume Detection (auto-triggered)

**This step runs silently before Step 1 asks anything.** It exists so the user can open a new Cowork session at a module subfolder (after parent setup completed) and have CoS pick up the prepared context automatically without re-running the wizard.

### 0a. Seed probe

On skill load, CoS checks the mounted folder for **any of these markers** (in priority order):

1. `project-studio/module-seed.yaml` — a structured module seed file written by the parent during Step 7 of the parent's setup.
2. `START-HERE.md` at the mount root — the human-readable companion to the seed.
3. A `project-studio/` directory that already contains `protocol/boot.md` (the module was previously set up and the user is resuming a completed project).

### 0b. Branching on seed state

- **Seed found (marker 1 or 2) + no completed project yet** → CoS is in **Module Resume Mode**. Skip Step 1 entirely. Read the seed, hydrate context, and jump to Step 8 (Module Resume Mode). Announce: *"I found a module seed from parent '[parent name]'. You're resuming as [module name]. Loading the prepared context now."*
- **Completed project found (marker 3)** → Normal resume protocol applies (`project-studio/protocol/resume.md`). Step 1 does NOT run. The full boot protocol takes over.
- **Neither found** → Fresh setup. Proceed to Step 1 normally. This is the default.

### 0c. Hard rule

**Do not auto-create Project Studio files based on partial/foreign markers.** If the mounted folder contains a `CLAUDE.md` that is NOT a Project Studio file, or a `project-studio/` directory that is missing `protocol/boot.md`, treat it as foreign content and proceed to Step 1 (the user will handle it via Scenario C/D1/D2 intake).

### 0d. Never ask the wizard questions when Step 0 matches

If Step 0 branches into Module Resume Mode (marker 1 or 2) or normal resume (marker 3), **do not ask Q1/Q2/Q2b/Q3**. The scenario is already locked by the parent or the previous session. Re-asking would double-gate the user.

---

## Step 1 — Scenario + Scale (deterministic gate)

Step 1 asks **three mandatory questions in a fixed order** (Q1 → Q2 → Q3), plus one conditional sub-question (Q2b) that only fires when Q1=Existing AND Q2=Multiple. No scenario-specific work begins until all three (or four) answers are in hand.

### Hard rules for Step 1

1. **Every question in this step MUST be asked explicitly via `AskUserQuestion` (or a numbered list in CLI mode).** Do NOT infer answers from context, folder state, earlier user messages, project type, or "obvious" signals. The user's earlier words are NOT substitutes for an answered question.
2. **Ask in strict order:** Q1, then Q2, then Q2b (if applicable), then Q3. Do not skip ahead. Do not ask Q3 before Q2b has been resolved.
3. **Q3 (Scale) is mandatory in ALL five scenarios (A, B, C, D1, D2).** The most common failure mode is skipping Q3 in D1/D2 because the conversation has already drifted into module/parent details after Q2b. Do not let that happen. After Q2b is answered, STOP and ask Q3 before announcing the scenario.
4. **Do NOT infer New/Existing from an empty or full folder** — ask Q1.
5. **Do NOT infer scale from project description, module count, or complexity hints** — ask Q3.
6. Before moving to Step 2, self-check: "Did I call `AskUserQuestion` (or show a numbered list) for Q1, Q2, Q2b-if-applicable, and Q3?" If any answer came from inference instead of an asked question, go back and ask it now.

### Q1: Is this a new project or an existing project?

Use `AskUserQuestion`.

- **New project** — Starting from scratch. No prior work anywhere (no codebase, no prior project-studio session, no files to bring in).
- **Existing project** — Has prior work somewhere: a local codebase, a git repo, a previous project-studio project, files on disk, or any other source. The user wants Project Studio to manage or extract context from it.

**Always ask Q1, even if the mounted folder looks empty.** An empty folder doesn't mean "new" — the user may have an existing project elsewhere.

### Q2: Single module or multiple modules?

Use `AskUserQuestion`.

- **Single module** — One thing: a website, OR an API, OR a mobile app, OR a dashboard.
- **Multiple modules** — Two or more pieces that belong to the same product: e.g. website + API, or web app + mobile app + admin panel.

**Definition of "module":** A module is an independently buildable/deployable piece of a product. A website and its backend API are two modules. A marketing site and the main app are two modules. A monorepo with one deployable is one module.

**1 module = 1 Project Studio project.** Even in the multi-module case, one folder hosts one module. Other modules are coordinated via parent architecture (preferred) or imports (fallback).

### Q2b (conditional): Does a parent coordination folder already exist?

**Only ask Q2b if Q1 = Existing AND Q2 = Multiple.** Skip otherwise.

Use `AskUserQuestion`.

- **Yes, a parent folder already coordinates these modules** — There's already a `CLAUDE.md` at the parent level that lists modules and holds `shared/` update files. → Scenario **D2**.
- **No, no parent folder yet** — The modules exist as siblings but there's no parent coordinator yet. → Scenario **D1**.
- **I'm not sure** — CoS checks: does the parent directory contain a `CLAUDE.md` with a module table? If yes → D2. If no → D1. Report what was found.

### Q3: Project scale?

**MANDATORY — ask this in every scenario (A, B, C, D1, D2). Never infer scale from context, module count, project type, or what the user said earlier. Ask the question verbatim, even if the answer seems obvious.**

Use `AskUserQuestion`. Use layman framing.

- **Light** — Quick work, solo, less than 1 day.
- **Standard** — Real project, 1 day to 1 month, solo or small team.
- **Heavy** — Long-running, 1+ months, multiple phases.

**Failure mode to avoid:** In D1 and D2 scenarios, Q2b pulls the conversation into parent/module details. After Q2b is answered, do NOT drift into Step 2. STOP, ask Q3 explicitly, then announce the scenario. If you catch yourself writing "Given the complexity, this sounds like a standard/heavy project…" — stop and ask Q3 instead.

**Anti-pattern example:** "This project uses React, Postgres, and Stripe integration — sounds like a heavy project." **WRONG.** That's not scale inference; scale comes from session time budget and work duration. A simple landing page can use complex tech. A 1-day sprint on a React+Postgres codebase is standard scale. A 6-week phased rebuild of the same stack is heavy. Always ask Q3.

### Scenario resolution table

**Pre-announce checkpoint:** Before showing this table to the user, verify that Q1, Q2, Q2b (if applicable), AND Q3 have all been answered via `AskUserQuestion` (or a numbered list). If Q3 is unanswered, ask it now — do not proceed.

After Q1 + Q2 (+ Q2b if applicable) + Q3, CoS announces the locked scenario and scale:

| Q1 | Q2 | Q2b | Scenario |
|---|---|---|---|
| New | Single | — | **A** — New + Single |
| New | Multiple | — | **B** — New + Multi |
| Existing | Single | — | **C** — Existing + Single |
| Existing | Multiple | No parent | **D1** — Existing + Multi, create parent |
| Existing | Multiple | Parent exists | **D2** — Existing + Multi, add to existing parent |

CoS says: *"Locked in: Scenario [X] at [scale] scale. Proceeding to Step 2."*

From here, Step 2 branches by scenario. Steps 3-7 are universal.

---

## Step 2 — Scenario-specific context gathering

**GATHERING PHASE** — collect all information needed before writing any files. Branch based on the scenario locked in Step 1.

---

### Step 2A — Scenario A (New + Single)

#### 2A.1: Gather brief

Ask for:
- Name (project name)
- One-sentence brief (what are we building/doing?)
- Goals (what does done look like?)
- Success metrics (how will we know we're winning?) — don't let the user skip this
- Constraints (time, budget, people, tech, legal)
- Stakeholders (who else cares?)
- Deadline or target date (if any)

#### 2A.2: Empty folder gate

For new projects, the mounted folder should be empty (except `.claude/` system files). Scan the folder. If non-system files exist, ask the user to clear it before proceeding:

*"For a new project, I need to start with an empty folder. Please clear this folder and confirm when done."*

---

### Step 2B — Scenario B (New + Multi)

#### 2B.1: Gather product-wide brief

Same fields as 2A.1 — name, one-sentence brief, goals, metrics, constraints, stakeholders, deadline — BUT framed at the **product level**, not at any single module. Phrase the prompts as *"What is the overall product you're building?"* not *"What is this website?"*. Per-module briefs come in 2B.3.

#### 2B.2: List all modules

*"List every module that will make up this product. A module is an independently buildable or deployable piece — e.g. website, API, mobile app, admin dashboard, ML service."*

CoS confirms back with a numbered list and asks *"Is that complete?"*.

After confirmation, CoS locks the **module inventory**. This list is authoritative for the rest of setup — it drives parent manifest, shared folder layout, team matrix, and two-tier roadmap.

#### 2B.3: Per-module purpose + folder name

For each module in the inventory, ask three micro-questions:

1. **Purpose** — *"One sentence: what does [module] do in the product?"*
2. **Folder name** — *"What subfolder name should this module live in? (default: lowercase-slug of the module name)"*
3. **Will a team be set up for this module now?** — *"Is this module actively being worked on right now, or is it just on the manifest for future work?"*

The answer to (3) determines whether Phase 3B iterates over this module during team setup. Modules marked "future work" get a placeholder entry in the parent manifest but no team, no roadmap, no seed file.

Hold these as `module_inventory[]` in setup context — each entry has `{name, slug, purpose, active, folder_path}`.

#### 2B.4: Pick the primary module (the one this session will open in)

*"Which module should this session focus on first? After parent setup completes, I'll hand you off to open a new session at that module folder and continue from there."*

The primary module is the one the user will resume in first. It is NOT special — all active modules get the same seed treatment — but it's the one the handoff instructions at the end of Step 7 point to.

#### 2B.5: Parent folder mount check

*"For multi-module projects, a parent folder coordinates them. Is this mounted folder the parent (with module subfolders as children)? Or is the mounted folder already the primary module itself?"*

- **Mounted folder is the parent** — Modules will be created as subfolders inside it. Full parent architecture active — manifest, shared/, communication files (outbox/inbox/bus), and handoff all work as designed.
- **Mounted folder is the primary module** — No parent access from this session. Cross-module context goes into `project-studio/imports/` instead of parent `shared/`. The module-seed/handoff mechanism is unavailable — user will have to set up the parent manually from a different mount later, and the other modules' setup will be independent Project Studio projects.

CoS flags clearly that the "primary-module mount" path forfeits the parent handoff and module-seed flow. Most users will pick "parent mount" after hearing that.

#### 2B.6: Empty folder gate

Same as 2A.2 — verify the mounted folder is empty before scaffolding. For "parent mount" path, the parent folder itself must be empty (or contain only `.claude/` system files). For "primary module mount" path, the module folder must be empty.

---

### Step 2C — Scenario C (Existing + Single)

#### 2C.1: Intake method

Ask how the existing work should come into Project Studio. Use `AskUserQuestion`:

*"How do you want to bring this project in?"*

- **Extract context only (migration-export)** — I want structured context (goals, roadmap, decisions, infrastructure) but NOT the code. Good if the code lives elsewhere or is managed in another way.
- **Bring in local codebase** — The code is on my computer. I'll copy/paste the folder contents here, or it's already mounted. Project Studio will manage this code directly.
- **Clone git repo** — I have a git repo URL. Clone it here and Project Studio will manage the code directly.

#### 2C.2: Execute intake

##### Path: Extract context only (migration-export)

Sub-question: *"Where is the project's data?"*

- **In another Project Studio session** — I'll paste an export prompt there.
- **In a local folder / git repo I can access from another Claude session** — Same, I'll paste a prompt.
- **I'll describe it from memory** — No source to extract from.

**If "another session" or "local/git in another session":** CoS presents the migration-export prompt (see "Migration Export Prompt" at the end of this file). User pastes into the source session, gets `migration-export.md`, pastes result back. CoS writes the result to `project-studio/imports/<slug>/migration-export.md`, validates it, and splits it into slice files.

**If "describe from memory":** CoS gathers context manually during the brief step below. Notes the gaps.

##### Path: Bring in local codebase

**Folder state check:**

- **If files found:** *"I see what looks like a [framework] codebase already in this folder. Is this the project?"*
  - If yes → this IS the codebase. Proceed directly to verify and contamination scan below. **This is the common path in Cowork mode** where the user has already mounted their project folder.
  - If no → *"Please clear this folder first, then copy your codebase in, and let me know when it's done."*
- **If no files found (empty folder):** *"Copy your codebase into this folder and let me know when it's done."*

**Verify codebase arrived:** CoS scans the folder: directory tree, package manifests, README, source files. Presents: *"I see a [framework] project with [N] source files. This looks like [description]. Is this right?"*

**Run contamination scan.** See `references/contamination-checklist.md`. Tier 1 (HIGH) archive/delete AI instruction files. Tier 2 (MEDIUM) flag directory name collisions. Tier 3 (LOW) flag prompt-like content. Present results, execute user decisions, re-scan clean.

**Graphify is invoked per-spawn, not pre-built.** Setup does NOT run `graphify .` at the project root. There is no global `GRAPH_REPORT.md`. Instead, when CoS later spawns a code-heavy specialist for a structural question at standard or heavy scale, the spawn prompt loads graphify as a skill and scopes it to the path under review. Skip graphify entirely on light scale. See `references/invokable-skills.md` for solo/combo loadouts, scope rules, and the Task-tool invocation template.

**Direct codebase scan.** Since the code is right here, CoS scans directly to build metadata — no "paste a prompt into another session" dance. Read: directory tree (2-3 levels), README, package manifests, config files, env var names (NOT values), framework detection.

**Scan discipline — only report what you can trace to an actual file.** Don't fill gaps based on what "typically" belongs in this kind of project. A hallucinated service becomes a false assumption in the brief, the roadmap, and the risk register. Present findings in two clearly labeled buckets:

- **Confirmed** — services/tech traceable to a literal line in a file.
- **Not found in files** — infrastructure categories you'd expect but found no evidence for (auth, search, email, cache, analytics).

Close with targeted gap questions, not an open-ended one: *"I didn't find any [auth / search / email / cache] configuration in the files — are you using anything for those?"*

##### Path: Clone git repo

1. *"What's the git repo URL?"*
2. Folder state check: same two branches as above (files found vs. empty).
3. Clone via `git clone <url> .`. If folder isn't empty, clone into a temp directory and move files after user confirms.
4. Verify clone (same as "Verify codebase arrived" above).
5. Run contamination scan (same as above).
6. Build code graph (same as above — standard/heavy only).
7. Direct codebase scan (same as above).

#### 2C.3: Brief + gap-fill

CoS already has codebase metadata (Path B/C) or migration-export data (Path A). Ask for anything not derivable:

- Name (if not obvious from folder/README)
- One-sentence brief
- Goals (if not in README)
- Success metrics — don't skip
- Constraints
- Stakeholders
- Deadline

Present: *"Based on your codebase/export, here's what I understand: [summary]. What am I missing?"*

#### 2C.4: Auto-.gitignore (if codebase path)

If Path B or C was used and `.git/` exists:
- If `.gitignore` exists, append `project-studio/` if not already present.
- If `.gitignore` doesn't exist, create it with `project-studio/`.

If no `.git/` directory: skip — *"No git repo detected. If you init git later, add `project-studio/` to your .gitignore."*

---

### Step 2D1 — Scenario D1 (Existing + Multi, no parent yet)

#### 2D1.1: Parent mount check (ask first, branches everything else)

*"Can I access the parent folder from this session? The parent folder is the directory that contains all your modules as subfolders."*

- **Yes, the mounted folder is the parent** → Branch A. Full parent architecture active, module-seed handoff available.
- **No, only the primary module's folder is mounted** → Branch B. Cross-module context goes into `project-studio/imports/` instead of parent `shared/`. No module-seed handoff from this session (user will have to open parent separately later).

#### 2D1.2: List all modules (with per-module purpose)

Ask the user what modules make up the product. For **Branch A**, pre-populate the candidate list by scanning subfolders under the mounted parent (skip `.git/`, `node_modules/`, `.claude/`, hidden dirs).

*"I see these candidate module folders: [list]. Tell me the full module list — which of these are modules, and are there any I missed?"*

For **Branch B**, ask the user to list modules from scratch:

*"List every module that makes up this product — e.g. website, API, mobile app, admin dashboard."*

CoS confirms back with a numbered list and asks *"Is that complete?"*.

Then for **each** module in the list, ask the same three micro-questions as 2B.3:

1. **Purpose** — one sentence.
2. **Folder name** — default to the existing subfolder name if in Branch A, otherwise ask.
3. **Active now?** — is this module being worked on right now, or is it just on the manifest for future work?

Hold `module_inventory[]` in setup context.

#### 2D1.3: Pick the primary module

*"Which module should this session focus on first? After parent setup completes, I'll hand you off to open a new session at that module folder and continue from there."*

The primary is the one the handoff block at the end of Step 7 will point to. For Branch B, the primary module is whichever module folder is actually mounted (there's only one option).

#### 2D1.4: Per-module intake (codebase scan vs. context extract)

##### Branch A (parent mounted): per-module, module by module

For **each active module** in `module_inventory[]`:

1. **Folder state check** — does the module subfolder already contain code?
   - **Yes, code present** → treat it like Scenario C "Bring in local codebase" for that module: verify, contamination scan (see `references/contamination-checklist.md`), direct codebase scan limited to that subfolder. No pre-built code graph — graphify is loaded per specialist spawn (see `references/invokable-skills.md`).
   - **No, empty** → ask *"Should I clone a git repo into [module], extract context from another session, or skip this module for now?"* Process per user choice.
2. Record the per-module infrastructure findings in `module_inventory[module].infrastructure_findings`. These get written to `project-studio/project/infrastructure/<module>.md` during Step 7.
3. **Do not walk into sibling modules' subfolders during the scan of module X.** Each module's scan is confined to its own folder. This is important for contamination discipline.

For **inactive modules**, skip the codebase scan entirely — just record folder name + purpose in the manifest.

##### Branch B (module-only mount): single-module scan + sibling stubs

1. **Intake for the primary module (the mounted folder):** Same as Scenario C — bring in local codebase or clone. Folder state check, verify, contamination scan, direct codebase scan. No pre-built code graph — graphify loads per spawn (see `references/invokable-skills.md`).
2. **For each non-primary module,** ask: *"How should [module] come in? Extract context only (migration-export from another session → lands in imports/), or just record the name on the manifest and skip?"*
3. Record all findings on the `module_inventory[]`.

#### 2D1.5: Product-wide brief + per-module brief gap-fill

CoS gathers **two layers** of brief:

1. **Product-wide brief** (one) — name, one-sentence product brief, overall goals, success metrics, constraints, stakeholders, deadline. Same fields as 2A.1, framed at the product level.
2. **Per-module brief** (one per active module) — for each active module, confirm the one-sentence purpose from 2D1.2 and ask for any module-specific goals, metrics, constraints, or deadlines that differ from product-wide. If a module has nothing beyond product-wide context, its brief is just the purpose line.

Present back: *"Here's what I understand. Product: [product brief]. Modules: [per-module briefs]. Anything missing?"*

#### 2D1.6: Auto-.gitignore

- Branch A: Add `*/project-studio/` and `shared/` to parent's `.gitignore` if parent has `.git/`. For each module with its own `.git/`, add `project-studio/` to that module's `.gitignore`.
- Branch B: Add `project-studio/` to the primary module's `.gitignore`.

#### 2D1.7: Hand off to Step 2.5 (context sort & cleanup)

**D1 projects almost always have stray context files scattered around:** old READMEs, draft plans, random notes, brand assets, old agent transcripts. Before Step 3 runs, route into **Step 2.5 — Context Sort & Cleanup** to classify and organise them.

---

### Step 2D2 — Scenario D2 (Existing + Multi, parent exists)

#### 2D2.1: Verify parent structure

CoS reads the existing parent `CLAUDE.md` and confirms it's a valid Project Studio parent manifest: has a module table, has a `shared/` directory alongside the manifest.

If the existing `CLAUDE.md` is NOT a Project Studio parent manifest (e.g., it's a regular codebase CLAUDE.md), escalate: *"The parent folder has a CLAUDE.md but it doesn't look like a Project Studio parent manifest. Do you want me to treat this as D1 (create a new parent manifest, which will rename the existing CLAUDE.md to CLAUDE.md.old so nothing is lost) or abort?"*

#### 2D2.2: Read existing parent manifest

Load the list of sibling modules from the parent table. Read the communication files in `shared/` (`bus.md`, each `<module>-outbox.md`) to understand current cross-module state. These existing files define the bus layout — new modules must fit into the same shape.

Load existing `shared/brand/`, `shared/docs/`, `shared/conventions/`, `shared/data/` if present (parent-level shared assets — see `references/parent-module-handoff.md`).

#### 2D2.3: Confirm the new module(s)

*"I see the parent has [sibling modules]. What modules are you adding? One at a time, or a batch?"*

For each new module, run the same three micro-questions as 2B.3: purpose, folder name, active-now. Verify each new module's folder is a subfolder of the parent.

Hold `new_modules[]` plus `existing_modules[]` (read from parent) as the effective `module_inventory[]`.

#### 2D2.4: Intake for the new module(s)

Per new module, same as Scenario C:
- Folder state check → bring in local codebase OR clone git repo OR empty (future work).
- Verify + contamination scan (confined to the module's own subfolder).
- Do NOT pre-build a code graph. Graphify loads per spawn at standard/heavy scale (see `references/invokable-skills.md`). Empty future-work modules require nothing at intake.
- Direct codebase scan.
- **Do not touch sibling modules' subfolders.** Contamination discipline from `references/multi-project.md` rule 8.

#### 2D2.5: Sibling context sync (from parent shared → local)

For each new module, pull context from parent-level shared files into the module's `project-studio/shared/`:

- Copy product-wide brief from parent `shared/brief.md` (if exists).
- Write a **`shared-index.md`** (not a copy) that points into parent-level shared assets via relative paths. See `references/parent-module-handoff.md` §shared-assets. This index lists parent shared resources without duplicating them.
- Copy the current state of the bus summary (last 20 bus entries) into `project-studio/shared/bus-snapshot.md` as a one-time bootstrap.
- Set `last-sync-timestamp` to now.

#### 2D2.6: Per-module brief gap-fill (product brief is already known)

The product-wide brief is already loaded from parent `shared/brief.md`. Ask only for each new module's module-specific brief (purpose, module goals, module metrics, module constraints, module deadline).

#### 2D2.7: Parent manifest update plan

Plan the update to parent `CLAUDE.md`: add a row per new module to the module table. For each new module, plan to create `shared/<module>-outbox.md` (empty, seeded with the template header). Don't execute — Step 7 writes.

#### 2D2.8: Team-setup scope decision

*"This parent already has teams for [existing modules]. Do you want me to:*
- *(a) Only set up teams for the new module(s)?*
- *(b) Review the existing parent-level team for promotion conflicts before I add new module teams?*
- *(c) Do a full matrix review across all modules?"*

Option (a) is the default fast path. Options (b) and (c) bring in `references/conflict-resolution.md` during Step 3.

#### 2D2.9: Auto-.gitignore

Add `project-studio/` to each new module's `.gitignore` (if module has its own `.git/`). Parent-level `.gitignore` should already include `*/project-studio/` and `shared/` from the original parent creation — verify, and add if missing.

#### 2D2.10: Hand off to Step 2.5 (context sort & cleanup)

**D2 projects may have stray context from before parent setup or from sibling-leakage.** Route into **Step 2.5** limited to the new module folders (sibling modules are untouchable) plus parent-level stray files (NOT `shared/` — that's already Project Studio territory).

---

## Step 2.5 — Context Sort & Cleanup (D1 + D2 only)

**Runs only for Scenarios D1 and D2 with parent access.** Skip entirely for A, B, C, and for D1/D2 without parent access (no parent = nothing to sort at parent level).

**Purpose:** Existing multi-module parents collect stray context over time — old READMEs, draft plans, random notes, brand assets, old agent transcripts, PDFs. These need to be classified, routed into the right module or parent-shared bucket, and stray Claude-legacy files need to be hard-deleted before boot protocol runs. Otherwise CoS will later read them as directives and hallucinate.

Full heuristics in `references/classifier-rules.md`. This step is the wizard flow that uses those rules.

### 2.5a. Scope the scan

CoS walks the tree **rooted at the parent folder** (D1) or the parent folder excluding existing sibling modules (D2). The walker respects a skip list:

```
.git, node_modules, venv, dist, build, target, __pycache__, .cache, .claude, .project-studio
```

For D2, also skip the subfolders of existing (non-new) modules — those are sibling territory and CoS must not read into them.

CoS presents the scan scope to the user: *"I'll walk these folders and classify every file: [parent root], [new module folders], [skip list]. Binary blobs and code directories will be skipped. OK?"*

### 2.5b. Classify files into 4 tiers

Every eligible file gets slotted into exactly one tier via the heuristics in `references/classifier-rules.md`:

- **Tier 1 — high confidence** — the heuristic rule fired cleanly. Example: `thekedar-homepage.md` with the token `thekedar` matching an active module name → module `thekedar`. File is routed automatically.
- **Tier 2 — medium confidence** — the heuristic matched but with weaker signal (e.g., filename hint only, or content hint only). Routed automatically but flagged for batch review.
- **Tier 3 — ambiguous** — no heuristic fired, or multiple heuristics conflicted. Shown to the user one at a time.
- **Tier 4 — cleanup candidates** — matched the cleanup pattern list (stray root `CLAUDE.md`, `roadmap*.md`, `TODO.md`, `*.draft.md`, `*old*`, agent transcript patterns, etc.). Flagged for hard delete.

### 2.5c. Present batch decision card

CoS presents ONE summary card per scan, not one card per file. The card shows:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Context Sort Results — <N> files classified
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tier 1 (high confidence) — <A> files
  → module:auth            <count>
  → module:payments        <count>
  → parent/shared/brand    <count>
  → parent/shared/docs     <count>

Tier 2 (medium confidence) — <B> files
  (sample: first 5 lines)
  auth-flow.md           → module:auth (filename hint)
  pricing-draft.md       → module:payments (content hint: "Stripe")
  ...

Tier 3 (ambiguous) — <C> files
  (will ask one by one)

Tier 4 (cleanup candidates) — <D> files
  root/CLAUDE.md                (stray parent CLAUDE.md)
  roadmap-v2.md                 (pattern: roadmap*.md at root)
  ai-transcript-2025-11.md      (agent transcript pattern)
  ...
```

Followed by an `AskUserQuestion`:

*"How do you want to handle this?"*

1. **Apply Tier 1 + Tier 2 as suggested, review Tier 3 one by one, confirm Tier 4 for hard delete** (recommended, batch path)
2. **Apply Tier 1 only, review Tier 2 + Tier 3 individually, skip Tier 4 cleanup for now**
3. **Review everything file-by-file** (slowest, safest)
4. **Cancel sort — just let me organise manually later**

Option 1 covers the 70% fast path where heuristics are good. Option 2 is for users who want more control. Option 3 is a last resort. Option 4 lets the user punt (CoS then proceeds to Step 3 without routing any files — the stray files stay where they are, but CoS adds an open question *"[N] unsorted stray context files remain — review later"* to the register).

### 2.5d. Execute Tier 1 + Tier 2 routes (if option 1 or 2)

Move files to their classified destinations **inside the parent tree**:

- `module:<name>` → move to `<parent>/<module-folder>/project-studio/imports/legacy/<original-path>` (note: imports, not project/). This keeps the legacy content read-only and traceable.
- `parent/shared/brand` → move to `<parent>/.project-studio/shared/brand/`.
- `parent/shared/docs` → move to `<parent>/.project-studio/shared/docs/`.
- `parent/shared/data` → move to `<parent>/.project-studio/shared/data/`.
- `parent/shared/conventions` → move to `<parent>/.project-studio/shared/conventions/`.

Note: **parent-level shared files live under `.project-studio/shared/`, not the parent-root `shared/`.** The parent-root `shared/` is reserved for communication files (bus.md, outboxes). This separation is critical — see `references/parent-module-handoff.md` §layout.

Log every move in a `sort-log.md` file at the parent level: `(source path) → (destination path) → (tier + reason)`.

### 2.5e. Resolve Tier 3 (ambiguous) one by one

For each Tier 3 file, CoS shows:

```
File: <path>
Size: <bytes> | Modified: <date>
Content preview (first 30 lines):
<preview>

Possible routes:
1. module:<name1>
2. module:<name2>
3. parent/shared/docs
4. parent/shared/brand
5. Leave where it is
6. Hard delete (this looks stale)
```

`AskUserQuestion` with those options. Apply the user's choice, log in `sort-log.md`, continue. If the user says "Apply this choice to the rest of Tier 3 if they're similar", CoS batch-applies to any Tier 3 file whose classifier signature matches.

### 2.5f. Confirm Tier 4 cleanup (hard delete)

CoS lists every Tier 4 file with a one-line reason per file:

```
Hard-delete list (these will be permanently removed, not archived):
  ./CLAUDE.md                        stray legacy file from pre-Project-Studio setup
  ./roadmap-v2.md                    stray roadmap at parent root (will be replaced by project-studio/project/roadmap.md)
  ./TODO.md                          stray todo file
  ./ai-transcript-2025-11.md         agent transcript (could be re-read as directive)
  ./NOTES.draft.md                   draft note pattern
  (N total)
```

`AskUserQuestion`:

*"Delete all N files?"*

1. **Yes, delete all** (recommended for clean boot protocol)
2. **Let me review one by one** (falls through to per-file yes/no)
3. **Skip cleanup for now** (files remain — boot protocol might still read and act on them; CoS adds a warning to the open-questions register)

**Hard delete, not archive.** The rationale: an archive folder inside parent still gets scanned by CoS on boot (it lives within the managed tree) and can cause hallucinated directives. Hard delete prevents that entirely. If the user wants a backup, they should copy the folder to somewhere OUTSIDE the parent before running the sort — CoS reminds them: *"I'm about to hard-delete N files. If you want a backup, copy them out of [parent path] first. Say 'yes delete' to proceed."*

### 2.5g. Close the sort

Write `sort-log.md` to `<parent>/.project-studio/sort-log-YYYY-MM-DD.md` so the audit trail survives. Announce: *"Sort complete. [A] files routed to modules, [B] files routed to parent shared, [C] files deleted. Log saved to sort-log-YYYY-MM-DD.md."*

Continue to Step 3.

---

## Step 3 — Team Setup

**Universal across all scenarios.** After Step 2, CoS knows the project brief, goals, constraints, scenario, scale, and (for existing projects) the codebase and infrastructure. Now build the team.

**Parent vs. single split:** For scenarios A and C, Step 3 runs as **single-project mode** (one team, the existing flow below). For scenarios B, D1, and D2 with parent access, Step 3 runs in **matrix mode** — Phase 3A sets up a parent-level team, Phase 3B sets up per-module teams, with a matrix view showing which personas are cross-module (shared) vs. module-specific. See the "Matrix mode" subsection at the end of Step 3.

### Hard rules for Step 3

1. **Every persona must be presented to the user with its assigned skill menu clearly visible before it is considered confirmed.** The skill list is not optional detail buried in a spawn-context block — it is surfaced as its own clearly labeled section in the presentation.
2. **The user must be given an explicit chance to edit the skill assignment for every persona, even if they say nothing about skills.** Do not assume silence = approval of the skills. Ask directly: "Keep these skills as-is, or add/remove/swap any?"
3. **Do not write persona files to disk until the user has explicitly approved both the persona body AND its skill list.** Both gates must pass, per persona.
4. **Apply user skill edits literally.** If the user says "drop jobs-to-be-done, add pricing-strategy", update the skill menu in context before moving to the next persona. Do not argue or re-suggest unless the edit creates an obvious conflict (e.g., the skill doesn't exist in `references/skill-catalog.md`).
5. **If the user adds a skill not in `references/skill-catalog.md`,** surface this ("That one's not in the catalog — want me to add it anyway, or pick the closest match?") but defer to the user's choice.

### 3a. Suggest an archetype

Based on the project type and brief, recommend a team archetype from `references/team-archetypes.md`. Present it as a starting point, not a prescription.

*"Based on what you've described, I'd suggest the **[Archetype Name]** team:"*

Show each specialist: Name, Role, Domain, 2-3 example skills.

**Light-scale override:** Suggest exactly 1 specialist (the single most relevant role) + optional critic. Skip the archetype presentation — just propose one persona directly.

### 3b. User selects and customizes

Present using `AskUserQuestion` (multi-select with "Add custom" option):

*"Which specialists do you want? You can keep, remove, rename, or add your own."*

### 3c. Generate persona files (generate-then-confirm, two-gate approval)

For each confirmed specialist, run this two-gate loop. Do **not** move to the next persona until both gates pass for the current one.

#### 3c.1 — Draft the persona body

Generate per `references/persona-schema.md`: Role, Background (2-3 sentences grounded in the project domain), Principles (3-5 specific, falsifiable beliefs), Obsession (one sentence — the lens for critique), Domain (what roadmap areas they own), Critique mode, Tone.

#### 3c.2 — Assign the skill menu

Pick 5-8 skills from `references/skill-catalog.md`, biased toward the persona's role and the project's specific needs. The persona will load only 1-3 per task (lazy-loading discipline).

#### 3c.3 — Present the persona with skills clearly displayed (MANDATORY)

Show the full spawn-context block as one block, AND immediately after it, show the skill menu again as its own clearly labeled section, like this:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [Name] — [Role]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Role: [Role title]

Background: [2-3 sentences]

Principles:
- [principle 1]
- [principle 2]
- ...

Obsession: [one sentence]

Domain: [what they own]

Critique mode: [how they challenge ideas]

Tone: [tone description]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Skills assigned to [Name] ([count])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [skill-1] — [one-line what it's for]
2. [skill-2] — [one-line what it's for]
3. [skill-3] — [one-line what it's for]
4. [skill-4] — [one-line what it's for]
5. [skill-5] — [one-line what it's for]
(optional 6-8 if relevant)
```

The skill section is **mandatory** — never skip it, never summarize it as "standard PM skills" or similar. Always enumerate with the exact skill names as they appear in `references/skill-catalog.md`, plus a brief per-skill purpose so the user can judge relevance.

#### 3c.4 — Gate 1: persona body approval

Ask: *"Does [Name]'s role, background, principles, and tone look right? Anything to adjust about who they are?"*

Wait for the user to answer. Apply any edits (background phrasing, principles, tone, etc.) before moving on. If no edits, confirm "Locked in [Name]'s persona body" and proceed to Gate 2.

#### 3c.5 — Gate 2: skill menu approval (MANDATORY, always ask even if the user said "looks good")

Use `AskUserQuestion` (or a numbered list in CLI mode):

*"Keep [Name]'s skill list as-is, or edit it?"*

Options:
1. **Keep as-is** — ship the 5-8 skills shown above.
2. **Add skills** — user names additional skills to append.
3. **Remove skills** — user names skills to drop.
4. **Swap skills** — user names one skill to remove and one to add.
5. **Replace entirely** — user gives a new list from scratch.

Apply the edits in context. Re-display the final skill list and ask: *"Final skill list for [Name]. Confirm?"* Wait for confirmation.

**You must ask Gate 2 even if the user only said "looks good" or "approved" at Gate 1.** "Looks good" is not implicit skill approval. Ask explicitly.

#### 3c.6 — Move to the next persona

Only after both gates pass for persona N, move to persona N+1 and repeat 3c.1 through 3c.5.

**Don't write persona files to disk yet.** Hold all approved personas in context. All file writes happen atomically in Step 7.

### 3d. Gap check

*"Your team covers [domains]. I notice there's no one owning [gap] — intentional?"*

Common gaps: SEO/analytics, copywriting/brand, testing/QA, project tracking, security.

---

### Step 3 — Matrix mode (B, D1, D2 with parent access)

When the scenario is B, D1, or D2 **and** parent folder is accessible, Step 3 runs in matrix mode instead of the single-project flow above. All rules from 3a-3d still apply per persona (two-gate approval, skill menu, gap check) — matrix mode just changes *how many teams* get built and *how they're scoped*.

#### 3m.1 — Persona scope field

Every persona in matrix mode carries a new field:

```yaml
scope: parent | shared | module:<module-slug>
```

- **parent** — operates only at the product/parent level. Owns product-wide vision, cross-cutting strategy, business outcomes. Not scoped to any one module. Example: a Product Lead who owns the overall roadmap and cross-module prioritisation.
- **shared** — active across 2+ modules. Travels with the shared persona mechanism (see `references/persona-schema.md` §scope-and-overrides). Each module that consumes a shared persona can add a per-module `persona-overrides.yaml` entry that tweaks the tone, principles, or skill menu for that module's use — without rewriting the source persona.
- **module:<slug>** — scoped to exactly one module. Lives in that module's `team/` folder only.

#### 3m.2 — Phase 3A: Parent-level team

CoS suggests a small parent-level team (typically 1-2 personas):

- A **Chief of Staff** persona scoped to `parent`. This CoS coordinates across modules, runs the sync command (see `references/module-communication.md`), owns promote-to-parent decisions, and maintains the parent manifest. Every parent has exactly one parent CoS.
- Optionally a **Product Lead / Strategist / Founder** scoped to `parent` for product-wide strategy.

Run the two-gate approval loop (3c.1-3c.6) for each parent-level persona.

#### 3m.3 — Phase 3B: Per-module teams (iterate by active module)

For each **active** module in `module_inventory[]` (inactive modules are skipped — they get teams later when they become active), run a scoped team setup:

1. **Suggest a module-level archetype** — based on the module's purpose, pick from `references/team-archetypes.md`. This is the "team archetype for just this module."
2. **Ask: does any parent-scoped persona need a per-module variant here?** — e.g., maybe the Product Lead wants to show up in the payments module but with different skills. If yes, draft it as a `shared` scope with a `persona-overrides[payments]` block.
3. **Draft module-specific personas** — role, background, principles, obsession tied to the module domain. Scope = `module:<slug>`.
4. **Run the two-gate approval loop** for every persona (body + skills), per `references/persona-schema.md`.

#### 3m.4 — Present the team matrix before locking

After every module's team is drafted, present a **matrix view**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Team Matrix — <product name>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

               │ parent │ auth │ payments │ admin │
───────────────┼────────┼──────┼──────────┼───────┤
Priya (CoS)    │   ●    │      │          │       │  scope: parent
Aisha (PM)     │   ●    │  ○   │    ○     │   ○   │  scope: parent, shared to all
Ravi (Eng)     │        │  ●   │          │       │  scope: module:auth
Maya (Eng)     │        │      │    ●     │       │  scope: module:payments
Sam (Design)   │        │  ○   │    ○     │       │  scope: shared (auth+payments)
Jo  (QA)       │        │      │          │   ●   │  scope: module:admin

●  = primary owner      ○  = consulted / shared
```

The matrix makes three things immediately visible:

- Every module has at least one primary owner (●). If a column has no ●, flag it.
- Shared personas (○) show where cross-module coupling exists.
- Parent row should be small — typically 1-2 personas.

#### 3m.5 — Matrix gap check

Before locking, run a gap check across the matrix:

- Every active module has ≥1 primary owner. (Blocker if not.)
- Product-wide domains (brief, roadmap priorities, cross-module blockers) have a parent or shared owner. (Warning if not.)
- No persona is primary-owning >2 active modules. (Warning — likely overloaded.)
- The parent team is ≤2 personas for light/standard, ≤3 for heavy. (Warning if larger — parent should be thin.)

Present flags to the user and ask for fixes.

#### 3m.6 — Persona overrides for shared personas (optional)

For any `shared` scope persona, ask: *"Do you want [Name] to behave the same across all modules, or should their principles/tone/skills be tweaked per module?"*

If tweaks are wanted, draft a `persona-overrides.yaml` block. The base persona file stays in the parent `team/` folder; each module's local override lives in that module's `team/persona-overrides.yaml`. See `references/persona-schema.md` §scope-and-overrides for the full override schema.

#### 3m.7 — Hold all personas in context, do not write yet

Same as 3c.6 — personas are held in setup context, written atomically in Step 7.

---

## Step 4 — Roadmap Planning

**This is a team job.** Specialists can now be spawned as sub-agents to contribute to roadmap planning.

### 4a. Gather roadmap inputs

CoS already has: brief, goals, metrics, constraints, deadline (Step 2), team roster (Step 3), and for existing projects: codebase scan, infrastructure, imported context.

**If imported roadmap exists** (from migration-export): load as reference input.

### 4b. First draft (CoS + specialist collaboration)

CoS spawns the relevant specialists (typically: PM/Product Lead + any specialist who owns a major domain) via Agent tool with a roadmap-planning prompt. Each specialist proposes milestones and tasks. CoS consolidates using `templates/roadmap.md.tmpl`.

Structure: Phase > Milestone (owner-tagged) > Atomic tasks.

**For existing projects with imported roadmaps:** Specialists run a **Roadmap Import Review** — for each imported item, recommend: Keep / Adapt / Drop / New. Present review before folding into draft.

### 4c. Priority + timeline check

*"Here's the proposed roadmap. For Phase 1, [PM name] prioritized [X] over [Y] because [reason]. Does this order feel right?"*

If deadline exists: *"This roadmap [fits / is tight / is overcommitted by N milestones] against your [date] deadline."*

### 4d. User confirms

Present full roadmap. User approves or adjusts. Iterate until confirmed. **Don't write to disk yet.**

### Scale variations

| Scale | Phases | Milestones | Tasks | Specialist involvement |
|---|---|---|---|---|
| Light | 1 | 1-3 | 2-5 total | 1 specialist contributes |
| Standard | 2-3 | 2-5 per phase | Full detail | Full team contributes |
| Heavy | 3-4 | 2-5 per phase | Full + dependencies noted | Full team + detailed task breakdown |

---

### Step 4 — Two-tier mode (B, D1, D2 with parent access)

When the scenario is B, D1, or D2 with parent access, Step 4 produces a **two-tier roadmap** instead of a single roadmap. Tier 1 lives at the parent level (product-wide milestones owned by the parent team). Tier 2 lives at each active module (per-module roadmap owned by that module's team). The tiers are linked but not collapsed.

#### 4t.1 — Build Tier 1 (parent milestones)

CoS spawns the parent-level team (usually parent CoS + Product Lead, if present). Prompt them to produce 3-8 product-wide milestones that:

- Represent **product outcomes**, not module-specific tasks. Example: "Product launches publicly," "Payments live end-to-end," "Admin dashboard in alpha with 5 users."
- Are **cross-cutting** or **coordination-level** — a parent milestone typically requires work in ≥2 modules, or it's a parent-only milestone (brand launch, fundraising round, compliance audit).
- Each milestone carries a `feeds_from` field listing the modules that must contribute work to land it. Example: *"Payments live end-to-end — feeds_from: payments, auth, admin"*.

Present: *"Here are the parent milestones Priya and the product lead drafted. For each one, here's which modules need to contribute. Look right?"*

#### 4t.2 — Build Tier 2 (per-module roadmap) for each active module

For each active module in the inventory:

1. Spawn that module's team (the personas scoped `module:<slug>` plus any `shared` personas).
2. Generate the module's roadmap as normal (phases, milestones, atomic tasks). Same structure as single-mode.
3. Each module milestone carries a `rolls_up_to` field — which parent milestone(s) does this module milestone contribute to? If a module milestone rolls up to none, flag it as "module-local" (that's fine, just labeled).
4. Present per module, confirm, move to next.

#### 4t.3 — Reconciliation pass

After Tier 1 + every Tier 2 is drafted, run a reconciliation pass:

- **For each parent milestone in Tier 1, verify its `feeds_from` modules each have ≥1 Tier 2 milestone that `rolls_up_to` it.** If a parent milestone has zero contributing module milestones, flag it — either the parent milestone is premature, or a module is missing a milestone.
- **For each Tier 2 milestone with no `rolls_up_to`, confirm with the user that it's intentionally module-local.** Most module milestones should feed a parent milestone; pure module-local ones are rare and worth pausing on.
- **Deadline check across tiers** — parent milestone deadlines must be ≥ the latest deadline of their contributing Tier 2 milestones.

Present flags, iterate with the user, lock the two-tier roadmap.

#### 4t.4 — Hold in context, write in Step 7

Same discipline as single-mode — no file writes yet. Step 7 writes:
- `parent/project-studio/roadmap.md` wait — there is no parent `project-studio/`. Parent-level roadmap lives in the parent CLAUDE.md (the data-only manifest) **or** in `.project-studio/shared/roadmap.md`. See `references/parent-module-handoff.md` §parent-roadmap for the exact file location.
- `<module>/project-studio/project/roadmap.md` — per-module roadmap (normal location).

---

## Step 5 — Connectors & Plugins

Suggest MCP connectors and plugins **driven by what the roadmap needs.** See `references/connectors.md` for full logic.

### 5a. Identify connector needs from roadmap

CoS scans the confirmed roadmap for tasks that imply external tool access:
- Design review → Figma connector
- Issue tracking → Linear/GitHub
- Research → Tavily/Firecrawl
- Content management → Notion
- Standard/heavy scale → scheduled-tasks for automated retros

### 5b. Search and suggest

Use `mcp__mcp-registry__search_mcp_registry` and `mcp__plugins__search_plugins` with project-type keywords. Present in three tiers:
- **Strongly suggested** (roadmap tasks depend on these)
- **Optional but useful**
- **Skip unless needed**

### 5c. User selects

*"Reply with which to install (or 'skip all')."*

For each installed connector: run identity probe (see `references/connectors.md`), capture stable ID + human handle. Hold for writing to CLAUDE.md in Step 7.

### 5d. Schedule recurring tasks (standard/heavy only)

Suggest milestone-triggered retro automation via `mcp__scheduled-tasks__create_scheduled_task` (see v3.1 addition below and Invariant #22 — the scheduled task fires only if the current milestone deadline has passed without a retro being filed; it does NOT default to a weekly cadence). For heavy: also suggest a monthly strategic review that reads all registers.

### Scale override

**Light-scale:** Skip Step 5 entirely unless user asks. No scheduled tasks.

---

## Step 6 — Setup Review

**Light-scale: Skip this step entirely.** Go directly to Step 7.

For standard and heavy: one review pass before any files are written.

### 6a. Consistency check

| Check | What could be wrong |
|---|---|
| Brief ↔ Roadmap | Goal not represented in any milestone. Roadmap task not serving any stated goal. |
| Team ↔ Roadmap | Milestone without owner. Specialist without any milestones. One specialist owns >50% of work. |
| Skills ↔ Tasks | Specialist assigned to task outside their skill range. |
| Constraints ↔ Plan | Roadmap exceeds deadline. Task requires tech/budget not available. |
| Connectors ↔ Tasks | Roadmap task requires data source with no connector installed. |
| Imports ↔ Assumptions (D1/D2) | Cross-module dependency assumed but not documented. |
| Parent ↔ Module (B/D1/D2) | Module registered in parent manifest. Shared context synced. |

### 6b. Seed registers

From all context gathered, CoS identifies initial entries for:
- **Assumptions** — what the plan bets on
- **Risks** — what could derail the project
- **Open questions** — what hasn't been answered

**Light-scale:** Merge into `notes.md` — 3-5 bullets max.

### 6c. Present review summary

```markdown
## Setup Review

**Brief:** [one sentence]
**Scenario:** [A/B/C/D1/D2]
**Scale:** [light/standard/heavy]
**Team:** [names + roles]
**Connectors:** [list or "none"]
**Roadmap:** [N phases, M milestones, K tasks] — deadline fit: [yes/tight/over/none]

**Consistency flags:**
- [issues found, or "None — clean"]

**Initial registers:**
- [N] assumptions, [N] risks, [N] open questions

**Everything look good? Say "yes" to build, or tell me what to change.**
```

User confirms. Loop until approved.

---

## Step 7 — Build Project

Write everything to disk atomically. **CLAUDE.md is written last** — its existence = "setup complete."

### 7a. Scaffold folder structure

**Exact invocation** (run from the mounted folder — the project root):

```bash
python3 <skill-path>/scripts/init_project.py --root . --scale <light|standard|heavy> --skill-path <skill-path>
```

Concrete example (Scenario A, standard scale, skill installed at `~/.claude/skills/project-studio`):

```bash
python3 ~/.claude/skills/project-studio/scripts/init_project.py --root . --scale standard --skill-path ~/.claude/skills/project-studio
```

The script has no required positional argument — the scaffold folder name defaults to `project-studio`, which is the convention. Do NOT pass a project name.

**Postflight assertion** (CoS runs this before moving on to 7b):

```bash
test -d ./project-studio/protocol && test -f ./project-studio/protocol/boot.md && test -f ./project-studio/registers/assumptions.md && echo "scaffold OK" || echo "SCAFFOLD FAILED - halt and report"
```

If the assertion prints `SCAFFOLD FAILED`, halt Step 7 and tell the user what's missing. Do not proceed to 7b with a partial scaffold.

**Python-less fallback (common in Cowork mode).** If `python3` or the workspace bash tool is unavailable, scaffold the identical structure using the Write tool directly — read `scripts/init_project.py` to see the exact directories, seed file contents, and protocol-file list. Both paths produce byte-equivalent output. **Do not skip scaffolding because Python is missing.**

**Multi-module note:** `init_project.py` scaffolds a single module's internal structure (protocol/, team/, project/, registers/, etc.). For Scenario B/D1/D2, run it once per active module from that module's folder. The **parent-level files** — communication layer (`shared/bus.md`, `shared/<module>-outbox.md`), state layer (`.project-studio/shared/`, `.project-studio/team/`), module seeds, shared-index, and START-HERE — must be written separately via the Write tool per Steps 7f and 7g. init_project.py does not handle these.

The structure depends on the scenario locked in Step 1.

**Scenario A — New + Single:**
```
./                              ← mounted folder
├── CLAUDE.md                   ← module CLAUDE.md (sole source of truth)
└── project-studio/             ← all management files
    ├── protocol/
    ├── team/
    ├── project/
    │   └── infrastructure/
    │       └── shared/
    ├── registers/
    ├── decisions/
    ├── log/
    ├── checkpoints/
    ├── retros/
    ├── imports/
    └── archive/
```

**Scenario B — New + Multi (parent architecture):**
```
./                              ← mounted folder (parent)
├── CLAUDE.md                   ← parent CLAUDE.md (data-only manifest)
├── shared/                     ← communication layer
│   ├── bus.md                  ← routed-message archive (from bus.md.tmpl)
│   ├── module1-outbox.md       ← module1 outgoing queue (from outbox.md.tmpl)
│   └── module2-outbox.md       ← module2 outgoing queue
├── .project-studio/            ← parent state layer
│   ├── shared/                 ← briefs, roadmap, brand, docs, conventions, data
│   └── team/                   ← parent-scoped + shared personas
└── module1/                    ← primary module
    ├── CLAUDE.md               ← module CLAUDE.md
    └── project-studio/
        ├── shared/
        │   └── shared-index.md ← index of parent shared assets (from template)
        ├── inbox.md            ← incoming messages (from inbox.md.tmpl)
        ├── outbox-staging.md   ← local draft queue (from outbox.md.tmpl staging)
        ├── protocol/
        ├── team/
        │   └── persona-overrides.yaml  ← per-module persona tweaks (if any)
        └── ...
```

**Scenario B without parent access (Cowork mounted at module level):** Same layout as Scenario A. Cross-module context lives in `project-studio/imports/` instead of parent `shared/`.

**Scenario C — Existing + Single:**
```
./                              ← mounted folder (has existing codebase)
├── CLAUDE.md                   ← module CLAUDE.md (NEW)
├── .gitignore                  ← updated with "project-studio/"
├── project-studio/             ← NEW — alongside existing code
│   ├── protocol/
│   ├── team/
│   ├── project/
│   │   └── infrastructure/     ← populated from codebase scan
│   ├── registers/
│   ├── imports/
│   └── ...
├── src/                        ← existing (untouched)
├── package.json                ← existing (untouched)
└── ...
```

**Scenario D1 — Existing + Multi, parent doesn't exist yet:**
```
./                              ← mounted folder (parent)
├── CLAUDE.md                   ← parent CLAUDE.md (NEW — data-only)
├── shared/                     ← NEW — communication layer
│   ├── bus.md                  ← routed-message archive (from bus.md.tmpl)
│   ├── module1-outbox.md       ← module1 outgoing queue (from outbox.md.tmpl)
│   └── module2-outbox.md       ← module2 outgoing queue
├── .project-studio/            ← NEW — parent state layer
│   ├── shared/                 ← briefs, roadmap, brand, docs, conventions, data
│   └── team/                   ← parent-scoped + shared personas
└── module1/                    ← primary module (existing codebase)
    ├── CLAUDE.md               ← module CLAUDE.md (NEW)
    ├── .gitignore              ← updated
    ├── project-studio/         ← NEW
    │   ├── shared/
    │   │   └── shared-index.md ← index of parent shared assets
    │   ├── inbox.md            ← incoming messages (from inbox.md.tmpl)
    │   ├── outbox-staging.md   ← local draft queue (from outbox.md.tmpl staging)
    │   ├── team/
    │   │   └── persona-overrides.yaml
    │   ├── imports/
    │   └── ...
    ├── src/                    ← existing
    └── ...
```

**Scenario D2 — Existing + Multi, parent already exists:**
```
./                              ← mounted folder (parent — already has CLAUDE.md)
├── CLAUDE.md                   ← parent CLAUDE.md (UPDATE — add new module to table)
├── shared/                     ← EXISTS — communication layer
│   ├── bus.md                  ← EXISTS
│   ├── module1-outbox.md       ← EXISTS (sibling)
│   └── module3-outbox.md       ← NEW (this module's outgoing queue)
├── .project-studio/            ← EXISTS — parent state layer
│   ├── shared/
│   └── team/
├── module1/                    ← sibling (DO NOT TOUCH)
└── module3/                    ← this module
    ├── CLAUDE.md               ← module CLAUDE.md (NEW)
    ├── project-studio/         ← NEW
    │   ├── shared/
    │   │   └── shared-index.md ← index of parent shared assets
    │   ├── inbox.md            ← incoming messages
    │   ├── outbox-staging.md   ← local draft queue
    │   ├── team/
    │   │   └── persona-overrides.yaml
    │   └── ...
    └── ...
```

**D1/D2 without parent access (Cowork at module level):** Same as Scenario C + imports.

### 7b. Write project files (in order)

**Template handling:** Files in `templates/` use `{{PLACEHOLDER}}` syntax. These are reference formats — `init_project.py` does NOT interpolate them. CoS reads the template, mentally replaces each `{{PLACEHOLDER}}` with the actual value, and writes the final content using the Write tool. If a placeholder has no value, omit that line entirely.

1. **Protocol files** → `project-studio/protocol/`: `boot.md` (or `boot-light.md` for light), `resume.md`, `invariants.md`.
2. **Team files** → `project-studio/team/`: `chief-of-staff.md`, each specialist persona as `<name-slug>.md`. For multi-module: `persona-overrides.yaml` if any shared persona was customised for this module in Step 3.
3. **Project files** → `project-studio/project/`: `brief.md`, `roadmap.md`.
4. **Infrastructure files** (if applicable) → `project-studio/project/infrastructure/`: per-module files, shared services in `shared/`.
5. **Register files** → `project-studio/registers/`: standard/heavy get `assumptions.md`, `risks.md`, `open-questions.md`, `learnings.md`. Light gets `notes.md`.
6. **Import files** (if applicable) → `project-studio/imports/`: `_manifest.md` and imported slice files.
7. **Shared context** (B/D1/D2 with parent only) → `project-studio/shared/`: `shared-index.md` (from `templates/shared-index.md.tmpl`), `infrastructure.md`, `design-system.md`, `brief.md`, `last-sync-timestamp`.
8. **Log** — Write initial entry to `project-studio/log/<YYYY-MM-DD>.md`.
9. **Checkpoint** — Write `project-studio/checkpoints/checkpoint-0-setup-complete.md`.
10. **Communication files** (B/D1/D2 with parent access only) — **Parent side:** `shared/bus.md` (from `templates/bus.md.tmpl`), `shared/<module-slug>-outbox.md` per active module (from `templates/outbox.md.tmpl` delivery variant). **Module side:** `project-studio/inbox.md` (from `templates/inbox.md.tmpl`), `project-studio/outbox-staging.md` (from `templates/outbox.md.tmpl` staging variant). See Step 7f for details and `references/module-communication.md` for the full mechanism.

### 7c. Write CLAUDE.md files (LAST — order matters)

Module CLAUDE.md must exist before parent references it.

| Scenario | What to write |
|---|---|
| **A (new+single)** | Write `./CLAUDE.md` (module, with instructions). Done. |
| **B (new+multi)** | Write `./module1/CLAUDE.md` (module). Then write `./CLAUDE.md` (parent manifest). |
| **C (existing+single)** | Write `./CLAUDE.md` (module, with instructions). Done. |
| **D1 (existing+multi, no parent)** | Write `./module1/CLAUDE.md` (module). Then write `./CLAUDE.md` (parent manifest). |
| **D2 (existing+multi, parent exists)** | Write `./module3/CLAUDE.md` (module). Then UPDATE `./CLAUDE.md` (add module row + new update file in `shared/`). |
| **B/D1/D2 without parent access** | Write `./CLAUDE.md` (module, same as A/C). No parent file. |

**Module CLAUDE.md** uses `templates/CLAUDE.md.tmpl`. **Parent CLAUDE.md** uses `templates/parent-claude.md.tmpl`.

### 7d. Handle .gitignore (if not already done in Step 2)

For each folder with `.git/`:
- Module root: add `project-studio/` to `.gitignore`.
- Parent root (if applicable): add `*/project-studio/` and `shared/` to `.gitignore`.
- No `.git/`: skip, advise user.

### 7e. Mirror roadmap to TodoList

Sync Phase 1's first milestone to the TodoList widget.

### 7f. Write parent-level extras (B, D1, D2 with parent access only)

**Skip for scenarios A, C, and any scenario without parent mount.**

For parent scenarios, Step 7 writes these additional files on top of 7a-7e:

1. **Parent shared-assets scaffold** → `<parent>/.project-studio/shared/` with four subfolders:
   - `brand/` — logos, icons, fonts, visual identity (seeded with a README pointing to where brand assets should go).
   - `docs/` — architecture docs, API contracts, glossary, shared product docs.
   - `data/` — reference datasets.
   - `conventions/` — coding standards, style guides, naming rules.
   - Any files routed here by Step 2.5 are already placed; the README explains the intent.

2. **Parent-level roadmap** → `<parent>/.project-studio/shared/roadmap.md` — the Tier 1 roadmap from Step 4t.1, with `feeds_from` fields intact.

3. **Parent-level brief** → `<parent>/.project-studio/shared/brief.md` — the product-wide brief (not any module's brief).

4. **Communication files:**
   - `<parent>/shared/bus.md` — empty, seeded with the template header (see `templates/bus.md.tmpl`). This is the routing archive managed by the sync command.
   - `<parent>/shared/<module-slug>-outbox.md` — one per active module, seeded with the outbox template header (delivery variant). This is the module's outgoing queue after sync.
   - Inside each active module's `project-studio/inbox.md` — seeded with the inbox template (see `templates/inbox.md.tmpl`). This is the module's incoming queue.
   - Inside each active module's `project-studio/outbox-staging.md` — seeded with the outbox template header (staging variant, see `templates/outbox.md.tmpl`). This is the module's local draft queue where CoS writes candidate messages during work sessions. Messages here have NOT been sent yet — they are flushed to the parent outbox on sync.
   - See `references/module-communication.md` for the full mechanism.

5. **Parent CLAUDE.md** — written in Step 7c for parent scenarios. It is **data-only** — just the module manifest table, no workflow instructions. Uses `templates/parent-claude.md.tmpl`.

6. **Team files for parent scope:** Parent-scoped personas go in `<parent>/.project-studio/team/`. Shared personas also live here (they're the canonical source), with each module's local override living inside that module's own `team/persona-overrides.yaml`.

### 7g. Write module seeds (B, D1, D2 with parent access only)

For **each active module**, write a **module seed file** that the module-side resume flow (Step 0 → Step 8) reads to hydrate context without re-running the wizard.

1. **`<module-folder>/project-studio/module-seed.yaml`** — structured seed. See `templates/module-seed.yaml.tmpl` for the schema. Includes:
   - Parent project name and absolute path
   - This module's name, slug, purpose, and role in the product
   - Pointer to parent `.project-studio/shared/brief.md` (relative path)
   - Pointer to parent `.project-studio/shared/roadmap.md` (the Tier 1 roadmap)
   - Pointer to the parent shared assets (`../.project-studio/shared/brand/`, etc.)
   - This module's personas (names + file paths inside module team/)
   - Shared personas this module consumes (names + file paths in parent team/ + override-file path if any)
   - This module's Tier 2 roadmap path (inside module project-studio/)
   - The sibling module list (names + folder paths) — read-only reference so CoS knows who the siblings are without reading them
   - Generated-at timestamp and parent setup session id

2. **`<module-folder>/START-HERE.md`** — human-readable companion. Plain markdown, written for the user, explaining:
   - "This is [module name] inside [product name]."
   - How to open a new Cowork session at this folder and get project-studio to pick up.
   - The one-line purpose of this module.
   - Where the parent shared assets live (relative path).
   - The primary-owner persona for this module.
   - First-task suggestion from the module's Tier 2 roadmap.

3. **`<module-folder>/project-studio/shared/shared-index.md`** — the index of parent-level shared assets. This is the file CoS reads at module-load to know what's available at parent level without pulling parent content into module context. Uses `templates/shared-index.md.tmpl`. Each entry has: asset path (relative), asset type, one-line description, last-known-updated timestamp.

### 7h. Initial parent manifest sync

For parent scenarios, update parent `CLAUDE.md` module table with each module's:
- Name
- Folder path (relative to parent)
- One-sentence purpose
- Status (Active / Paused / Future)
- Setup date
- Seed generated: Yes/No

For D2, this is an update (add rows) not a fresh write. Preserve all existing rows.

### 7i. Handoff instructions output (B, D1, D2 with parent access only)

After all writes complete, CoS emits a **handoff block** telling the user exactly how to continue in module sessions:

```markdown
## Parent setup complete — handoff to modules

Your parent project is ready at: <parent path>
Active modules with seeds: <module list>

### To start working on [primary module]:

1. Open a **new Cowork session**.
2. Mount the folder: `<parent path>/<primary module folder>`
3. Project Studio will auto-detect the module seed and load into **Module Resume Mode**.
   You won't be asked the setup wizard questions again — the module inherits the parent's brief, shared assets, and its own team/roadmap.
4. Your first suggested milestone: `<first Tier 2 milestone>` — owned by `<primary owner>`.

### To start working on a different module:

Same steps, mount that module's folder instead. Each active module has its own seed and team ready to go.

### This (parent) session

This parent session is now the **coordination session**. Use it to:
- Run the sync command when modules have new messages: `project-studio sync` (reads every module outbox, routes to inboxes, appends to bus.md). See `references/module-communication.md`.
- Update the Tier 1 roadmap when product priorities change.
- Add new modules later (D1/D2 flow).
- Review cross-module conflicts when a module wants to promote a change to parent.

You can close this session and come back to it later — the state is durable.
```

CoS does **not** automatically run anything from the handoff block. It's instructions for the user.

### 7j. Announce

```markdown
## Project ready: [Project Name]

**Scenario:** [A/B/C/D1/D2]
**Team:** [roster]
**Scale:** [light/standard/heavy]
**First milestone:** [name] — owned by [specialist]
**Parent architecture:** [active / imports-only / standalone]

**Next:** Tell me what to work on, or say "start with milestone 1.1".
The boot protocol is now active — every prompt goes through specialists.

**How it works from here:** You tell me what to work on. I route it to the right specialist(s), they critique and propose, and I present their recommendation. Nothing gets written or changed until you say "yes". This is the **propose-then-yes gate** — it applies to every file edit for the rest of the project. The only exception is persona context notes (append-only audit history).
```

---

## Step 8 — Module Resume Mode (triggered from Step 0 when a seed is found)

Step 8 is not a wizard step the user walks through — it's the flow that runs when Step 0's seed probe finds `project-studio/module-seed.yaml` at the mount root. It exists so opening a module subfolder after parent setup is a zero-friction experience.

### 8a. Read the seed

CoS reads `project-studio/module-seed.yaml`. Validates that all required fields are present:

- `parent.name`, `parent.path`
- `module.name`, `module.slug`, `module.purpose`
- `shared.brief_path`, `shared.roadmap_path`, `shared.assets_root`
- `team.module_personas[]`, `team.shared_personas[]`
- `roadmap.local_path`
- `siblings[]`

If any field is missing, fall back to wizard Step 1 (can't safely hydrate from an incomplete seed) and warn the user: *"Your module-seed.yaml is incomplete — field [x] is missing. Falling back to normal setup. You may want to re-run parent setup or fix the seed manually."*

### 8b. Scaffold minimum module structure if needed

If the seed exists but `project-studio/protocol/`, `project-studio/team/`, or `project-studio/registers/` are missing (the user may have only received the seed + start-here without running parent Step 7 in full), CoS scaffolds those directories using the same logic as `scripts/init_project.py` or the Write tool fallback.

**Do not overwrite existing files.** Only create missing ones. If the module was partially built already, keep what's there.

### 8c. Hydrate context from parent shared

Load read-only pointers to parent-level shared files (do NOT copy their contents into the module tree):

- Read `project-studio/shared/shared-index.md` to know what's available.
- When a task later references "the product brief" or "brand colors", CoS follows the relative path from the shared-index into the parent shared folder.
- Create `project-studio/shared/bus-snapshot.md` if it doesn't exist yet — this is a lightweight local summary of recent bus traffic, updated on sync.

### 8d. Write module personas (if not already written)

If `team/` is empty but the seed lists personas, write them now using the same templates and two-gate rules applied during parent Step 3. Since personas were already drafted and approved during parent setup, this is a pure write pass — no re-approval. The seed contains the approved persona content verbatim.

Shared personas are NOT written into the module's `team/` folder — they are referenced from parent. If the module has `team/persona-overrides.yaml`, CoS reads it and applies overrides at spawn time only (per `references/persona-schema.md` §scope-and-overrides).

### 8e. Write module roadmap (if not already written)

If `project-studio/project/roadmap.md` is empty but the seed has `roadmap.local_path` with content, write it now. Same principle — the roadmap was already drafted and approved during parent Step 4t.2.

### 8f. Initialise communication files

Ensure these exist inside the module:

- `project-studio/inbox.md` — seeded from template if missing.
- `project-studio/outbox-staging.md` — local draft queue for outgoing messages. This is the file CoS writes drafts to at auto-draft gates (see `references/module-communication.md` §auto-draft-gates). Periodically synced to the parent's `shared/<module>-outbox.md` when the user runs a sync command from this module.

### 8g. Read today's incoming messages

Check `inbox.md` for unread entries. If any exist, surface them at session start:

```
You have 3 unread messages from siblings:
  • auth     → decision: "switched password hashing to argon2" (2h ago)
  • payments → question: "should we unify the billing webhook?"   (yesterday)
  • parent   → milestone: "Tier 1 milestone 'Auth done' is 80%"   (3d ago)

Want me to summarise, open one, or mark all read?
```

Don't block setup on these — they're informational. The user decides what to do.

### 8h. Announce and enter normal work mode

```
Module session ready: <module name>
Parent: <parent name>
Your team: <module + shared persona roster>
Your roadmap: <first active milestone from Tier 2>
Inbox: <N unread>

Ready to work. Tell me what to pick up, or say "continue [milestone]".
```

From this point, the normal per-turn boot protocol (`project-studio/protocol/boot.md`) takes over. Step 8 only runs once — it's the one-time hydration at first open.

### 8i. Fallback: seed present but parent unreachable

If the module was mounted alone (user opened Cowork at the module folder, not the parent), CoS cannot follow the relative paths in the seed into parent shared. In that case:

- Accept the module-local personas, roadmap, and briefs. These live inside the module and are fully readable.
- For parent shared assets: flag them as "out of reach from this session" in a warning. The user can either (a) remount at the parent level, (b) copy the parent shared assets into the module manually, or (c) accept working without them.
- Communication files (`shared/<module>-outbox.md`, `shared/bus.md`) are unreachable too. Outbox drafts stay in `project-studio/outbox-staging.md` until the user opens a session with parent access and runs sync.

---

## Setup Interruption Recovery

If context compacts or session dies before Step 7c completes:

1. On resume, check: does root CLAUDE.md exist with project-studio markers?
2. **CLAUDE.md exists + `project-studio/` populated →** Setup complete. Run normal resume protocol.
3. **CLAUDE.md missing + `project-studio/` partially exists →** Interrupted during Step 7. Read today's log + existing files. Summarize: *"Setup was interrupted at Step 7. Here's what was confirmed: [summary]. Continue building, or start over?"*
4. **CLAUDE.md missing + no `project-studio/` →** Interrupted before Step 7. In-conversation context lost. Ask user to re-describe, or check for notes.
5. **Parent CLAUDE.md exists but module CLAUDE.md missing (D2) →** Module setup interrupted. Parent is intact. Resume module setup.

---

## Light-Scale Fast Track

| Full step | Light equivalent |
|---|---|
| Step 1 (Scenario + Scale) | Same 3 questions — skip Q2b if not needed. |
| Step 2 (Scenario context) | Brief + goals + constraints only. Skip infrastructure gathering. |
| Step 3 (Team) | 1 specialist + optional critic. One persona, generate-then-confirm. |
| Step 4 (Roadmap) | 1 phase, 1-3 milestones, 2-5 tasks. CoS drafts, specialist reviews. |
| Step 5 (Connectors) | **Skip entirely** unless user asks. |
| Step 6 (Review) | **Skip entirely.** |
| Step 7 (Build) | Same structure, `notes.md` instead of registers. Minimal checkpoint. |

Target: setup completes in **3-5 user interactions** for light, vs 8-12 for standard.

---

## Scenario Flow Diagram

```
START
  │
  ├─ Step 1 — Scenario + Scale (deterministic gate)
  │   │
  │   ├─ Q1: New or Existing?
  │   ├─ Q2: Single or Multiple modules?
  │   ├─ Q2b (only if Existing+Multi): Parent exists?
  │   └─ Q3: Scale?
  │
  │   Scenario resolution:
  │     New + Single              → A
  │     New + Multi                → B
  │     Existing + Single          → C
  │     Existing + Multi, no parent → D1
  │     Existing + Multi, parent    → D2
  │
  ├─ Step 2 — Scenario branch
  │   │
  │   ├─ A → 2A.1 brief · 2A.2 empty folder gate
  │   ├─ B → 2B.1 brief · 2B.2 list modules · 2B.3 per-module purpose · 2B.4 pick primary · 2B.5 parent mount · 2B.6 empty folder gate
  │   ├─ C → 2C.1 intake method · 2C.2 execute intake · 2C.3 brief + gap-fill · 2C.4 gitignore
  │   ├─ D1 → 2D1.1 list · 2D1.2 primary · 2D1.3 parent mount + intake (Branch A or B)
  │   └─ D2 → 2D2.1 verify parent · 2D2.2 read manifest · 2D2.3 confirm new module · 2D2.4 intake · 2D2.5 sibling sync · 2D2.6 brief + gap-fill · 2D2.7 parent update plan · 2D2.8 gitignore
  │
  ├─ Step 3 — Team Setup (universal)
  ├─ Step 4 — Roadmap Planning (universal, team job)
  ├─ Step 5 — Connectors (universal, roadmap-driven; light: skip)
  ├─ Step 6 — Review (universal; light: skip)
  └─ Step 7 — Build (structure varies by scenario)
```

---

## Migration Export Prompt (Reference)

This is the extraction prompt used in the migration-export path. Unchanged from the original:

> Export this entire project's data for migration. Read every file in the project folder and produce a single file called `migration-export.md` saved to the project root. Structure it exactly like this:
>
> \# Migration Export
>
> \#\# Project Brief
> (one sentence brief, extracted from CLAUDE.md or context)
>
> \#\# Goals
> (bulleted list)
>
> \#\# Success Metrics
> (bulleted list with numeric targets if they exist)
>
> \#\# Constraints
> (deadlines, budget, tech, people)
>
> \#\# Team Roster
> For each persona: name, role, and domain only. Do not include principles, obsession, skill menu, or other persona details.
>
> \#\# Roadmap State
> (full atomic roadmap with owner tags, marking completed vs pending items)
>
> \#\# Active Assumptions
> (from registers/assumptions.md — active only)
>
> \#\# Active Risks
> (from registers/risks.md — active only)
>
> \#\# Open Questions
> (from registers/open-questions.md — unresolved only)
>
> \#\# Key Decisions
> (from decisions/ — summary of each ADR)
>
> \#\# Learnings
> (from registers/learnings.md)
>
> \#\# Infrastructure Map
> For each live module (app, website, API, admin panel, etc.) scan the codebase:
> - Name, type, production URL, framework, language, hosting
> - Environment URLs (production, staging, dev)
> - Connected services: scan .env files and configs for external services
>   - For each: service name, what it's used for, account identifier (NOT keys), env var names (NOT values)
> - Deployment method (CI/CD, auto-deploy, manual)
> - Repo location
> For services shared across modules: service name, which modules, account identifier
> Do NOT include API keys, secrets, tokens, or passwords.
>
>