<!--
chat-end-card.md — the canonical group-exit card template for Solo-Vibing v0.2 cascade.

Binding spec: D2.3 v1.3 §Chat-end card template (template body and three render variants carried forward verbatim from v1.2; v1.3 amendment 2 corrects the handoff-prompt fence's "Read first" path to `.cascade/run-state.json` per D2.1 v2.1's canonical path).

═══ Renderers ═══

Every group-exit skill renders this template at its Group-exit branch:
  - Pattern T  `/onboard`        (Group A exit)
  - Pattern P  `/discovery`      (Group B exit)
  - Pattern M  `/constitution`   (Group C exit)
  - Pattern F  `/specify`        (Group D exit)
  - Pattern C  `/update-linear`  (Group E exit, chain's last stage)
  - Pattern C  `/wrap`           (Group F exit, chain's last stage)
  - Pattern G  `/verify`         (Group G exit)
  - Pattern N  `/retro`          (Group H exit → renders the terminal variant only)

Per-skill variant-selection logic lives in each skill's /Chains section
(see child_B_chains_sections.md for the v0.2 authored set).

═══ Four variants ═══

  - normal           — base body; both <optional> additive blocks empty
  - reset-triggered  — base body + reset-framing additive block
                       (Group F only; fires when D2.2 band-3 triggered the exit)
  - manual-halt      — base body + manual-halt-framing additive block
                       (any group; fires when /cascade-halt set
                        cascade:run-state.manual_halt = true; can co-occur with
                        reset-triggered if a manual halt followed a band-3 reset)
  - terminal         — base body MINUS the HANDOFF PROMPT fence section,
                       with the "Next:" line in §Where we are in the cascade
                       replaced by the terminal-form text
                       (Group H only, fires after /retro seal)

═══ Variant encoding ═══

The <!-- variant: normal --> block contains the full base body. The other
three variants hold only delta content. The renderer applies the deltas as:

  - reset-triggered:   append the block's content after the HANDOFF PROMPT fence
  - manual-halt:       append the block's content after the HANDOFF PROMPT fence
                       (or after the reset-triggered block if both fire)
  - terminal:          strip the HANDOFF PROMPT fence section from the base body
                       AND replace the "Next:" line in §Where we are in the
                       cascade with this block's content

The renderer (the skill's /Chains Group-exit branch) strips all
<!-- variant: ... --> and <!-- /variant --> markers from the rendered card
before emitting; the markers exist only here for renderer guidance.

═══ Field origins ═══

Filled from cascade:run-state.json directly:
  <MARKER>                  ← .marker
  <product>                 ← .product
  <parent_feature_name>     ← .parent_feature_name
  <milestone-id>            ← .active_milestone
  <N> (Queue version)       ← .queue_version
  <ticket-id-or-N/A>        ← .next_ticket  (or .active_stages[0].ticket if mid-build)
  <timestamp>               ← .last_group_exit_at

Computed at render time:
  <X>, <this-group>         ← group letter from .last_completed_group
  <group-name>              ← derived from the group letter
                              (A=Onboarding, B=Discovery, C=Constitution,
                               D=Specify, E=Plan-Review-Linear, F=Build-Wrap,
                               G=Verify, H=Retro)
  <next-group-letter>       ← .last_completed_group + 1
  <next-stage>              ← the first stage of <next-group-letter>
  <next group name>         ← derived from <next-group-letter>
  Completed list            ← groups A through .last_completed_group
  <N> chat boundaries
    to terminal milestone   ← remaining queue length + remaining group count
  <one-sentence summary>    ← exit manifest's outputs.summary
                              (per D2.1 v2.1 common-manifest-fields;
                               per D4.6 v1.1 §CLI surface)
  <artifact> entries        ← exit manifest's outputs array, in declared order
                              (per D4.6 v1.1 §CLI surface — no flattening across
                               manifests; the exit manifest aggregates the group's
                               externally-visible artifacts by construction)
  <16-char-prefix> for
    Last sealed manifest    ← sha256 prefix of the manifest file at
                              .last_completed_group_exit_manifest_path
                              (per D2.3 v1.3 §Handoff verification predicate
                               schema additions)
  <16-char-prefix> for
    Handoff sha             ← sha256 prefix of THIS card body, computed per the
                              Handoff sha exclusion rule below

═══ Handoff sha exclusion rule (CRITICAL) ═══

The "Handoff sha: <16-char-prefix>" line in §Cascade state is EXCLUDED from the
card-body sha computation. The renderer computes sha256 over the markdown from
the opening ═══ row to the closing ═══ row, inclusive, with the Handoff sha
line removed (or skipped) before hashing. The computed prefix is then embedded
back as the Handoff sha line value, and the full card (with the embedded sha)
is what gets written to .cascade/handoff/last.md and emitted inline.

See D2.3 v1.3 §Group-exit mechanics atomicity step 1 for the full write
sequence; see D2.3 v1.3 §Handoff verification predicate checks 1–3 for the
verification side that re-checks the sha at every new-chat paste.

═══ Round-trip property with D4.6 v1.1 ═══

D4.6 v1.1's `solo-cascade resume [<group-letter>]` re-derives every field this
template carries from cascade:run-state.json + the named exit manifest at
.last_completed_group_exit_manifest_path. Round-trip correctness is the file's
verification criterion: substitute fields into this template → compute its
Handoff sha → verify against the on-disk card's embedded Handoff sha and the
re-derived card's recomputed Handoff sha. The
`test_chat_end_card_round_trip_with_solo_cascade_resume` integration test in
Child A's failing-test seed asserts this property (deferred until D4.6 v1.1
implementation lands).
-->

<!-- variant: normal -->
═══════════════════════════════════════════════════════════
GROUP <X> COMPLETE — <group-name>
═══════════════════════════════════════════════════════════

## What just happened
<one-sentence summary of the group's work>

## What was produced
- <artifact 1> at <path>
- <artifact 2> at <linear-ticket-or-doc-id>
- ...

## Where we are in the cascade
Completed: <group A name>, <group B name>, ..., <this group name>
Next: <next group name>
Estimated remaining: <N> chat boundaries to <terminal milestone>

## Cascade state
- Marker: <MARKER>
- Active product: <product>
- Parent feature: <parent_feature_name>
- Active milestone: <milestone-id>
- Queue version: <N>
- Last sealed manifest: <ticket-stage>.json (sha256: <16-char-prefix>)
<!-- The Handoff sha line below is EXCLUDED from card-body sha computation per D2.3 v1.3 §Group-exit mechanics atomicity step 1. -->
- Handoff sha: <16-char-prefix>
- Run-state lock: released

## ▼ HANDOFF PROMPT — copy everything between the fences ▼

```
Resume cascade at <next-stage>.

Marker: <MARKER>
Product: <product>
Parent feature: <parent_feature_name>
Group entry: <next-group-letter>
Active ticket: <ticket-id-or-N/A>
Active milestone: <milestone-id-or-N/A>
Queue version: <N>
Prior group exit: <this-group> sealed at <timestamp>
Read first:
  - cascade:run-state from .cascade/run-state.json
  - <next-stage>'s primary input: <path or linear-id>

Continue per the cascade's autonomy mode in .solo-config.json.
```

## ▲ END HANDOFF PROMPT ▲
<!-- /variant -->

<!-- variant: reset-triggered (delta: append after HANDOFF PROMPT fence; Group F only; fires when D2.2 band-3 triggered the group exit) -->
Reset reason: token band 3 reached at cycle 2. The handoff prompt above is the only thing you need; cascade state has been flushed and the new chat will hydrate fully.
<!-- /variant -->

<!-- variant: manual-halt (delta: append after HANDOFF PROMPT fence, or after the reset-triggered block if both fire; any group; fires when /cascade-halt set cascade:run-state.manual_halt = true) -->
Manual halt at <timestamp>. Reason: <founder-supplied or 'unspecified'>. The new chat will surface §manual-halt-pending for confirmation before resuming.
<!-- /variant -->

<!-- variant: terminal (delta: strip the HANDOFF PROMPT fence section from the base body AND replace the "Next:" line in §Where we are in the cascade with the line below; Group H only, fires after /retro seal) -->
Next: open a new spec via `/specify` in a new chat to begin the next feature.
<!-- /variant -->
