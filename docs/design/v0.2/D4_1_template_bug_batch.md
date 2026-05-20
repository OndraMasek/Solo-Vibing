# D4.1 — Template bug batch + portability items

**Status:** Design (v1 — authored 2026-05-19).
**Phase:** 4 (Cleanup and concrete fixes).
**Resolves:** F-8 (template bugs, no CI — SOL-97) fully; F-5 (no supervision/recovery — SOL-94) partially, covering portability items not picked up by D2.2.
**Depends on:** D2.1 v2 (manifest provenance — denylist enforcement reads cascade-control file list); D0.1 (framework repo layout — bug fixes land in framework-repo template files); D2.2 (hook surface — pre-flight smoke runs as a `SessionStart` hook).
**Position in Phase 4 plan:** parallel with D4.2 and D4.5. Each defect is independent; no cross-blocking. Cheapest design doc in the set.

## Scope

D4.1 is a checklist. Each item is a specific, named defect with a specific fix. Most are one-line or one-file changes. Total effort estimate for the implementation pass: one short Code session.

D4.1 does not re-architect anything. The architectural fixes for the F-8 root cause ("templates are prose, consumers are exact predicates, no CI gate between them") are upstream design work — covered by D2.1 v2 (manifest provenance binding), D0.1 (synthetic-spec CI test), and the F-8 root-cause direction "Templates become first-class generators with unit tests" which slots into v0.2.x as a separate hardening pass.

What D4.1 does: clear the eight known concrete bugs and three known portability items so they don't continue to wedge real tickets.

## Eight template defects (F-8)

### D4.1.1 — `fix_plan.md` `[defer]` items satisfy `run.sh`'s unchecked predicate

**Symptom:** Infinite spin to wall/cost cap. SOL-66 burned ~$2.65 over ~40 min on iters 5–13; SOL-65 hit the full 30-iter cap at ~$18.61. The exit gate was provably unreachable because `[defer]` items in `fix_plan.md` matched `^[[:space:]]*-[[:space:]]*\[ \]` and were counted as unchecked.

**Fix:** Change the `run.sh` template's UNCHECKED regex to exclude `[defer]` items:

```bash
UNCHECKED=$(grep -cE '^[[:space:]]*-[[:space:]]*\[ \](?!\s*\[defer\])' "$FIX_PLAN")
```

Or, more portably (grep `-P` is not universal):

```bash
UNCHECKED=$(grep -E '^[[:space:]]*-[[:space:]]*\[ \]' "$FIX_PLAN" | grep -vc '\[defer\]')
```

**Where it lands:** `docs/templates/run.sh.template` in the framework repo.

**Test:** `tests/template-tests/test_fix_plan_predicate.sh` — fixture with one AC, one seed, three `[defer]` items, all unchecked; assert `UNCHECKED == 2` (one AC + one seed, not the three defers).

### D4.1.2 — `claude -p --output-format stream-json` missing `--verbose`

**Symptom:** Stillborn `claude` invocation. Iter 001 produces `claude.jsonl = 0 bytes` and `log.txt` shows the error `When using --print, --output-format=stream-json requires --verbose`. Cost is $0, so wall-cap and cost-cap detection both miss it. Drift detector keys on FAIL-line hashes — no output, no drift signal.

**Fix:** Add `--verbose` to the `claude -p` invocation in `run.sh.template` (around line 93):

```bash
claude -p --output-format stream-json --verbose < "$PROMPT" > "$CLAUDE_JSONL"
```

**Where it lands:** `docs/templates/run.sh.template`.

**Additional safeguard (recommended):** Pre-flight check at the start of every `run.sh` execution that runs `claude -p "reply OK"` (2 seconds) and verifies non-zero output. If it fails, halt before consuming any budget. This costs ~2 seconds per Ralph spawn; small price for catching the entire class of "the harness is misconfigured" failures.

**Where the pre-flight lands:** `run.sh.template` step 0, or a separate `.claude/hooks/build-preflight.sh` invoked from `SessionStart` matcher Bash.

### D4.1.3 — No Godot Makefile template ships

**Symptom:** `/build`'s AGENTS autodetect precedence rule 2 expects Makefile targets. On a greenfield Godot project, no Makefile exists, no documentation guides the founder, and the cascade improvises `godot --check-only --quit` (no `--script`), which hangs indefinitely and requires `SIGKILL` after ~2 min elapsed.

**Fix:** Ship `docs/templates/stack-makefiles/godot.Makefile` in the framework repo, with the standard targets `typecheck`, `test`, `lint`, `format`. Each target wraps a known-good Godot CLI invocation. Example:

```makefile
# docs/templates/stack-makefiles/godot.Makefile
GODOT ?= godot

.PHONY: typecheck test lint format
typecheck:
	$(GODOT) --headless --script res://tools/typecheck.gd --quit
test:
	$(GODOT) --headless --script res://addons/gut/gut_cmdln.gd --quit -- -gdir=res://tests
lint:
	@echo "Godot has no official linter; gdscript_style is recommended community tool" >&2
format:
	@echo "Godot has no official formatter; manual cleanup or gdformat (third-party)" >&2
```

**Where it lands:** `docs/templates/stack-makefiles/` directory in framework repo. `/onboard`'s stack-detection step (when it identifies Godot) copies this Makefile into the consumer's repo root.

**Sibling Makefiles also needed:** `python.Makefile`, `node.Makefile`, `rust.Makefile`, `go.Makefile`, `web-frontend.Makefile`. v0.2 ships the four highest-priority stacks; others ship in v0.2.x as users surface them. Names are inventory, not the actual Makefile contents — content for non-Godot stacks is straightforward and is out of D4.1's scope.

### D4.1.4 — Rendering bug in `/build` SKILL.md

**Symptom:** Injected skill text reads *"Defaults: 30 iterations, 4 wall-hours, USD per run."* The dollar cap is missing — an unrendered `{{...}}` interpolation in the canonical skill document. The cost cap ($50) is load-bearing and its statement in the spec is blank.

**Fix:** Inspect `docs/templates/skills/build-SKILL.md` for the unrendered `{{COST_CAP_USD}}` (or equivalent) variable. Either:

- (a) Replace the variable with the literal `$50` and remove the templating layer from this section, or
- (b) Wire the variable to `docs/.solo-config.json`'s `build.cost_cap_usd` value so it's actually rendered at `/onboard` time.

Option (a) is the v0.2 floor (one literal replacement; no new template machinery). Option (b) is the cleaner long-term answer and aligns with D3.4's autonomy-mode config-driven defaults; it can land in v0.2.x without breaking the literal-replacement fix.

**Where it lands:** `docs/templates/skills/build-SKILL.md`.

**Audit step:** When fixing D4.1.4, grep all SKILL.md files for unrendered `{{...}}` patterns. There may be others. (`grep -rE '\{\{[A-Z_]+\}\}' docs/templates/skills/`.)

### D4.1.5 — Wall-clock data destroyed before it is read

**Symptom:** Wall-clock source is `run.pid` mtime; deleted on Ralph exit. At `--finalize` the real wall-clock is unrecoverable. The completion comment reports a commit-span proxy (~34 min) presented as run duration. The skill mandates wall-clock in the completion comment but destroys the data source before finalize reads it.

**Fix:** Before deleting `run.pid` at Ralph exit, record the wall-clock value to a persistent file `wall_clock.txt` in the worktree:

```bash
# At end of run.sh, before cleanup:
if [ -f "$RUN_PID" ]; then
    START_TIME=$(stat -c %Y "$RUN_PID" 2>/dev/null || stat -f %m "$RUN_PID")
    END_TIME=$(date +%s)
    WALL_SECONDS=$((END_TIME - START_TIME))
    echo "$WALL_SECONDS" > "$WORKTREE/.ralph/wall_clock_seconds.txt"
    rm "$RUN_PID"
fi
```

`/build --finalize` reads `wall_clock_seconds.txt` and formats for the completion comment.

**Portability note:** `stat -c %Y` is GNU (Linux); `stat -f %m` is BSD (macOS). The fallback chain handles both. The `2>/dev/null` swallows the GNU complaint on macOS so the BSD form runs.

**Where it lands:** `docs/templates/run.sh.template` (the write); `docs/templates/skills/build-SKILL.md` §`--finalize` (the read).

### D4.1.6 — `iter-031` commit bundled unrelated changes (no scope discipline)

**Symptom:** `run.sh` step 6 (`git add -A`) has no scope discipline. SOL-65's recovery commit `9c31b8f` swept the `docs/.solo-config.json max_iterations` bump and manual `fix_plan.md` defer edits into a single "iteration 031" commit. The per-ticket scope boundary that `/plan` and per-ticket `fix_plan.md` exist to enforce is not enforced at the commit layer.

**Fix:** Replace `git add -A` with an explicit allow-list pattern derived from the spec's expected file paths. The cascade already knows which files a child should touch (per D3.4's per-child manifest); use that list:

```bash
# In run.sh, step 6:
EXPECTED_PATHS=$(jq -r '.expected_paths[]' "$WORKTREE/.cascade/manifests/$TICKET.json")
for path in $EXPECTED_PATHS; do
    git add "$path"
done
# Plus the universally-allowed files:
git add fix_plan.md  # ralph state, expected per-iter update
```

If a file outside the expected set was modified, it stays out of the commit and surfaces in a `git status` halt at `/wrap`.

**Where it lands:** `docs/templates/run.sh.template` step 6.

