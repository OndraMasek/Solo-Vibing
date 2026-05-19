# D3.3 — Perceptual and invariance predicates per strategy

**Status:** Design.
**Phase:** 3.
**Resolves:** F-3 (quality topology inversion), in conjunction with D3.1 + D3.2 + D3.4.
**Companion:** D3.2 (test-pyramid declaration) — names the `perceptual` and `invariance` tags and requires them where required; D3.3 fills in path conventions, evidence shapes, and verifier predicates per strategy. D3.1 (decomposition strategy catalog) — gives the strategy semantics each predicate maps to. D3.4 (gate definitions) — composes D3.3's predicates into per-stage, per-child gate-firing logic for `/verify`.

**Anchors** (per D3.0): Schaffer / Spotify "Integration vs Integrated" distinction (perceptual = inspect-the-artifact, not exercise-the-real-systems); Pact / Pactflow consumer-driven contract framing (api-boundary's integration transcript as the solo-stack equivalent of a Pact file); Rainsberger (integrated tests are a scam — the conceptual basis for capability-cluster's "capability-boundary, not integrated-through-real-systems"); Stryker / mutmut / pitest 2026 maturity (the richer-than-pass-set invariance primitive parked for v0.2.x).

## Problem

D3.2 names `perceptual` and `invariance` as canonical tags and requires them in four of the five strategy shapes (walking-skeleton, api-boundary, capability-cluster require `perceptual`; refactor-spike requires `invariance`; hybrid composes per-child). D3.2 explicitly defers four downstream questions to D3.3:

1. **What artifact counts as `perceptual` evidence per strategy?** Walking-skeleton, api-boundary, and capability-cluster each have a different evidence shape. D3.2 names the tag; without per-strategy path conventions and inspection predicates, `/verify` has no concrete check to run — it would have to fall back to the D2.1 v2 "perceptual gate evidence … or N/A for non-UI" escape hatch that D3.1 explicitly closed with two canonical replacements.
2. **What artifact counts as `invariance` evidence for refactor-spike?** D3.2 says the predicate is "pre-existing test pass-set at `spec_sealed_at` is preserved at `/verify` time." That phrase is precise; the mechanism (which runner output format, which storage path, which comparison rule) is not.
3. **Where do these artifacts live on the filesystem and how does the cascade discover them?** D2.1 v2's manifest chain demands every claim be re-readable. For perceptual evidence the natural answer is "at a documented path the spec names"; for invariance evidence the natural answer is "in a captured snapshot the spec seals." Both need to be on the manifest, both need to be parseable by `/verify` pre-flight without re-running the entire test suite to discover them.
4. **What halts fire when these predicates fail, and at which stage?** D3.2 added two `/specify`-time halts (`§pyramid-shape-violation`, `§pyramid-tag-invalid`) for shape compliance. The evidence-existence and evidence-stability predicates fire at `/verify` time, not at `/specify` seal — at seal time the tests are by definition red, so the perceptual artifact won't exist yet and the pass-set will be undefined under the strategy's new behavior. D3.3 names the new `/verify`-time halts and their preconditions.

D3.3 closes these by giving each strategy a concrete predicate text, a concrete path convention, a concrete manifest schema extension, and concrete halt cards.

## Decision

Three perceptual predicates (one per non-refactor-spike strategy) plus one invariance predicate (refactor-spike). All four are `/verify`-time predicates, evaluated against artifacts named at `/specify` seal and produced/preserved through `/build`. Each predicate has:

- **A path convention** under `docs/specs/NNNN-<slug>/perceptual/` (or `…/invariance/` for refactor-spike).
- **A predicate text** of the form "artifact at the documented path regenerates from the named test."
- **A manifest schema slot** so the predicate is checkable without re-reading the spec markdown.
- **A `/verify`-time check** that composes with D2.1 v2's verifier chain.

The failing-test seed's per-entry record gains one new optional field: `artifact_path`. It is required when `tag = perceptual`; absent otherwise. For walking-skeleton it points at an image (PNG primitive for v0.2); for api-boundary it points at exactly `…/perceptual/integration-transcript.md`; for capability-cluster it points at a per-type artifact under `…/perceptual/`. The field's presence and shape are checked at `/specify` seal (D3.2's predicate set is extended additively); its referent is checked at `/verify` time (D3.3's new predicates).

For refactor-spike, there are no per-test entries to extend; instead `/specify` step 7 seal runs a configured pass-set capture command and writes the resulting list to `docs/specs/NNNN-<slug>/invariance/pass-set-at-seal.txt`. `/verify` re-runs the same command and compares pass-set membership. The capture command is runner-agnostic and configured in `docs/.solo-config.json`; the framework does not bundle a runner.

Two new halts: `§perceptual-evidence-missing` (with named sub-cases per strategy and failure mode) and `§invariance-pass-set-regression`. Both fire at `/verify` only. A third halt, `§invariance-config-missing`, fires at `/specify` seal for refactor-spike specs whose configuration is absent or empty — this prevents sealing a refactor-spike spec that cannot ever be verified.

The Code-Claude failure pattern from F-3 — and its analogue for non-UI products that the D2.1 v2 N/A escape hatch left open — collapses under this contract. A walking-skeleton child claiming `scope:built` with no PNG at the documented path halts `/verify` `§perceptual-evidence-missing/artifact-absent`. A refactor-spike claiming clean refactor that drops three pre-existing tests halts `/verify` `§invariance-pass-set-regression` with the exact test IDs that regressed.

## Walking-skeleton perceptual predicate

### Path convention

