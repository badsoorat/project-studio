# Import Slices — Modular Context Selection

When a new project relates to existing projects, the user selects which context slices to import. Slices are independent — any combination is valid. CoS builds a single composite extraction prompt from the user's selections.

## The 7 Import Slices

Each slice is a self-contained chunk of context. Users pick any combination via multi-select (presented through `AskUserQuestion`).

---

### Slice 1: Infrastructure

**Plain-language label:** *"Technical details — domains, hosting, services (Stripe, databases, APIs), environment setup"*

**What it captures:** Module profiles (name, type, URL, framework, hosting), connected services (name, purpose, account ID, env var names), environment URLs, deployment method, shared services across modules.

**Extraction prompt block:**

```
## Infrastructure
For each live module (app, website, API, admin panel, etc.) scan the codebase and list:
- Name and type (website, web app, mobile app, API, desktop app)
- Production URL (if deployed)
- Framework and language (e.g., Next.js, TypeScript)
- Hosting/deployment platform (e.g., Vercel, AWS, Netlify)
- Environment URLs (production, staging, dev — URLs only)
- Connected services: scan .env files, config files, and package dependencies
  - For each external service found: service name, what it's used for,
    account identifier if visible (e.g., Stripe account ID, project name),
    and environment variable names that reference it (NOT the values)
- Deployment method (CI/CD pipeline, auto-deploy, manual)
- Source code location (repo URL or monorepo path)

For services used by multiple modules (shared services):
- Service name, which modules use it, account identifier (NOT keys)
- Any known constraints or limits

Do NOT include API keys, secrets, tokens, or passwords — only names and identifiers.
```

**Imported to:** `imports/<project>/infrastructure.md`

**Loaded when:** Task mentions a module by name, a service (Stripe, WorkOS, etc.), deployment, hosting, or environments.

---

### Slice 2: Design System

**Plain-language label:** *"Design details — colors, fonts, spacing, component patterns, visual language"*

**What it captures:** Design tokens, color palette, typography scale, spacing, component specs, brand assets location, dark mode approach.

**Extraction prompt block:**

```
## Design System
If a DESIGN.md, design tokens file, theme config, or tailwind.config exists,
include its full contents. Otherwise extract from the codebase:
- Color palette: hex values with semantic names/roles (primary, secondary,
  surface, error, success, etc.)
- Typography: font families, size scale (headings through captions),
  weight scale, line heights
- Spacing scale (if defined — e.g., 4px base unit, or a named scale)
- Border radius values (small, medium, large, full)
- Shadow values (if defined)
- Key component patterns: button variants, card layouts, form field styles,
  navigation patterns, modal/dialog styles
- Icon system: library used (Lucide, Heroicons, etc.), sizing convention
- Brand assets: where logos, icons, and illustrations live (file paths)
- Dark mode: yes/no, implementation approach (CSS variables, class toggle, etc.)
- Responsive breakpoints: values used and naming convention
```

**Imported to:** `imports/<project>/design-system.md`

**Loaded when:** Task involves UI, visual design, styling, colors, fonts, or "look and feel."

---

### Slice 3: Content & Copy

**Plain-language label:** *"Content — website copy, product descriptions, messaging, tone of voice"*

**What it captures:** Page content, headlines, CTAs, brand voice notes, content structure, meta descriptions.

**Extraction prompt block:**

```
## Content & Copy
Extract the key content and messaging from the project:
- Homepage: headline, subheadline, CTA text, key value propositions
- Key product/service descriptions (features, benefits, how it works)
- Navigation labels and site structure (what pages exist and their purpose)
- Pricing page copy (plan names, descriptions, feature lists — not prices)
- About page: company/product story, mission statement
- Tone of voice notes (if documented anywhere — brand guide, style guide)
- Any brand voice guidelines, writing rules, or content standards found
- Meta descriptions and page titles for key pages
- Common CTAs used across the site
- Testimonials or social proof copy (if present)

Focus on the messaging and structure, not the layout.
```

**Imported to:** `imports/<project>/content-copy.md`

**Loaded when:** Task involves messaging, copy, content structure, brand voice, or rewriting.

---

### Slice 4: Project Context

**Plain-language label:** *"Project context — what the project is about, goals, who it serves, key constraints"*

**What it captures:** Brief, goals, success metrics, target audience, constraints, stakeholders.

**Extraction prompt block:**

```
## Project Context
Extract the project's foundational context:
- One-sentence project description (what is this?)
- Goals: what does success look like? (bulleted list)
- Success metrics: measurable targets (with numbers if they exist)
- Target audience / user personas: who is this for?
- Constraints: timeline, budget, technology, people, legal
- Stakeholders: who else cares about this project?
- Problem statement: what problem does this solve? Why does it exist?
- Current status: where is the project at right now? (launched, beta, etc.)

If a brief.md, PRD, or README with project context exists, include its contents.
```

**Imported to:** `imports/<project>/project-context.md`

**Loaded when:** Task needs understanding of what the related project is about, its goals, audience, or constraints.

---

### Slice 5: Decisions & Learnings

**Plain-language label:** *"Decisions & learnings — why things were built this way, what worked, what didn't"*

**What it captures:** ADR summaries, learnings register, key trade-offs, post-mortems.

