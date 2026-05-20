# Child A — chat-end card authoring notes

**Authored:** 2026-05-19 (paired session with `chat-end-card.md` deliverable).
**Phase:** Child 0001-A — `v0.2-templates-and-config` (walking-skeleton strategy).
**Spec basis:** D2.3 v1.3 §Chat-end card template (binding); D2.1 v2.1 (canonical run-state path); D4.6 v1.1 §CLI surface (round-trip counterparty); `decomposition.md` Child 0001-A scope.
**Status:** Drafted. Variant-encoding choice surfaced for founder ratification; otherwise authored.

---

## What this session produced

One template file: `docs/templates/chat-end-card.md`. Authored against D2.3 v1.3's binding spec with v1.3 amendment 2 applied (handoff-prompt fence's "Read first" path corrected to `.cascade/run-state.json` per D2.1 v2.1).

The file lands in the v0.1 `docs/templates/` directory per `repo-state-summary.md` Part 1; per D2.3 v1.3 §Cross-references, the chat-end card is **explicitly not** a D4.1 (template bug batch) item — Child A is its authorship lane.

## Variant-encoding decision (surfaced for founder ratification)

The handoff flagged this as TBD: comments-or-conditional-text matching `spec.md.template`'s convention, or four separate template files. I authored the **comments-or-conditional-text default** per the handoff's preference, with this specific encoding:

- `<!-- variant: normal -->` contains the **full base body**.
- The other three variants contain **only delta content**:
  - `<!-- variant: reset-triggered -->` — append-after-fence additive block.
  - `<!-- variant: manual-halt -->` — append-after-fence additive block (may co-occur with reset-triggered).
  - `<!-- variant: terminal -->` — replacement content for "Next:" line, paired with strip-the-fence directive (in the marker description).

**Why this and not four complete bodies.** Three of the four variants share ~95% of their content with the normal variant. Encoding four full bodies would multiply the maintenance burden by 4×: a single edit to the base body (e.g., a field rename or a §Cascade state addition) would need to propagate to all four copies, and the four copies would inevitably drift over time. Encoding three of the variants as deltas keeps the base body authoritative and the variants minimal.

**Why this and not `<!-- variant: ... -->` blocks scattered through the base body** (the "not-terminal vs terminal" sub-marker approach I considered first). That approach is more elegant for a *renderer* but harder for a *reader* to scan and harder to assert against in a smoke test — the four variant names wouldn't all appear literally in the file, and `test_chat_end_card_template_has_four_variants` would have to assert variant-name-set semantics rather than marker presence.

**Why this and not four files** (`chat-end-card.md` + `chat-end-card-terminal.md` + …). Four files is what you'd reach for if the variants were genuinely distinct templates with little overlap. They aren't. Three of the four are textual deltas of ~1 sentence each on top of a shared body.

**The renderer's view.** The renderer (each skill's `/Chains` Group-exit branch) reads `docs/templates/chat-end-card.md`, identifies the selected variant from runtime state, and applies the delta. For the additive variants (reset-triggered, manual-halt), the delta is "append the block's content after the HANDOFF PROMPT fence." For the terminal variant, the delta is "strip the HANDOFF PROMPT fence section AND replace the 'Next:' line." The leading comment block in the template file documents both of these renderer rules explicitly.

**The reader's view.** When a person opens `docs/templates/chat-end-card.md` to understand "what does a chat-end card look like," they see the full normal-variant body first (the most common case) and then three short delta blocks. The leading comment block frames everything.

**Item to ratify with the founder.** If the preference is actually four-complete-bodies-in-one-file (each `<!-- variant: ... -->` block holding a full body), the redesign is straightforward — duplicate the base body into each of the three derivative variants and inline the deltas. Cost: ~3× the file length, but the renderer's logic simplifies to "extract the marked block, substitute fields, emit." I'd accept that trade if the founder prefers reader-side simplicity over file-size minimality.

## F-Usr-3 disposition (Project Instructions step 5 acknowledgment)

The handoff flagged F-Usr-3 as potentially surfacing during this authoring: the v1.3 Project Instructions step 5 acknowledgment ("emit a short 'Resuming cascade at <next-stage>' acknowledgment naming Marker, Product, Parent feature, Active ticket, Active milestone — for founder verification — and proceed") is heavy if the chat-end card already names those fields. The question is whether the new chat should re-emit them.

**Disposition for this session: deferred, not blocking.** The template's authoring is orthogonal to F-Usr-3 — the template defines what the *card* says; F-Usr-3 is about what the *new chat at startup* says after parsing the pasted card. The new chat's verification flow is the SessionStart-equivalent in chat-Claude (a project-instruction-driven flow in Groups A–E, G, H; a SessionStart hook in Group F). That flow is owned by:

