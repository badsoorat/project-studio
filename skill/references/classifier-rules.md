# Classifier Rules — Context Sort & Cleanup

The heuristics and decision rules behind Step 2.5 of the setup flow. This is how CoS walks a pre-existing parent or module tree and decides what is (a) module-specific context, (b) shared context, (c) ambiguous, or (d) cleanup — without guessing and without dragging the user through a file-by-file interview for thousands of files.

Companion to `references/setup-flow.md` §Step 2.5 and `references/contamination-checklist.md`.

---

## Why classification matters

When Project Studio is set up over an existing codebase (Scenarios C, D1, and D2), the folder is rarely empty and rarely tidy. It contains:

- The actual code (stays put, never classified).
- Planning documents, meeting notes, old briefs, stale screenshots.
- Architecture sketches, API contracts, brand assets.
- Half-finished previous-session output from another skill.
- Files with no obvious owner — "do I keep this or delete it?"

Without classification, one of two bad things happens:

1. **Over-inclusion.** Everything gets dragged into `project-studio/` or parent shared, Claude reads stale context at every turn, and the project is polluted forever.
2. **Under-inclusion.** Nothing gets sorted, the existing context is ignored, and the user has to manually paste facts back in for weeks.

Classification gives CoS a disciplined way to process a tree in bulk, present a batch decision to the user, and only drop into per-file interview for the genuinely ambiguous cases.

---

## Scope

Classification runs in Step 2.5 after the scenario branch (B/D1/D2) finishes its intake. It covers everything under the **setup scope** — which is:

- **Scenario B (new product):** not applicable. New product = empty tree.
- **Scenario D1 (new parent over existing module folders):** every file under the parent directory.
- **Scenario D2 (adding a new module to an existing parent):** every file under the new module's folder only. Do NOT walk sibling module folders.
- **Scenario C (single-project retrofit):** every file under the project root.

Files under a **skip list** are never classified or touched:

```
.git/            node_modules/       venv/             env/
.venv/           __pycache__/        .cache/           dist/
build/           target/             out/              .next/
.nuxt/           coverage/           .pytest_cache/    .tox/
.mypy_cache/     .ruff_cache/        .gradle/          .mvn/
.claude/         .project-studio/    project-studio/   .cowork/
.DS_Store        Thumbs.db
```

The skip list is absolute. Never classify, never read, never delete files under these paths — they are either infrastructure, build artefacts, or already-owned by Project Studio.

---

## The 4-tier classification

Every file in scope ends up in exactly one of four tiers.

### Tier 1 — High-confidence module context

A file that clearly belongs to a single module's private context (brief, notes, research, sketches, decisions). Gets routed into that module's `project-studio/imports/legacy/` folder (not read into active context, kept as archive).

### Tier 2 — High-confidence shared context

A file that clearly belongs to the parent-level shared layer (product brief, brand asset, API contract, glossary, convention). Gets routed into `<parent>/.project-studio/shared/<category>/`.

### Tier 3 — Ambiguous

A file that can't be placed confidently into Tier 1 or Tier 2 with the available heuristics. Goes into a per-file review list presented to the user with batch-apply options.

### Tier 4 — Cleanup

A file that is clearly stale, duplicate, temporary, or junk — and safe to hard-delete with user approval. Never auto-deleted; always confirmed.

### Tier distribution expectations

On a typical D1 walk over a 500-file tree:

| Tier | Expected % | Count on 500 files |
|---|---|---|
| Tier 1 (module) | 40-60% | 200-300 |
| Tier 2 (shared) | 5-15% | 25-75 |
| Tier 3 (ambiguous) | 15-30% | 75-150 |
| Tier 4 (cleanup) | 10-30% | 50-150 |

If Tier 3 is consistently over 50%, the heuristics are too weak — either the tree is genuinely chaotic or the heuristics need tightening. Log it and move on; don't try to force files into higher tiers.

---

## The 8 heuristics

