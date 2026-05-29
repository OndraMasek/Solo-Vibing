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


---

<!-- BEGIN v0.2 Phase 3 halt cards (Child 0001-A halt-messages-append.md) -->

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

<!-- END v0.2 Phase 3 halt cards -->

<!-- BEGIN v0.2 Child 0001-C halt cards (halt-messages-append-childC.md) -->

## §compact-deferred-unsafe

**When fired.** PreCompact detected mid-cascade activity — one or more entries
in `cascade:run-state.active_stages[]` with unsealed manifests. The auto-compact
is blocked; the cascade continues; the next safe-boundary check will retry.

**Diagnostic context.** The list of active stages, the trigger (`manual` or
`auto`), the current `compact_cycles` count.

**Recovery.** None required — the deferral is intentional. The compact will
fire automatically when the cascade reaches the next safe boundary (typically
within minutes, at most one Ralph iteration). If the cascade runs out of context
before reaching a safe boundary, a manual `/compact` at a safe boundary will
succeed.

If deferrals stack and `compact_cycles` rises to 2 without ever reaching a safe
boundary, the cascade transitions to `§session-reset-required` per D2.2 §Compact
mechanics's max-2-cycles rule. The transition is intentional; context signal
has degraded enough that re-verifying against filesystem evidence is cheaper
than continuing.

## §kill-received-remote

**When fired.** A sidecar `/build-kill <ticket>` invocation has set
`cascade:run-state.kill_in_progress = "<ticket>"` AND incremented `queue_version`.
The Group F chat (Claude Code) was running Ralph for the same ticket when the
Stop-hook orchestrator read the flag at the next safe boundary.

**Diagnostic context.** The active ticket, the kill timestamp (from
`cascade:run-state.kill_initiated_at`), the originating chat surface
(`cascade:run-state.kill_initiated_from`, typically `"sidecar"` or `"chat-Claude"`).

**Recovery.** None required for the cascade — the kill was intentional. The
orchestrator clears `cascade:run-state.kill_in_progress`, removes the ticket
from `active_stages[]`, and the founder picks up either by:

  - Opening a new chat for the next queued ticket (the `queue_version` increment
    means the killed ticket is no longer in the queue).
  - Running `/cascade-halt` to halt the cascade entirely (sets `manual_halt`).
  - Running `/build <ticket> --resume` if the kill was a mistake (re-queues
    the ticket; `queue_version` increments again).

The Stop hook itself takes no recovery action beyond clearing `kill_in_progress`
and surfacing this card. The cascade's continuation is the founder's next
deliberate input.

## §manual-halt-pending

**When fired.** A `/cascade-halt` invocation (founder-initiated; not
`/build-kill`) has set `cascade:run-state.manual_halt = "<ticket-or-marker>"`.
The Stop-hook orchestrator read the flag at the next safe boundary.

**Diagnostic context.** The active ticket or marker, the halt timestamp (from
`cascade:run-state.manual_halt_at`), the halt reason if the founder supplied
one via `/cascade-halt --reason="<text>"` (`cascade:run-state.manual_halt_reason`).

**Recovery.** The halt is intentional. To resume the cascade:

  - Run `/cascade-resume` (or `solo-cascade resume` per D4.6 v1.1) to re-derive
    the chat-end card and continue.
  - Clear the flag manually via direct edit to `.cascade/run-state.json` if
    the halt should be retired without resumption (advanced; rarely needed).

The Stop hook itself takes no recovery action beyond surfacing this card and
preserving the `manual_halt` flag. The flag persists until the founder runs
`/cascade-resume` or clears it manually; the next chat opened detects it
during paste-verification (per D2.3 v1.3 §Handoff verification predicate)
and re-surfaces this card.

**Interaction with `kill_in_progress`.** The two flags are mutually exclusive
by convention; `/cascade-halt` errors out if `kill_in_progress` is non-null
(founder must `/build-kill` first or wait for the kill to complete). v0.2 ships
two-step; v0.2.x may chain per F-Usr-2's queued amendment.

### Sub-case: `/shape-tampering`