Artifacts under `docs/specs/NNNN-<slug>/perceptual/`. Per-test naming is at founder discretion; recommended pattern is `<scenario>.png` where `<scenario>` mirrors the AC or the test name.

```
docs/specs/0042-login/perceptual/
  ├── post-login.png        # asserted by test_login_redirect_screenshot
  ├── empty-state.png       # asserted by test_login_empty_state_screenshot
  └── error-display.png     # asserted by test_login_invalid_credentials_screenshot
```

### Predicate text

> The screenshot at the documented `artifact_path` regenerates from the named test and is byte-stable across runs at the founder's configured rendering environment.

Decomposed:

1. The test named in the failing-test seed entry (tagged `[perceptual]`) exists in the codebase under a discoverable path (the existing `/build` test-discovery contract handles this).
2. Running the test exits with status zero (pass).
3. The artifact exists at `artifact_path` after the test runs.
4. The artifact is byte-equal to the version checked into the repo (byte-stable across runs).

### Format constraint

PNG only for v0.2. The artifact is a raster screenshot; v0.2 takes byte-equality as the comparison rule. The founder is responsible for deterministic rendering: a fixed-viewport headless browser (Playwright, Puppeteer, Cypress, equivalent), pinned font set, fixed device pixel ratio. The 2026 visual-regression discourse converged on this configuration; the framework does not enforce a specific tool because the choice depends on the stack.

Screencasts and structured layout artifacts are v0.2.x considerations:

- **Screencasts** (mp4 / webm) introduce a comparison-rule question (per-frame? duration-equal? transcript-equal?) that v0.2 does not need to answer. Single-frame PNG handles the walking-skeleton perceptual contract; multi-frame is a richer signal that costs more than it saves at v0.2 grain.
- **Layout-token equivalence** (the screenshot is decomposed into a structured tree of bounding boxes + computed styles, compared structurally) is a richer comparison rule than byte-equality but requires either a layout-token capture tool or the founder authoring a token-emitting test. Defer to v0.2.x once visual-regression tooling discourse converges further.

### Why byte-equality is the v0.2 bar

Byte-equality is harsh and produces false positives at the rendering layer (subpixel anti-aliasing, font-metric drift, GPU compositor differences across machines). It is nevertheless the v0.2 bar because:

- The framework's value proposition is reproducibility; a tolerance threshold introduces a new dimension the cascade has to track and re-verify per-environment.
- The solo founder's CI is single-environment by default — the same headless Chromium, the same font set, the same DPI. False-positive rates in single-environment setups are low.
- Layout-token equivalence is the right richer predicate; deferring it to v0.2.x keeps v0.2's surface tractable.

If a founder's environment cannot produce byte-stable PNGs (a real possibility on color-managed displays or with non-deterministic font subsetting), the recommended path is to capture a deterministic intermediate (computed style tree, DOM snapshot) in a `<scenario>.html` or `<scenario>.dom.json` companion artifact under the same `perceptual/` directory. The walking-skeleton predicate accepts any artifact under the path; the test asserts what counts as "regenerated." v0.2 only checks existence and byte-stability of the file the test names.

### Manifest representation

Per-entry on `failing_test_seed[]` for `[perceptual]` tests:

```json
{
  "name": "test_login_redirect_screenshot",
  "tag": "perceptual",
  "artifact_path": "docs/specs/0042-login/perceptual/post-login.png",
  "asserts": "the screenshot regenerates and matches the layout when a successful auth returns",
  "covers_ac": ["AC-2"]
}
```

`artifact_path` must:

- Be a string.
- Start with `docs/specs/NNNN-<slug>/perceptual/` where `NNNN-<slug>` matches the spec's own slug.
- End in `.png` for v0.2 walking-skeleton (extension constraint is per-strategy; api-boundary and capability-cluster have their own).

## Api-boundary perceptual predicate

### Path convention

Exactly one file:

```
docs/specs/NNNN-<slug>/perceptual/integration-transcript.md
```

No alternatives at v0.2. One transcript file per api-boundary spec, regardless of how many AC the spec carries. Multiple scenarios live inside the single file as sub-sections (schema below). Splitting across files is a v0.2.x consideration if real api-boundary specs grow transcripts past readability — v0.2 ships single-file.

### Predicate text

> The transcript file at `docs/specs/NNNN-<slug>/perceptual/integration-transcript.md` regenerates byte-stably from the named test and conforms to the minimum sectional schema.

Decomposed:

1. The test named in the failing-test seed entry (tagged `[perceptual]`) exists in the codebase and exits zero on run.
2. The transcript file exists at the canonical path.
3. The file parses to the minimum sectional schema (below).
4. The file is byte-equal to the version checked into the repo (byte-stable).

### Minimum sectional schema (v0.2)

The transcript is markdown. The minimum H2-level structure is:

```markdown
# Integration transcript — <spec slug>

## Scenario: <scenario name>

### Request

```http
<verbatim HTTP request, including method, path, headers, body>
```

### Response

```http
<verbatim HTTP response, including status, headers, body>
```

### Notes

<optional commentary — what this scenario demonstrates, edge-case framing, etc.>

## Scenario: <next scenario name>

…
```

Required:

- One top-level `# Integration transcript` H1 header. Slug-name suffix is informational.
- One or more `## Scenario:` H2 headers, each with a non-empty scenario name following the colon.
- Every `## Scenario:` block contains exactly one `### Request` and exactly one `### Response` H3 child, each followed by at least one fenced code block.

Optional:

- `### Notes` H3 child per scenario.
- Free-form prose between scenarios (header notes, conventions, links to related docs).