- For chat-Claude groups: the Project Instructions paste-block content (D2.3 v1.3 §Project Instructions block), authored by `/onboard` (D2.3 v1.3 §`/onboard` integration point).
- For Group F: the SessionStart=startup hook, authored by Child C (`.claude/hooks/`).

So F-Usr-3's resolution lives in Project Instructions text (chat-Claude) or hook output (Group F), not in `chat-end-card.md`. Surface it to subsequent Child A sessions when the Project Instructions block is authored (Child A includes `.solo-config` schema additions; if Project Instructions text is also under Child A's scope per `decomposition.md`, F-Usr-3 surfaces there), or to Child C when the hook output shape is authored.

**Note carried forward for the queue.** F-Usr-3 remains in the partially-absorbed-inline queue from this session's predecessor (per the v1.2 + D4.6 paired review). Subsequent Child A or Child C sessions own the disposition.

## Failing-test seed for Child A's chat-end card slice

Per Child A's walking-skeleton strategy, the failing-test seed assertions live in the spec's §Failing-test seed section (will be authored under D3.2's pyramid declaration when Child A's `/specify` runs). For now, the test sketches:

### `test_chat_end_card_template_exists` — `[smoke]`

**Assertion.** `docs/templates/chat-end-card.md` exists and is non-empty.

**Why.** The simplest viability check; if the file is missing, every downstream test fails for the wrong reason. Covers Child A AC for "the chat-end card template ships."

**Test path (pytest-flavored sketch):**
```python
from pathlib import Path
def test_chat_end_card_template_exists():
    path = Path("docs/templates/chat-end-card.md")
    assert path.exists(), "template missing"
    assert path.stat().st_size > 0, "template empty"
```

### `test_chat_end_card_template_has_four_variants` — `[smoke]`

**Assertion.** The file contains the four `<!-- variant: <name> -->` markers literally, one per variant.

**Why.** Asserts the variant-encoding scheme is present and the variant set isn't accidentally truncated. The four markers are the contract the renderer keys on; missing any of them means at least one render path is broken.

**Test path:**
```python
def test_chat_end_card_template_has_four_variants():
    text = Path("docs/templates/chat-end-card.md").read_text()
    for name in ("normal", "reset-triggered", "manual-halt", "terminal"):
        assert f"<!-- variant: {name}" in text, f"missing variant: {name}"
```

Note the loose `<!-- variant: {name}` substring match (no trailing space/quote) — accommodates the variant-marker descriptions in the file (e.g., `<!-- variant: reset-triggered (delta: append after HANDOFF PROMPT fence; ...) -->`) without requiring the test to know the exact descriptor wording.

### `test_chat_end_card_template_excludes_handoff_sha_from_body` — `[unit]`

**Assertion.** The template contains a comment encoding the Handoff sha exclusion rule (the rule that the `Handoff sha:` line is excluded from card-body sha computation).

**Why.** The rule is load-bearing for D2.3 v1.3 §Group-exit mechanics atomicity step 1 and §Handoff verification predicate checks 1–3. If the rule isn't documented in the template, the renderer (especially a chat-Claude renderer reading the template fresh) may inadvertently include the line in the sha computation, producing cards that fail check 1 at every new-chat paste.

**Test path:**
```python
def test_chat_end_card_template_excludes_handoff_sha_from_body():
    text = Path("docs/templates/chat-end-card.md").read_text()
    # Either of these substrings indicates the rule is documented:
    rule_present = (
        "EXCLUDED from card-body sha computation" in text
        or "excluded from card-body sha" in text.lower()
    )
    assert rule_present, "Handoff sha exclusion rule not documented in template"
```

### `test_chat_end_card_round_trip_with_solo_cascade_resume` — `[integration]` (deferred)

**Assertion.** `solo-cascade resume --json` against a synthetic `cascade:run-state.json` produces field values that, when substituted into the template, yield a card whose recomputed `card_content_sha256` matches the round-trip computation.

**Why.** This is the file's correctness criterion w.r.t. D4.6 v1.1. If the template carries fields D4.6 v1.1 doesn't re-derive (or omits fields D4.6 v1.1 does re-derive), the round-trip fails and `solo-cascade resume` as a recovery path silently breaks.

**Deferral.** Marked `[integration]` and deferred until D4.6 v1.1 implementation lands (Phase 4, Child D — `tools/solo-verify` and related CLI tooling). For now, the test is documented as a seed; the implementation slot lives in the same Phase 4 session that lands `solo-cascade resume`.