**When fired.** A `Write` or `Edit` tool call attempted to mutate the spec's
`Strategy:` field or `Failing-test seed` tag set in a way that violates the
sealed parent manifest's `pyramid_shape`. The PreToolUse `pyramid-tampering.sh`
hook detected the mismatch and denied the tool call.

**Diagnostic context.** The file path of the spec under write, the parent
manifest path, the proposed strategy vs sealed strategy, the violating tag
set (`forbidden tag <X> present`, `required tag <Y> missing`, or
`tag <Z> not in required/optional set`).

**Recovery.** Two paths depending on intent:

  - **Re-tag the seed entries to match the sealed shape.** If the tampering was
    unintentional (e.g., the model proposed a `[contract]` test for a
    walking-skeleton strategy where `contract` is forbidden), re-tag the
    failing-test seed entries to use tags from the sealed `required` or
    `optional` sets.
  - **Unseal and re-seal under a new strategy.** If the strategy itself needs
    to change (e.g., the work has shifted from walking-skeleton to
    capability-cluster), run `/specify <MARKER>-N --unseal` to re-run the
    four-hat panel under the new strategy. The pyramid_shape will regenerate
    from the strategy → shape catalog in D3.2.

The hook is a pre-flight defense; the at-write gate inside `/specify` (Gate 1
per D3.2 §Downstream consumer touch-points) is the authoritative shape-check.
If the hook missed (e.g., MultiEdit conservatively allowed), the at-write gate
catches the violation at seal time.

<!-- END v0.2 Child 0001-C halt cards -->

<!-- BEGIN v0.2 Child 0001-D halt cards (solo-verify novel codes) -->

## §evaluator-internal-error

**When fired.** `solo-verify` (or an in-skill predicate evaluator) crashed with an unexpected exception while evaluating a gate. The crash is in the evaluator, not in the cascade artifact — the cascade may be valid; the evaluator's confidence is unknown.

**Diagnostic context.** The stage and gate that was being evaluated, the exception class and message (one line), the path to a stderr capture (if the runner persists one). solo-verify exits 4.

**Recovery.** Re-run the same `solo-verify <stage> --gate <name>` invocation. If it crashes deterministically, the evaluator has a bug — file a v0.2.x issue with the manifest fixture that triggers it. If it succeeds, the prior crash was transient (filesystem flake, partial write); the gate result is now trustworthy.

**Alternatives.** Skip the gate via `solo-verify --force-pass <stage>.<gate>` is **not** supported — there is no waiver button (per `D2_1_revision_decisions.md` decision 5). The only path forward is a clean re-run or an evaluator bug-fix.

## §cascade-fs-inconsistent

**When fired.** `solo-verify` could not evaluate a gate because the on-disk cascade state is inconsistent with what the gate's predicate expects: missing manifest a chain walk requires, malformed JSON in a manifest, sha256 in `cascade:run-state.json` pointing at a file that doesn't exist. The artifact is not necessarily broken; the *bookkeeping* is.

**Diagnostic context.** The inconsistency type (manifest-absent / manifest-malformed / sha-stale / cascade-dir-missing), the path that was expected, the path that was found (if different). solo-verify exits 4.

