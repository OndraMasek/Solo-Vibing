# Child A continuation — `spec.md.template` + `halt-messages.md` authoring notes

**Authored:** 2026-05-19 (paired session with `spec.md.template` and `halt-messages-append.md` deliverables).
**Phase:** Child 0001-A continuation — `v0.2-templates-and-config` (walking-skeleton strategy).
**Spec basis:** D3.2 §Spec template addition (binding for spec template Pyramid shape + per-test tag + three variants); D3.1 §Spec template addition (§Decomposition strategy section); D3.2/D3.3/D3.4 §Halt conditions (binding for the eleven new halts); `decomposition.md` Child 0001-A scope; the parent spec at `spec.md` AC-2 (which counts "eleven new Phase 3 halts" from D3.2/D3.3/D3.4).
**Status:** Drafted. Three items surfaced for founder ratification; otherwise authored.

---

## What this session produced

Two artifacts:

1. `spec.md.template` — the v0.2 spec authoring template with D3.2's amendments (Pyramid shape preamble in §Failing-test seed, per-test `[tag]` notation, three rendering variants) and D3.1's §Decomposition strategy section (defensively included; see disposition below).

2. `halt-messages-append.md` — an append-ready block containing the eleven new Phase 3 halt cards in the order specified by `decomposition.md` Child 0001-A (D3.2 → D3.3 → D3.4). Comment headers describe how the executing Claude Code session pastes the block into v0.1's existing `docs/templates/halt-messages.md`.

Both files land in `docs/templates/` per `repo-state-summary.md` Part 1. The executing Claude Code session against `OndraMasek/Solo-Vibing` does the in-place amendment.

## Variant-encoding decision (different from chat-end-card.md, intentionally)

The handoff said: "Encode using HTML comment markers per the `chat-end-card.md` precedent (single file, comment markers; **the additive-vs-alternative encoding is a per-content decision** — see if any of the three rendering variants share enough content to use deltas, otherwise author each as a complete alternative block)."

**Decision:** three complete alternative blocks, not additive deltas. Each `<!-- variant: ... -->` block in §Failing-test seed holds a full section body. The renderer (`/specify` step 3) selects one block and strips the others.

**Why this differs from `chat-end-card.md`'s additive-deltas-from-normal scheme.** The two templates' variants have structurally different relationships:

- **`chat-end-card.md`'s variants are textual deltas.** Three of four variants are ~95% identical to normal (the reset-triggered and manual-halt variants append a single framing sentence after the HANDOFF PROMPT fence; the terminal variant strips the fence and replaces one line). Encoding three additional full bodies would 4× the maintenance burden and invite drift.

- **`spec.md.template`'s variants are structural alternatives.** Each variant is a categorically distinct §Failing-test seed body — the regular variant has a tag-set pyramid + per-AC test list; refactor-spike has no test list at all and instead explains the invariance predicate; hybrid has neither a pyramid nor tests. There's no shared base body to factor out; trying to encode these as deltas would yield a base body that's barely more than the section header, with three variants that each rewrite essentially everything below it.

**The framework now has two variant-encoding patterns.** This is intentional. The patterns reflect their content:
  - **Additive-deltas-from-default** (chat-end-card.md): use when variants share a large body and differ by appended or replaced fragments.
  - **Alternative-complete-blocks** (spec.md.template): use when variants are categorically distinct full bodies.

**Item to surface to the founder.** If the preference is one consistent pattern across all templates, the spec template could be force-fit into additive-deltas. The cost would be a small base body and three near-total-rewrite deltas — a worse fit for the content than alternative blocks. I'd push back on that change but accept it if explicitly directed.

**The `/specify` skill's read-side.** Either pattern is straightforward for the renderer: scan for `<!-- variant: <name> -->` markers, select the matching block by strategy lookup, strip the others, strip the markers. Child 0001-B's `/specify` skill amendments (per AC-6) implement this scan in step 3.

## D3.1 §Decomposition strategy fold-in: included defensively