**Test path (sketch for when D4.6 v1.1 implementation is available):**
```python
def test_chat_end_card_round_trip_with_solo_cascade_resume(tmp_path):
    # Set up synthetic cascade:run-state.json + a synthetic exit manifest
    # Run `solo-cascade resume --json` against it
    # Substitute its output into docs/templates/chat-end-card.md (normal variant)
    # Compute card_content_sha256 over the resulting card body (excluding Handoff sha line)
    # Assert match against D4.6 v1.1's own re-derived sha
    ...
```

## Round-trip property statement

The template's correctness w.r.t. the rest of the cascade is the **round-trip property**:

> For every (cascade:run-state.json, exit manifest, variant) tuple, the card rendered by substituting fields into `docs/templates/chat-end-card.md` is byte-for-byte equivalent (modulo whitespace normalization) to the card re-derived by D4.6 v1.1's `solo-cascade resume`.

Two halves of the property:

1. **Render → re-derive.** A card emitted by a skill's `/Chains` Group-exit branch is reproducible by `solo-cascade resume` from the same cascade:run-state and exit manifest. Tested by `test_chat_end_card_round_trip_with_solo_cascade_resume`.

2. **Re-derive → verify.** A card re-derived by `solo-cascade resume` passes the v1.3 §Handoff verification predicate's nine checks when pasted into a new chat. Tested by the predicate's own integration tests (out of scope for Child A; lives in Child C/Child D).

The Handoff sha exclusion rule is the linchpin of both halves: the rule defines what content the sha covers, which both the renderer and `solo-cascade resume` must agree on. Documenting the rule in the template (and asserting it via `test_chat_end_card_template_excludes_handoff_sha_from_body`) is the smallest defense against drift.

## Surfaced items for the founder

Numbered list of items needing explicit confirmation before Child A's chat-end card slice is sealed:

1. **Variant-encoding ratification.** The single-file additive-deltas-from-normal scheme as authored. Alternatives: four-complete-bodies-in-one-file, or four separate files. My recommendation is the as-authored scheme on maintenance-burden grounds; surfacing for explicit signoff.

2. **Failing-test seed placement.** The four tests above are sketched as pytest functions, matching the Python stdlib stance of Child D's `tools/solo-verify`. If Child A's test runner ends up being something else (per the `decomposition.md` mention of `pytest -q --tb=no | grep PASSED | sort` as one of several runner examples — this is just an example, not a commitment), the test sketches need translation. Defer to whatever runner Child A's `/specify` ultimately declares.

3. **F-Usr-3 carry-forward.** Confirmed deferred from this session; surfaces in subsequent Child A (Project Instructions text authoring) or Child C (hook output shape authoring). No action required this session.

## What's NOT in this deliverable

Items the handoff or v1.3 spec name but that are out of scope for this slice:

- **Per-skill `/Chains` Group-exit branches.** Authored last session in `child_B_chains_sections.md`. Not modified.
- **`.cascade/handoff/last.md` atomicity protocol.** Owned by D2.3 v1.3 §Group-exit mechanics atomicity; implemented in each skill's exit step (Child B) and the Stop hook (Child C). The template file just supplies the card body the protocol writes.
- **The §Handoff verification predicate.** Owned by D2.3 v1.3; implemented in the Project Instructions block (chat-Claude) and the SessionStart hook (Group F). The template file just supplies the schema the predicate validates against.
- **`solo-cascade resume` CLI.** Owned by D4.6 v1.1; implemented in Child D's `tools/solo-verify`-adjacent tooling. The template file is the round-trip counterparty, not the implementation.
- **Remaining Child A items.** `spec.md.template` amendments per D3.2, `halt-messages.md` appendage, `.solo-config` schema additions, `docs/.solo-config.example.json`, `docs/templates/capability-artifact-types.md`, committed empty directories, gitignore updates. All listed in `decomposition.md` Child 0001-A files-in-scope. The next session picks them up (see handoff).

## Cross-references

- **D2.3 v1.3** — binding spec for the template body, variant set, and the handoff-prompt fence's path correction.
- **D2.1 v2.1** — canonical run-state path `.cascade/run-state.json` used in the handoff-prompt fence and in the template's "Read first" line.
- **D4.6 v1.1** — round-trip counterparty for the template; re-derives every field the template carries.
- **`decomposition.md` Child 0001-A** — files-in-scope row that names the chat-end card as one of Child A's items.
- **`child_B_chains_sections.md`** — the eleven `/Chains` section blocks that name this template as their Group-exit render target and select the variant per pattern.
- **`repo-state-summary.md` Part 2** — `docs/templates/` row confirms the directory exists in v0.1; the chat-end card joins the existing templates.
