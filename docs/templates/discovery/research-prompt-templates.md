# Research prompt templates

Phase 2 of /discovery. Five mandatory research areas, plus founder-selected tier-2 areas. Each prompt below is passed to the research-investigator agent, which runs deep research and returns structured findings.

Freshness rule (enforced by the agent): for any ecosystem-velocity topic — tooling, competitor features, pricing, regulation — sources older than 6 months are treated as stale and must be re-verified or discarded.

---

## Mandatory 1 — Problem validation

> Investigate whether **{{SEGMENT}}** actually experiences **{{PROBLEM}}** as a real, painful, frequent problem — or whether it's a problem the founder imagines they have.
>
> Find: evidence the problem is real (forum complaints, support threads, survey data, existing paid workarounds); how the segment currently solves it and what that costs them in time/money/frustration; how frequently the problem occurs; whether the segment would recognize this as a top-5 pain or a minor annoyance.
>
> Report disconfirming evidence explicitly — if the problem looks weak or niche, say so.

## Mandatory 2 — Market sizing

> Estimate the realistic addressable market for a solution to **{{PROBLEM}}** aimed at **{{SEGMENT}}**.
>
> Find: how many entities are in the segment; what fraction plausibly have the problem acutely enough to pay; comparable products' user counts or revenue as a sanity check; whether this is a "thousands of customers at low price" or "dozens at high price" shape, or too small to sustain anything.
>
> Distinguish total market from realistically-reachable market for a solo founder with no distribution. Give ranges, not false precision.

## Mandatory 3 — Competition

> Map the competitive landscape for solutions to **{{PROBLEM}}**.
>
> Find: direct competitors (same problem, same segment); indirect competitors and DIY/manual workarounds; for the top 3-5, what they do well, where they're weak, their pricing, their apparent traction; whether the space is crowded-but-bad, crowded-and-good, or genuinely empty (and if empty, why — often that's a graveyard signal, not an opportunity).
>
> Be specific about where **{{SOLUTION}}** would actually differ, and whether that difference is defensible or trivially copied.

## Mandatory 4 — Solution viability

> Assess whether **{{SOLUTION}}** would actually solve **{{PROBLEM}}** for **{{SEGMENT}}** well enough that they'd adopt and pay.
>
> Find: evidence that this *mechanism* works (analogous solutions in adjacent spaces, prior attempts and why they succeeded or failed); adoption friction — what the segment has to change, learn, or trust; whether the value is obvious on first use or requires a leap of faith; switching costs from current workarounds.
>
> Surface the strongest reason a member of {{SEGMENT}} would try this once and never return.

## Mandatory 5 — Technical feasibility

> Assess whether **{{SOLUTION}}** is buildable by a solo technical founder at roughly 20 hr/week.
>
> Find: the hard technical problems and whether they're solved-and-libraried or genuinely research-grade; external dependencies (APIs, platforms, data sources) and their reliability, cost, and terms-of-service risk; the realistic shape of a v0.1 that's small enough to ship but real enough to validate; where {{RISKS}} intersect the technical plan.
>
> Flag anything that would require a team, significant capital, or a breakthrough — those are kill signals for a solo build.

---

## Tier-2 prompts (founder-selected)

Run only the ones relevant to this idea. The founder picks at the end of Phase 1; common ones:

### Regulatory / compliance

> Investigate the legal, regulatory, and compliance landscape for offering **{{SOLUTION}}** to **{{SEGMENT}}**. Licensing, data-protection obligations, jurisdiction-specific rules, liability exposure, and which of these are blockers vs manageable overhead for a solo founder.

### Go-to-market channels

> Investigate how a solo founder with no audience would actually reach **{{SEGMENT}}** for **{{SOLUTION}}**. Which channels the segment is reachable on, what acquisition looks like for comparable products, organic vs paid viability, and the realistic cost and time to first 100 users.

### Pricing

> Investigate pricing for **{{SOLUTION}}** aimed at **{{SEGMENT}}**. What comparable products charge and on what model (subscription / usage / one-time); the segment's willingness and ability to pay; price anchors already set by competitors; whether free-tier expectations make monetization hard.

### Timing / "why now"

> Pressure-test the claim that **{{WHY_NOW}}** makes this viable today. What specifically changed (technology, cost curves, regulation, behavior); whether the window is opening or already closing; whether earlier attempts failed on timing or on something more fundamental.

### Founder-fit / capability gap

> Investigate what building and running **{{SOLUTION}}** demands that the founder may lack, and how solvable each gap is — what's learnable in weeks, what needs a partner or hire, what's a structural mismatch.

---

## Output contract

Every prompt run produces, via the research-investigator agent:

1. A deep report at `docs/research/NNNN-<slug>.md`.
2. A `## Artifact` block of summary findings, which /discovery turns into a Linear research summary `[<MARKER>-DOC-NNNN] research: <topic>` using the CF2 structure.

Findings the agent is not confident about are prefixed `uncertain:` and carry what would resolve the uncertainty. A mandatory prompt that produces no deep report is a `BLOCKED` for /discovery — mandatory prompts cannot be skipped.
