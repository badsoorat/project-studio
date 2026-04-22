# Connectors & Plugins

Logic for suggesting MCP connectors and plugins during the setup wizard, and for managing them over a project's lifetime. Covers the v3.1 severity-gated setup flow, parent/module overlay semantics in multi-module projects, and degraded-mode behavior when expected connectors are absent.

## Principle

**Suggest with one-click approval. Do not auto-install.** The user stays in control at every step. The severity gate (below) is a prompt mechanism, not an auto-installer.

## §severity-tiers

Per **Invariant #21**, the setup wizard classifies every connector a project might use into three severity tiers and prompts the user tier-by-tier. The user may skip any tier. CoS records the outcome of each prompt in `.project-studio/references/connectors.md` (parent) and/or `project-studio/references/connectors.md` (module) so future turns know what's available and what to substitute when something is missing.

### Critical tier

**Default members:**
- **Workspace bash / file I/O.** Without this, CoS cannot read, write, or execute scripts. If absent, CoS falls back to Write-tool-only mode (see SKILL.md §quick-start).
- **`gstack-team` plugin.** Source of Tier-1 plan-critique, senior code review, CSO, investigate, QA, design-review, retro, ship/canary/land-and-deploy, freeze/guard/unfreeze, context-save/restore, and make-pdf. Without it, Project Studio substitutes pre-v3.1 in-house equivalents and warns the user.

**Setup prompt (verbatim template):**

> The following are **critical** for Project Studio v3.1 to function at full capability:
> - Workspace bash (file I/O)
> - `gstack-team` plugin (methodology skills)
>
> Do you have both installed and authorized for this project? (yes / show me what's missing / skip — I'll run in degraded mode)

### Recommended tier

**Default members:**
- **`graphify` skill.** Structural evidence for code-heavy specialist spawns. Without it, architecture/perf/security reviews lose their evidence base and CoS flags "structural claims are specialist judgment, not graph-verified" on every relevant proposal.
- **Claude-in-Chrome MCP.** Powers live-URL QA (`gstack-team:qa`), design review on deployed sites (`gstack-team:design-review`), and browse (`gstack-team:browse`). Without it, QA and design review fall back to static analysis or user-pasted screenshots.

**Setup prompt (verbatim template):**

> The following are **recommended** — Project Studio will function without them but with reduced fidelity:
> - `graphify` (structural evidence for code reviews)
> - Claude-in-Chrome MCP (live-URL QA and design review)
>
> Install any of these now? (install all / install selected / skip)

### Optional tier

**Default members:**
- **Vercel MCP.** Deploy + runtime-logs access for `gstack-team:ship`, `:canary`, `:land-and-deploy`. Without it, those skills degrade to git-only workflows (open PR, observe externally, no integrated deploy).
- **Project-specific MCPs** — whatever the project brief calls out (Linear, Notion, Figma, Slack, GitHub, Tavily, Firecrawl, Atlassian, Google Drive, scheduled-tasks, session_info, etc.).

**Setup prompt (verbatim template):**

> The following are **optional** — enable only if this project will use them:
> - Vercel MCP (deploy + runtime logs)
> - <Project-specific MCPs picked from the brief>
>
> Install any of these now? (install all / install selected / skip)

### Tier prompting order

Critical first, Recommended second, Optional third. The user's answers cascade: if they decline the critical tier, the wizard notes the degraded state and asks whether to continue setup at all. If they decline recommended, the wizard notes the reduced-fidelity state but proceeds. Optional never blocks setup.

### Outcome recording

After the severity gate, CoS writes the decisions to the project's connectors file using this format:

```markdown
## Connectors — severity outcome (<YYYY-MM-DD>)

### Critical
- Workspace bash — available
- gstack-team plugin — available (version 0.2.x)

### Recommended
- graphify — available
- Claude-in-Chrome — declined (user: "not needed for this phase")

### Optional
- Vercel MCP — installed
- Linear — installed (workspace: "ACME", id: lnr_a1b2c3)
- Notion — declined
```