**Recovery.** Manual: read `cascade:run-state.json` and walk the chain by hand until you find the break. If the break is at the leaf (the last sealed stage's manifest is missing or malformed), `--reconcile` against that stage. If the break is deeper, `--rerun=<stage>` against the deepest still-intact stage's downstream. Both paths are documented per D4.5 / D4.6 v1.1 §Halt conditions.

**Alternatives.** None — inconsistent state must be repaired before evaluation can proceed. The evaluator's refusal here is load-bearing: silently passing a gate whose evidence the evaluator can't read would propagate the inconsistency.

<!-- END v0.2 Child 0001-D halt cards -->

<!-- BEGIN SOL-121 audit-gap halt cards (23 referenced-but-undefined codes; 2026-05-29 audit) -->

### §ac-list-drift

**When:** `solo-verify`'s AC-list chain check found the spec's current AC-list `sha256` differs from the value sealed in the upstream manifest's `ac_list_sha256`, or the spec file the chain references is absent.

**Recommendation:** `/specify <MARKER>-N --unseal` to re-seal against the current AC list, then re-fire the cascade from the unseal point.
**Rationale:** Every downstream stage chains against the sealed AC list; a changed list means work proceeds against an unreviewed spec.

**Alternatives:**
1. `git checkout <sealed-commit> -- docs/specs/NNNN-<slug>/spec.md` — restore the sealed text if the AC edit was accidental; preserves the chain.
2. Restore the spec from VCS if it was deleted — the chain cannot verify against an absent file.

**Diagnostic context:** spec path; sealed sha256 vs current sha256; ticket. solo-verify exits 2 (provenance).

---

### §four-hat-seal-broken

**When:** At `/build` pre-flight, the spec's current AC-list sha differs from `/review`'s `four_hat_seal_sha256` — the four-hat seal no longer covers the spec being built.

**Recommendation:** `/specify <MARKER>-N --unseal`, then re-run `/review` and `/plan`.
**Rationale:** Building against a spec whose AC list drifted past the four-hat seal builds unreviewed scope.

**Alternatives:**
1. Restore the spec to the four-hat-sealed version from VCS — preserves the seal if the edit was accidental.

**Diagnostic context:** spec path; `four_hat_seal_sha256` vs current AC sha; ticket. solo-verify exits 2 (provenance).

---

### §onboard-linear-init-failed

**When:** The `onboard.linear-projects` gate found no `/onboard` manifest, fewer than the six required Linear projects (Product / Architecture / Design / Milestones / Backlog / Done), or a missing Status doc.

**Recommendation:** `/onboard <product>` to bootstrap the Linear projects.
**Rationale:** The cascade's Linear product layer (D1) is a precondition for every downstream stage that mirrors to Linear.

**Alternatives:**
1. Verify the Linear API key has create-project permission and the team has space for six projects, then re-run `/onboard`.

**Diagnostic context:** projects-created count vs required six; `status_doc_id` presence; ticket.

---

### §onboard-config-write-failed

**When:** The `onboard.config-write` gate found `docs/.solo-config.json` absent, non-parsing, missing `marker`, missing the `workflow.default_strategy` slot (or carrying a value outside the strategy enum), or missing the `invariance` top-level key.

**Recommendation:** `/onboard <product>` to (re)write the config, or hand-edit `docs/.solo-config.json` to add the missing field.
**Rationale:** Skills read marker, strategy default, and invariance config from this file; a malformed config halts the cascade at the first stage that reads it.

**Alternatives:**
1. Hand-add the single missing field (e.g. `"invariance": {"pass_set_capture_command": ""}`) if only one predicate failed — faster than a full re-onboard.

**Diagnostic context:** config path; failing predicate (absent / unparseable / missing-marker / missing-default_strategy / invalid-strategy-value / missing-invariance); offending value verbatim; ticket.

---

### §four-hat-incomplete

**When:** The `review.four-hat-objection-coverage` gate found no `/review` manifest, a missing per-hat manifest (user / engineer / pm / skeptic), or a manifest lacking `unresolved_count`.

**Recommendation:** `/review <MARKER>-N` (or `/review --continue` to re-dispatch a missing hat).
**Rationale:** The four-hat panel is the spec's adversarial review; an incomplete panel means the spec was not fully challenged before build.

**Alternatives:**
1. `/review --continue` to re-dispatch only the absent hat — cheaper than a full re-review.

**Diagnostic context:** ticket; missing hat name (sub-case `transcript-absent`) or missing field (sub-case `objections-section-missing`).

---

### §four-hat-objections-unresolved

**When:** The `/review` manifest reports `unresolved_count > 0` — four-hat objections remain without Incorporate / Defer / Reject resolutions.

**Recommendation:** Address each unresolved objection in the four-hat doc, then `/review --continue`.
**Rationale:** `/build` and `/plan` require all findings resolved; sealing with open objections buries known disagreements.

**Alternatives:**
1. `/specify <MARKER>-N --unseal` — if the unresolved objections indicate fundamental rework rather than line edits.

**Diagnostic context:** `unresolved_count`; ticket; four-hat doc slug.

---

### §four-hat-ac-list-drift

**When:** The `review.ac-list-seal` gate found the spec's current AC-list sha differs from the `/review` manifest's `seal_sha256`, or the spec file is absent.

**Recommendation:** `/specify <MARKER>-N --unseal`, then re-run `/review`.
**Rationale:** The review seal certifies a specific AC list; drift past it invalidates the review.

**Alternatives:**
1. Restore the spec to the review-sealed version from VCS — preserves the seal if the edit was accidental.

**Diagnostic context:** spec path; sealed sha vs current sha; ticket. solo-verify exits 2 (provenance).

---

### §plan-decomposition-invalid

**When:** The `plan.decomposition-shape` gate found no `/plan` manifest, or a manifest naming zero children.

**Recommendation:** `/plan <MARKER>-N`; the decomposer must emit at least one child.
**Rationale:** A decomposition with no children is not a plan; downstream `/build` has nothing to fire against.

**Alternatives:**
1. `/specify <MARKER>-N --unseal` — if the parent is genuinely a single indivisible unit of work (rare; usually a re-plan suffices).

**Diagnostic context:** ticket; child count; parent strategy.

---

### §linear-state-inconsistent

**When:** The `update-linear.diff-applied` gate found no `/update-linear` manifest, or a manifest lacking `diff_sha256` or `tickets_updated[]`.

**Recommendation:** `/update-linear <MARKER>-N`.
**Rationale:** Without a recorded diff and ticket-update set, the cascade cannot confirm Linear reflects the planned state.

**Alternatives:** None — re-running `/update-linear` is the sanctioned path; the Linear-side reconciliation lives in the skill.

**Diagnostic context:** ticket; missing field (`diff_sha256` / `tickets_updated`).

---

### §pyramid-tampering-detected

**When:** The `build.pyramid-tampering` gate found the spec markdown's `**Pyramid shape:**` declaration names a different strategy than the sealed manifest's `pyramid_shape.strategy`.

**Recommendation:** Restore the spec markdown to the sealed shape, or `/specify <MARKER>-N --unseal`.
**Rationale:** The pyramid shape is sealed at `/specify`; a post-seal change to the strategy declaration mutates the test-coverage contract `/build` runs against.

**Alternatives:**
1. Restore only the `**Pyramid shape:**` line if the strategy change was unintentional — preserves the seal.
2. `/specify <MARKER>-N --unseal` if the strategy genuinely changed — regenerates `pyramid_shape` from the D3.2 catalog.

**Diagnostic context:** claimed strategy vs sealed strategy; spec path; ticket.

---

### §build-test-drift

**When:** The `build.test-execution` gate found the latest backpressure entry reports `first_fail_hash_changed`, or the backpressure log is unreadable.

**Recommendation:** Investigate the diverging test failure, then `/build <MARKER>-N-K --continue`.
**Rationale:** The failing-test seed is the build invariant; a changed first-FAIL hash means the test or implementation drifted off the seed contract.

**Alternatives:**
1. Inspect `.ralph/<MARKER>-N-K/backpressure.jsonl` directly if the log is merely unreadable rather than corrupt.

**Diagnostic context:** last backpressure entry; ticket; backpressure log path.

---

### §build-finalize-incomplete

**When:** The `build.finalize` gate found no backpressure log, `fix_plan_unchecked_count != 0`, one or more seed tests not `passing`, a missing `commit_sha`, or a commit SHA absent from git's object store.

**Recommendation:** `/build <MARKER>-N-K --continue` until every fix-plan item is checked, all seed tests pass, and the work is committed.
**Rationale:** Finalize is the build's completion contract; an unmet predicate means the child is not built.

**Alternatives:**
1. Verify the build commit was not rebased away if `commit_sha` is recorded but absent from the object store.

**Diagnostic context:** failing predicate (no-log / unchecked-fix-plan / seed-not-passing / no-commit / commit-missing); unchecked count or not-passing sample; commit sha; ticket.

---

### §product-doc-mirror-drift

**When:** The `wrap.mirror-sha-match` gate found the filesystem `docs/product/*.md` sha differs from the Linear doc sha.

**Recommendation:** Re-run `/wrap <MARKER>-N-K` to re-mirror docs from filesystem to Linear.
**Rationale:** The filesystem is canonical for product docs; a sha mismatch means Linear is stale.

**Alternatives:** None — re-mirroring via `/wrap` is the sanctioned reconciliation.

**Diagnostic context:** fs sha vs Linear sha; ticket.

---

### §wrap-label-transition-failed

**When:** The `wrap.linear-state-updated` gate found `linear_label_transition != "scope:built"` or the ticket was not moved to the Done project. Emitted from two call sites in `solo-verify` (the per-predicate halt and the gate-spec dispatch).

**Recommendation:** Re-run `/wrap <MARKER>-N-K`; investigate Linear API failures.
**Rationale:** `scope:built` plus Done placement is the child's terminal Linear state; a failed transition leaves the cascade's Linear view inconsistent with completed work and blocks `/verify`'s child-completion check.

**Alternatives:**
1. Edit the ticket label and project in Linear directly if the API write failed transiently — then re-run `/wrap` to re-seal the manifest.

**Diagnostic context:** actual label vs expected `scope:built`; `done_project_id` presence; ticket.

---

### §verify-child-not-built

**When:** The `verify.child-completion` gate found a child with no `/wrap` manifest, or a child not labeled `scope:built`.

**Recommendation:** Complete `/build` then `/wrap` for the named child, then re-run `/verify <milestone>`.
**Rationale:** Milestone verification aggregates per-child evidence; an unbuilt child has no evidence to aggregate.

**Alternatives:** None — every child of the milestone must complete `/wrap` before `/verify` can evaluate.

**Diagnostic context:** child ticket; milestone; actual label (if present).

---

### §hybrid-nesting-too-deep

**When:** `/verify`'s per-child dispatch encountered a hybrid child at recursion depth ≥ 1 — v0.2 caps hybrid nesting at one level per D3.4 §`/verify` dispatch.

**Recommendation:** Flatten the nesting so no hybrid child contains another hybrid child; or defer the deeper split to v0.2.x.
**Rationale:** Deeper-than-one hybrid recursion has no defined gate-composition path in v0.2; the cap is a deliberate scope boundary.

**Alternatives:**
1. Re-`/specify` the offending child under a concrete (non-hybrid) strategy if its work fits one.

**Diagnostic context:** child ticket; recursion depth; milestone.

---

### §retro-doc-unsealed

**When:** The `retro.doc-sealed` gate found no `/retro` manifest, or a manifest lacking `lessons_summary_line`.

**Recommendation:** `/retro <milestone>` (idempotent — re-running renders the same content if the input `/verify` manifest is unchanged).
**Rationale:** The retro doc and its Status-doc lessons line are the milestone's durable record; an unsealed retro leaves the cascade's terminal stage incomplete.

**Alternatives:** None — `/retro` is the sole producer of the retro doc.

**Diagnostic context:** milestone; missing artifact (manifest / `lessons_summary_line`).

---

### §child-seed-not-subset

**When:** The `plan.child-inheritance` gate determined a child's `failing_test_seed[]` is not a strict subset of the parent's seed. The deep subset check fires inside the `/plan` skill at write time; the gate reserves this code.

**Recommendation:** `/plan <MARKER>-N --rerun=decompose`; fix the offending child's seed so it draws only from the parent's seed.
**Rationale:** A child seed that introduces tests absent from the parent's seed builds scope the parent spec never sealed.

**Alternatives:**
1. `/specify <MARKER>-N --unseal` if the parent seed itself is missing a test the child legitimately needs — add it at the parent, then re-decompose.

**Diagnostic context:** child ticket; offending seed entries (present in child, absent from parent); parent ticket.

---

### §child-shape-inheritance-broken

**When:** The `plan.child-inheritance` gate determined a child's `pyramid_shape` was neither inherited from the parent nor overridden cleanly per D3.2, or its `artifact_path` / `artifact_type` / invariance fields did not propagate per D3.3. The deep check fires inside the `/plan` skill at write time; the gate reserves this code.

**Recommendation:** `/plan <MARKER>-N --rerun=decompose`; fix the child's shape and artifact fields.
**Rationale:** Per-child gate composition depends on a well-formed inherited or overridden shape; a broken inheritance leaves the child unverifiable at `/verify`.

**Alternatives:** None — re-decompose is the sanctioned repair.

**Diagnostic context:** child ticket; broken field (`pyramid_shape` / `artifact_path` / `artifact_type` / `invariance_artifact`); parent ticket.

---

### §wrap-lock-imbalance

**When:** The `wrap.mirror-sha-match` gate's predicate set found per-resource lock acquisitions did not match releases for the `/wrap` run (per D2.1 v2 /wrap row). Lock-balance accounting fires inside the `/wrap` skill; the gate reserves this code.

**Recommendation:** Re-run `/wrap <MARKER>-N-K`; inspect `.solo-locks/` for a stale lock left by an interrupted run.
**Rationale:** An unbalanced lock means a resource the wrap acquired was never released — concurrent same-product stages can deadlock against it.

**Alternatives:**
1. Remove the stale lock file under `.solo-locks/` manually if no live process holds it, then re-run `/wrap`.

**Diagnostic context:** ticket; acquired-vs-released lock counts; offending resource path under `.solo-locks/`.

---

### §cascade-control-write-blocked

**When:** A `Write` / `Edit` / `MultiEdit` tool call targeted a path matching a pattern in `.claude/agents/build-write-denylist.txt`. The `pretool-write-denylist.sh` PreToolUse hook denied the call (per D4.1.7 / spec AC-21).

**Recommendation:** Edit the file manually outside the cascade, or invoke the skill that has authority to write it.
**Rationale:** Cascade-control files (config, rules, halt-messages, `.cascade/*`, `.solo-locks/*`) are load-bearing; a build agent must not grow its own write surface. The denylist is itself denylisted.

**Alternatives:**
1. If a skill legitimately needs to write the path, route the change through that skill rather than the build agent.

**Diagnostic context:** attempted relative path; matched denylist pattern; denylist file path (`.claude/agents/build-write-denylist.txt`).

---

### §cascade-state-terminal

**When:** `solo-cascade resume` (D4.6 v1.1) was invoked after the cascade reached its terminal stage (Group H / `/retro`); there is no next group beyond H. Surfaced from `.claude/skills/retro/SKILL.md`'s Group H exit.

**Recommendation:** Open a new spec via `/specify` in a new chat to begin the next feature.
**Rationale:** The cascade terminates at `/retro`; resume has nothing to re-derive past the terminal manifest.

**Alternatives:** None — the terminal is intentional; the next action is a new feature, not a resume.

**Diagnostic context:** milestone; `last_completed_group = "H"`; terminal retro manifest path (`.cascade/manifests/<milestone>-retro.json`).

---

### §verify-strategy-unrecognized

**When:** `/verify`'s per-child dispatch encountered a child whose strategy is outside the canonical enum `{walking-skeleton, api-boundary, capability-cluster, refactor-spike, hybrid}`. A defensive halt — upstream `/specify`'s `spec.strategy-annotation` gate should have caught it.

**Recommendation:** `/specify <child-ticket> --unseal`, set a strategy from the canonical enum, re-seal, then re-run `/verify <milestone>`.
**Rationale:** Gate dispatch selects predicates by strategy; an unrecognized strategy has no dispatch path.

**Alternatives:**
1. uncertain: if the strategy value looks corrupted rather than wrong, inspect the child's `/specify` manifest for a write error before re-specifying — `solo-verify <child> --gate spec.strategy-annotation` confirms.

**Diagnostic context:** child ticket; offending strategy value verbatim; milestone.

<!-- END SOL-121 audit-gap halt cards -->
