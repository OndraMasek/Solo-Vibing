<!--
halt-messages.md — APPEND-READY BLOCK for the v0.2 Phase 3 halts.

This file is NOT a complete replacement for v0.1's `docs/templates/halt-messages.md`.
It is an append-ready block containing FOURTEEN new halt cards in the order
specified by `decomposition.md` Child 0001-A, extended with three D3.1 halts
per founder ratification (option (a); see history note below).

  D3.2 (2): §pyramid-shape-violation, §pyramid-tag-invalid
  D3.3 (6): §perceptual-evidence-missing, §invariance-pass-set-regression,
            §invariance-config-missing, §invariance-pass-set-empty,
            §invariance-seal-tampering, §invariance-config-changed
  D3.4 (3): §strategy-annotation-unresolved,
            §verify-milestone-aggregation-failed, §provenance-chain-broken
  D3.1 (3): §strategy-missing, §strategy-conflict-unresolved,
            §hybrid-without-child-overrides

═══ For the executing Claude Code session against `OndraMasek/Solo-Vibing` ═══

  1. Read the existing `docs/templates/halt-messages.md` (v0.1).
  2. Identify the file's append point (typically end-of-file; verify by reading
     the v0.1 structure first — the file should already have entries like
     §incomplete-failing-test-seed, §wrap-tests-red, §build-finalize-incomplete,
     etc. per D2.1 v2's halt set).
  3. Verify NONE of the fourteen §-codes below already appear in the file
     (the test `test_halt_messages_no_duplicate_halt_codes` per Child A's
     failing-test seed enforces this).
  4. Append the block below verbatim, stripping these comment lines and the
     "═══ Begin appendable content ═══" / "═══ End appendable content ═══"
     markers.

═══ History — D3.1 halts disposition ═══

The D3.1 §Halt conditions section names three halts that were NOT in the
initial `decomposition.md` Child 0001-A scope but were surfaced for founder
ratification in this session's notes doc as a fold-in candidate:

  §strategy-missing                 — fires when /specify seals without
                                      §Decomposition strategy section,
                                      with malformed value, or with the
                                      step-1 annotation still present.
  §strategy-conflict-unresolved     — fires when clarify-walker surfaced a
                                      strategy-conflict question and the
                                      spec sealed without it being marked
                                      resolved.
  §hybrid-without-child-overrides   — fires when parent is sealed hybrid
                                      and /plan's decomposer produced
                                      children without explicit strategy.

Three dispositions were considered:
  (a) Fold into Child A's halt-messages.md appendage in the executing
      Claude Code session.
  (b) Schedule as a separate amendment session under Child A.
  (c) Defer to v0.2.x with a note that /specify and /plan can render
      generic halts at runtime in their absence.

