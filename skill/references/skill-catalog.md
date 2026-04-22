# Skill Catalog — Role to Skills Mapping

This is the reference personas use to pick skills per task. Not every skill is always needed. Each persona loads 1-3 skills per task based on what the prompt calls for.

**Lazy loading discipline:** never pre-load all skills from a menu. Read the task, pick the 1-3 most relevant skills, load those, execute.

**Namespace note (v3.1):** Project Studio v3.1 uses the `gstack-team:` plugin as a direct runtime dependency. All methodology-style skills that originated in the gstack workflow are referenced by their fully qualified plugin-namespaced names (e.g., `gstack-team:review`, `gstack-team:qa`, `gstack-team:retro`). Unqualified aliases like `review` or `retro` are no longer accepted — specialists must invoke the qualified form so the correct implementation loads. If the `gstack-team` plugin is not installed, see `references/connectors.md` §degraded-mode for substitutions. See `references/gstack-integration.md` for the full capability-to-skill mapping.

## Quick lookup (role → jump target)

Use this table to jump to the right section without scanning the whole file.

| Persona role | Primary section(s) | Common picks |
|---|---|---|
| Product Manager | Product Management | product-manager, jobs-to-be-done, write-spec |
| Engineer / Backend / Full-stack | Engineering | clean-code, system-design, gstack-team:investigate |
| Frontend Engineer | Engineering → Frontend specific | senior-frontend, frontend-design, motion-react-animations |
| Designer / UX | Design | refactoring-ui, ux-heuristics, design-system-architect |
| Researcher | Research | customer-research, mom-test, design:user-research |
| Marketer / Growth | Marketing & Growth | one-page-marketing, copywriting, cro-methodology |
| Salesperson / BD | Sales & Revenue | predictable-revenue, pricing-strategy, sales-enablement |
| Writer / Content | Content Creation & Writing | copywriting, content-strategy, doc-coauthoring |
| CoS / Meta | Process & Meta | gstack-team:context-save, gstack-team:retro, context-engineering-kit |
| Any persona (docs) | File Formats & Documents | docx, xlsx, pptx, pdf, gstack-team:make-pdf |
| Any persona (web) | Browser & Web | gstack-team:browse, firecrawl, connect-chrome |
| Plan author (any role) | Plan-Critique | gstack-team:plan-ceo-review, gstack-team:plan-eng-review, gstack-team:plan-design-review, gstack-team:plan-devex-review |
| Release engineer | Deploy & Ship | gstack-team:ship, gstack-team:canary, gstack-team:land-and-deploy |

**How to use this table:**
1. Match the persona's role to the first column.
2. Jump to the listed section below for the full catalog.
3. From that section, pick 1-3 skills specifically relevant to the current task. Do not default to "Common picks" without checking the prompt.

---

## Product Management

**Core:**
- product-manager — general PM practice
- inspired-product — empowered teams, discovery
- jobs-to-be-done — customer-centric framing
- write-spec / product-management:write-spec — specs & PRDs
- product-management:roadmap-update — roadmap maintenance
- product-management:sprint-planning — sprint design
- product-management:product-brainstorming — idea exploration
- product-management:metrics-review — metrics analysis
- product-management:stakeholder-update — status comms

**Adjacent:**
- lean-startup, lean-ux — validation
- mom-test — customer interviews
- continuous-discovery — research rhythm
- obviously-awesome — positioning
- traction-eos — accountability
- yc-startup-fundamentals — early-stage fundamentals
- yc-sv-development-framework — dev decisions
- gstack-team:office-hours — YC-style product interrogation

---

## Engineering

**Architecture:**
- clean-architecture — layered design
- system-design — distributed systems
- ddia-systems — data-intensive systems
- domain-driven-design — domain modeling
- saas-architecture-deep-dive — SaaS patterns
- software-design-philosophy — complexity management

**Code Quality:**
- clean-code — readability & discipline
- refactoring-patterns — safe refactors
- pragmatic-programmer — craftsmanship
- code-review-senior-perspective — PR review (companion to gstack-team:review)
- gstack-team:review — pre-land rigor review (Scope Drift Detection, Implementation/Test items)
- gstack-team:cso — OWASP + STRIDE security audit

**Performance & Reliability:**
- release-it — stability patterns
- high-perf-browser — web perf
- postgresql-performance-expert — db tuning
- vercel-react-best-practices — React perf

**Integration & Ops:**
- integration-patterns-mastery — API integrations
- devops-pathfinders — server ops
- gstack-team:ship — pre-merge disciplined flow
- gstack-team:land-and-deploy — merge + production deploy
- gstack-team:canary — progressive rollout with auto-rollback

