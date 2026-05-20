# D4.6 v1.1 — Cascade resume primitive (amendment-only pass)

**Status:** Design (v1.1 — amendments-only pass against v1; **not adversarially reviewed** as a unit. v1.1 applies three changes derived from `D2_3_v1_2_and_D4_6_four_hat_review.md`: one critical (F-Eng-1 path), one critical (F-Eng-2 / F-Int-1 `last_group_artifacts[]` drop), one important amendment absorbed inline (F-Int-6 group-exit-manifest selection).)
**Phase:** 4 (Cleanup and concrete fixes).
**Authored:** 2026-05-19, paired with `D2_1_trust_model_v2_1.md` and `D2_3_hybrid_session_boundary_v1_3.md`.
**Predecessor:** `D4_6_cascade_resume.md` (v1 — the full primitive design).
**Scope of v1.1:** §CLI surface (path change + last_group_artifacts drop + F-Int-6 read amendment), §Halt conditions (path change in one row), §Composition with D2.3 v1.3 §Handoff verification predicate (cross-reference relabeling v1.2 → v1.3 and addition of F-Int-6 alignment). All other v1 sections carry forward unchanged.

## Changelog — v1 → v1.1

| # | Section revised | Change | Resolves | Severity |
|---|---|---|---|---|
| 1 | §CLI surface — `solo-cascade resume` (no group letter) paragraph 1 | Canonical run-state path: `docs/.cascade/run-state.json` → `.cascade/run-state.json` at repo root. | F-Eng-1 | Urgent |
| 2 | §CLI surface — "What was produced" derivation paragraph | Drop the `cascade:run-state.last_group_artifacts[]` read. Read the last sealed parent manifest's `outputs` field directly. v1.3's schema stays minimal — no new run-state field added. | F-Eng-2 / F-Int-1 | High |
| 3 | §CLI surface — "Last sealed manifest" field derivation | The manifest read is explicitly the **group's exit manifest** = the parent manifest, never a subagent or per-iteration manifest. The field source is `cascade:run-state.last_completed_group_exit_manifest_path` (a v1.3 schema addition — confirmed at v1.3 §Handoff verification predicate). | F-Int-6 (absorbed inline) | Medium |
| 4 | §Halt conditions — §cascade-state-missing row | Path update to `.cascade/run-state.json`. | F-Eng-1 | Urgent |
| 5 | §Composition with D2.3 v1.3 §Handoff verification predicate (renamed from v1.2) | Cross-reference label updates v1.2 → v1.3. | Lockstep with v1.3 | Cleanup |
| 6 | §Cross-references — D2.3 reference | Label updates v1.2 → v1.3. | Lockstep with v1.3 | Cleanup |

The §Decision, §Why this matters, §`--rewrite-file` / `--json` / `--explain` flag sections, §Exit semantics, §Composition with chat-Claude vs Claude Code, §Why this lives in D4.6 and not D4.5, §Files this introduces, §Implementation order, §What v0.2 does not ship, and §Open items are all unchanged from v1.

---

## §CLI surface (v1.1 amended)

### `solo-cascade resume` (no group letter)

Reads `cascade:run-state.json` from **`.cascade/run-state.json`** at repo root (canonical path per D2.1 v2.1, sibling to `.cascade/session/`, `.cascade/manifests/`, `.cascade/halt/`). Computes the next group from `last_completed_group + 1` (A=0 … H=7); halts §cascade-state-terminal if `last_completed_group == "H"` and no new feature has begun. Otherwise re-derives the chat-end card body and the handoff prompt, prints to stdout.

The re-derivation populates every field the chat-end card template (D2.3 v1.3) requires:
- `Marker`, `Product` ← `cascade:run-state.marker`, `.product`
- `Parent feature` ← `cascade:run-state.parent_feature_name`
- `Group entry` ← computed next group
- `Active ticket` ← `cascade:run-state.next_ticket` (or `active_stages[0].ticket` if mid-build)
- `Active milestone` ← `cascade:run-state.active_milestone`
- `Queue version` ← `cascade:run-state.queue_version`
- `Prior group exit` ← `cascade:run-state.last_group_exit_at`
- `Last sealed manifest` and its sha ← read from `cascade:run-state.last_completed_group_exit_manifest_path` and the corresponding manifest file's sha256. The exit manifest is **always the parent manifest** for the just-completed group (per D2.3 v1.3 §`/Chains` contract per-pattern statement): `/onboard`'s manifest for A, `/discovery`'s for B, `/constitution`'s for C, `/specify`'s for D (containing the merged four-hat outputs), `/update-linear`'s for E (the last stage of the chain), `/wrap`'s for F (per-ticket, the last F chat), `/verify`'s for G (containing `children_gate_outcomes[]`), `/retro`'s for H. **Never** a subagent manifest, a per-iteration intermediate, or a non-terminal chain stage's manifest.
- `Handoff sha` ← computed over the re-derived card body per D2.3 v1.3 §Group-exit mechanics atomicity