**Founder ratification: (a) accepted.** The three D3.1 halts are folded in
below as halts 12–14 of this appendage. The parent spec's AC-2 needs a
one-line amendment (from "eleven new Phase 3 halts" to "fourteen new Phase 3
halts, including the three D3.1 halts that enforce the §Decomposition
strategy section's surface"). The notes doc and continuation handoff carry
this amendment as a follow-on action for the parent spec edit pass.

═══ Begin appendable content ═══

### §pyramid-shape-violation

**When:** /specify's seal verifier or /plan's pre-flight detected the failing-test seed violates the per-strategy pyramid shape declared in §Decomposition strategy. Specific sub-cases:
  - `missing-required` — a tag listed in the pyramid shape's required set is absent from every entry in `failing_test_seed[]`.
  - `forbidden-present` — a tag listed in the pyramid shape's forbidden set appears in at least one entry.
  - `strategy-mismatch` — `pyramid_shape.strategy` does not equal `outputs.decomposition_strategy`.
  - `shape-tampering` — `pyramid_shape.required_tags` / `optional_tags` / `forbidden_tags` are not set-equal to the D3.2 catalog values for the declared strategy.
  - `refactor-spike-nonempty` — strategy is refactor-spike but `failing_test_seed[]` is non-empty.
  - `hybrid-nonempty` — parent is hybrid but `pyramid_shape` is non-null OR `failing_test_seed[]` is non-empty.
  - `artifact-path-invalid` (firing at `spec.strategy-evidence`) — a `[perceptual]` entry's `artifact_path` violates the strategy's path convention (walking-skeleton requires `docs/specs/<NNNN>-<slug>/perceptual/*.png`; api-boundary requires the fixed `integration-transcript.md` path; capability-cluster requires the type-extension match per `docs/templates/capability-artifact-types.md`).

**Recommendation:** `/specify <MARKER>-N --continue`, retag tests or revise the failing-test seed to satisfy the pyramid.

**Rationale:** A pyramid-violating seed is a /specify defect; downstream stages cannot iterate around it because the seed shape is upstream of every downstream gate.

**Alternatives:**
  1. `/specify <MARKER>-N --unseal` — if the violation is structural rather than a small retag (e.g., the strategy was wrong and the seed is correct).
  2. For refactor-spike with non-empty seed: consider whether the spec is genuinely refactor-spike or should be hybrid; re-seal under the correct strategy.

**Diagnostic context:**
  - Violation sub-case: one of (missing-required | forbidden-present | strategy-mismatch | shape-tampering | refactor-spike-nonempty | hybrid-nonempty | artifact-path-invalid).
  - Strategy verbatim from §Decomposition strategy.
  - Required tags verbatim from `pyramid_shape.required_tags`.
  - Forbidden tags verbatim from `pyramid_shape.forbidden_tags`.
  - Offending entry name + tag (for missing-required, forbidden-present, refactor-spike-nonempty).
  - Catalog value vs sealed value diff (for shape-tampering).
  - `artifact_path` verbatim + expected convention (for artifact-path-invalid).

When `§pyramid-shape-violation` and `§incomplete-failing-test-seed` fire together at /specify seal, the halt card surfaces both findings with `§incomplete-failing-test-seed` taking precedence on the recommendation line; adding a test resolves both.

---

### §pyramid-tag-invalid

**When:** A test entry in the failing-test seed has a `tag` value not in the canonical enum `{unit, integration, contract, smoke, perceptual, invariance}`.

**Recommendation:** `/specify <MARKER>-N --continue`, retag the offending entry to one of the canonical six.

**Rationale:** Out-of-enum tags are unverifiable by definition; D3.4's gate-firing predicates cannot match against them.

**Alternatives:** None — retag is the only recovery.

**Diagnostic context:**
  - Offending entry name verbatim.
  - Offending tag value verbatim.
  - Canonical enum verbatim: `{unit, integration, contract, smoke, perceptual, invariance}`.

---

### §perceptual-evidence-missing

**When:** /verify pre-flight detected a perceptual evidence predicate failed for at least one child. Sub-cases (per D3.3 predicates P1–P4 and P5 for refactor-spike file-absence):
  - `artifact-absent` — the file referenced by `artifact_path` (or `invariance_artifact.pass_set_path` for refactor-spike) is not present on the filesystem.
  - `regeneration-failed` — the named test exited non-zero at /verify re-run; the artifact may or may not be present, but the contract "regenerates from the named test" is broken.
  - `byte-stability-failed` — the artifact exists at the path but is not byte-equal to the checked-in version after the test re-runs. For walking-skeleton/capability-cluster this almost always means non-deterministic rendering; for api-boundary it almost always means a non-deterministic API response (timestamp, ULID, random token) leaking into the transcript.
  - `transcript-shape-violation` (api-boundary only) — the file parses but is missing the minimum H1/H2/H3 schema (no `# Integration transcript` H1; no `## Scenario:` H2; a scenario block missing `### Request` or `### Response`).
  - `path-outside-convention` — `artifact_path` is outside the `docs/specs/<NNNN>-<slug>/perceptual/` prefix (this should have been caught at /specify seal; if it reaches /verify, the manifest has been tampered with).

**Recommendation:**
  - For `artifact-absent`: re-run `/build <child-ticket>` and verify the test produces the artifact at the path. If the test names a different path than the manifest's `artifact_path`, the spec and the test are out of sync — fix the test or `/specify <spec> --unseal` and revise the seed.
  - For `regeneration-failed`: read the test's failure output; the named test is genuinely failing at /verify. Fix the implementation; re-run `/build`.
  - For `byte-stability-failed`: examine the artifact's diff between checked-in and freshly-generated. The fix is in the test framework's configuration (fix viewport, pin font, scrub timestamps), not in the cascade.
  - For `transcript-shape-violation`: the test's output formatter is generating non-conforming markdown. Fix the formatter; the predicate requires the minimum H1/H2/H3 schema.
  - For `path-outside-convention`: the manifest has been hand-edited. `--unseal` and re-seal; do not back-patch the field manually.

**Rationale:** Perceptual evidence is the artifact a human-or-machine downstream consumer reads to verify the cascade's claim. A missing or malformed artifact at the documented path means the cascade's claim cannot be independently verified — exactly the failure mode F-3 names.

**Alternatives:** `/specify <ticket> --unseal` if the structural change required is larger than a test/implementation fix.

**Diagnostic context:**
  - Sub-case: one of (artifact-absent | regeneration-failed | byte-stability-failed | transcript-shape-violation | path-outside-convention).
  - Child ticket ID.
  - Strategy verbatim.
  - `artifact_path` from manifest.
  - Filesystem state at the path: "absent" | "present, size N bytes, sha256 H".
  - Test name verbatim.
  - For `byte-stability-failed`: diff summary (lines changed for text, byte-count delta for binary).
  - For `transcript-shape-violation`: the first H2 or H3 the parser expected but did not find.

---

### §invariance-pass-set-regression

**When:** /verify pre-flight for a refactor-spike child re-ran the configured pass-set capture command, and the verify-time pass-set is missing one or more test IDs that were present in `pass-set-at-seal.txt` (D3.3 predicate P9).

**Recommendation:** Identify the regressed test IDs from the diff. The refactor has changed observable behavior — either fix the regression (the refactor was supposed to preserve behavior; restore it) or, if the regression is intentional and represents a behavior change, `/specify <ticket> --unseal` and re-seal under a strategy that authors new tests (walking-skeleton if greenfield-shaped; capability-cluster if a capability is being modified; api-boundary if a contract is changing). Refactor-spike is the wrong strategy for intentional behavior change.

**Rationale:** Refactor-spike's entire contract is invariance preservation. A pass-set regression means the contract has been broken; downstream gates cannot let the milestone ship with the strategy's promise unmet.

**Alternatives:** If the regression is suspected to be a flake (non-deterministic test failing on this run), re-run `/verify`. Flaky tests in the pre-existing pass-set are a separate problem; D3.3 does not provide flake-tolerance, but the founder may diagnose by running `solo-verify invariance <ticket>` repeatedly.

**Diagnostic context:**
  - Child ticket ID.
  - List of test IDs present in `pass-set-at-seal.txt` but absent from `pass-set-at-verify.txt` (the regression set).
  - Seal-time count vs verify-time count.
  - Paths to both `pass-set-at-seal.txt` and `pass-set-at-verify.txt` for the founder to diff manually.

---

### §invariance-config-missing

**When:** /specify seal for a refactor-spike spec (or /verify for a refactor-spike child) found `docs/.solo-config.json` absent, missing the `invariance.pass_set_capture_command` key, or the capture command exited non-zero on its first invocation. Sub-cases:
  - `config-file-absent` — `docs/.solo-config.json` does not exist.
  - `key-missing` — file exists but `invariance.pass_set_capture_command` key is absent or empty.
  - `capture-failed` — command exists in config but exits non-zero (also fires at /verify per predicate P8).

**Recommendation:** Create `docs/.solo-config.json` if absent. Add `invariance.pass_set_capture_command` as a string that, when run from the repo root, prints one passing test ID per line on stdout and exits zero. Verify by running the command manually; once it succeeds, `/specify <ticket> --continue` resumes the seal.

**Rationale:** Refactor-spike's invariance predicate requires a capture command; without it, neither seal nor verify can compute the pass-set. Sealing without the config would produce a refactor-spike spec that is permanently un-verifiable, defeating the strategy.

**Alternatives:** `/specify <ticket> --unseal` and re-seal under a different strategy if no capture command is feasible for this codebase (rare; see `docs/.solo-config.example.json` for runner-specific examples).

**Diagnostic context:**
  - Sub-case: one of (config-file-absent | key-missing | capture-failed).
  - Path to `docs/.solo-config.json` (whether it exists).
  - The configured command verbatim if present.
  - The command's stdout and exit code on the most recent invocation.

---

### §invariance-pass-set-empty

**When:** /specify seal for a refactor-spike spec ran the configured capture command successfully (exit zero) but the resulting `pass-set-at-seal.txt` contained zero test IDs.

**Recommendation:** `/specify <ticket> --unseal` and reconsider the strategy. Refactor-spike against a codebase with no passing tests has no contract to preserve; the spec is likely walking-skeleton (greenfield shape) or capability-cluster (new behavior added to a stack that may or may not have tests elsewhere). If the codebase genuinely has no tests yet and a refactor is needed, write a walking-skeleton spec to establish the test base first, then a refactor-spike on top of it.

**Rationale:** An empty pass-set produces a trivially-satisfied invariance predicate (the empty set is a subset of every set), so a refactor-spike with an empty seal-time pass-set offers no verification value. The strategy is misapplied; the seal halt redirects.

**Alternatives:** None — the strategy needs to change.

**Diagnostic context:**
  - Child ticket ID.
  - Path to the empty `pass-set-at-seal.txt`.
  - The configured capture command's stdout (verbatim, to confirm it really was empty rather than corrupt).

---

### §invariance-seal-tampering

**When:** /verify pre-flight for a refactor-spike child found the sha256 of `pass-set-at-seal.txt` at /verify time does not match the manifest's `pass_set_sha256` (D3.3 predicate P6). The file has been edited post-seal.

**Recommendation:** `/specify <ticket> --unseal` and re-seal. Do not hand-edit the file — the manifest's contract is grounded in the seal-time content; hand-editing breaks D2.1 v2.1's chain integrity at the next stage's pre-flight.

**Rationale:** The seal-time pass-set is the durable contract for the refactor-spike strategy. A mismatched sha means either the file was deliberately edited (changing the contract) or it was corrupted (the file no longer reflects the seal-time intent); either way, the manifest cannot be trusted.

**Alternatives:** None — chain integrity must be restored by re-sealing.

**Diagnostic context:**
  - Child ticket ID.
  - Path to `pass-set-at-seal.txt`.
  - `pass_set_sha256` from manifest verbatim.
  - Recomputed sha256 of the file verbatim.

---

### §invariance-config-changed

**When:** /verify pre-flight for a refactor-spike child found the sha256 of the configured `invariance.pass_set_capture_command` string at /verify time does not match `capture_command_sha256` on the manifest (D3.3 predicate P7). The capture command has been edited between seal and verify; the new command produces a different pass-set, making the comparison invalid.

**Recommendation:** Two options:
  1. `/specify <ticket> --unseal` and re-seal under the new command (the new command becomes the manifest's `capture_command_sha256`).
  2. Revert the command in `docs/.solo-config.json` to the sealed version (the founder reads the manifest's `capture_command_sha256`, then chooses which command the prefix matches).

**Rationale:** The invariance comparison is meaningful only when seal-time and verify-time pass-sets are produced by the same command. A command change between seal and verify silently swaps the comparison contract.

**Alternatives:** None — the command must match its sealed sha for the predicate to be valid.

**Diagnostic context:**
  - Child ticket ID.
  - `capture_command_sha256` from manifest verbatim.
  - Recomputed sha256 of the current `invariance.pass_set_capture_command` verbatim.
  - The current command string verbatim from `docs/.solo-config.json`.

---

### §strategy-annotation-unresolved

**When:** /specify seal detected that the strategy field at §Decomposition strategy still carries the step-1 annotation "proposed by /specify; founder to confirm" — the founder did not explicitly accept or revise the proposal before seal.

**Recommendation:** Re-run `/specify <ticket> --continue`. At step 5, either accept the proposed strategy verbatim (which clears the annotation) or revise it to a different strategy.

**Rationale:** Per D3.1, the strategy is the populator for the pyramid shape, the perceptual evidence shape, and the verify-time gate. A strategy that the founder did not affirmatively confirm is not load-bearing; sealing with the annotation in place would let a /specify default cascade downstream unchallenged.

**Alternatives:** None — the annotation must clear before seal.

**Diagnostic context:**
  - Verbatim contents of the §Decomposition strategy section.
  - The annotation line being detected.
  - The spec markdown's `spec_path`.

---

### §verify-milestone-aggregation-failed

**When:** /verify's milestone-aggregation gate (`verify.milestone-aggregation` per D3.4) found one or more per-child gates halted. This is not a separate failure mode; it is the aggregation halt card itself, surfaced as a milestone-level §halt for /retro and human readability.

**Recommendation:** Address each per-child halt independently per its sub-card's recommendation; re-run `/verify <milestone>` once children are fixed.

**Rationale:** A milestone cannot ship while any child gate has halted. Per-child halts have their own recovery paths; the milestone halt is a roll-up, not an additional defect.

**Alternatives:** If a child's halt is unrecoverable in the milestone's timeframe, `/plan <milestone> --drop-child <ticket>` removes the child from the milestone. (Note: D4.x decides whether `--drop-child` ships in v0.2; if not, the founder manually deletes the child ticket and re-runs `/plan`.)

**Diagnostic context:**
  - List of halted children with their sub-cards (each child's halt embedded as a sub-section).
  - List of passed children.
  - Total counts: N halted of M total.
  - Milestone ID.
  - Paths to per-child halt diagnostics.

---

### §provenance-chain-broken

**When:** Any stage's `<stage>.provenance` gate found a manifest chain break: missing manifest file, sha mismatch, or named-parent mismatch. This is the consolidated halt code for D2.1 v2.1's chain-recovery patterns (per D3.4 §Halt conditions), unifying the per-stage provenance halts under a single named code for cleaner `solo-verify` reporting.

**Recommendation:** `--reconcile` per D2.1 v2.1's chain-recovery pattern (or `--rerun=<stage>` per D4.5 for absent-manifest cases per D4.6 v1.1 §Halt conditions). Manual diff of `.cascade/manifests/` against `cascade:run-state.active_stages[]` to identify the break point.

**Rationale:** A broken provenance chain means the cascade cannot trust any downstream evidence; halting prevents tainted artifacts from propagating.

**Alternatives:** None — chain integrity must be restored before downstream stages can resume. Exit code 3 (per D3.4 §Exit codes) is reserved for this halt class because the recovery is `--reconcile`, distinct from standard halts where stage retry suffices.

**Diagnostic context:**
  - Stage attempting to read.
  - Manifest path expected.
  - Manifest path found (or "absent").
  - Sha expected.
  - Sha found.
  - Parent name expected (the `parent_manifest` field of the failing stage's intended write).
  - Parent name found (the actual `parent_manifest` on the manifest at the path, or "absent").

═══ End appendable content for D3.2/D3.3/D3.4 halts; D3.1 halts 12–14 follow ═══

---

### §strategy-missing

**When:** Spec sealed without the `## Decomposition strategy` section, or with a value outside the five-strategy enum `{walking-skeleton, api-boundary, capability-cluster, refactor-spike, hybrid}`, or with the "proposed by /specify; founder to confirm" annotation still present at seal.

**Recommendation:** `/specify <MARKER>-N --continue`, add or correct the section. At step 5, the founder confirms a strategy verbatim from the enum and the step-1 annotation comment clears.

**Rationale:** D2.1 v2.1's verifier predicate for /specify's manifest requires `outputs.decomposition_strategy` to be in the enum. Absence halts at /plan's pre-flight regardless, but the friendlier halt is at /specify's seal step so the spec is fixed before downstream stages run. The §Decomposition strategy section is load-bearing for /plan (decomposer reads strategy to find per-child overrides), D3.2's pyramid declaration (populator reads strategy to select required/optional/forbidden tags), D3.3's integration anchor (perceptual evidence shape per strategy), and D3.4's gate composition.

**Alternatives:** None — the field is load-bearing and the seal halt is the first line of defense. `/specify <MARKER>-N --unseal` is available if the underlying confusion is which strategy fits, but step 1's proposal + step 4's clarify-walker normally resolve that before seal.

**Diagnostic context:**
  - Spec path.
  - Current section state: one of (`missing` — section header absent; `malformed` — section header present but body empty or malformed; `invalid-value` with the offending value verbatim — body present but not in the enum; `annotation-present` — value is valid but the step-1 annotation comment block has not been removed).
  - For `annotation-present`: the verbatim annotation text detected.
  - Canonical enum verbatim: `{walking-skeleton, api-boundary, capability-cluster, refactor-spike, hybrid}`.

---

### §strategy-conflict-unresolved

**When:** Clarify-walker at /specify step 4 surfaced a strategy-conflict clarify question (a four-hat finding whose locus implies a different strategy than the step-1 proposal) and the spec sealed without the question being marked resolved — founder answer absent, empty, or pending.

**Recommendation:** `/specify <MARKER>-N --unseal`, resolve the clarify question at step 4. The founder either confirms the original strategy with rationale for overriding the four-hat finding, or revises the strategy to match the finding. Either resolution is recorded verbatim in the spec's `## Open Questions` section per the four-hat override pattern.

**Rationale:** An unresolved strategy conflict is a sealed disagreement between the founder and a four-hat finding; sealing without resolution buries the disagreement and downstream stages have no record of which view to trust. The conflict represents a genuine ambiguity that downstream code paths (different pyramid shape, different perceptual evidence requirement, different gate composition) cannot navigate without explicit founder direction.

**Alternatives:** None — re-seal under `/specify --unseal` is the only sanctioned recovery. Manually editing the spec's clarify section to mark the question resolved without re-running `/specify` breaks the manifest's `ac_list_sha256` chain (D2.1 v2.1 predicate) and is caught at /plan pre-flight anyway with a less-helpful halt code.

**Diagnostic context:**
  - Spec path.
  - Clarify question text verbatim (the question clarify-walker emitted at step 4).
  - Conflicting four-hat finding: hat (engineer | usability | reviewer | integrator), locus, severity (urgent | medium-high | medium | low), finding summary.
  - Founder's proposed strategy at last seal attempt (verbatim from `## Decomposition strategy`).
  - The four-hat finding's implied strategy (the strategy clarify-walker's question proposed as the alternative).

---

### §hybrid-without-child-overrides

**When:** Parent spec sealed with `outputs.decomposition_strategy = hybrid`, and /plan's decomposer produced one or more children whose `## Decomposition strategy` field is absent, empty, or inherits the parent's `hybrid` value without an explicit per-child override.

**Recommendation:** `/plan <MARKER>-N` re-decompose with explicit per-child strategy assignment. Each child of a hybrid parent must carry an explicit non-hybrid strategy in its `## Decomposition strategy` section (or, in the case of a sub-hybrid child needing its own decomposition, must re-seal under `/specify` as a heavyweight child with its own decomposition.md sub-tree — v0.2 caps hybrid nesting at one level per D3.4 §`/verify` dispatch).

**Rationale:** Per D3.1, hybrid is a meta-strategy — a flag indicating the parent contains slices of multiple strategies, not a guide to gate composition. Without per-child strategy overrides, children inherit a flag rather than a shape, and downstream gates (D3.4) cannot compose: there is no parent-level pyramid shape (per D3.2 the hybrid catalog entry is `null`), no parent-level integration anchor (per D3.3 hybrid defers integration coverage to per-child evidence), and no parent-level gate composition (per D3.4 the milestone-aggregation gate iterates per-child gates). A hybrid parent without per-child overrides is an unverifiable structure.

**Alternatives:**
  1. `/specify <MARKER>-N --unseal` if hybrid was the wrong call. Per D3.1's catalog, the first preference for a feature that resists a single strategy is to split it into two parents under different strategies; hybrid is reserved for the case where the slices are too small or too coupled to split cleanly.
  2. If the founder genuinely intends hybrid and /plan's decomposer cannot find a clean per-child strategy assignment, this is a /plan-side defect (the decomposer should surface a finding before producing the un-overridden children). File a v0.2.x improvement to /plan's decomposer rather than working around this halt.

**Diagnostic context:**
  - Parent spec path; parent strategy = `hybrid` (confirmed).
  - List of children without explicit strategy: each entry includes child ticket ID, child spec path (if heavyweight) or child entry in decomposition.md (if lightweight), the child's current `## Decomposition strategy` value (one of: `absent`, `empty`, `hybrid` inherited).
  - Decomposer's output verbatim — the decomposition.md content emitted by the most recent /plan run for diagnostic comparison.
  - Total counts: M children with strategy / N children without strategy / total milestone size T.

═══ End appendable content ═══