The handoff said: "If D3.1's `## Decomposition strategy` section isn't already present, fold it in alongside the D3.2 amendments."

**Decision:** included the section in `spec.md.template`. Rationale:

- D3.1 is Phase 3 design (v0.2 amendment); Phase 3 has not yet been landed in v0.1 per `repo-state-summary.md` Part 2 (the v0.1 framework does not yet have D3.1's strategy enum on `/specify`'s manifest, does not yet have D3.2's pyramid_shape field, etc.). So almost certainly the §Decomposition strategy section is NOT yet in v0.1's `spec.md.template`.
- D3.4 §spec.strategy-annotation gate requires §Decomposition strategy to be present at /specify seal. If the template doesn't carry the section, the gate halts every spec at §strategy-annotation-unresolved on the first seal attempt.
- Including the section here is cheap and protective; excluding it risks every v0.2 spec halting on first /specify seal.

**Verification step for the executing Claude Code session.** Read the actual v0.1 `docs/templates/spec.md.template` byte-for-byte before applying the patch. If §Decomposition strategy is already present (from any prior amendment pass), remove it from this session's output to avoid duplication; otherwise paste verbatim from this session's draft.

## v0.1 byte-for-byte content not in KB — apply-time reconciliation required

The handoff said: "Identify the current v0.1 `## Failing-test seed` section content (via `project_knowledge_search` against the prior SDG-style template or the v0.1 framework template inventory; if the search doesn't surface the exact wording, surface to founder for paste)."

**Status:** the searches did not return the v0.1 `spec.md.template` content byte-for-byte. The KB has:
- The worked example at `docs/specs/0001-wrap-build-log/spec.md` (referenced by `repo-state-summary.md`; not directly in KB but its structure is referenced by D3.2 which says it "uses `[unit]` exactly this way and is template-compliant under D3.2 with no rewrite needed").
- The parent spec at `spec.md` (in this project) which is hand-authored and follows the v0.1 template structure closely.
- D3.1/D3.2/D3.3/D3.4 binding specs that name every amendment.

**Decision:** authored a coherent v0.2-shaped template that:
  - matches the section ordering inferred from the parent spec (`# title` heading; **Status/Type/Strategy/Marker/Product/Date** frontmatter-style; `## Motivation`; `## Scope boundary`; `## Decomposition strategy`; `## Acceptance criteria`; `## Failing-test seed`; `## Related research findings`; `## Open questions`; `## Provenance`),
  - carries all v0.2 binding-spec amendments,
  - is internally self-consistent.

The executing Claude Code session at framework-repo apply-time **must reconcile against the actual v0.1 `spec.md.template` byte-for-byte**:

- If the v0.1 template's structural sections are differently named or ordered, preserve v0.1's structure and patch only the sections D3.2/D3.1 amend (specifically: insert §Decomposition strategy if absent; replace §Failing-test seed body with the three-variants block from this session's output).
- If the v0.1 template has additional sections this session's draft omits, keep them.
- The patch surface is: §Decomposition strategy (new section) + §Failing-test seed body (replace existing body with the three-variants block). Everything else in this session's `spec.md.template` is illustrative of the surrounding template; not authoritative against v0.1.

**Alternative path (preferred if available):** the founder pastes the v0.1 `docs/templates/spec.md.template` content into a follow-up turn before the executing Claude Code session runs. With the v0.1 wording in hand, this session's output can be re-cast as a precise patch (or the file re-authored as a true minimal-delta).

## D3.1 halts surfaced gap (three halts not in this batch)

Per `decomposition.md` Child 0001-A, this session's halt scope is the eleven halts from D3.2/D3.3/D3.4. The parent spec at `spec.md` AC-2 confirms: "the eleven new Phase 3 halts" enumerated from those three docs only.

D3.1 §Halt conditions specifies three additional halts:
  - `§strategy-missing` — /specify seals without §Decomposition strategy section, with malformed value, or with the step-1 annotation still present.
  - `§strategy-conflict-unresolved` — clarify-walker surfaced a strategy-conflict question and the spec sealed without it being marked resolved.
  - `§hybrid-without-child-overrides` — parent sealed hybrid and /plan's decomposer produced children without explicit strategy.

These are **not in this session's eleven-halt scope** and almost certainly **not yet in v0.1** (D3.1 is Phase 3 design, same status as D3.2/D3.3/D3.4).

**Three possible dispositions.** The notes embed this in `halt-messages-append.md`'s header comment block for the executing session's awareness, with these options:
  - **(a)** Fold into Child A's halt-messages.md appendage in the executing Claude Code session — same authoring lane, same file, same template structure. Child A's appendage gains three halts and the test `test_halt_messages_has_eleven_new_halt_codes` updates to assert **fourteen** halts (or stays as eleven and a separate `test_halt_messages_has_three_d3_1_halt_codes` is added).
  - **(b)** Schedule as a separate amendment session under Child A. Cost: an extra session for ~150 lines of work that mechanically mirror what this session already did.
  - **(c)** Defer to v0.2.x. Cost: `/specify` and `/plan` either render generic halts at runtime (less informative) or hard-code the missing halt-card content (defeats the centralized `halt-messages.md` pattern).

**Recommendation: (a).** The three D3.1 halts are the same shape as the eleven in this batch and live in the same file. Folding them in is the cheapest add; the executing Claude Code session can do it in the same pass. Surface for founder signoff before the apply pass runs.

## F-Usr-3 disposition (Project Instructions step 5 acknowledgment)

The handoff flagged F-Usr-3 as potentially surfacing here if Project Instructions text is in Child A scope.

**Disposition:** not in scope for this session. `decomposition.md` Child 0001-A files-in-scope does NOT name `docs/templates/project-instructions.md` or any equivalent Project Instructions template file. The Project Instructions paste-block is dynamically rendered by `/onboard` per D2.3 v1.3 §`/onboard` integration point — it's not a static template that lives in `docs/templates/`.

**Carry-forward.** F-Usr-3 remains queued for Child 0001-B (`/onboard` skill amendments, which would author the `/onboard` step-7 render logic per D2.3 v1.3) or Child 0001-C (`.claude/hooks/` infrastructure, which carries the SessionStart hook output shape for Group F). Whichever session lands the Project Instructions step-5-equivalent is the one that resolves F-Usr-3.

## Failing-test seed for Child A's spec-discipline slice

Per the handoff's sketch, four tests at session end. Authored as pytest-flavored stubs (matching prior session's seed; runner selection is Child A's `/specify` call). Three of the four can run before D4.6 v1.1 implementation lands; the round-trip-style integration test is not relevant for these two template files.

### `test_spec_template_has_pyramid_shape_preamble` — `[smoke]`

**Assertion.** `docs/templates/spec.md.template` contains the Pyramid shape preamble line (the literal substring `**Pyramid shape:**`) at least once.

**Why.** Asserts the D3.2 §Spec template addition's most diagnostic substring is in place. If the preamble is missing, /specify step 3's renderer has nothing to substitute into, and every spec sealed via the template fails D3.4 §spec.pyramid-shape.

**Test path:**
```python
from pathlib import Path
def test_spec_template_has_pyramid_shape_preamble():
    text = Path("docs/templates/spec.md.template").read_text()
    assert "**Pyramid shape:**" in text, "D3.2 §Spec template addition not applied"
```

### `test_spec_template_has_three_rendering_variants` — `[smoke]`

**Assertion.** The file contains the three `<!-- variant: <name> -->` markers literally, one per variant.

**Why.** Asserts the variant-encoding scheme is present and complete. Missing any variant means /specify cannot render specs for that strategy class without falling back to default behavior (which is undefined).

**Test path:**
```python
def test_spec_template_has_three_rendering_variants():
    text = Path("docs/templates/spec.md.template").read_text()
    for name in ("regular", "refactor-spike", "hybrid"):
        assert f"<!-- variant: {name}" in text, f"missing variant: {name}"
```

Note: variant name `regular` (not the strategy names) is the canonical marker for the walking-skeleton/api-boundary/capability-cluster body. If the founder prefers a different marker name (e.g., `<!-- variant: with-tests -->`), surface for ratification — see "Items to surface" below.

### `test_halt_messages_has_eleven_new_halt_codes` — `[smoke]`

**Assertion.** `docs/templates/halt-messages.md` contains each of the eleven `§<halt-code>` substrings literally, exactly once each.

**Why.** Asserts the eleven new halt cards are present (the smoke level — substring match — not the unit level of asserting card structure).

**Test path:**
```python
def test_halt_messages_has_eleven_new_halt_codes():
    text = Path("docs/templates/halt-messages.md").read_text()
    halts = [
        "§pyramid-shape-violation",
        "§pyramid-tag-invalid",
        "§perceptual-evidence-missing",
        "§invariance-pass-set-regression",
        "§invariance-config-missing",
        "§invariance-pass-set-empty",
        "§invariance-seal-tampering",
        "§invariance-config-changed",
        "§strategy-annotation-unresolved",
        "§verify-milestone-aggregation-failed",
        "§provenance-chain-broken",
    ]
    for code in halts:
        assert text.count(code) >= 1, f"missing halt code: {code}"
```

Updates to **fourteen halt codes** if the D3.1 fold-in disposition (a) is accepted (adding `§strategy-missing`, `§strategy-conflict-unresolved`, `§hybrid-without-child-overrides`).

### `test_halt_messages_no_duplicate_halt_codes` — `[unit]`

**Assertion.** No halt code appears as the heading of more than one card. Detects accidental re-adds (e.g., if a future amendment re-adds a D3.1 halt that's already present).

**Why.** Halt-card heading uniqueness is the invariant the centralized `halt-messages.md` pattern relies on. Two cards with the same heading produce nondeterministic recommendation rendering at halt-time.

**Test path:**
```python
import re
def test_halt_messages_no_duplicate_halt_codes():
    text = Path("docs/templates/halt-messages.md").read_text()
    # Match heading lines like "### §<code>" exactly (not in-prose mentions)
    headings = re.findall(r"^###\s+(§\S+)\s*$", text, flags=re.MULTILINE)
    seen = {}
    for h in headings:
        seen[h] = seen.get(h, 0) + 1
    duplicates = {k: v for k, v in seen.items() if v > 1}
    assert not duplicates, f"duplicate halt codes: {duplicates}"
```

The regex matches `### §<code>` heading lines specifically. In-prose mentions of `§<code>` (cross-references inside other cards' Recommendation or Alternatives sections) are not matched, which is the desired behavior.

## Surfaced items for founder — ratified 2026-05-19

All three items resolved. Updates landed in this session:

1. **Variant-encoding pattern divergence — ratified as-authored.** Both patterns kept: chat-end-card.md uses additive-deltas-from-default; spec.md.template uses three-complete-alternatives. Each pattern fits its content (95% overlap vs 10% overlap). The framework now carries two encoding patterns, both using the same `<!-- variant: <name> -->` / `<!-- /variant -->` marker convention so the renderer-side parser is shared — the difference is in the application logic (append-after-fence vs select-one-strip-others), documented in each template's leading comment block.

2. **D3.1 halts fold-in — option (a) accepted.** The three D3.1 halts (§strategy-missing, §strategy-conflict-unresolved, §hybrid-without-child-overrides) are folded into `halt-messages-append.md` as halts 12, 13, 14 — bringing the total to fourteen halts in the appendage. The file's prelude updated to reflect option (a) acceptance; the appendable-content block extended with the three new cards in D3.1's binding-spec order. **Parent spec amendment needed:** AC-2 in `0001-v0.2-cascade-integration/spec.md` reads "eleven new Phase 3 halts" — this needs a one-line edit to "fourteen new halts, including the three D3.1 halts that enforce the §Decomposition strategy section's surface." Carried forward in the continuation handoff as a follow-on action item for the parent spec edit pass.

3. **Variant marker name — accepted default.** `<!-- variant: regular -->` retained for the walking-skeleton/api-boundary/capability-cluster case.

## Surfaced items (historical, for archive)

The original surfaced-item list (before founder ratification) is preserved here for traceability with subsequent sessions:

1. **Variant-encoding pattern divergence ratification.** Two patterns now exist in the framework's templates: chat-end-card.md (additive-deltas-from-default) and spec.md.template (three-complete-alternatives). My recommendation is the as-authored split — each pattern fits its content. Alternative: force one pattern across both, with the cost-trade laid out above.

2. **D3.1 halts fold-in disposition.** Three halts (§strategy-missing, §strategy-conflict-unresolved, §hybrid-without-child-overrides) are needed by D3.1's gate predicates and not in this session's scope. Recommendation: (a) fold into Child A's halt-messages.md appendage. The executing Claude Code session can absorb them in the same pass; this session's `halt-messages-append.md` will need a single edit to add three more cards in D3.1's binding-spec format.

3. **Variant marker name.** The regular variant is marked `<!-- variant: regular -->`. Alternatives: `<!-- variant: with-tests -->` (more semantic), `<!-- variant: standard -->`, `<!-- variant: walking-skeleton -->` (per `decomposition.md`'s sketch language; misleading though, since the same block also serves api-boundary and capability-cluster). My pick: `regular` for terseness. Surface for ratification if the founder has a preference.

## What's NOT in this deliverable

Items the handoff or v1.3 spec name but that are out of scope for this slice:

- **`docs/templates/.solo-config.json.template`** (and `docs/.solo-config.json`, `docs/.solo-config.example.json`) — the next session's scope.
- **`docs/templates/capability-artifact-types.md`** — the next session's scope (the new 7-row table from D3.3).
- **`.gitignore` updates** for `docs/specs/*/invariance/pass-set-at-verify.txt` — the next session's scope.
- **Committed-empty-directory `.gitkeep` files** for `.cascade/manifests/`, `.cascade/halt/`, `.solo-locks/`, `.ralph/`, `docs/product/` — the next session's scope.
- **The actual v0.1-to-v0.2 reconciliation** of `spec.md.template` and `halt-messages.md` — owned by the executing Claude Code session against the framework repo.
- **The four D3.4 spec gates' evaluator logic** (`spec.strategy-annotation`, `spec.pyramid-shape`, `spec.failing-test-seed`, `spec.perceptual-artifact-path`, `spec.provenance`) — owned by Child 0001-B (`.claude/skills/specify/SKILL.md` step 7 amendments).

## Cross-references

- **D3.2 §Spec template addition** — binding for the Pyramid shape preamble, per-test tag notation, and three rendering variants. Direct authoring source for the regular variant's body shape.
- **D3.2 §Halt conditions** — binding for §pyramid-shape-violation and §pyramid-tag-invalid.
- **D3.3 §Halt conditions** — binding for §perceptual-evidence-missing through §invariance-config-changed (six halts).
- **D3.4 §Halt conditions** — binding for §strategy-annotation-unresolved, §verify-milestone-aggregation-failed, §provenance-chain-broken.
- **D3.1 §Spec template addition** — binding for the §Decomposition strategy section. Defensively included in `spec.md.template` per the recommendation above.
- **D3.1 §Halt conditions** — binding for the three D3.1 halts surfaced as a fold-in candidate.
- **`decomposition.md` Child 0001-A** — files-in-scope row that names this session's deliverables.
- **`spec.md` AC-2** — explicit "eleven new Phase 3 halts" count + per-D-doc attribution.
- **`child_A_chat_end_card_authoring_notes.md`** — prior-session notes; variant-encoding pattern precedent contrasted in §Variant-encoding decision above.
- **`repo-state-summary.md`** Part 1 — confirms `docs/templates/spec.md.template` and `docs/templates/halt-messages.md` both exist in v0.1; this session amends in-place.