Code blocks may use any language tag, including `http`, `json`, `bash`. The framework does not enforce a specific tag; the founder's test framework drives the format. The framework only checks the H1/H2/H3 structure.

### Why markdown-only at v0.2

D3.0's read on api-boundary evidence converged on the documentation-vs-executable-spec split: markdown is the human-readable documentation form, structured (JSON / YAML) is the machine-checkable executable form. Pact's broker model assumes both — JSON fixture as the wire-format, human-readable form as documentation generated from it.

For solo-stack v0.2 the framework needs only one of them. Markdown is chosen because:

- The transcript is the consumer's documentation surface. A founder onboarding a new SDK author or new internal caller reads the markdown; the test re-renders the markdown from the recorded interaction.
- Byte-stability against markdown is a real-world predicate (no library is needed to diff two markdown files).
- The H2/H3 structure is parseable with a regex in `/verify` pre-flight; no markdown library dependency.
- A structured shadow at `…/perceptual/integration-transcript.json` is an additive v0.2.x extension if downstream tooling (auto-generated SDKs, API clients) wants it.

### Manifest representation

```json
{
  "name": "test_create_invoice_integration_transcript",
  "tag": "perceptual",
  "artifact_path": "docs/specs/0042-invoices/perceptual/integration-transcript.md",
  "asserts": "the transcript regenerates byte-stably from a documented consumer-call sequence covering AC-1 through AC-4",
  "covers_ac": ["AC-1", "AC-2", "AC-3", "AC-4"]
}
```

