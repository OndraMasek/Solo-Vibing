# Challenge checklist

Phase 3 of /discovery. Run every check below against the current idea brief and the Phase 2 research findings. This is adversarial by design — the job is to find the reason this idea fails, not to confirm it works. If every iteration approves, the checklist is too soft; sharpen it.

Auditor stance (per `rules/auditor-stance.md`): state each finding as a fact, not a feeling. "Market sizing found ~400 reachable entities" — not "the market might be a bit small." No reassuring closers. Prefix genuine hypotheses with `uncertain:` and say what would resolve them.

For each check: record PASS / FAIL / UNCERTAIN and a one-line finding. The verdict rubric at the bottom maps the pattern of results to one of four verdicts.

## A. Problem reality

- **C1 — Is the problem real?** Did Phase 2 problem-validation find independent evidence, or only the founder's assertion? FAIL if the only evidence is the founder's own intuition.
- **C2 — Is it painful enough?** Would the segment rank this a top-5 pain, or a minor annoyance they'd never pay to remove? FAIL if it's an annoyance.
- **C3 — Is it frequent enough?** A real, painful, once-a-year problem rarely sustains a product. FAIL if the occurrence rate is too low to build a habit or a renewal.
- **C4 — Does the segment already solve it acceptably?** If the current workaround is "good enough" for the segment, the wedge is thin. FAIL if no one is actually unhappy with the status quo.

## B. Market

- **C5 — Is the reachable market big enough?** Not the total market — the slice a solo founder with no distribution can realistically reach. FAIL if Phase 2 sizing came back too small to sustain the founder's goal.
- **C6 — Is the willingness-to-pay real?** Evidence the segment pays for adjacent things, not just that they'd "love" a free version. FAIL if the segment is structurally non-paying.

## C. Competition & differentiation

- **C7 — Is the space a graveyard?** An "empty" market is often empty because it was tried and failed. FAIL if competition research found dead competitors and no clear reason this attempt is different.
- **C8 — Is the differentiation defensible?** Does `{{SOLUTION}}`'s difference survive a competitor copying it in a weekend? FAIL if the only moat is "we did it first."
- **C9 — Is it 10x, or 10%?** Switching costs are real; a marginally-better product doesn't move people. FAIL if the improvement over the current workaround is incremental.

## D. Solution viability

- **C10 — Is the value obvious on first use?** Or does it require a leap of faith the segment won't take? FAIL if adoption depends on trust the founder hasn't earned.
- **C11 — Does the mechanism actually work?** Did Phase 2 find analogous mechanisms succeeding, or is this an untested causal story? UNCERTAIN is acceptable here; FAIL if Phase 2 found the mechanism failing in adjacent spaces.

## E. Technical feasibility

- **C12 — Is it buildable solo at ~20 hr/week?** FAIL if Phase 2 feasibility flagged team-scale work, significant capital, or a research-grade unsolved problem.
- **C13 — Are the external dependencies safe?** APIs, platforms, data sources that could change terms, raise prices, or disappear. FAIL if a single dependency can kill the product.

## F. Founder-fit & timing

- **C14 — Is founder-fit real?** Domain knowledge, unfair access, lived experience — or just enthusiasm? FAIL if "I want to" is the whole answer.
- **C15 — Are the capability gaps closable?** FAIL if a gap is structural (needs a co-founder or a skill that takes years), not closable by learning or tooling.
- **C16 — Does "why now" hold up?** Did Phase 2 confirm something actually changed, or is the window imagined / already closed? FAIL if "why now" collapsed under research.

## G. Internal consistency

- **C17 — Does the brief contradict itself?** E.g. a niche segment paired with a mass-market sizing claim. FAIL on unresolved internal contradiction.
- **C18 — Do the AI-recommended fields hold up?** Scrutinize every `(ai-recommended)` field harder than `(user)` fields — these are guesses, not founder conviction. FAIL if a load-bearing field is an unvalidated AI guess.
- **C19 — Did Phase 1's stated risks get addressed?** The founder named risks in north-star Q5. FAIL if Phase 2 confirmed a named risk is fatal and unmitigated.

## Verdict rubric

Map the pattern of results to one verdict. When patterns overlap, the more severe verdict wins.

- **kill** — any FAIL in section A (problem reality) that Phase 2 confirmed and Phase 4 can't realistically fix; OR a structural FAIL in C12 / C13 / C15 (can't be built / can't be sustained / can't be staffed by this founder); OR 3+ FAILs spread across A-E with no credible refine path.
- **pivot** — the problem is real (section A largely PASSes) but the framing is wrong: FAIL on C8/C9 (no defensible 10x) AND/OR C14/C16 (founder-fit or timing wrong) — i.e. a good problem, wrong solution or wrong founder-framing. Pivot keeps the problem, discards the current approach.
- **refine** — FAILs and UNCERTAINs that are real but addressable by editing the brief: internal contradictions (C17), unvalidated AI-recommended fields (C18), thin-but-fixable differentiation, a too-broad segment. Phase 4 proposes specific edits and the idea returns to Phase 3.
- **approve** — no FAILs in sections A-E; any remaining UNCERTAINs are non-load-bearing or have a clear resolution path; internal consistency holds. Proceed to Phase 5 approve branch.

A `refine` verdict at the iteration cap with no founder extension converts to `kill` with the note "iteration cap reached without convergence" — repeated refine-at-cap usually means attachment to a flawed premise.