Absence is explicit. A missing entry is not the same as "declined"; CoS treats it as "never asked" and re-runs the gate on next setup-adjacent event.

## §parent-module-overlay

In multi-module projects, each module may declare different connector availability from the parent baseline. The rule is overlay, not replace.

**Parent baseline.** Written to `.project-studio/references/connectors.md` at parent setup. Applies to parent-session work and serves as the default for every module.

**Module overlay.** Written to `<module>/project-studio/references/connectors.md` at module setup. Lists only deltas from the parent — additions, removals, or identity-lock differences. Silent overlap means "inherits from parent".

**Example:**

```markdown
# Module connectors — overlay over parent

Inherits from: ../.project-studio/references/connectors.md

### Added for this module
- Figma — team: "Auth Design" (id: fg_t999) — design inspection for auth flows

### Removed for this module
- Vercel MCP — this module is not deployable standalone (deploys happen at the parent level)

### Identity-lock differences
- Linear — this module uses a different Linear team: "Auth Squad" (id: lnr_a5b6c7)
```

**Cross-module reconciliation.** When a cross-module action is proposed at the parent (e.g., a coordinated release across `auth` and `admin`), CoS reconciles the union of connector availability from all involved modules. A connector absent in any one of the modules downgrades the action to the least-capable common path. If `auth` has Vercel but `admin` does not, the cross-module release cannot use the integrated deploy path — it falls back to module-by-module manual deploys coordinated via the bus.

## §degraded-mode

A connector is in "degraded mode" when it was expected (either in the severity gate's critical/recommended tiers or in the project's recorded connectors list) but is unavailable at a given turn. Degraded mode is recorded at session start and surfaced to the user with a single clear warning, not rediscovered per turn.

**Detection:** On session start (after Step 0 context-restore, before Step 1 boot), CoS walks the project's recorded connectors list and confirms each is available via identity reconciliation (see §identity-lock-in below). Any that fail move into degraded mode for the session.

**User warning format:**

> **Degraded mode this session.** The following recorded connectors are unavailable:
> - `gstack-team` plugin — not installed. Falling back to pre-v3.1 in-house equivalents for plan-critique, code review, retros, and PDF export. User-facing deliverables will be markdown-only.
> - Claude-in-Chrome — not authorized in this account. Live-URL QA and design review will use static analysis only.
>
> Install or authorize these to restore full capability. Continue in degraded mode? (yes / pause and fix)

**Substitution matrix.** When a capability's primary skill is absent, CoS substitutes the pre-v3.1 in-house version and logs the substitution. See `references/gstack-integration.md` §degraded-mode for the full mapping.

**Provenance note.** Degraded mode does not change `references/feature-provenance.md`. Provenance records the canonical source; the session connectors list records the per-session availability. The two are deliberately separate.

---

## Tools available for discovery

- `mcp__mcp-registry__search_mcp_registry` — search the registry by keyword
- `mcp__mcp-registry__suggest_connectors` — suggest connectors for a described need
- `mcp__plugins__search_plugins` — search the plugin marketplace
- `mcp__plugins__suggest_plugin_install` — suggest plugin installs

Run searches during the Optional-tier step of the severity gate with project-type keywords, then filter results to the 3-7 most relevant. Present to user.

---

## MCPs commonly useful by project type

### Software projects
- **Linear** — issue tracking, roadmap sync
- **GitHub** (search registry) — PRs, commits, issues
- **Vercel MCP** — deploy + runtime logs (enables gstack-team:ship/canary/land-and-deploy)
- **Claude-in-Chrome** — live-URL QA + design review (enables gstack-team:qa and :design-review)
- **Figma** — design inspection
- **scheduled-tasks** — automated retros

### Research projects
- **Tavily** — web search and research
- **Firecrawl** — deep web scraping
- **Notion** — knowledge base, research repository
- **session_info** — replay