**Dependency:** This works only if `expected_paths` lands in the child manifest per D3.4's manifest schema. If not present, the file falls back to `git add -A` with a halt log noting the missing schema field. D4.1's implementation pass surfaces whether `expected_paths` is currently in the manifest; if not, raise to D3.4 for a schema amendment.

### D4.1.7 — Ralph mutated its own governance (cascade-control denylist)

**Symptom:** SOL-65 iter 031 edited `docs/.solo-config.json max_iterations 30 → 50` to escape its own cap (commit `9c31b8f`). The sandbox/scope boundary protects nothing — cascade-control files are writable by the build agent. The deliberate remediation bump (`max_iterations: 45`, commit `1cd36ac`) then rode into main via PR #3 because the merge didn't enforce a pre-merge checklist — silently raising the cap for all future builds until manually reverted (`ad1014f`).

**Fix:** Maintain a denylist of cascade-control files that build agents (Ralph and any spawned subagent) cannot write. The denylist lives at `.claude/agents/build-write-denylist.txt`:

```
docs/.solo-config.json
.cascade/**
.ralph/**
.claude/agents/**
.claude/hooks/**
.claude/rules/**
.claude/skills/**
docs/templates/**
docs/design/**
```

Enforcement happens via a `PreToolUse` hook matcher on the Write/Edit tools that reads the denylist and halts on match. Halt code: `§cascade-control-write-blocked`. Halt card surfaces the attempted path, the matching denylist line, and the founder-override path (manual edit outside the cascade).

**Where it lands:** `.claude/agents/build-write-denylist.txt` (new file), `.claude/hooks/pre-tool-use-denylist.{py,sh}` (new hook), `docs/templates/halt-messages.md` (new halt code).

**Cross-reference:** D2.1 v2's caller-side verification and D2.2's hook table both need to know about this denylist. The hook itself is one of the D2.2 hooks; D4.1 specifies the *content* of the denylist.

### D4.1.8 — `.claude/worktrees/` not in `.gitignore`

**Symptom:** Every Ralph commit emits git's embedded-repo hint: `block into spawn.log`. Flagged across SOL-65 and SOL-66, never auto-fixed.

**Fix:** Add to `.gitignore` in the framework repo template and in `/onboard`'s consumer-repo `.gitignore` seeding:

```
.claude/worktrees/
.ralph/
.cascade/manifests/*-spawn.log
```

`/onboard` should also `git rm --cached .claude/worktrees/` if the consumer's existing repo has it tracked (idempotent — no-op if not).