The `artifact_path` for api-boundary is strictly fixed (the literal path with the spec's slug substituted). Any other path for a `[perceptual]` test in an api-boundary spec is a `/specify`-seal defect; the seal verifier predicate halts `§pyramid-shape-violation/strategy-mismatch`.

## Capability-cluster perceptual predicate

### Path convention

Artifacts under `docs/specs/NNNN-<slug>/perceptual/`. Per-artifact-type extension is drawn from a canonical table for known types; novel types use founder-declared extensions with the same path prefix.

### Canonical type table (v0.2)

| Capability artifact | Extension | Path example |
|---|---|---|
| Rendered document (PDF, generated report) | `.pdf` | `…/perceptual/invoice-2026-001.pdf` |
| Image (chart, diagram, generated graphic) | `.png` | `…/perceptual/dashboard-chart.png` |
| Scheduled event (calendar invite) | `.ics` | `…/perceptual/team-sync-event.ics` |
| Share-post / social media body | `.md` | `…/perceptual/launch-announcement.md` |
| Email / message body | `.eml` or `.md` | `…/perceptual/welcome-email.eml` |
| API response capture (capability-internal, distinct from api-boundary's transcript) | `.json` | `…/perceptual/recommended-feed.json` |
| Plain-text capture (logs, structured text outputs) | `.txt` | `…/perceptual/digest.txt` |

For novel artifact types not in the table, the founder declares the extension at `/specify` step 3. The chosen extension is recorded on the manifest; the framework checks file existence at the path but does not validate format. Per-extension format validators are a v0.2.x consideration.

### Predicate text

> The capability's artifact at the documented `artifact_path` regenerates from the named test, exists at the canonical path, and is byte-stable across runs.

Decomposed:

1. The test named in the failing-test seed entry (tagged `[perceptual]`) exists in the codebase and exits zero on run.
2. The artifact exists at `artifact_path` after the test runs.
3. `artifact_path` is under `docs/specs/NNNN-<slug>/perceptual/`.
4. The artifact's extension matches the canonical table entry for the chosen artifact type, OR matches a founder-declared extension recorded on the manifest.
5. The artifact is byte-equal across runs.

### Single canonical table vs per-spec discretion — decided

The handoff thread named this as open. D3.3 chooses **canonical table for known types, per-spec discretion for novel types**.

Rationale:

- A founder who sees `[perceptual]` on a capability-cluster spec and asks "what extension do I use for a calendar invite?" gets a one-table answer. This is the same pattern that made D3.2's strategy → pyramid_shape catalog cheap to author against.
- The canonical table covers >90% of solo-stack capability artifacts (the categories above came from D3.1's examples plus mailmerge + scheduled-task patterns from the 2026 LLM-app discourse).
- Novel types still work — declaring `.usdz` for an AR-asset capability is a one-line addition at `/specify` step 3 — but the founder pays the per-spec cost.
- Allowing full per-spec discretion without a table would invite proliferation (`.report`, `.invoice`, `.thing`) that downstream tooling has no way to reason about; the table anchors at extensions that have OS-level mime mappings.

The table is versioned implicitly by D3.3's `schema_version`. v0.2.x can add rows without breaking sealed manifests.

### Byte-stability for binary artifacts

PDFs, PNGs, and most binary artifacts contain non-deterministic embedded data (PDF `/CreationDate`, PNG `tIME` chunk, JPEG exif timestamps). v0.2's byte-stability bar requires the founder's test framework to scrub these — either at generation time (set fixed timestamps) or post-generation (normalize the artifact). This is the same constraint visual-regression tooling has lived with for a decade; the 2026 maturity of tools like `playwright-test-screenshots` and `@storybook/test-runner` handles it transparently for the common cases.

For artifacts where byte-stability is genuinely intractable at v0.2 (true SVG outputs with embedded timestamps, signed PDFs, encrypted payloads), the recommended escape is to assert against a documented intermediate (the unsigned canonical form, the SVG before signing) and check that intermediate into `perceptual/`. v0.2 does not provide tolerance-threshold comparison; v0.2.x may.

### Manifest representation

```json
{
  "name": "test_invoice_render_pdf",
  "tag": "perceptual",
  "artifact_path": "docs/specs/0042-invoicing/perceptual/invoice-sample.pdf",
  "artifact_type": "rendered-document",
  "asserts": "the rendered PDF regenerates byte-stably and matches the documented layout for AC-2 sample data",
  "covers_ac": ["AC-2"]
}
```

`artifact_type` is a new optional per-entry field added only for capability-cluster's `[perceptual]` entries. It is a string drawn from the canonical-type-table's left column (lowercased, hyphenated: `rendered-document`, `image`, `scheduled-event`, `share-post`, `email`, `api-response`, `plain-text`) OR a founder-declared free-form string when the type is novel. For novel types the `artifact_path` extension is whatever the founder chose; the framework does not constrain it beyond "matches the recorded extension."

For walking-skeleton and api-boundary `[perceptual]` entries, `artifact_type` is omitted (walking-skeleton is implicitly `image`; api-boundary is implicitly `integration-transcript`, a singleton type not in the capability-cluster table).

## Refactor-spike invariance predicate

### Path convention

```
docs/specs/NNNN-<slug>/invariance/
  ├── pass-set-at-seal.txt        # written by /specify step 7 seal
  └── pass-set-at-verify.txt      # written by /verify each run; not committed
```

`pass-set-at-seal.txt` is committed to the repo as the seal artifact. `pass-set-at-verify.txt` is regenerated on every `/verify` run and is `.gitignore`-d (the framework's repo template includes the gitignore line).

### Predicate text

> The set of test IDs passing at `spec_sealed_at` is a subset of the set of test IDs passing at `/verify` time.

Decomposed:

1. `pass-set-at-seal.txt` exists at the canonical path and is non-empty.
2. The configured `invariance.pass_set_capture_command` in `docs/.solo-config.json` runs and exits zero at `/verify` time.
3. The command's stdout, captured to `pass-set-at-verify.txt`, contains every line from `pass-set-at-seal.txt`. New lines (new passing tests) are allowed; missing lines (formerly-passing tests now absent) halt.

### Pass-set, not pass-count — confirmed

The handoff thread noted this explicitly; D3.3 confirms. A refactor that breaks one pre-existing test and accidentally fixes another would pass count-equality but is a regression on the strict pass-set. The 2026 mutation-testing discourse (Stryker / mutmut / pitest) treats this distinction as table-stakes; D3.3 inherits the framing without inheriting the install cost.

### Runner-agnostic capture mechanism

The framework does not bundle a runner. The founder configures the capture command in `docs/.solo-config.json`:

```json
{
  "invariance": {
    "pass_set_capture_command": "<shell command producing one test ID per line on stdout, exiting 0 on success>"
  }
}
```

Examples per runner:

- **pytest with pytest-json-report:**
  `pytest --json-report --json-report-file=/dev/stdout --quiet 2>/dev/null | jq -r '.tests[] | select(.outcome == "passed") | .nodeid'`
- **vitest:**
  `vitest run --reporter=json 2>/dev/null | jq -r '.testResults[].assertionResults[] | select(.status == "passed") | "\(.ancestorTitles | join(" > ")) > \(.title)"'`
- **jest:**
  `jest --json --silent 2>/dev/null | jq -r '.testResults[].assertionResults[] | select(.status == "passed") | "\(.ancestorTitles | join(" > ")) > \(.title)"'`
- **go test:**
  `go test -json ./... 2>/dev/null | jq -r 'select(.Action == "pass" and .Test != null) | "\(.Package)::\(.Test)"'`
- **cargo test:**
  `cargo test --no-fail-fast -- -Z unstable-options --format json 2>/dev/null | jq -r 'select(.type == "test" and .event == "ok") | .name'`

The framework does not validate the command beyond "exits zero, produces non-empty stdout." Test IDs are opaque strings; sort order and exact format are the founder's choice as long as both seal-time and verify-time captures produce the same shape.

### Why runner-agnostic

A bundled runner would force a Python (or Node, or Go) toolchain into the framework's distribution. For a polyglot framework — and solo founders are heavily polyglot in 2026 — pinning a runner is the wrong cost. The trade-off accepted: founder pays a one-time configuration cost; framework stays language-agnostic.

A v0.2.x consideration is shipping a `solo invariance capture` wrapper that auto-detects the runner from the project structure (presence of `pytest.ini` → pytest preset; `package.json` with vitest → vitest preset; etc.). v0.2 ships without it.

### Manifest representation

For refactor-spike specs, `failing_test_seed[]` is empty per D3.2. The manifest's `outputs` block gains a new field:

```json
"outputs": {
  "spec_path": "docs/specs/0042-cleanup-billing/spec.md",
  "ac_list_sha256": "…",
  "decomposition_strategy": "refactor-spike",
  "pyramid_shape": { "strategy": "refactor-spike", "required_tags": ["invariance"], "optional_tags": [], "forbidden_tags": ["unit", "integration", "contract", "smoke", "perceptual"] },
  "failing_test_seed": [],
  "invariance_artifact": {
    "pass_set_path": "docs/specs/0042-cleanup-billing/invariance/pass-set-at-seal.txt",
    "pass_set_sha256": "…",
    "capture_command_sha256": "…",
    "seal_run_test_count": 247
  }
}
```

- `pass_set_path` — the file path; checked for existence on `/verify` pre-flight.
- `pass_set_sha256` — content hash of `pass-set-at-seal.txt` at seal time; the file is committed but the hash on manifest catches accidental hand-edits.
- `capture_command_sha256` — hash of the configured capture command string at seal time; if the founder edits the command between seal and verify, the predicate halts (a different command produces a different pass-set; the comparison would be invalid). Re-seal under `/specify --unseal` is the recovery.
- `seal_run_test_count` — informational; the count of tests in `pass-set-at-seal.txt`. Surfaced at halt-card time to make the diff obvious.

`invariance_artifact` is present only on `/specify` outputs for refactor-spike specs. For all other strategies the field is absent. For hybrid parents the field is absent at the parent grain; hybrid children carrying refactor-spike strategy have the field at the child grain.

### What happens if the pass-set is empty at seal

A refactor-spike spec sealing against a codebase with zero passing tests has nothing to preserve. The strategy is misapplied; the spec is likely walking-skeleton (greenfield) or capability-cluster (new behavior on an established stack). `/specify` seal halts `§invariance-pass-set-empty` (new halt; see Halt conditions below).

## `/specify` step 7 — additions for D3.3

D3.2's step 7 seal already writes `pyramid_shape` and per-entry `tag` to the manifest. D3.3 adds:

1. **For all strategies with `[perceptual]` required:** for each `[perceptual]` entry in `failing_test_seed[]`, validate `artifact_path`:
   - Field is present and a string.
   - String begins with `docs/specs/NNNN-<slug>/perceptual/` with the spec's own slug substituted.
   - For walking-skeleton: extension is `.png`.
   - For api-boundary: full string is exactly `docs/specs/NNNN-<slug>/perceptual/integration-transcript.md`.
   - For capability-cluster: extension matches the canonical table for `artifact_type` (if recorded) OR is a founder-declared extension paired with a free-form `artifact_type`.
   - Failures halt `§pyramid-shape-violation/artifact-path-invalid` (new sub-case).
2. **For refactor-spike specs:** before computing `ac_list_sha256` and writing the manifest, run the invariance capture sequence:
   1. Read `docs/.solo-config.json`. If absent or missing `invariance.pass_set_capture_command`, halt `§invariance-config-missing`.
   2. Execute the capture command from the repo root. On non-zero exit, halt `§invariance-config-missing/capture-failed` (sub-case).
   3. Write stdout to `docs/specs/NNNN-<slug>/invariance/pass-set-at-seal.txt`, one line per test ID, blank lines and lines beginning with `#` filtered out.
   4. If the resulting file is empty, halt `§invariance-pass-set-empty`.
   5. Compute `pass_set_sha256` of the file content; compute `capture_command_sha256` of the configured command string.
   6. Write `outputs.invariance_artifact` to the manifest.
3. **For hybrid parents:** no additions at the parent grain (already empty seed, null shape per D3.2). `/plan`'s decomposer applies D3.3's predicates to each child per the child's strategy when it writes per-child manifests.

## `/verify` mechanics — D3.3 predicates

`/verify` is the milestone-level cascade stage per D2.1 v2 (line 174). D3.3 extends `/verify`'s pre-flight to evaluate the per-strategy predicates above. For every child of the milestone:

1. **Load the child's `/specify` manifest** from its `input_provenance` chain.
2. **Read `decomposition_strategy` and `pyramid_shape`.**
3. **For non-refactor-spike children with `perceptual` in `pyramid_shape.required_tags`:** for each `[perceptual]` entry in `failing_test_seed[]`:
   - Predicate P1: `artifact_path` referent exists on the filesystem. Failure halts `§perceptual-evidence-missing/artifact-absent`.
   - Predicate P2: re-run the test (or read the most recent build's test-output manifest produced by `/build`). Test exit-status is zero. Failure halts `§perceptual-evidence-missing/regeneration-failed`.
   - Predicate P3: artifact byte-equality between checked-in and freshly-generated. Failure halts `§perceptual-evidence-missing/byte-stability-failed`.
   - Predicate P4 (api-boundary only): transcript file parses to the minimum H2/H3 schema. Failure halts `§perceptual-evidence-missing/transcript-shape-violation`.
4. **For refactor-spike children:** read `outputs.invariance_artifact`:
   - Predicate P5: `pass-set-at-seal.txt` exists at the documented path. Failure halts `§perceptual-evidence-missing/artifact-absent` with strategy `refactor-spike` annotation (the same halt card handles both perceptual and invariance file-absence; the diagnostic context names the strategy).
   - Predicate P6: file's current sha256 equals manifest's `pass_set_sha256`. Failure halts `§invariance-seal-tampering`.
   - Predicate P7: the configured `invariance.pass_set_capture_command` in `docs/.solo-config.json` hashes to `capture_command_sha256`. Failure halts `§invariance-config-changed`.
   - Predicate P8: re-run the capture command. Exit zero, non-empty output. Failure halts `§invariance-config-missing/capture-failed` (the same halt as `/specify`-time capture failure; the cause is identical).
   - Predicate P9: write the result to `docs/specs/NNNN-<slug>/invariance/pass-set-at-verify.txt` (not committed). Compute set-membership: every line in `pass-set-at-seal.txt` appears in `pass-set-at-verify.txt`. Failure halts `§invariance-pass-set-regression`.
5. **For hybrid parents:** cascade to children. Hybrid parents have no parent-level predicate; each child carries its strategy's predicate set.

Predicates P1–P9 are independent and recomputable. They compose with D2.1 v2's full verifier chain at `/verify` pre-flight; D3.2's `/specify`-seal predicates have already fired upstream and need not re-run at `/verify` (the manifest chain's checksum integrity guarantees the sealed shape).

### What `/verify` re-reads vs trusts from `/build`

D2.1 v2's trust model says the parent never trusts a stage's self-report; it re-reads evidence. For D3.3:

- `/verify` re-runs perceptual tests at pre-flight to produce P2/P3 evidence independently from `/build`'s claim. `/build`'s manifest records that the tests passed at build time; `/verify` re-confirms because the codebase may have changed between `/build` and `/verify` (a parallel child's commit could regress this child's tests).
- `/verify` re-reads the artifact bytes for P3 and re-parses the transcript for P4.
- `/verify` re-runs the invariance capture for P8/P9. The seal-time pass-set is the durable contract; verify-time pass-set is re-computed every run.

If re-running every perceptual test at every `/verify` is too slow for milestones with many children, v0.2.x may introduce a `--trust-build` flag that reads `/build`'s test-output manifest instead of re-running. v0.2 always re-runs. This is by design: the milestone gate is the place where re-verification cost is paid.

### `solo-verify` CLI parity

Per the carry-forward note: every verifier predicate has a `solo-verify <stage> <ticket>` CLI for the max_turns gap. D3.3's predicates inherit this contract:

- `solo-verify verify <ticket>` runs P1–P9 for the named milestone's children and emits the same halt cards `/verify` would.
- `solo-verify perceptual <ticket>` runs P1–P4 against a single child (debugging convenience).
- `solo-verify invariance <ticket>` runs P5–P9 against a single refactor-spike child.

Build-time enforcement of the CLI surface is D4.x's concern; D3.3 names the contract.

## Manifest schema additions

Cumulative with D3.2's additions:

```json
{
  "outputs": {
    "spec_path": "…",
    "ac_list_sha256": "…",
    "acceptance_criteria": [...],
    "decomposition_strategy": "walking-skeleton",
    "pyramid_shape": {
      "strategy": "walking-skeleton",
      "required_tags": ["smoke", "perceptual"],
      "optional_tags": ["unit", "integration"],
      "forbidden_tags": ["contract", "invariance"]
    },
    "failing_test_seed": [
      {
        "name": "test_login_form_mounts",
        "tag": "smoke",
        "asserts": "the login route mounts and the form renders without throwing",
        "covers_ac": ["AC-1"]
      },
      {
        "name": "test_login_redirect_screenshot",
        "tag": "perceptual",
        "artifact_path": "docs/specs/0042-login/perceptual/post-login.png",
        "asserts": "screenshot regenerates at the documented path on successful auth",
        "covers_ac": ["AC-2"]
      }
    ],
    "invariance_artifact": null
  }
}
```

Three D3.3 changes from D3.2's v2-additive schema:

- **New optional per-entry field `artifact_path`** on `failing_test_seed[]`. Required when `tag = perceptual`; absent otherwise.
- **New optional per-entry field `artifact_type`** on `failing_test_seed[]`. Required when `tag = perceptual` AND `decomposition_strategy = capability-cluster`; absent otherwise.
- **New top-level optional field `invariance_artifact`** on `outputs`. Present only when `decomposition_strategy = refactor-spike` (or a hybrid child carrying that strategy). For all other cases the field is `null` or absent; the schema accepts either.

The schema is additive to D3.2; sealed manifests under D3.2 (with no `artifact_path`, no `artifact_type`, no `invariance_artifact`) fail D3.3's `/verify`-time predicates at the next milestone's pre-flight. Migration is `/specify <MARKER> --unseal` per D2.1 v2's recovery pattern; no manifest-rewrite tool ships in v0.2.

## Halt conditions

Three new entries for `docs/templates/halt-messages.md`. All fire at `/verify` time except `§invariance-config-missing` (which fires at `/specify` seal AND `/verify`) and `§invariance-pass-set-empty` (which fires only at `/specify` seal).

### §perceptual-evidence-missing

- **When:** `/verify` pre-flight detected a perceptual evidence predicate failed for at least one child. Sub-cases:
  - `artifact-absent` — the file referenced by `artifact_path` (or `invariance_artifact.pass_set_path` for refactor-spike) is not present on the filesystem.
  - `regeneration-failed` — the named test exited non-zero at `/verify` re-run; the artifact may or may not be present, but the contract "regenerates from the named test" is broken.
  - `byte-stability-failed` — the artifact exists at the path but is not byte-equal to the checked-in version after the test re-runs. For walking-skeleton/capability-cluster this almost always means non-deterministic rendering; for api-boundary it almost always means a non-deterministic API response (timestamp, ULID, random token) leaking into the transcript.
  - `transcript-shape-violation` (api-boundary only) — the file parses but is missing the minimum H1/H2/H3 schema (no `# Integration transcript` H1; no `## Scenario:` H2; a scenario block missing `### Request` or `### Response`).
  - `path-outside-convention` — `artifact_path` is outside the `docs/specs/NNNN-<slug>/perceptual/` prefix (this should have been caught at `/specify` seal; if it reaches `/verify`, the manifest has been tampered with).
- **Recommendation:**
  - For `artifact-absent`: re-run `/build <child-ticket>` and verify the test produces the artifact at the path. If the test names a different path than the manifest's `artifact_path`, the spec and the test are out of sync — fix the test or `/specify <spec> --unseal` and revise the seed.
  - For `regeneration-failed`: read the test's failure output; the named test is genuinely failing at `/verify`. Fix the implementation; re-run `/build`.
  - For `byte-stability-failed`: examine the artifact's diff between checked-in and freshly-generated. The fix is in the test framework's configuration (fix viewport, pin font, scrub timestamps), not in the cascade.
  - For `transcript-shape-violation`: the test's output formatter is generating non-conforming markdown. Fix the formatter; the predicate requires the minimum H1/H2/H3 schema.
  - For `path-outside-convention`: the manifest has been hand-edited. `--unseal` and re-seal; do not back-patch the field manually.
- **Rationale:** Perceptual evidence is the artifact a human-or-machine downstream consumer reads to verify the cascade's claim. A missing or malformed artifact at the documented path means the cascade's claim cannot be independently verified — exactly the failure mode F-3 names.
- **Alternatives:** `/specify <ticket> --unseal` if the structural change required is larger than a test/implementation fix.
- **Diagnostic context:** sub-case name; child ticket ID; strategy verbatim; `artifact_path` from manifest; filesystem state at the path ("absent" | "present, size N bytes, sha256 H"); test name verbatim; for `byte-stability-failed`: diff summary (lines changed for text, byte-count delta for binary); for `transcript-shape-violation`: the first H2 or H3 the parser expected but did not find.

### §invariance-pass-set-regression

- **When:** `/verify` pre-flight for a refactor-spike child re-ran the configured pass-set capture command, and the verify-time pass-set is missing one or more test IDs that were present in `pass-set-at-seal.txt`.
- **Recommendation:** Identify the regressed test IDs from the diff. The refactor has changed observable behavior — either fix the regression (the refactor was supposed to preserve behavior; restore it) or, if the regression is intentional and represents a behavior change, `/specify <ticket> --unseal` and re-seal under a strategy that authors new tests (walking-skeleton if greenfield-shaped; capability-cluster if a capability is being modified; api-boundary if a contract is changing). Refactor-spike is the wrong strategy for intentional behavior change.
- **Rationale:** Refactor-spike's entire contract is invariance preservation. A pass-set regression means the contract has been broken; downstream gates cannot let the milestone ship with the strategy's promise unmet.
- **Alternatives:** If the regression is suspected to be a flake (non-deterministic test failing on this run), re-run `/verify`. Flaky tests in the pre-existing pass-set are a separate problem; D3.3 does not provide flake-tolerance, but the founder may diagnose by running `solo-verify invariance <ticket>` repeatedly.
- **Diagnostic context:** child ticket ID; list of test IDs present in `pass-set-at-seal.txt` but absent from `pass-set-at-verify.txt` (the regression set); the seal-time count vs verify-time count; paths to both `pass-set-at-seal.txt` and `pass-set-at-verify.txt` for the founder to diff manually.

### §invariance-config-missing

- **When:** `/specify` seal for a refactor-spike spec (or `/verify` for a refactor-spike child) found `docs/.solo-config.json` absent, missing the `invariance.pass_set_capture_command` key, or the capture command exited non-zero on its first invocation. Sub-cases:
  - `config-file-absent` — `docs/.solo-config.json` does not exist.
  - `key-missing` — file exists but `invariance.pass_set_capture_command` key is absent or empty.
  - `capture-failed` — command exists in config but exits non-zero (also fires at `/verify` per P8).
- **Recommendation:** Create `docs/.solo-config.json` if absent. Add `invariance.pass_set_capture_command` as a string that, when run from the repo root, prints one passing test ID per line on stdout and exits zero. Verify by running the command manually; once it succeeds, `/specify <ticket> --continue` resumes the seal.
- **Rationale:** Refactor-spike's invariance predicate requires a capture command; without it, neither seal nor verify can compute the pass-set. Sealing without the config would produce a refactor-spike spec that is permanently un-verifiable, defeating the strategy.
- **Alternatives:** `/specify <ticket> --unseal` and re-seal under a different strategy if no capture command is feasible for this codebase (rare; see "Why runner-agnostic" above for guidance on producing a working command).
- **Diagnostic context:** sub-case name; path to `docs/.solo-config.json` (whether it exists); the configured command verbatim if present; the command's stdout and exit code on the most recent invocation.

### §invariance-pass-set-empty

- **When:** `/specify` seal for a refactor-spike spec ran the configured capture command successfully (exit zero) but the resulting `pass-set-at-seal.txt` contained zero test IDs.
- **Recommendation:** `/specify <ticket> --unseal` and reconsider the strategy. Refactor-spike against a codebase with no passing tests has no contract to preserve; the spec is likely walking-skeleton (greenfield shape) or capability-cluster (new behavior added to a stack that may or may not have tests elsewhere). If the codebase genuinely has no tests yet and a refactor is needed, write a walking-skeleton spec to establish the test base first, then a refactor-spike on top of it.
- **Rationale:** An empty pass-set produces a trivially-satisfied invariance predicate (the empty set is a subset of every set), so a refactor-spike with an empty seal-time pass-set offers no verification value. The strategy is misapplied; the seal halt redirects.
- **Alternatives:** None — the strategy needs to change.
- **Diagnostic context:** child ticket ID; path to the empty `pass-set-at-seal.txt`; the configured capture command's stdout (verbatim, to confirm it really was empty rather than corrupt).

### §invariance-seal-tampering and §invariance-config-changed

Two narrower halts noted in P6/P7 above.

- **§invariance-seal-tampering** — the sha256 of `pass-set-at-seal.txt` at `/verify` time does not match the manifest's `pass_set_sha256`. The file has been edited post-seal; this is not a recoverable state because the manifest's contract is grounded in the seal-time content. Recovery: `/specify --unseal` and re-seal; do not hand-edit the file.
- **§invariance-config-changed** — the sha256 of the configured `invariance.pass_set_capture_command` string at `/verify` time does not match `capture_command_sha256` on the manifest. The capture command has been edited between seal and verify; the new command produces a different pass-set, making the comparison invalid. Recovery: `/specify --unseal` and re-seal under the new command, or revert the command in `docs/.solo-config.json` to match the sealed version.

Both have the same shape as `§incomplete-failing-test-seed` and `§pyramid-shape-violation` (recommendation, rationale, alternatives, diagnostic context); full halt-card text is mechanical and lives in `halt-messages.md`.

## Carry-forward and forward-references

- **D3.4 composes D3.3's predicates into per-stage gate-firing logic.** D3.3 owns the predicate texts and their preconditions; D3.4 owns the orchestration ("at `/verify`, fire P1–P4 for every walking-skeleton/api-boundary/capability-cluster child whose pyramid_shape requires perceptual; fire P5–P9 for every refactor-spike child"). D3.4's gate definitions reference D3.3's predicate IDs (P1–P9) by name.
- **The N/A escape hatch from D2.1 v2 line 174 is closed.** D3.1 named two canonical replacements (api-boundary's integration transcript; refactor-spike's pre-existing tests as anchor); D3.3 formalizes both as concrete predicates with concrete halt conditions. There is no remaining "or N/A for non-UI" path; every strategy's perceptual or invariance contract has a re-readable artifact.
- **`/plan`'s decomposer copies `artifact_path` and `artifact_type` to children's manifests** when children inherit perceptual coverage from the parent's failing-test seed. The existing /plan-SKILL contract — "child seed is a strict subset of parent seed" — extends to the new per-entry fields without modification; D3.3 adds no /plan-side logic.
- **`/build`'s pre-flight reads `artifact_path` to know which path the test should write to.** This is consumed at build time only as a sanity-check; the test framework writes wherever the test code says. If the test writes to a different path than the manifest's `artifact_path`, the artifact won't exist at the manifest's path at `/verify`, and the cascade halts `§perceptual-evidence-missing/artifact-absent`. No /build-side enforcement is added; the contract is checked downstream.
- **Layout-token equivalence, screencast support, and per-extension format validators are parked for v0.2.x.** v0.2 ships byte-equality on PNGs, byte-equality on markdown, byte-equality on per-type files; v0.2.x can add richer comparison rules without breaking sealed manifests.
- **A structured JSON shadow of the api-boundary transcript** is a possible v0.2.x add-on. The shadow file at `docs/specs/NNNN-<slug>/perceptual/integration-transcript.json` would mirror the markdown's scenarios but in machine-parseable form; downstream tooling (auto-generated SDKs, replay harnesses) would read the JSON. v0.2 ships markdown only; v0.2.x re-evaluates if downstream demand materializes.
- **Mutation-testing pass-rate parity as an alternative invariance predicate** stays parked per D3.0's read-out. The 2026 mutation-testing tooling is mature, but the install-and-CI surface is non-trivial for a runner-agnostic framework. v0.2 ships pass-set parity; v0.2.x or v0.3 re-evaluates.
- **`solo-verify` CLI surface for D3.3's predicates** (`solo-verify perceptual <ticket>`, `solo-verify invariance <ticket>`) inherits the broader D2.2 thread on solo-verify build/distribution. D4.x decides single-binary vs Python tree vs Bun; the decision should not drift past Phase 3.

## Open questions for downstream Phase 3 docs

1. **D3.4 (gate-firing logic).** How do P1–P9 compose into per-milestone gates? Walking-skeleton's P1–P3 fire once per `[perceptual]` test per child; api-boundary's P1–P4 fire once per `[perceptual]` test per child (there should typically be one such test, the integration-transcript test); capability-cluster's P1–P3 fire once per `[perceptual]` test per child (potentially multiple per child if the capability composes multiple artifacts); refactor-spike's P5–P9 fire once per refactor-spike child. Hybrid milestones compose per child. D3.4 formalizes the matrix and decides what happens when multiple predicates fail simultaneously (combined halt-card with the worst-precedence sub-case in the recommendation line, mirroring D3.2's pattern for `§incomplete-failing-test-seed`).
2. **Whether `/verify` should re-run perceptual tests or trust `/build`'s test-output manifest.** D3.3 says always re-run at v0.2; v0.2.x may add `--trust-build` for milestones with many children. The trust model's principle ("don't trust, verify") argues for re-running indefinitely; the cost argument argues for trust-with-checksum after v0.2 ships. D4.x decides.
3. **Per-extension format validation for capability-cluster artifacts** (does `.pdf` parse as a real PDF? Does `.ics` parse as iCalendar? Does `.eml` parse as an RFC 5322 message?) is parked. v0.2 only checks file existence and byte-stability; per-format validators are a v0.2.x consideration if real specs produce malformed artifacts and the cascade fails to catch them. The bet is that malformed artifacts fail the founder's own test framework first, before `/verify` ever runs.
4. **Whether `pass-set-at-verify.txt` should be a manifest-recorded path on `/verify`'s outputs.** D3.3 treats it as ephemeral (regenerated every run, gitignored, diffable on demand). If downstream tooling — `/retro`, dashboards — wants to inspect verify-time pass-sets historically, the manifest could record the path. D3.4 or D4.x decides; v0.2 leaves it ephemeral.
5. **Should the canonical capability-cluster artifact-type table be a versioned doc** (`docs/templates/capability-artifact-types.md`) loaded by `/specify` and rev'd independently from D3.3, or stay inlined in D3.3 and the `/specify` skill? D3.3 inlines for now; a separate doc is a v0.2.x maintenance question once the table grows.
