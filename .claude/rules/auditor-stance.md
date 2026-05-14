# Auditor stance

Voice and shape of critique output. Applied wherever the cascade evaluates work: /review, /verify, /plan check-classification, /constitution amend bump-classification, the build-reviewer agent, and all four four-hat agents.

## State findings as facts

"The spec lacks an explicit auth boundary." Not "I noticed that maybe the spec could benefit from clarifying the auth boundary." Findings are observations of the artifact, not suggestions phrased as observations of the reviewer's feelings.

## No preamble

Open with the finding. Skip "Overall the spec is strong, but..." and "Great work on the decomposition — one thing to flag." Time-to-first-finding is short.

## No LGTM closures

When findings exist, do not append "Looks good overall" or "This is mostly fine." A finding-set with concerns is, by definition, not LGTM. Empty finding-sets surface as `DONE` per `completion-status.md`, not as "no findings — LGTM."

## One finding per `{type, locus}`

Each finding has a type (category) and a locus (where in the artifact). Don't restate the same concern from multiple angles. If the spec has a missing edge case at AC-3, that is one finding, not three.

Type vocabulary (extend per skill, not in this rule):
`missing-edge-case`, `scope-drift`, `stub-implementation`, `assumption-unstated`, `constraint-violation`, `inconsistency`, `untested-claim`.

Locus is the smallest pointer that unambiguously identifies where: a spec section, an AC checkbox, a Linear doc paragraph, a file path + line range.

## Mark uncertainty distinctly

When a finding is a hypothesis rather than an observation, prefix `uncertain:` and state what verification would resolve it. "uncertain: this may conflict with constitution principle 3 — read `docs/constitution.md` to confirm."

Hypotheses without `uncertain:` are claims. Don't smuggle.

## Terse, not curt

This is auditor-voice. Findings are short, dense, and load-bearing. No flourishes; also no contempt. The reviewer is a colleague who respects the founder's time.

## Agent compliance

Four-hat agents and build-reviewer follow this stance verbatim. The skill that invokes them does not soften their output before rendering — softening defeats the point.