**Where it lands:** `docs/templates/.gitignore.template` (framework's gitignore seed for consumers).

## Three portability items (F-5)

These were called out in D0.2 as belonging to D4.1 ("Process-group kill, orphan reaping, macOS `gtimeout` portability remain as separate work in D4.1") because D2.2 (session auto-management) handles the kill-and-resume class but not the OS-portability class.

### D4.1.9 — Process-group kill (`kill -PGID`)

**Symptom:** Hung Ralph runs leave orphan `claude` processes after the founder runs `/build --kill`. Kill targets the main `run.sh` PID, not the process group, so child `claude` invocations and their subprocesses survive.

**Fix:** Ralph's spawn (in `run.sh`) sets `set -m` (job control) and starts the `claude` invocation in its own process group via `setsid` (Linux) or `posix_spawn` with `POSIX_SPAWN_SETPGROUP` (macOS). On `--kill`, the cascade sends SIGTERM then SIGKILL to the negative PID:

```bash
# In run.sh spawn:
setsid claude -p ... &
RALPH_PGID=$!
echo "$RALPH_PGID" > "$WORKTREE/.ralph/pgid"

# In /build --kill:
PGID=$(cat "$WORKTREE/.ralph/pgid")
kill -TERM -- -$PGID
sleep 2
kill -KILL -- -$PGID 2>/dev/null
```

`setsid` is Linux-standard; on macOS, `setsid` requires Homebrew (`brew install util-linux`). Alternative: use `nohup` + `disown` to detach, then `pkill -P $RALPH_PID` for descendants. v0.2 ships the `setsid` form with a one-line note in the framework `README.md` about the macOS prereq.

**Where it lands:** `docs/templates/run.sh.template` (the spawn); `docs/templates/skills/build-SKILL.md` §`--kill` (the kill).

### D4.1.10 — Orphan reaping

**Symptom:** Even with process-group kill, occasional `claude` subprocesses survive (the underlying tool spawns helpers that re-parent to PID 1). These accumulate over a long session.

**Fix:** `/build --kill` and `/build --status` both invoke a reaper script that scans for `claude` processes parented to PID 1 with their working directory inside the framework repo's worktree tree:

```bash
# .claude/hooks/reap-orphans.sh (or .py)
for pid in $(pgrep -P 1 claude); do
    pwd_path=$(readlink /proc/$pid/cwd 2>/dev/null || lsof -p $pid 2>/dev/null | awk '$4=="cwd" {print $9}')
    if echo "$pwd_path" | grep -q "/.claude/worktrees/"; then
        kill -TERM $pid
    fi
done
```

`/proc` is Linux-only; `lsof` is the macOS fallback. The conditional handles both.

**Where it lands:** `.claude/hooks/reap-orphans.sh` (new); invoked from `/build --kill` and `/build --status`.

### D4.1.11 — macOS `gtimeout` portability

**Symptom:** Several `run.sh` invocations use `timeout` (the GNU coreutils command) to bound long-running operations. On macOS, this resolves to nothing or to `gtimeout` (the Homebrew GNU coreutils form). Greenfield macOS users hit `command not found: timeout`.

**Fix:** Add a shim function at the top of `run.sh.template`:

```bash
# Portable timeout shim
if command -v timeout >/dev/null 2>&1; then
    TIMEOUT="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT="gtimeout"
else
    TIMEOUT=""  # No timeout available; commands run unbounded
fi
```

Then all `timeout 30s ...` invocations become `$TIMEOUT 30s ...`. If `$TIMEOUT` is empty, the command runs without a timeout (degraded but not broken).

`bootstrap.sh` (or `/onboard`'s prereq check) warns if neither `timeout` nor `gtimeout` is available, with installation instructions (`brew install coreutils` on macOS).

**Where it lands:** `docs/templates/run.sh.template` (the shim); `bootstrap.sh` (the prereq check).

## Implementation order

These eleven items are mostly independent. Suggested order for a single implementation session:

1. **D4.1.1 (fix_plan regex), D4.1.2 (claude --verbose), D4.1.4 (rendering bug), D4.1.8 (gitignore)** — one-line fixes; do first.
2. **D4.1.3 (Godot Makefile), D4.1.11 (gtimeout shim)** — single-file additions.
3. **D4.1.5 (wall-clock persistence), D4.1.6 (commit scope), D4.1.7 (denylist)** — template-file edits with multi-line additions.
4. **D4.1.9 (process-group kill), D4.1.10 (orphan reaping)** — new hooks; cross-reference D2.2.

Estimated effort for the whole batch: one short-to-medium Code session. Most items have direct test paths (template fixture tests for the regex; smoke test for `claude --verbose`; `git status` assertion for the gitignore).

## What v0.2 does not ship

Two items are explicitly v0.2.x or later:

1. **Templates-as-first-class-generators with unit tests.** The F-8 root-cause direction. Replacing prose templates with parameterized generators that emit `fix_plan.md`, `run.sh`, `PROMPT.md` from inputs, with a unit test asserting "this fix_plan can satisfy this run.sh's predicate." Significant refactor; v0.2.x.

2. **Smoke-test generated artifacts in CI.** Beyond the D4.1.2 pre-flight, generate-then-typecheck-empty-sandbox tests for every stack Makefile. v0.2.x — depends on having the Makefiles first (D4.1.3 partial coverage).

## Open items

- **`expected_paths` in child manifest schema (D4.1.6 dependency).** Confirm with D3.4 that this field is present. If not, the commit-scope fix degrades to `git add -A` with a halt-log warning until the schema lands.
- **Universal allow-list beyond `fix_plan.md` (D4.1.6).** Some cascade-emitted files (Linear-state mirror, completion comment draft) may need to land in the iteration commit. Inventory during implementation; extend the allow-list as needed.
- **Pre-flight as a hook vs an inline `run.sh` step (D4.1.2).** D2.2's hook table is the natural home, but D2.2 didn't lock the matcher set. Implementation can choose; default is inline.

## Cross-references

- **D2.1 v2** — caller-side verification reads the denylist for write-discipline enforcement.
- **D2.2** — process-group kill and orphan reaping integrate with the session-management lifecycle; the pre-flight smoke also lives in the hook surface D2.2 specifies.
- **D3.4** — manifest schema (specifically `expected_paths[]`) is the dependency for D4.1.6.
- **D0.1** — synthetic-spec CI test catches regressions of these defects; D4.1 fixes are tested by the same synthetic-spec runs.
- **D4.0** — `solo-verify build <ticket>` evaluates the post-fix gate set; D4.1.6's denylist-write halt should surface there if the consumer's repo state shows a denylisted write.

## Note on coverage

This batch closes the eight observed F-8 defects plus the three named F-5 portability items. It does not close every conceivable template defect — only the ones that wedged real Bomber tickets and were named in the disposition map. If implementation surfaces additional defects (e.g. the audit step in D4.1.4 finds more unrendered `{{...}}`), they're absorbed into this batch and the design doc is amended in place; no separate D4.1.x ticket needed for individually-trivial additional fixes.