Each file is evaluated against 8 heuristics. Each heuristic produces a score contribution toward one of the 4 tiers. The final tier is the highest-scoring after all heuristics apply.

### H1 — Folder location

**Signal strength:** very strong.

Path-based classification. Runs first. Rules:

| Path pattern (relative to scope root) | Tier | Category |
|---|---|---|
| `<module-slug>/...` (where module-slug is in the inventory) | Tier 1 | module:<slug> |
| `shared/`, `common/`, `assets/`, `brand/`, `docs/`, `conventions/`, `standards/` | Tier 2 | shared:<dirname> |
| `tmp/`, `temp/`, `trash/`, `old/`, `deprecated/`, `archive/`, `backup/` | Tier 4 | cleanup |
| `README*`, `LICENSE*`, `CHANGELOG*`, `CONTRIBUTING*` at scope root | Tier 2 | shared:docs |
| any `*.md` at scope root | Tier 2 | shared:docs |
| `~$*`, `*.tmp`, `*.bak`, `.DS_Store`, `Thumbs.db` | Tier 4 | cleanup |
| no match | — | defer to H2 |

H1 is deterministic. If it fires, no other heuristic changes the tier — only adds category detail.

### H2 — Filename semantics

**Signal strength:** strong.

Filename word-matching after extension strip. Rules (case-insensitive, whole-word or hyphen-separated):

| Filename matches | Tier | Category |
|---|---|---|
| `brief`, `vision`, `product`, `roadmap`, `strategy`, `plan` | Tier 2 | shared:brief/roadmap |
| `logo`, `favicon`, `icon`, `brand`, `style-guide`, `typography`, `palette` | Tier 2 | shared:brand |
| `api-contract`, `openapi`, `swagger`, `schema`, `erd`, `architecture`, `glossary` | Tier 2 | shared:docs |
| `style`, `conventions`, `naming`, `standards`, `lint`, `prettier`, `eslintrc` | Tier 2 | shared:conventions |
| `persona`, `user-research`, `interview`, `survey`, `journey`, `wireframe`, `mockup` | Tier 1 | module (needs H3 to place) |
| `notes`, `scratch`, `wip`, `draft`, `todo` | Tier 3 | ambiguous |
| `*.log`, `*.tmp`, `*.cache`, `*.pid`, `*.lock` | Tier 4 | cleanup |
| starts with `_` or `.` and is a markdown/text file | Tier 3 | ambiguous |
| no match | — | defer to H3 |

### H3 — Content signature

**Signal strength:** strong.

Only runs on small text files (< 100 KB) to keep the walk cheap. Reads the first 40 lines.

Rules:

- **"product brief" / "value proposition" / "target user" in first 20 lines** → Tier 2 shared:brief.
- **"api endpoint" / "request body" / "response" / YAML with `paths:` / `openapi:` declaration** → Tier 2 shared:docs.
- **"ADR" / "architecture decision record" / numbered `## Context / ## Decision / ## Consequences`** → Tier 1 module:decisions (routes to `imports/legacy/decisions/`).
- **"meeting notes" / "standup" / "retro" / dated heading (YYYY-MM-DD)** → Tier 1 module:notes.
- **Mostly code (heuristic: > 30% of lines start with code-ish chars like `{`, `}`, `function`, `class`, `def`, `import`, `const`, `let`, `var`)** → NOT classified (belongs to the codebase, CoS leaves it alone).
- **Empty file (0 bytes or only whitespace)** → Tier 4 cleanup.
- **< 5 lines of content** → Tier 3 ambiguous (too small to classify).

### H4 — Extension + size

**Signal strength:** medium.

Rules:

| Extension | Size | Tier |
|---|---|---|
| `.md`, `.txt`, `.rst`, `.org` | > 500 bytes | Tier 1 or Tier 2 (from H1/H2/H3) |
| `.md`, `.txt`, `.rst`, `.org` | < 500 bytes | Tier 3 ambiguous (tiny text often wrong) |
| `.svg`, `.png`, `.jpg`, `.webp`, `.ico`, `.pdf`, `.sketch`, `.fig`, `.xd` | any | Tier 2 shared:brand IF filename matches brand words, else Tier 1 module:assets |
| `.csv`, `.xlsx`, `.xls`, `.tsv`, `.parquet`, `.jsonl` | > 0 bytes | Tier 2 shared:data IF filename has no module words, else Tier 1 module:data |
| `.yaml`, `.yml`, `.toml`, `.json` at scope root | any | Tier 2 shared:conventions IF matches config-file patterns (`.eslintrc`, `prettier`, etc.), else NOT classified (codebase config) |
| `.docx`, `.doc`, `.pptx`, `.ppt`, `.key`, `.pages` | any | Tier 1 module:docs (user-generated, usually module-specific) |
| `.zip`, `.tar`, `.gz`, `.7z`, `.rar` | any | Tier 3 ambiguous (need user to say what's in it) |
| `.log`, `.tmp`, `.bak`, `.swp`, `.pid` | any | Tier 4 cleanup |
| unknown extension | any | Tier 3 ambiguous |

### H5 — Modification time

**Signal strength:** weak (tie-breaker only).

Rules:

- **Modified in the last 30 days** → boost toward "active" category (Tier 1 or Tier 2).
- **Modified 30-180 days ago** → no boost.
- **Modified 180-365 days ago** → slight boost toward Tier 4 cleanup.
- **Modified > 365 days ago AND in a junk-path** → strong boost toward Tier 4.
- **Modified > 365 days ago AND in a non-junk path** → slight boost toward Tier 3 ambiguous (stale but not obviously cleanup).

H5 is always a tie-breaker, never the primary classifier. A file can be 3 years old and still be an important shared asset.

### H6 — Duplicate detection

**Signal strength:** medium.

Uses a fast content hash (e.g., SHA-1 of first 4KB + file size) to detect duplicates.

Rules:

- **Exact duplicate of another file in scope** → the older copy is Tier 4 cleanup, the newer copy keeps its tier from other heuristics. If they have the same mtime, the one deeper in the tree is kept.
- **Exact duplicate of a file under a known parent shared path** → Tier 4 cleanup (the parent version wins).
- **Exact duplicate of a file already inside a `project-studio/` or `.project-studio/` folder** → Tier 4 cleanup (the managed version wins).

Hash collisions are extremely rare at this scale and are handled by comparing the first 16 KB of each file. If both match, the files are treated as identical for classification purposes.

### H7 — Cross-module presence

**Signal strength:** strong (D1 only).

Only runs in Scenario D1 (new parent over multiple existing module folders).

Rules:

- **Same filename appears in 2+ module folders with similar content (hash prefix match)** → Tier 2 shared (promote to `<parent>/.project-studio/shared/`).
- **Same filename appears in 2+ module folders with divergent content** → Tier 3 ambiguous (user decides whether to pick one, keep both, or fork).
- **Same filename at scope root and inside 1+ module folders** → Tier 2 shared (the root copy is the canonical one).

### H8 — Explicit annotation

**Signal strength:** overriding.

Any file containing a leading comment or header like:

```
<!-- project-studio: shared -->
<!-- project-studio: module:<slug> -->
<!-- project-studio: cleanup -->
<!-- project-studio: keep -->
```

...is placed in the corresponding tier regardless of other heuristics. `keep` means "don't classify, don't touch, leave in place" (Tier 0).

H8 lets the user pre-annotate files before running setup if they want precise control.

---

## Scoring and resolution

Heuristics run in the order H1 → H8. The first heuristic to produce a definitive classification (H1, H8) wins immediately. For the rest, scores accumulate:

```
score[Tier 1] += H2, H3, H4, H5, H6, H7 contributions toward Tier 1
score[Tier 2] += H2, H3, H4, H5, H6, H7 contributions toward Tier 2
score[Tier 3] += H2, H3, H4 ambiguity signals
score[Tier 4] += H4, H5, H6 cleanup signals
```

The winning tier is `max(score)`. If the max is tied between two tiers, the file goes to Tier 3 ambiguous (never silently default).

### Confidence levels

Each classification carries a confidence:

- **High** — H1 or H8 fired, OR the winning tier's score is ≥ 2× the next highest.
- **Medium** — winning tier's score is 1-2× the next highest.
- **Low** — scores are close OR only weak heuristics fired.

CoS displays confidence in the decision card so the user can focus review effort on low-confidence items.

---

## Walk algorithm

Pseudocode for the full walk:

```
def walk(scope_root, module_inventory):
    results = {tier1: [], tier2: [], tier3: [], tier4: []}

    for path in os.walk(scope_root):
        if path matches any skip_list entry:
            continue
        if path is a directory:
            continue
        if path is under .git, .project-studio, project-studio, or .claude:
            continue

        file = FileInfo(path)

        # H8: explicit annotation overrides everything
        if file.has_annotation():
            results[file.annotated_tier].append(file)
            continue

        # H1: folder location
        tier, category, confidence = apply_H1(file, module_inventory)
        if tier:
            results[tier].append(file)
            continue

        # H2-H7: scoring
        scores = {1: 0, 2: 0, 3: 0, 4: 0}
        apply_H2(file, scores)
        apply_H3(file, scores)  # reads file content if small text
        apply_H4(file, scores)
        apply_H5(file, scores)
        apply_H6(file, scores, duplicate_index)
        if scenario == "D1":
            apply_H7(file, scores, module_inventory)

        tier = argmax(scores)
        confidence = compute_confidence(scores)
        results[tier].append((file, category, confidence))

    return results
```

The walk is single-pass and read-only. Nothing is moved, copied, or deleted until the user approves the batch decision in Step 2.5c.

---

## Presenting the results

At the end of the walk, CoS prints a summary:

```
Classification complete. Walked 487 files under <scope>.

Tier 1 (module context):  214 files   →  route to module imports/legacy/
  auth:      94 files
  payments:  78 files
  admin:     42 files

Tier 2 (shared context):  38 files    →  route to .project-studio/shared/
  brief/roadmap:   3 files
  brand:          12 files
  docs:           18 files
  conventions:     5 files

Tier 3 (ambiguous):       86 files    →  per-file review (batch options available)
  low confidence:         31 files
  medium confidence:      55 files

Tier 4 (cleanup, hard delete): 149 files
  known junk:             112 files   (logs, tmp, cache, empty)
  stale duplicates:        22 files
  stale + junk-path:       15 files

Batch decision options:
  [1] Apply tier 1 + tier 2 routing, review tier 3 one-by-one, confirm tier 4 delete
  [2] Apply tier 1 + tier 2 routing only, leave tier 3 and tier 4 alone
  [3] Dry run — show me where each file would go, let me approve the plan
  [4] Cancel — do nothing, skip classification
```

Option [1] is recommended unless the user has strong reasons to be cautious.

---

## Tier 3 per-file review

Tier 3 files get a concise per-file prompt with batch-apply. Example:

```
Tier 3 review — 86 files. You can apply your answer to all similar files.

File 1/86:  payments/notes-2024-09.md   (12 KB, modified 487 days ago)
            Heuristics: H2 matched "notes"; H3 found date heading; H5 flagged stale.
            Confidence: medium.

  [a] route to module:payments imports/legacy/
  [b] route to .project-studio/shared/docs/
  [c] hard delete
  [d] leave in place
  [s] skip to next file
  [A] apply "a" to all remaining tier 3 files with this signature
  [D] apply "hard delete" to all remaining stale tier 3 files
```

The signature match for batch-apply is based on extension + folder + modification-time bucket. If the user picks `[A]`, CoS applies the same action to any remaining Tier 3 file in the same bucket and subtracts those from the review queue.

---

## Tier 4 cleanup confirmation

Tier 4 is never deleted without explicit confirmation. The Tier 4 card:

```
Tier 4 hard delete — 149 files, 23.4 MB total.

Category breakdown:
  Logs:           87 files    8.1 MB
  Tmp/bak:        34 files    2.2 MB
  Empty files:    12 files    0 B
  Stale dups:     16 files   13.1 MB

Safety check:
  - No files under .git/ (confirmed)
  - No files under src/, lib/, app/ (confirmed)
  - No files matching *.config.* at scope root (confirmed)
  - Nothing created in the last 7 days (confirmed)

Backup recommendation:
  The delete is PERMANENT — files are not moved to trash.
  Create a tarball backup first? [Y/n]

Proceed with delete? [y/N/details]
```

If the user picks `details`, CoS prints the full file list paginated.

If the user picks `Y` on backup, CoS runs a single bash command to create `<scope>/.project-studio/pre-sort-backup-<timestamp>.tar.gz` before deleting anything. The backup file is added to `.gitignore` and documented in the sort-log.

---

## Sort-log

Every run of Step 2.5 produces a sort-log at `<scope>/.project-studio/sort-log-<timestamp>.md`. It's the audit trail of what was classified where and why. Contents:

```markdown
# Context Sort & Cleanup — Sort Log

**Scope:** <scope-root>
**Scenario:** <B|D1|D2|C>
**Started:** 2026-04-11T14:32:00Z
**Finished:** 2026-04-11T14:41:17Z
**Total files walked:** 487
**Files classified:** 487
**Files routed:** 338 (Tier 1: 214, Tier 2: 38, Tier 3 resolved: 86)
**Files deleted:** 149 (Tier 4)
**Backup:** `.project-studio/pre-sort-backup-20260411-143200.tar.gz`

## Tier 1 routing

| Source | Destination | Heuristic |
|---|---|---|
| `auth/old-brief.md` | `auth/project-studio/imports/legacy/old-brief.md` | H1 (module path) |
| `auth/research-2023.md` | `auth/project-studio/imports/legacy/research-2023.md` | H1 + H3 |
| ...

## Tier 2 routing

| Source | Destination | Heuristic |
|---|---|---|
| `brief.md` | `.project-studio/shared/brief.md` | H2 (brief word) + H4 |
| `brand/logo.svg` | `.project-studio/shared/brand/logo.svg` | H1 (shared path) |
| ...

## Tier 3 decisions (per-file)

| Source | Decision | User note |
|---|---|---|
| `payments/notes-2024-09.md` | Tier 1 (module:payments) | (batch-applied) |
| `random.csv` | Tier 4 delete | (individual) |
| ...

## Tier 4 deletions

(full list of deleted files with size and original path)

## Safety notes

- No .git/, src/, or config files were touched.
- Backup created at path above.
- Classifier version: 1.0
```

The sort-log stays in the project permanently as a historical record. It is read-only after Step 2.5 finishes.

---

## Anti-patterns

- **Walking the skip list.** Skip list is absolute. If CoS is tempted to walk `.git/` to find a forgotten asset, that's an invariant violation.
- **Moving files without sort-log entries.** Every routed file gets logged. No silent moves.
- **Hard-deleting without confirmation.** Tier 4 is always confirmed. Even in chatty mode, even with high confidence, even if the user seems eager.
- **Re-running classification on an already-managed tree.** If `.project-studio/` already exists at the scope root, classification is NOT the right tool — that's a resume scenario. Step 2.5 only runs during initial setup.
- **Running classification inside a skip-listed subtree.** E.g., classifying files under `node_modules/` because the skip list "didn't catch that exact path". If a path looks like a dependency cache or build output, add it to the skip list — don't classify it.
- **Batch-applying across different signatures.** Batch-apply only applies to files with matching signature (extension + folder bucket + mtime bucket). Never apply across unrelated files just because the user is in a hurry.