The "What just happened," "What was produced," and "Where we are in the cascade" prose sections are also re-derived **from the group's exit manifest directly** — no `cascade:run-state.last_group_artifacts[]` indirection. Specifically:
- "What just happened" reads the exit manifest's `outputs` summary field (a single-sentence description that every stage's exit manifest carries per D2.1 v2.1 common-manifest-fields) and renders it as the one-sentence summary.
- "What was produced" enumerates the exit manifest's `outputs` array — each entry already names its `path`, `linear_id`, or `doc_id` per D2.1 v2.1's manifest schema. D4.6 lists them verbatim in the order the manifest declares them. No flattening across multiple manifests is performed (the exit manifest by construction already aggregates the group's externally-visible artifacts; subagent and intermediate-stage outputs are not externally visible at the cross-group boundary).
- "Where we are in the cascade" lists groups A through `last_completed_group` as "Completed," and `next_group` as "Next," driven entirely by `cascade:run-state.last_completed_group`. No manifest read needed for this section.

The prose is necessarily terser than what the original group-exit render produced — it lacks the in-chat dialogue context — but it carries every field the §Handoff verification predicate requires.

### `solo-cascade resume <group-letter>`

Same as the no-letter form but with an explicit assertion that the next group equals the supplied letter. Halts §cascade-resume-group-mismatch if `cascade:run-state.last_completed_group + 1 != <group-letter>`. Useful when the founder knows which group they expect to resume into and wants the primitive to confirm rather than infer.

### `--rewrite-file`

Side effect: writes the re-derived card to `.cascade/handoff/last.md` using the atomic write protocol from D2.3 v1.3 §Group-exit mechanics atomicity (write to `.tmp`, fsync, rename). Without `--rewrite-file`, the primitive is purely read-only. The flag exists for the case where `.cascade/handoff/last.md` is missing or corrupted and the founder wants both the stdout output (to paste) and a restored file (for path b to work again next time).

**Open item carried from v1:** flag-default flip (F-Usr-4 — defer rewrite default to v0.2.x). v1.1 keeps `--rewrite-file` opt-in to preserve the "primitive is read-only by default" property; v0.2.x decides whether to flip default-on once dogfood reveals which mode is more common.

### `--json`

Output the card fields as a JSON object rather than the rendered markdown. Useful for `solo-verify`'s pre-flight chain and for programmatic resume tooling. The JSON shape matches the parsed-card representation the §Handoff verification predicate consumes (keys: `marker`, `product`, `parent_feature`, `group_entry`, `active_ticket`, `active_milestone`, `queue_version`, `prior_group_exit_at`, `last_completed_group_exit_manifest_path`, `last_sealed_manifest_sha256`, `handoff_sha256`, `card_body` containing the rendered markdown).

Note the `last_completed_group_exit_manifest_path` key — the v1.1 amendment surfaces the exit manifest's path explicitly so programmatic consumers can re-read it without re-deriving the path from `cascade:run-state`. The v1.3 schema field is the source of truth; D4.6's JSON shape mirrors it for convenience.

### `--explain`

Print a diagnostic trace of the re-derivation: which fields came from which source files, which computations were performed, and which manifests were consulted. Used for debugging when re-derivation produces an unexpected card (typically because `cascade:run-state` is itself in a surprising state).

The v1.1 amendment makes the `--explain` output more informative: in addition to the previously-traced fields, the trace now names the specific group exit manifest path consulted for "What just happened" and "What was produced," and traces back to which `cascade:run-state` field pointed at that manifest. This makes F-Int-6 cases (a misidentified exit manifest) diagnosable without source-reading.

---

## §Halt conditions (v1.1 amended)

| Halt code | Condition |
|---|---|
| §cascade-state-missing | **`.cascade/run-state.json`** does not exist. Recovery: run `/onboard` first. |
| §cascade-state-unparseable | The file exists but is not valid JSON or fails schema validation. Recovery: D4.5's `--reconcile` against the upstream stage. |
| §cascade-state-terminal | `last_completed_group == "H"` and no new feature has begun (no active spec). Recovery: start a new feature via `/specify` in a fresh chat. |
| §cascade-resume-group-mismatch | Caller supplied a group letter that doesn't match `last_completed_group + 1`. Recovery: omit the letter, or correct it. |
| §cascade-resume-rewrite-failed | `--rewrite-file` was set and the atomic rename failed (typically: disk full, permission denied, filesystem doesn't support rename). Recovery: re-run without `--rewrite-file`, then copy stdout into the file manually. |
| §cascade-resume-manifest-chain-broken | The manifest chain that the re-derivation needs is inconsistent (sha mismatch between `cascade:run-state.last_sealed_manifest_sha256` and the named manifest file's actual sha, OR `cascade:run-state.last_completed_group_exit_manifest_path` points at a file that doesn't exist or is unparseable). Recovery: D4.5's `--reconcile` against the named stage (for the manifest-chain class of break) **or** D4.5 `--rerun=<exit-stage>` (for the named-but-absent-file class). **D4.6 stops here** rather than rewriting against a broken chain. |

The last halt (§cascade-resume-manifest-chain-broken) is the seam between D4.6 and D4.5. D4.6 never repairs manifest chains — that is D4.5's job. If `cascade:run-state` and the manifest chain disagree, D4.6 halts and points at D4.5.

**v1.1 also widens the halt's trigger surface** to cover the case where `last_completed_group_exit_manifest_path` names a file that no longer exists (e.g., the founder deleted it, or a `--reconcile` is mid-flight against it). This addresses one slice of F-Rev-2: stages without a `--reconcile` path can still hit the halt via the absent-file class, which routes to D4.5 `--rerun=<exit-stage>`. The full F-Rev-2 disposition (per-stage `--reconcile` availability) is queued for v0.2.x in D4.5's amendment plan; v1.1 only commits the D4.6-side trigger expansion.

---

## §Composition with D2.3 v1.3 §Handoff verification predicate (v1.1 amended)

The re-derived card MUST pass the §Handoff verification predicate when pasted into a new chat. v1.3's checks 1–9 all read from fields D4.6 populates from `cascade:run-state`. Specifically:

- Check 1 (paste body sha == embedded Handoff sha): D4.6 computes `Handoff sha` over the re-derived body, so this trivially passes.
- Check 2 (file body sha == file embedded sha): if `--rewrite-file` was used, D4.6's atomic write guarantees this.
- Check 3 (paste sha == file sha): if `--rewrite-file` was used, both came from the same re-derivation.
- Checks 4–9 (marker / group / ticket / milestone / stale-group / queue-version): all populated from `cascade:run-state`, which by definition matches itself.

The predicate-passing property is the contract D4.6 is built to satisfy. If a re-derived card ever fails the predicate, the bug is in `cascade:run-state.json` or the named exit manifest (caught by §cascade-state-unparseable or §cascade-resume-manifest-chain-broken), not in D4.6's re-derivation logic.

The v1.1 amendment makes one further composition explicit: **the "Last sealed manifest" line in the card** is the `last_completed_group_exit_manifest_path` field's value, with its sha256 prefix. This matches what check-7 of v1.3 §Handoff verification predicate compares against; D4.6's re-derivation is byte-stable here by construction.

---

## §Cross-references (v1.1 amended — only labels changed)

- **D2.1 v2.1** — D4.6 reads sealed manifests for the "Last sealed manifest" card field; never writes manifests. The canonical run-state path is `.cascade/run-state.json` (sibling to other `.cascade/` artifacts) per v2.1's path amendment.
- **D2.2** — `cascade:run-state` schema is D2.2's contribution; D4.6 reads it. The v1.3 field additions (`queue_version`, `last_completed_group`, `last_group_exit_at`, `active_milestone`, `parent_feature_name`, `next_chain_step`, `last_completed_group_exit_manifest_path`) are D2.3 v1.3's contribution; D4.6 reads them.
- **D2.3 v1.3** — names D4.6 as the framework-controlled recovery for §handoff-missing, §handoff-card-corrupted, §handoff-state-mismatch. D4.6 satisfies the §Handoff verification predicate contract by construction.
- **D3.4** — gate definitions are upstream of D4.6; the manifest chain D4.6 reads is built by D3.4-defined gates passing. No direct interaction.
- **D4.0** — `solo-verify` build/distribution is sibling; `solo-cascade` ships alongside under the same Python stdlib + setuptools packaging.
- **D4.5** — handoff-recovery role moves *from* D4.5 (where D2.3 v1.1 incorrectly named it) *to* D4.6 (where it correctly belongs). D4.5's five primitives are otherwise unchanged. The §cascade-resume-manifest-chain-broken halt is the explicit handoff from D4.6 back to D4.5 when a manifest chain needs repair. v1.1 widens this seam to also cover absent-exit-manifest cases (routed to `--rerun=<exit-stage>`).

---

## What's not changing in v1.1

Recorded here for traceability; all v1 content in these sections carries forward verbatim into v1.1:

- §Decision (one-paragraph what-and-why summary).
- §Why this matters (the framework-controlled recovery argument).
- §Exit semantics (exit codes 0 and 1).
- §Composition with chat-Claude vs Claude Code (CLI surface from the three contexts).
- §Why this lives in D4.6 and not D4.5 (separation rationale).
- §Files this introduces (`tools/solo-cascade`, `tools/solo-cascade-tests/`, plus updates to `docs/templates/halt-messages.md`).
- §Implementation order (six-step plan).
- §What v0.2 does not ship (`solo-cascade status`, `solo-cascade halt`, auto-resume, multi-host resume).
- §Open items (naming, concurrent-write interaction, prose terseness).

These sections do not need re-stating in v1.1; v1 remains the authoritative source for them. v1.1 is a focused amendment doc — its purpose is to land the three changes named in the changelog, not to re-state the full design.
