# Registers

Registers are **append-only** files that capture decisions, assumptions, risks, open questions, and learnings as the project progresses. They are the project's long-term memory. Never edit historical entries — only append.

All registers live in `registers/` (assumptions, risks, open-questions, learnings) or `decisions/` (ADR-style decisions).

## Why registers matter

- **Durability:** surviving context compaction.
- **Accountability:** why did we decide X? Who owned it?
- **Audit:** what were we betting on, and did those bets pay off?
- **Learning:** what surprised us, and how should future decisions change?

---

## assumptions.md

Everything the plan is betting on. Revisit regularly.

```markdown
# Assumptions

## Active

### A-<N> — <short title>
**Assumed:** <YYYY-MM-DD>
**By:** <persona or user>
**Statement:** <what we're assuming to be true>
**Confidence:** <low / medium / high>
**Impact if wrong:** <what breaks>
**Test plan:** <how will we validate>
**Status:** active

### A-<N+1> — ...

## Validated

### A-<N> — <title>
**Assumed:** <date>
**Validated:** <date>
**Outcome:** true | false | partially
**Notes:** <one line>

## Invalidated

### A-<N> — <title>
**Assumed:** <date>
**Invalidated:** <date>
**Reality:** <what's actually true>
**Impact:** <what we changed in response>
```

**When to append:** whenever a specialist or user asserts something the plan depends on, but it hasn't been tested.

---

## risks.md

What could kill or damage the project.

```markdown
# Risks

## Active

### R-<N> — <short title>
**Logged:** <YYYY-MM-DD>
**By:** <persona>
**Description:** <what could go wrong>
**Likelihood:** <low / medium / high>
**Impact:** <low / medium / high>
**Severity:** <low / medium / high / critical>  (= likelihood × impact)
**Owner:** <persona responsible for mitigation>
**Mitigation:** <plan to prevent or reduce>
**Trigger:** <what would signal this is becoming real>
**Status:** active

## Mitigated

### R-<N> — ...
**Mitigated:** <date>
**How:** <what was done>

## Realized

### R-<N> — ...
**Realized:** <date>
**Impact:** <what actually happened>
**Response:** <what we did>
```

**When to append:** whenever a specialist flags something concerning during critique or planning.

---

## open-questions.md

Things punted for later. Revisit before major decisions.

```markdown
# Open Questions

## Unresolved

### Q-<N> — <short question>
**Raised:** <YYYY-MM-DD>
**By:** <persona or user>
**Question:** <the actual question>
**Why it matters:** <what depends on this>
**Who to ask:** <who might know>
**Blocks:** <roadmap items blocked, or "none">
**Status:** unresolved

## Resolved

### Q-<N> — <question>
**Raised:** <date>
**Resolved:** <date>
**Answer:** <what we concluded>
**Resolved by:** <persona or user>
```

**When to append:** anytime a question comes up that isn't answered immediately. Better to capture than forget.

---

## learnings.md

Surprises — what happened that we didn't expect, and what it changes.

```markdown
# Learnings

### L-<N> — <short title>
**Date:** <YYYY-MM-DD>
**Context:** <what we were doing>
**Surprise:** <what we didn't expect>
**Implication:** <what this changes>
**Surfaced by:** <persona>

### L-<N+1> — ...
```

**When to append:** whenever something is genuinely surprising (good or bad). Not every observation — only things that shift the project's understanding.

---

## decisions/ — ADR-style records

One file per significant decision. Format:

```markdown
# D-<N> — <short decision title>

**Date:** <YYYY-MM-DD>
**Status:** accepted | superseded by D-<M> | reversed
**Decision maker:** <user, or delegated persona>

## Context
<What situation led to this decision? 2-4 sentences.>

## Options considered
1. **<Option A>** — <one-line summary>
2. **<Option B>** — <one-line summary>
3. **<Option C>** — <one-line summary>

## Decision
<Which option was chosen and why. 2-4 sentences.>

## Consequences
- <Positive consequence>
- <Negative consequence or tradeoff>
- <Open question or new assumption>

## Specialists consulted
- [Role — position they took]
- [Role — dissenting position, if any]
```

**When to create:** significant decisions — architectural choices, scope changes, strategic pivots, team changes, pricing decisions, etc. Not every small decision.

**File naming:** `decisions/D-<NNN>-<slug>.md` e.g., `decisions/D-001-pick-postgres-over-mongo.md`

---

## known-discrepancies.md (existing-projects only)

Populated during Step 6 of setup when audit finds doc vs. reality gaps that weren't fixed.

```markdown
# Known Discrepancies

### <YYYY-MM-DD> — <short title>
**Docs say:** <claim in docs>
**Reality:** <what was found>
**Surfaced by:** <persona>
**Decision:** not fixed — <reason>
**Impact:** <why we accept this>
```

---

## audit-log.md (existing-projects only)

Populated during Step 6 of setup.

```markdown
# Audit Log

## <YYYY-MM-DD> — Initial audit
**Scope:** <what was audited>
**Auditors:** <personas involved>
**Discrepancies found:** <count, or "none">
**Discrepancies fixed:** <count>
**Discrepancies accepted:** <count>
**Summary:** <one paragraph>
```

---

## Rules for all registers

1. **Append-only.** Never delete entries. If something is wrong, add a correction entry.
2. **Every entry has a date and an owner.**
3. **Every entry has a status** where applicable. Move entries between status sections as states change.
4. **Terse and specific.** Registers are for scanning, not reading cover-to-cover.
5. **Reviewed in retros.** Milestone-triggered retros (standard/heavy projects — see Invariant #22) scan each register. If the milestone cadence is itself weekly, retros become weekly by side-effect; CoS does not schedule retros on a fixed calendar.

## How personas use registers

During critique, personas look at registers to:
- Check whether the proposal validates or contradicts active assumptions
- See if proposal addresses or ignores active risks
- See if p