**Debugging:**
- gstack-team:investigate — root cause analysis
- gstack-team:qa — live QA via headless browser
- webapp-testing — playwright testing

**Frontend specific:**
- senior-frontend
- frontend-design
- motion-react-animations

**Planning:**
- gstack-team:autoplan — end-to-end feature planning (intake → CEO review → impl plan)
- gstack-team:careful — raise rigor for high-stakes changes

---

## Design

**UX/UI:**
- ui-ux-pro-max — general UI/UX
- refactoring-ui — visual polish
- ux-heuristics — usability audit
- design-everyday-things — foundational design
- gstack-team:design-consultation — brand/design-system consultation
- design-system-architect / design-system-creation — systems
- design-html — production HTML/CSS
- design-shotgun — design variants

**Specialized:**
- web-typography
- top-design — award-tier web
- ios-hig-design — iOS native
- microinteractions — interaction polish
- motion-design / ui-animation — motion
- ui-design-styles — style references

**Design process:**
- design-thinking — 5-phase methodology
- design-sprint — 5-day sprints
- lean-ux — hypothesis-driven
- gstack-team:design-review — deployed-site visual audit (hierarchy, spacing, AI-slop checks)
- gstack-team:plan-design-review — plan-level design critique
- gstack-team:plan-devex-review — plan-level DX critique
- design:design-critique — Figma critique
- design:design-handoff — dev handoff
- design:accessibility-review — a11y audit
- design:design-system — system docs
- design:ux-copy — microcopy

---

## Research

- customer-research — research practice
- mom-test — interview technique
- continuous-discovery — research rhythm
- ethnographic-research-sim — simulated research
- jobs-to-be-done — JTBD framing
- design:user-research — research planning
- design:research-synthesis — synthesizing findings
- product-management:synthesize-research — research synthesis
- virtual-customer-research — synthetic personas
- india-market-intelligence — India market data
- article-extractor — source extraction
- firecrawl — web scraping
- lead-research-assistant — lead research

---

## Marketing & Growth

**Strategy:**
- one-page-marketing — full plan
- obviously-awesome — positioning
- storybrand-messaging — narrative
- made-to-stick — memorable messaging
- crossing-the-chasm — market adoption
- blue-ocean-strategy — market creation
- marketing:campaign-plan — campaigns
- marketing:competitive-brief — competition
- product-marketing-context — foundation
- competitor-alternatives — vs pages

**Copy:**
- copywriting — web copy
- copy-editing — editing
- cold-email — B2B outreach
- email-sequence — lifecycle emails
- marketing:email-sequence / marketing:draft-content
- social-content — social media
- content-research-writer — long-form
- technical-storytelling — technical content
- scorecard-marketing — quiz/assessment funnels

**SEO & Discovery:**
- seo-audit — SEO health
- ai-seo — LLM-era SEO
- schema-markup — structured data
- programmatic-seo — scaled pages
- content-strategy — editorial strategy
- marketing:seo-audit

**Paid & Ads:**
- paid-ads — platform strategy
- ad-creative — ad iterations
- competitive-ads-extractor — competitor ads

**Conversion:**
- cro-methodology — CRO fundamentals
- page-cro — landing page CRO
- popup-cro — modals
- form-cro — forms
- signup-flow-cro — signup
- onboarding-cro — activation
- paywall-upgrade-cro — upgrade flows
- churn-prevention — retention
- ab-test-setup — experiments
- analytics-tracking — measurement

**Launch & Growth:**
- launch-strategy — GTM
- landing-page-mastery — landing pages
- free-tool-strategy — free-tool marketing
- lead-magnets — gated content
- referral-program — virality
- contagious — word-of-mouth
- influence-psychology — persuasion
- marketing-psychology — behavioral science
- improve-retention — retention
- hooked-ux — habit loops
- drive-motivation — motivation design

**Brand:**
- brand-guidelines — visual brand
- brand-voice:enforce-voice / brand-voice:brand-voice-enforcement — voice
- brand-voice:guideline-generation — build guidelines
- brand-voice:discover-brand — discover materials
- marketing:brand-review — brand QA
- pathfinders-labs-brand-guidelines — specific brand

---

## Sales & Revenue

- predictable-revenue — outbound
- sales-enablement — collateral
- pricing-strategy — pricing
- hundred-million-offers — offer design
- revops — operations
- negotiation — tactics
- saas-financial-projections — projections
- saas-business-logic-analyst — billing audits

---

## Content Creation & Writing

- content-research-writer — research-backed writing
- copywriting / copy-editing
- content-strategy — e