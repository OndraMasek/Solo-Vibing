# [SOL-DOC] Four-hat review — 0003 provenance root

**Subject:** `docs/specs/0003-provenance-root/spec.md` (SOL-112).
**Reviewed:** 2026-05-29, chat-Claude inline panel.
**Mode caveat:** single-model inline simulation. Per the D2.1 v2 F-1 fix, full compliance requires the parent to recompute objection coverage from independent per-subagent transcripts at /build time; this design-pass review is a single-model simulation and is acceptable for spec sealing, not a substitute for the hook-fired panel.

**Code: transcribe this comment to `docs/specs/0003-provenance-root/four-hat-review.md` alongside the spec, per the SOL-107 re-seal pattern.**

---

## User hat (does this serve the solo founder?)

**U-1 (Medium).** The whole feature is invisible plumbing. A solo founder gets zero new capability — they get a gate that *starts working*. Risk: it reads as ceremony for ceremony's sake. **Disposition:** accept, with framing. The value statement in §Goal must make the payoff concrete: "after this, `preflight-provenance.sh` catches a broken chain before you spend a build's worth of tokens on it." That is the founder-facing benefit. Spec §Problem already states this; no change required.

**U-2 (Low).** Could the founder just keep waiving the gate forever? Yes — and for a one-person repo that might even be rational. **Disposition:** accept as a real option, reject as the default. The bootstrap exception is fine as a *temporary* waiver; leaving it permanent means the trust model is decorative. Note added via AC-6 (formal retirement). No spec change.

## Engineer hat (is it correct and buildable?)

**E-1 (High).** AC-2 is ambiguous about whether the *root* is `/onboard`'s null-upstream manifest or a non-null 0001/0002 manifest. `preflight-provenance.sh` lines 91–99 reject a null `postcondition_manifest_path` for non-onboard stages. So if the next stage to run is `/review` on a 0002 ticket, the run-state's `last_completed_stage` must be **non-null** and point at a real 0002-stage manifest — `/onboard`'s null floor alone fails AC-3. **Disposition:** ratified, spec amended. AC-2 now states both halves explicitly and AC-3 fixes the test to the actual next stage.

**E-2 (High).** "Recompute from merged evidence" is principled but underspecified: a manifest's `outputs` array names paths/linear_ids/doc_ids, but the *gate-outcome* semantics (manifest existence ≡ all gates passed) means re-sealing asserts those gates passed. For 0001/0002 the gates were **never run by the hook substrate** (it was non-functional — see SOL-113). So re-sealing would assert a pass that no verifier produced. **Disposition:** load-bearing objection, resolved into the spec via **AC-4 path (b): the re-seal must actually run `solo-verify <stage> <ticket>` against the merged state and seal only if it exits 0.** Converts "assert the gates passed" into "run the gates now, against the real merged artifacts, seal the real result." If `solo-verify` halts, the root is not sealed.

**E-3 (Medium).** Depends on SOL-113 AND SOL-115 to even execute. If 0003 is specced now but can't build until both land, the sequencing must be explicit so /plan doesn't decompose into something un-buildable. **Disposition:** accept; spec §Dependencies names both as prerequisites. /plan must not schedule /build before SOL-113 merges.

**E-4 (Low).** `sha256_manifest_self_zeroed` lives in `common.sh` (the lib SOL-113 repoints to). Until SOL-113 lands, the function the seal depends on is in a file nothing successfully sources. **Disposition:** accept, covered by E-3 sequencing.

## PM hat (is the scope right and the priority honest?)

**P-1 (Medium).** Labelled the highest-value v0.2.x item, but it cannot ship first — SOL-113 must precede it. **Disposition:** accept, no conflict. Priority (High) reflects value; sequence (after SOL-113) reflects dependency. Both recorded.

**P-2 (Medium).** Scope could balloon into "re-seal the entire history." The spec caps it at 0001 + 0002 + the `/onboard` floor and explicitly excludes pre-0001 work. **Disposition:** accept; out-of-scope list holds the line.

**P-3 (Low).** AC-6 edits a note in the *0002* spec directory from *0003*'s build. **Disposition:** accept; one-line provenance breadcrumb, not a scope leak. Spec allows a successor note under 0003 instead. /build picks.

## Skeptic hat (what breaks, what's the worst case?)

**S-1 (High).** Worst case: the re-seal runs `solo-verify` against 0001/0002 and it **halts** — the merged artifacts genuinely don't satisfy the v0.2 gates. Then there is no legitimate root and the feature *fails to deliver* by design. **Disposition:** ratified — and yes, that's the *correct* outcome. A halt means 0001/0002 shipped with a real gap; the honest move is to surface it, not paper over it. Resolved into the spec via **AC-5**: a halt during root-seal stops /build and surfaces the gate gap as a new finding; it never fabricates a passing seal.

**S-2 (Medium).** Is there a *third* path the spec missed — e.g. a dedicated `solo-verify seal-root` command? **Disposition:** considered, rejected for v0.2.x. Inventing a new command is more surface than reusing `/onboard` + `--reconcile`/`--rerun`. If /plan proves the existing primitives genuinely cannot seal a historical root, *then* a minimal new primitive becomes a design-surface item.

**S-3 (Low).** The spec itself seals under a "final bootstrap exception." Circular? **Disposition:** accept, unavoidable, bounded. Some link must seal without an upstream — that's what `/onboard`'s null floor is for. The 0003 seal riding a documented final exception is the induction base case, not a smell. Recorded in §Provenance.

---

## Objection ledger

| # | Hat | Severity | Status | Resolution path |
|---|-----|----------|--------|-----------------|
| U-1 | User | Medium | Resolved (accept) | Framing only; §Goal states the payoff |
| U-2 | User | Low | Resolved (accept) | AC-6 retires the waiver |
| E-1 | Engineer | High | **Resolved** | AC-2 amended: root must be a non-null 0001/0002 manifest, not the onboard floor alone |
| E-2 | Engineer | High | **Resolved** | AC-4: each manifest sealed by an executed `solo-verify` exit-0 run; no asserted passes |
| E-3 | Engineer | Medium | Resolved (accept) | §Dependencies; /plan must not build before SOL-113 |
| E-4 | Engineer | Low | Resolved (accept) | Covered by E-3 |
| P-1 | PM | Medium | Resolved (accept) | Priority ≠ sequence; both recorded |
| P-2 | PM | Medium | Resolved (accept) | Out-of-scope list caps it |
| P-3 | PM | Low | Resolved (accept) | /build picks note location |
| S-1 | Skeptic | High | **Resolved** | AC-5: a halt surfaces a finding, never a faked seal |
| S-2 | Skeptic | Medium | Resolved (reject) | Reuse existing primitives; new command only if /plan proves necessity |
| S-3 | Skeptic | Low | Resolved (accept) | Final bootstrap exception is the induction base case |

**Spec-blocking unresolved count: 0.** Both High objections (E-2, S-1) are resolved *into the spec*: E-2 into AC-4 (executed `solo-verify` exit-0 seal, no asserted passes), S-1 into AC-5 (a halt surfaces a finding, never a faked seal). Sealed 2026-05-29 with `ac_list_sha256 = 1c9c7549b8f600bd`.
