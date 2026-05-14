# Halt messages

How to render a halt-card when a skill returns `BLOCKED` or `NEEDS_CONTEXT` per `rules/completion-status.md`. A halt-card is the user-visible artifact at the end of a halted skill run. Its job is to tell the founder, in 30 seconds, three things: what halted, what to do next, and what the alternatives are.

Voice rules: `rules/auditor-stance.md`. Findings are facts; no preamble; no LGTM closures; mark uncertainty with `uncertain:`.

## Card schema

Every halt-card has five sections. Skills that halt render all five in this order:

~~~
## Halt: <skill-name> <status>

**Reason:** <one-line statement of what halted. Auditor-voice — state the fact, name the locus.>

**Recommended next action:**
<exact command or operation>

<one-line rationale tying the recommendation to the reason>

**Alternatives:**
1. <command or operation> — <one-line tradeoff>
2. <command or operation> — <one-line tradeoff>
3. <command or operation> — <one-line tradeoff>

**Diagnostic context:**
- <relevant state: ticket label, file path, commit SHA, agent finding, cost>
- <one more>
- <one more>
~~~

Field rules:

- **Status** is one of `BLOCKED` or `NEEDS_CONTEXT` per `rules/completion-status.md`. `DONE_WITH_CONCERNS` never renders as a halt-card — it surfaces as a summary card with concerns listed.
- **Reason** is one sentence. Auditor-voice: "Spec checksum mismatch at `docs/specs/0007-login-form/spec.md`." Not "I think the spec might have been edited."
- **Recommended next action** is a single command or operation the founder can copy-paste, with a one-line rationale. Never empty; if no recommendation is justified (e.g. spec-level FAIL with no clear path), state that and recommend founder review.
- **Alternatives** is 1–4 items in priority order. Each has the operation and its tradeoff. Omit the section entirely if there are no alternatives (rare).
- **Diagnostic context** is 1–5 lines of state the founder needs to verify the halt or recover work. Skip irrelevant lines; the goal is signal density, not completeness.

## Pattern registry

Skills reference these patterns by name when they halt — e.g. `halt-card per docs/templates/halt-messages.md §spec-drift`. The pattern fixes the recommendation logic; the skill fills in the values.

### §spec-drift

**When:** `sha256(docs/specs/NNNN-<slug>/spec.md)` does not match the value sealed in the four-hat document.

**Recommendation:** `/specify <MARKER>-N --unseal`
**Rationale:** Re-seal the four-hat so the build runs against a reviewed spec.

**Alternatives:**
1. Revert the spec markdown to the sealed version (`git checkout <sealed-commit> -- docs/specs/NNNN-<slug>/spec.md`) — preserves the seal if the edit was accidental.
2. `/specify <MARKER>-N --continue` and re-trigger the four-hat to incorporate the edit — preserves the edit if it's intentional but non-architectural.

**Diagnostic context:** sealed sha256, current sha256, four-hat doc slug.

---

### §four-hat-unresolved

**When:** Most recent iteration of the four-hat Linear document has findings without Incorporate / Defer / Reject resolutions.

**Recommendation:** Open the four-hat doc and resolve each pending finding.
**Rationale:** /build and /plan require all findings resolved before they fire.

**Alternatives:**
1. `/specify <MARKER>-N --continue` — re-enter the resolution flow.
2. `/specify <MARKER>-N --unseal` — if the unresolved findings indicate fundamental rework is needed.

**Diagnostic context:** four-hat doc slug, count of unresolved findings, iteration number.

---

### §label-mismatch

**When:** Observed scope label on a ticket is outside the state machine defined in `rules/scope-labels.md`.

**Recommendation:** Edit the ticket labels in Linear directly to match the expected state.
**Rationale:** /build and downstream skills refuse to fire on stale labels per `scope-labels.md` §Refusal protocol. Auto-repair is not available — founder intervention preserves intent.

**Alternatives:**
1. Re-run the upstream skill that should have set the expected label (e.g. `/plan <MARKER>-N` if children are missing `scope:sealed`).
2. If the mismatch reflects an unsupported state combination, surface the bug rather than mask it — open an issue.

**Diagnostic context:** ticket ID, observed labels, expected labels per the state machine.

---

### §iteration-or-wall-cap-with-progress