**Extraction prompt block:**

```
## Decisions & Learnings
Extract major decisions and learnings from the project:

### Key Decisions
For each major decision found in decision records, ADRs, README,
code comments, or architecture docs:
- What was decided
- Why (what problem it solved)
- What alternatives were considered and why they were rejected
- What was the outcome (if known)

### Learnings
For each learning, retrospective finding, or post-mortem:
- What was learned (the insight)
- What triggered it (what went wrong or right)
- What would be done differently

### Trade-offs
Any documented trade-offs (speed vs quality, build vs buy, etc.)
with the reasoning behind the choice made.

Do NOT include implementation details — focus on the WHY behind decisions.
```

**Imported to:** `imports/<project>/decisions-learnings.md`

**Loaded when:** Task involves architecture choices, repeating a past problem, or understanding why something was built a certain way.

---

### Slice 6: Roadmap

**Plain-language label:** *"Roadmap — what was planned, what's done, what's in progress, what's next"*

**What it captures:** Full roadmap with phases, milestones, completion status, owner tags, dependencies, abandoned items.

**Extraction prompt block:**

```
## Roadmap
Export the full project roadmap:
- All phases (current and future)
- All milestones within each phase
- All tasks within each milestone
- Status of each item: completed / in progress / planned / abandoned
- Owner tags (who was responsible for each item)
- Dependencies between items
- Notes on WHY items were abandoned or deprioritized (if documented)
- Completion dates for finished items (if available)

Preserve the full hierarchy: Phase > Milestone > Task.
Mark completed items clearly (e.g., with [x] or ✓).
```

**Imported to:** `imports/<project>/roadmap.md`

**Loaded when:** Step 7 (Roadmap Creation) only — for specialist review. NOT loaded during regular per-turn routing. This is reference material for planning, not working state.

**Special handling:** Imported roadmaps trigger the Roadmap Import Review flow (see `references/setup-flow.md` Step 7). Specialists review each item and recommend keep/adapt/drop/new. The imported roadmap is never adopted as-is.

---

### Slice 7: Codebase Patterns

**Plain-language label:** *"Code patterns — architecture style, folder structure, naming conventions, tech patterns"*

**What it captures:** Framework patterns, API design, file organization, coding conventions, testing approach.

**Extraction prompt block:**

```
## Codebase Patterns
Extract the architectural and coding patterns from the codebase:
- Folder structure: top-level directory tree (2-3 levels deep)
- Architecture pattern: monolith, microservices, serverless, monorepo, etc.
- API design style: REST, GraphQL, tRPC, RPC, etc.
- API conventions: URL patterns, versioning, error response format
- State management approach (if frontend): Redux, Zustand, Context, etc.
- Database: type (Postgres, MySQL, MongoDB, etc.), ORM/query builder,
  migration approach
- Authentication: approach and library (NextAuth, Clerk, WorkOS, etc.)
- Testing: framework, coverage approach, test file naming/locations
- Naming conventions: files, functions, components, routes, database tables
- Error handling pattern: how errors are caught, logged, and surfaced
- Environment config: how env vars are structured and loaded
- Any CONTRIBUTING.md, coding standards, or architecture docs found

Focus on PATTERNS, not implementation details. The goal is to understand
the conventions so a new project can follow them (or deliberately diverge).
```

**Imported to:** `imports/<project>/codebase-patterns.md`

**Loaded when:** Task involves code architecture, file structure decisions, or maintaining consistency with a related codebase.

---

## How CoS Builds the Composite Prompt

CoS assembles a single extraction prompt from the user's slice selections:

```
Export selected context from this project for use in a new project called
"<new project name>". Read the codebase and project files. Output everything
in a single file called `context-export.md` saved to the project root.

Do NOT include API keys, secrets, tokens, or passwords anywhere in the export.

# Context Export: <source project name>

<only the selected slice blocks appear here, concatenated in order>
```

**Example:** User selected Infrastructure + Design System + Project Context for the website project. CoS generates a single prompt containing only those 3 extraction blocks. The user pastes this one prompt, gets one file back, pastes the result into the new project session.

---

## Adding Slices After Setup

Users can add import slices mid-project without re-running setup:

1. User says something like "I need the design system from the website project"
2. CoS checks `imports/_manifest.md` — sees `website` exists but `design-system` wasn't imported
3. CoS generates only the Design System extraction prompt for that project
4. User pastes into old project session → gets result → pastes back
5. CoS writes to `imports/website/design-system.md`
6. CoS updates `imports/_manifest.md` with new slice and timestamp
7. No other files touched

If the user references a project not yet in the manifest, CoS treats it as adding a new related project — asks which slices to import, generates the composite prompt, and creates the import entry.

---

## Re-syncing an Existing Slice

When the user says "the website's infrastructure has changed, update the import":

1. CoS reads manifest to identify which slices exist for that project
2. Generates the extraction prompt for the slice(s) to re-sync
3. User pastes into source project session → gets updated export → pastes back
4. CoS overwrites the relevant file in `imports/<project>/`
5. Updates manifest timestamp for that slice
6. Flags differences to the team: *"The website now uses Clerk instead of WorkOS for auth. This might affect how we handle login in this project."*