**When:** /build hit `iteration_cap` or `wall_cap` AND the last 3 iteration commits show forward progress in `fix_plan.md`.

**Recommendation:** `/build <MARKER>-N-K --continue`
**Rationale:** Progress is being made; another cap-bounded run is likely to converge.

**Alternatives:**
1. `/build <MARKER>-N-K --reset --confirm` — if the run is thrashing rather than progressing (founder's judgment from the last 3 commits).
2. Raise the relevant cap in `docs/.solo-config.json` first if progress is slow but real.
3. `/specify <MARKER>-N --unseal` — if the failing-test seed itself is questionable (rare at this halt).

**Diagnostic context:** iteration count, wall-clock, last 3 commit SHAs + first-line messages, this-run cost, cumulative cost across `--continue` runs.

---

### §cost-cap

**When:** /build hit `cost_cap`.

**Recommendation:** Raise `max_usd_cost` in `docs/.solo-config.json`, then `/build <MARKER>-N-K --continue`.
**Rationale:** The cap is post-iteration; spend can exceed cap by one iteration's worth. If progress is real, lifting the cap is cheaper than re-spec.

**Alternatives:**
1. `/build <MARKER>-N-K --reset --confirm` — restart with the existing cap if the run is thrashing.
2. `/specify <MARKER>-N --unseal` — split the parent if cost growth suggests undecomposability.

**Diagnostic context:** iteration count, cap value, this-run cost, cumulative cost.

---

### §drift

**When:** /build hit `drift` (3 consecutive iterations failing the same backpressure command with the same first-FAIL hash) OR /plan's decomposer flagged scope-resistance / undecomposability that maps to a stable failing condition.

**Recommendation:** `/specify <MARKER>-N --unseal`
**Rationale:** A stable failing test means the spec is wrong, not the implementation. `--reset` won't help. Re-spec the parent.

**Alternatives:**
1. Manually edit the failing-test seed in the spec, then `/specify <MARKER>-N --continue` — narrow fix for the rare case where the seed is wrong but the spec is otherwise correct.

**Diagnostic context:** drift hash, last 3 failing-backpressure outputs (verbatim, truncated to first FAIL line), failing test names.

---

### §backpressure-unresolved

**When:** /build's run.sh shows the same backpressure failure for ≥5 iterations with non-drift symptoms (different hashes; failing but not stably).

**Recommendation:** `/build <MARKER>-N-K --reset --confirm`
**Rationale:** Ralph is thrashing on the same item without converging or stably failing. Archive and re-plan from `fix_plan.md`'s current state.

**Alternatives:**
1. `/build <MARKER>-N-K --continue` — if the last iteration showed partial progress (founder's judgment).
2. `/specify <MARKER>-N --unseal` — if the failing AC is fundamentally unclear.

**Diagnostic context:** iteration count where the same item first appeared as failing, last 5 backpressure outputs (truncated).

---

### §interrupted

**When:** /build exited with `interrupted` (SIGINT / SIGTERM / host reboot).

**Recommendation:** `/build <MARKER>-N-K --continue`
**Rationale:** Interruption is mechanical; the iteration boundary is clean.

**Alternatives:**
1. `/build <MARKER>-N-K --status` first to see where Ralph stopped, then decide.
2. `/build <MARKER>-N-K --reset --confirm` — only if the interruption corrupted state (rare).

**Diagnostic context:** last iteration counter, last commit SHA, lockfile state.

---

### §live-collision

**When:** /build invoked while `.ralph/<MARKER>-N-K/run.pid` exists and the PID is alive.

**Recommendation:** `/build <MARKER>-N-K --status` to check Ralph's state.
**Rationale:** Two parallel Ralph runs on the same ticket will conflict on `fix_plan.md`. Resolve the conflict before starting a new run.

**Alternatives:**
1. `/build <MARKER>-N-K --kill` — if the running loop is stuck or wrong.
2. Wait for the existing loop to complete (use the tail one-liner from the original "Ralph running" card).

**Diagnostic context:** PID, iteration counter, wall-clock since start, cumulative cost.

---

### §build-reviewer-findings

**When:** /build's finalize phase invoked build-reviewer and the agent returned `BLOCKED` (any finding above threshold; v0.1 is halt-on-any).

**Recommendation:** Review the findings inline, edit `.ralph/<MARKER>-N-K/fix_plan.md` to address each, then `/build <MARKER>-N-K --continue`.
**Rationale:** build-reviewer halts on any finding in v0.1; the path is to fix and re-iterate, not to override.

**Alternatives:**
1. `/build <MARKER>-N-K --reset --confirm` — if findings suggest the run took a fundamentally wrong direction.
2. `/specify <MARKER>-N --unseal` — if a finding flagged a spec-level gap.

**Diagnostic context:** build-reviewer's findings block verbatim (one entry per finding: type, locus, severity, description).

---

### §linear-sync-failed

**When:** /build's finalize phase completed locally but the Linear write failed (`linear.sync.pending` marker exists).

**Recommendation:** `/build <MARKER>-N-K --sync`
**Rationale:** Local state is canonical; Linear is recoverable via retry.

**Alternatives:**
1. Manually edit the Linear ticket if `--sync` repeatedly fails (escape hatch; document the manual edit in /retro).

**Diagnostic context:** marker file path, last attempted write target, Linear API error if surfaced.

---

### §incomplete-failing-test-seed

**When:** /plan's decomposer flagged an AC not covered by the parent's failing-test seed.

**Recommendation:** `/specify <MARKER>-N --continue`, expand the failing-test seed to cover AC-X.
**Rationale:** Single AC gap — targeted re-spec is cheaper than full rebuild.

**Alternatives:**
1. `/specify <MARKER>-N --unseal` — if multiple AC have seed gaps (systemic spec issue).
2. Remove AC-X from the spec — if deferring the feature is the right call.

**Diagnostic context:** AC text, parent failing-test seed verbatim, decomposer finding (type, severity, locus).

---

### §undecomposable-parent

**When:** /plan's decomposer flagged the parent as resisting chunking into Code-Claude-sized slices.

**Recommendation:** `/specify <MARKER>-N --unseal` to split the parent into two parent specs.
**Rationale:** Two parent specs are easier to maintain, review, and parallelize. Undecomposability is a spec defect, not a build-time concern.

**Alternatives:** none — splitting is the only sanctioned recovery.

**Diagnostic context:** parent AC count, decomposer's scope-resistance finding verbatim.

---

### §ac-fail-with-fix-children

**When:** /verify minted fix-children for `med`-or-`low` severity diagnoser findings on FAIL AC.

**Recommendation:** Run each fix-child through `/build <MARKER>-N-fix-K` to resolve.
**Rationale:** Fix-children are scope-of-the-original-spec retries; the cascade resumes through them rather than re-planning.

**Alternatives:**
1. Re-run `/verify <MARKER>-N` after the fix-children are built to re-walk the failed AC.

**Diagnostic context:** failed AC list, fix-child IDs, diagnoser severity per finding.

---

### §ac-fail-spec-level

**When:** /verify's diagnoser surfaced a `high` severity spec-level finding (no fix-child minted; root cause is the spec, not the implementation).

**Recommendation:** `/specify <MARKER>-N --unseal`
**Rationale:** Spec-level gap; fix-child can't close it. Re-spec the parent.

**Alternatives:**
1. Manually edit the spec to address the gap, then `/specify <MARKER>-N --continue` — if the founder can scope the fix without a full re-seal.

**Diagnostic context:** failed AC, diagnoser finding (type, locus, description verbatim).

---

### §research-investigator-failed

**When:** /discovery's research-investigator agent failed on a mandatory Phase 2 prompt (timeout, source-freshness failure, no deep report produced).

**Recommendation:** Re-invoke /discovery to retry the prompt (research-investigator runs are idempotent within a slug).
**Rationale:** Mandatory prompts are load-bearing; skip is not an option.

**Alternatives:**
1. Manually scope the research prompt narrower, then re-invoke /discovery — if the agent timed out or hit source-freshness limits.
2. Defer the prompt to a tier-2 manual research pass — if the topic is genuinely unsearchable at this point (rare).

**Diagnostic context:** prompt text, slug, NNNN counter, agent error if surfaced.

---

### §corrupted-discovery-state

**When:** /discovery cannot locate or parse the `[<MARKER>-DOC-NNNN] discovery: state` Linear document — doc deleted, doc body unparseable, or no such doc exists.

**Recommendation:** Rename the corrupt state doc to `[<MARKER>-DOC-NNNN] discovery: state (corrupt-<timestamp>)` (preserving it as audit trail), then re-invoke /discovery to allocate a fresh state doc. Resume Phase 1 from the most recent `[<MARKER>-DOC-NNNN] discovery: idea-brief-v<N>` document's content.
**Rationale:** The state doc is the cross-surface resume anchor; with it gone or unreadable, the idea-brief docs hold the last good Phase 1 state and the surviving artifacts (research summaries, challenge memos) are still retrievable in Linear. Re-creating state preserves prior work.

**Alternatives:**
1. Hand-edit the state doc body in Linear if the corruption is visible (e.g. truncated JSON in the document's code block) — niche, but possible because Linear documents are mutable.
2. Restart /discovery from Phase 1 if no idea-brief docs exist — full restart is rare but is the documented escape hatch.

**Diagnostic context:** parse error or Linear MCP error string, last good iteration number from any `discovery: idea-brief-v<N>` doc, the state doc's `[<MARKER>-DOC-NNNN]` ID.

---

### §ticket-ac-drift

**When:** /build's precondition check found the parent ticket's AC text diverged from `docs/specs/NNNN-<slug>/spec.md`'s Acceptance criteria section (text-only comparison; checkbox state is not part of the diff).

**Recommendation:** Edit `spec.md` to capture the intended AC, then `/specify <MARKER>-N --continue` to re-mirror the ticket.
**Rationale:** `spec.md` is the canonical source of AC text per /specify Notes. The ticket is a read-only mirror written by /update-linear; direct ticket-AC text edits are not supported and would be overwritten on the next sync.

**Alternatives:**
1. Revert the ticket AC text to match `spec.md` manually in Linear, then re-run `/build` — preserves the spec if the ticket edit was accidental.
2. `/specify <MARKER>-N --unseal` — if the edit reflects a real scope change that needs four-hat review.

**Diagnostic context:** path to `spec.md`, ticket ID, list of AC lines that differ (spec text vs ticket text).

---

### §wave-merge-conflict

**When:** /wrap attempted to merge a wave's child branches into the default branch at wave-end and `git merge` failed with conflict.

**Recommendation:** Resolve the conflict manually in the default branch, commit, push, then re-run `/wrap <MARKER>-N-K --resume-merge` on the last child of the wave.
**Rationale:** Wave-2 children branch from default; without the Wave-1 merge they cannot see Wave-1's code. The merge step is non-skippable for multi-wave plans.

**Alternatives:**
1. If the conflict suggests a real spec interaction, `/specify <MARKER>-N --unseal` to re-plan with the dependency made explicit.

**Diagnostic context:** wave number, list of child branches being merged, conflicted file paths, `git status` output.

---

### §missing-context

**When:** A required context file is missing (spec markdown, north-star, idea-brief, config file, template).

**Recommendation:** For /onboard step 1 template-set gaps, run `bash bootstrap.sh --refresh-templates` to re-overlay the upstream template files without touching project state. For all other cases, create the missing artifact via the appropriate upstream skill.
**Rationale:** /build, /plan, /verify, /constitution all halt rather than guess at missing inputs. The Bomber-test findings showed that fresh forks could reach this halt with no fixable recovery — `--refresh-templates` closes that escape hatch.

**Alternatives:** none — context resolution is mandatory. Do not re-clone the template repo; that destroys `.env`, marker selection, and any post-onboard work.

**Diagnostic context:** missing file path(s), the skill or process that creates it (e.g. `docs/product/north-star.md` is written by /discovery's approve exit).

---

### §founder-declined

**When:** /constitution presented an amendment edit at the confirmation gate and the founder declined; OR /specify's clarify phase was abandoned mid-flow without confirmation.

**Recommendation:** No action required — state is unchanged.
**Rationale:** Declines are valid endings; the gate exists to make them explicit.

**Alternatives:**
1. Re-invoke the skill with different framing (e.g. `/constitution amend <different-topic>`) if the intent is still desired.

**Diagnostic context:** topic / clarify-stage, proposed change summary verbatim from the confirmation gate.

---

### §linear-unavailable

**When:** The Linear MCP connector is not connected in the Claude.ai project, or a Linear query returns errors. Surfaced by /onboard (step 2), /status, /next, /audit-self.

**Recommendation:** Add (or reconnect) the Linear connector in Claude.ai settings, then re-run the command.
**Rationale:** Every cascade stage and dashboard surface reads live Linear state; with no connector there is nothing to query.

**Alternatives:** none — the connector is mandatory for any Linear-touching operation.

**Diagnostic context:** which operation was attempted, the Linear error string if surfaced, whether the connector shows as connected in Claude.ai settings.

---

### §github-unavailable

**When:** The GitHub MCP connector is not connected in the Claude.ai project, or a GitHub query returns errors. Surfaced by /onboard (step 2).

**Recommendation:** Add (or reconnect) the GitHub connector in Claude.ai settings, then re-run the command.
**Rationale:** Chat-Claude needs GitHub MCP to read repo state remotely — without it, /specify, /plan, /verify, and /audit-self lose codebase visibility during cascade stages. v0.1 only verifies the connection at /onboard; v0.2 will wire individual skills to GitHub tools.

**Alternatives:** none — the connector is mandatory for any GitHub-touching operation. The GitHub MCP endpoint URL may change; verify against https://github.com/github/github-mcp-server if the connector fails.

**Diagnostic context:** which operation was attempted, the GitHub error string if surfaced, whether the connector shows as connected in Claude.ai settings.

---

### §onboard-setup

**When:** A /onboard environment prereq failed — `.env` is not gitignored, `.env` is missing, or the Linear personal API key is invalid / revoked.

**Recommendation:** Fix the named setup issue (gitignore `.env`, create `.env`, or paste a fresh `LINEAR_API_KEY`), then `/onboard --reinit <step>`.
**Rationale:** /onboard halts rather than proceed with a leaky or unauthenticated setup — the `.env` gitignore check and key validation are the most common silent-failure modes in fresh forks.

**Alternatives:** none for the gitignore case — it is security-load-bearing. For an invalid key, rotating it in Linear and re-pasting is the only path.

**Diagnostic context:** which prereq failed, the file path involved, `.env` gitignore status.

---

### §github-remote-missing

**When:** /onboard step 2.5 found no `origin` remote configured. The local repo has commits but no place to push them.

**Recommendation:** `gh repo create <name> --source=. --private --push --remote=origin` from the repo root (requires `gh` installed and authed).
**Rationale:** The canonical happy path is to let `gh` create the GitHub repo with no auto-init, so first push lands on a clean remote with single linear history. Bootstrap should have offered this; reaching this halt means either bootstrap ran before `gh` was authed, or the founder declined the bootstrap prompt.

**Alternatives:**
1. Manual setup: create the GitHub repo via the web UI **without** "Initialize this repository with a README" checked, then `git remote add origin <url>` and `git push -u origin main`. The auto-init box is what causes the parallel-history conflict — leave it off.
2. Skip the remote entirely (defer GitHub push to later). Chat-Claude will not be able to read the repo via the GitHub connector until a remote exists, so /discovery in chat will be blind to repo state — only do this if you intend to stay in code mode for /discovery.

**Diagnostic context:** `git remote -v` output, `gh auth status` output, repo directory name (used as default repo name).

---

### §parallel-history-risk

**When:** /onboard step 2.5's auto-push (after step 6's commit) failed against the GitHub remote because the remote has commits that do not share history with the local branch. Typically caused by pre-creating the GitHub repo via the web UI with "Initialize this repository with a README" checked.

**Recommendation:** If the remote contains only auto-init noise (README / LICENSE / .gitignore from GitHub's templates), force-with-lease the local history over it: `git push --force-with-lease origin main`. Verify the remote is empty of intentional work first.
**Rationale:** A parallel-history conflict on a fresh fork is almost always an unintended GitHub auto-init. The local history is the canonical one — it was created by bootstrap.sh with the founder's first commit. Force-pushing replaces the unwanted remote init.

**Alternatives:**
1. Merge with unrelated histories: `git merge --allow-unrelated-histories origin/main` and resolve conflicts (founder-friendly but verbose; preserves the auto-init commit as ancestor — usually undesirable).
2. Recreate the remote: delete the GitHub repo, run `gh repo create <name> --source=. --private --push` to recreate without auto-init.

**Diagnostic context:** `git log --oneline -5` of local, `git log --oneline -5 origin/main`, common-ancestor check (`git merge-base local origin/main` returns nothing on parallel histories).

---

### §map-codebase-rejected

**When:** The `codebase-mapper` agent produced a draft `docs/onboarding/codebase-map.md` and the founder rejected it — invoked via `/map-codebase` directly, or via /onboard step 0's brownfield path.

**Recommendation:** Re-invoke `/map-codebase` — the agent re-runs the analysis from scratch.
**Rationale:** The map is founder-confirmed before it is trusted; a rejected draft means the agent's heuristics missed something the founder can see.

**Alternatives:**
1. Give the agent a correction hint on re-invocation (e.g. name the framework it missed) — narrows the re-analysis.
2. Hand-write `docs/onboarding/codebase-map.md` — escape hatch if the repo is unusual enough that the heuristics won't converge.

**Diagnostic context:** what the founder flagged as wrong, the agent's draft summary, repo size / stack signals.

---

### §cascade-environmental-drift

**When:** /update-linear's pre-write consistency check found the cascade's environment changed underneath it — parent label altered externally, a child archived mid-cascade, spec markdown deleted, or the `blockedBy` graph diverged from /plan's last-written state.

**Recommendation:** `/plan <MARKER>-N` — re-run the planning cascade to re-converge against current Linear state.
**Rationale:** The divergence is environmental, not a spec defect. Re-planning re-derives the wave structure; autonomous fixes already written to Linear during the prior cascade persist.

**Alternatives:**
1. If a child was archived by mistake, un-archive it in Linear first, then re-run /update-linear directly — avoids a full re-plan.
2. `/specify <MARKER>-N --unseal` — only if the divergence reflects a real scope change rather than an accidental edit.

**Diagnostic context:** parent ID + observed vs expected label, archived child IDs, spec markdown path, `blockedBy` diff against /plan's last-written graph.

---

### §adr-reversal

**When:** /review check g found the spec or its children reverse a decision recorded in a prior `Accepted` ADR.

**Recommendation:** Review the reversal. If the new direction is correct, file a superseding ADR; if not, `/specify <MARKER>-N --unseal` to remove the reversal from the spec.
**Rationale:** Even a mechanically obvious ADR reversal is a decision change — it deserves an explicit founder call, not an autonomous fix.

**Alternatives:**
1. File a superseding ADR documenting the reversal, then `/specify <MARKER>-N --continue` — if the reversal is intentional and the founder wants to keep the rest of the spec.

**Diagnostic context:** reversed ADR ID + title, the spec locus that reverses it, verbatim text of the original decision.

---

### §constitution-violation

**When:** /review check j found the spec, a child description, or a generated artifact contradicts a principle in `docs/constitution.md`.

**Recommendation:** `/specify <MARKER>-N --unseal` — bring the spec back in line with the constitution.
**Rationale:** A constitution violation is spec drift, not a decomposition error; /plan cannot iterate out of it.

**Alternatives:**
1. `/constitution amend <topic>` — if the violated principle is the thing that should change; amend the constitution first, then re-run the cascade.

**Diagnostic context:** the violated principle quoted verbatim, the spec / child locus that contradicts it, constitution version.

---

### §spec-incomplete

**When:** /review check k found incompleteness in the spec — `[NEEDS CLARIFICATION: ...]` markers, stub sections, empty AC text, or a TODO / placeholder failing-test seed.

**Recommendation:** `/specify <MARKER>-N --continue` — re-enter the Clarify phase and fill every incomplete locus.
**Rationale:** Incompleteness means the Clarify phase did not sweep; /plan cannot decompose around gaps.

**Alternatives:**
1. `/specify <MARKER>-N --unseal` — if the incompleteness is structural rather than a handful of unfilled fields.

**Diagnostic context:** bullet list of every incomplete locus (marker text, empty AC IDs, stub section headings).

---

### §review-iteration-cap

**When:** /review's stability rule (same `(type, locus)` across two consecutive review docs) or the iteration cap (`iteration_count >= 3`) pushed an iterate-type finding (checks a, c, d, f, i) to spec-halt.

**Recommendation:** `/specify <MARKER>-N --unseal` — iteration is not converging on this finding; the spec needs rework.
**Rationale:** An iterate-type finding that survives stability or the cap is a sign the decomposition cannot resolve it — the root cause is upstream in the spec.

**Alternatives:** none — re-specing is the only sanctioned recovery.

**Diagnostic context:** finding type + locus, the two review docs naming it, `iteration_count`.

---

### §wrap-tests-red

**When:** /wrap step 1 re-ran the child's failing-test seed and one or more tests are still red.

**Recommendation:** `/build <MARKER>-N-K --continue`
**Rationale:** /wrap will not commit or transition a child with red tests — the TDD gate is enforced at session close even though build-reviewer already passed the diff.

**Alternatives:**
1. `/build <MARKER>-N-K --reset --confirm` — if the red tests suggest the run took a wrong direction rather than stopping short.

**Diagnostic context:** failing test names, X/Y passing count, last commit SHA.

---

### §wrap-scope-breach

**When:** /wrap step 2 found the child's changed-file set includes files outside its expected scope.

**Recommendation:** Review the out-of-scope files, then `/build <MARKER>-N-K --continue` — Ralph re-runs with the scope boundary reinforced in `fix_plan.md`.
**Rationale:** A child for one concern that modified an unrelated surface has drifted; /wrap halts rather than commit cross-scope changes.

**Alternatives:**
1. `/build <MARKER>-N-K --reset --confirm` — if the drift is large enough that the run is best restarted.
2. If the out-of-scope changes are actually correct and necessary, `/specify <MARKER>-N --unseal` to widen the child's scope, then rebuild.

**Diagnostic context:** list of out-of-scope changed files, the child's expected surface, commit SHAs touching them.

## Voice rules

Per `rules/auditor-stance.md`, applied verbatim to halt-cards:

- **State findings as facts.** "Spec checksum mismatch at <path>." Not "The spec may have been edited."
- **No preamble.** Open with the halt reason. No "Unfortunately, the cascade encountered an issue."
- **No LGTM closures.** A halt-card is not a celebration. Skip "Hope this helps!" and similar.
- **One finding per `{type, locus}`.** Don't restate the same concern from multiple angles.
- **Mark uncertainty distinctly.** Prefix `uncertain:` when the recommendation is a hypothesis rather than observation, and state what would resolve the uncertainty. Example: "uncertain: drift may be caused by the failing-test seed itself — read `docs/specs/0007-login-form/spec.md`'s Failing-test seed section to confirm."
- **Terse, not curt.** Halt-cards are dense; the founder will read every word. No flourishes; also no contempt.

## Rendering examples

### Example 1 — /build hits drift

~~~
## Halt: /build BLOCKED

**Reason:** Drift detected — 3 consecutive iterations failing `npm test` with the same first-FAIL hash.

**Recommended next action:**
/specify AI-7 --unseal

A stable failing test means the spec is wrong, not the implementation. `--reset` won't help.

**Alternatives:**
1. Manually edit the failing-test seed in docs/specs/0007-login-form/spec.md, then /specify SOL-7 --continue — narrow fix if the seed is wrong but the spec is otherwise correct.

**Diagnostic context:**
- Drift hash: a3f1c08b9d2e
- Failing test: test_login_redirects_on_success
- Last 3 commits: 4f8a2c1, 9b3e1d7, c1f2a8b
- Cumulative cost: $42.18 across initial + 2 --continue runs
~~~

### Example 2 — /plan hits incomplete failing-test seed

~~~
## Halt: /plan BLOCKED

**Reason:** AC-3 ("user sees password-strength meter") is not covered by AI-7's failing-test seed.

**Recommended next action:**
/specify AI-7 --continue

Single AC gap — targeted re-spec is cheaper than full rebuild.

**Alternatives:**
1. /specify AI-7 --unseal — if multiple AC have seed gaps (systemic spec issue).
2. Remove AC-3 from the spec — if deferring the feature is the right call.

**Diagnostic context:**
- AC-3 text: "User sees password-strength meter as they type."
- Parent failing-test seed: test_login_form_renders, test_login_redirects_on_success, test_login_rejects_bad_password
- Decomposer finding: type=missing-edge-case severity=high locus=AC-3
~~~

### Example 3 — /verify hits ac-fail-with-fix-children

~~~
## Halt: /verify BLOCKED

**Reason:** 2 AC failed acceptance walkthrough; 2 fix-children minted.

**Recommended next action:**
/build AI-7-fix-1
/build AI-7-fix-2

Fix-children are scope-of-the-original-spec retries; the cascade resumes through them.

**Alternatives:**
1. /verify AI-7 — re-walk the failed AC after fix-children are built.

**Diagnostic context:**
- AC-2 FAIL: "Logout clears session." Diagnoser: severity=med locus=src/auth/session.ts:42
- AC-5 FAIL: "Error toast on bad password." Diagnoser: severity=low locus=src/components/LoginForm.tsx:88
- Fix-children: AI-7-fix-1 (covers AC-2), AI-7-fix-2 (covers AC-5)
~~~

### Example 4 — /wrap halts on red tests

~~~
## Halt: /wrap BLOCKED

**Reason:** AI-7-2's failing-test seed still has 2 red tests at session close.

**Recommended next action:**
/build AI-7-2 --continue

Ralph resumes from fix_plan.md to close the remaining red tests; /wrap will not commit a child with red tests.

**Alternatives:**
1. /build AI-7-2 --reset --confirm — if the red tests suggest the run took a wrong direction rather than stopping short.

**Diagnostic context:**
- Failing tests: test_session_expiry, test_logout_clears_token
- 6/8 passing
- Last commit: e2c91a4
~~~

## Notes for skill authors

- **Always render all five sections in order.** Skipping the diagnostic context turns the halt-card into a non-debuggable artifact.
- **Pick exactly one pattern per halt.** Composite halts (e.g. `iteration_cap` AND backpressure failure) pick the more actionable pattern and reference the other in Diagnostic context. Composite-pattern syntax is reserved for v1.1+.
- **Don't pre-format the founder's command line.** Recommendations and alternatives use the exact command strings the founder would type, with no surrounding shell syntax (no `$`, no `>`).
- **Diagnostic context is for state, not for the verbose dump.** If a backpressure log is 500 lines, surface the first FAIL line; the founder can `tail` the rest.
- **`uncertain:` is permitted in the rationale when the diagnosis is hypothetical.** State what would resolve the uncertainty.
- **Halt-cards surface to chat as the primary audience.** Skills that interact with Linear tickets (e.g. /build, /verify) also post a diagnostic comment on the ticket containing the halt-card body plus any extra state (`fix_plan.md` snapshot, etc.). The chat-rendered card is the canonical version; the ticket comment is a copy for ticket-context recovery.
- **Thin commands may word their halts inline.** `/start` and `/config` carry small, self-describing halt conditions (a bad label, an invalid config value) and word them inline rather than rendering a five-section card — they do not reference this template. Use a registry pattern when the halt has a non-obvious recommendation; use an inline message when the fix is self-evident from the error.

## Open questions (deferred to v1.1+)

- **Composite-pattern syntax.** When multiple patterns apply simultaneously, currently the skill picks one and references the others in Diagnostic context. A formal syntax (e.g. `§drift+§cost-cap`) is v1.1.
- **Auto-recommendation from agent severity.** Some agents could pre-recommend a pattern (e.g. decomposer surfacing scope-resistance always maps to `§undecomposable-parent` or `§drift` based on signal). Currently the invoking skill does the mapping; pushing it agent-side reduces drift but couples agent and template versions. v1.1 candidate.
- **Halt-log persistence.** Halt-cards render to chat and (for ticket-bound skills) to a Linear comment. A central `docs/halt-log/<date>.md` archive across all halt events is v1.1.
- **Localization.** v0.1 is English-only.
- **Pattern coverage for the cascade's remaining skills — RESOLVED in extraction chat 7 (Batch 3 growth).** The 5 Batch 3 revised skills landed their post-extraction bodies and the registry grew to cover them: /onboard (`§linear-unavailable`, `§onboard-setup`, `§map-codebase-rejected`; reuses `§missing-context` for missing template files), /update-linear (`§cascade-environmental-drift`; also reuses `§missing-context` / `§label-mismatch`), /review (`§adr-reversal`, `§constitution-violation`, `§spec-incomplete`, `§review-iteration-cap`; reuses `§incomplete-failing-test-seed` for check b), /wrap (`§wrap-tests-red`, `§wrap-scope-breach`). /retro is halt-free by design (best-effort compilation; only `DONE_WITH_CONCERNS` and `NEEDS_CONTEXT` exits, neither of which renders a halt-card) and owes no patterns. Command surfaces: /status and /next reach `§linear-unavailable`; /map-codebase reaches `§map-codebase-rejected`; /start and /config word their thin halts inline and do not render template halt-cards.
