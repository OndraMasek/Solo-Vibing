# `.claude/hooks/pyramid-tampering.sh` — pre-flight pyramid-shape guard

**Status:** Patch-ready new file. Authored in the Solo Claude Stack Claude.ai project; consumed by an executing Claude Code session against `OndraMasek/Solo-Vibing`.

**Scope:** wraps the D3.2 §Downstream consumer touch-points pyramid-tampering predicate as a `PreToolUse` hook. Fires when the model attempts to Write or Edit a spec file under `docs/specs/*/spec.md`. Reads the sealed parent manifest's `pyramid_shape` and `failing_test_seed[]` tag set; compares against the proposed write content's tag set; halts the tool call on mismatch.

This is the `build.pyramid-tampering` gate from Child 0001-B continuation 1's `/build` amendment, realized as a hook. It also guards `/specify` re-seal cases (a `/specify --continue` that tries to mutate the seed tags after a parent seal).

**v0.1 reconciliation:** none. v0.1 has no `.claude/hooks/` per `repo-state-summary.md` Part 2.

---

## Output shape

PreToolUse uses the standard `hookSpecificOutput` wrapper per D2.2 §Hook events table. On block:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "§pyramid-shape-violation/shape-tampering: ..."
  }
}
```

On pass: exit 0 with no stdout (the tool call proceeds normally).

Per D2.2 §Hook events table, PreToolUse v2.0.45+ supports `permissionDecision: "deny"`. Older versions use exit 2 only. The script uses both — emits the JSON for new versions, exits 2 for compatibility.

---

## Matcher

Wired in `.claude/settings.json` to PreToolUse with `tool_name` matchers `Write|Edit|MultiEdit`. The script's first action is to inspect the tool input's file path; if the path doesn't match `docs/specs/*/spec.md`, the script exits 0 silently (the matcher is broad to catch all Write/Edit tools; the script narrows by path).

---

## Script content

```bash
#!/usr/bin/env bash
# .claude/hooks/pyramid-tampering.sh
#
# Pre-flight pyramid-shape guard per D3.2 §Downstream consumer touch-points.
# Fires on PreToolUse for Write/Edit/MultiEdit; narrows to spec file paths;
# validates the proposed write's tag set against the sealed parent manifest's
# pyramid_shape.
#
# Halt code: §pyramid-shape-violation/shape-tampering
#
# Output: hookSpecificOutput wrapper with permissionDecision: "deny" on block;
# exit 2 also (for Claude Code versions <v2.0.45 that don't read the JSON).

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
. "$SCRIPT_DIR/_lib.sh"

trace "pyramid-tampering: fired"

read_hook_payload

# Extract tool name and input. PreToolUse payload shape per D2.2:
#   {"tool_name": "Write", "tool_input": {"file_path": "...", "content": "..."}, ...}
tool_name="$(jq_field '.tool_name')"
file_path="$(jq_field '.tool_input.file_path // .tool_input.path')"

# Narrow to spec file paths. The pattern matches docs/specs/<NNNN>-<slug>/spec.md
# (with or without leading ./, with or without leading project-root prefix).
case "$file_path" in
  */docs/specs/*/spec.md|docs/specs/*/spec.md)
    : # match, proceed
    ;;
  *)
    trace "pyramid-tampering: file_path '$file_path' is not a spec file; exiting clean"
    exit 0
    ;;
esac

trace "pyramid-tampering: matched spec file_path=$file_path tool_name=$tool_name"

# Derive ticket from the spec path. Path shape: docs/specs/<NNNN>-<slug>/spec.md
# We need the parent manifest to validate against. v0.1's /specify writes
# .cascade/manifests/<MARKER>-<N>-specify.json; we need to derive that from
# either the spec path's NNNN or the cascade:run-state's active ticket.
#
# Cleanest: read cascade:run-state.active_stages[] and find the entry whose
# .ticket maps to this spec path. If multiple, pick the most recent.
# Fallback: read all .cascade/manifests/*-specify.json and find one whose
# outputs.spec_path matches this file.

if ! read_run_state; then
  echo "pyramid-tampering: cannot validate without .cascade/run-state.json" >&2
  # No run-state = no cascade context = no pyramid to validate against.
  # Conservative: allow the write but log a warning. /specify's at-write gate
  # will catch shape violations regardless; this hook is a pre-flight signal.
  exit 0
fi

# Find a specify manifest whose outputs.spec_path matches this file
manifests_dir="$CLAUDE_PROJECT_DIR/.cascade/manifests"
parent_manifest=""
if [ -d "$manifests_dir" ]; then
  # Normalize file_path to be relative-to-project (strip $CLAUDE_PROJECT_DIR prefix)
  rel_file_path="${file_path#"$CLAUDE_PROJECT_DIR"/}"
  rel_file_path="${rel_file_path#./}"
  for manifest in "$manifests_dir"/*-specify.json; do
    [ -f "$manifest" ] || continue
    if ! read_manifest "$manifest"; then
      continue
    fi
    manifest_spec_path="$(manifest_field '.outputs.spec_path')"
    if [ "$manifest_spec_path" = "$rel_file_path" ] || [ "$manifest_spec_path" = "$file_path" ]; then
      parent_manifest="$manifest"
      break
    fi
  done
fi

if [ -z "$parent_manifest" ]; then
  # No sealed parent for this spec. Either this is a fresh /specify (no seal
  # yet, no pyramid to defend) or the manifest has been deleted. Both are
  # acceptable — the at-write gate in /specify will set up the pyramid_shape
  # at first seal, and this hook can't validate something that doesn't exist.
  trace "pyramid-tampering: no sealed parent for $rel_file_path; allowing write"
  exit 0
fi

trace "pyramid-tampering: found parent manifest $parent_manifest"

# Re-read the manifest into MANIFEST
read_manifest "$parent_manifest"

# Extract sealed pyramid_shape (the canonical shape per D3.2)
sealed_strategy="$(manifest_field '.outputs.decomposition_strategy')"
sealed_pyramid_shape="$(echo "$MANIFEST" | jq -c '.outputs.pyramid_shape // null')"
sealed_seed="$(echo "$MANIFEST" | jq -c '.outputs.failing_test_seed // []')"

if [ "$sealed_pyramid_shape" = "null" ]; then
  # Hybrid parent — defers pyramid to children. No shape to enforce here.
  trace "pyramid-tampering: parent strategy=$sealed_strategy with null pyramid_shape (hybrid); allowing"
  exit 0
fi

# Extract proposed content from tool_input
# For Write: tool_input.content is the full new content.
# For Edit/MultiEdit: tool_input.new_string (single) or tool_input.edits[].new_string (multi).
# All three shapes: get the bytes that will land on disk.
proposed_content=""
case "$tool_name" in
  Write)
    proposed_content="$(jq_field '.tool_input.content')"
    ;;
  Edit)
    # Edit produces a new file from old + replacement; the new content is
    # not trivially derivable from tool_input alone. For Edit, read the
    # current file, apply the replacement in-memory, then check.
    old_str="$(jq_field '.tool_input.old_string')"
    new_str="$(jq_field '.tool_input.new_string')"
    current="$(cat "$file_path" 2>/dev/null || echo "")"
    # Bash string replace; for the first occurrence (matches Edit's contract)
    proposed_content="${current/"$old_str"/"$new_str"}"
    ;;
  MultiEdit)
    # MultiEdit applies a list of edits in order. The same replay logic
    # would be needed. For v0.2 conservatism, refuse to predict MultiEdit's
    # output for tamper detection — the at-write gate will catch it.
    trace "pyramid-tampering: tool=MultiEdit not handled at pre-flight; allowing (at-write gate will catch)"
    exit 0
    ;;
  *)
    trace "pyramid-tampering: tool=$tool_name not Write/Edit; exiting clean"
    exit 0
    ;;
esac

if [ -z "$proposed_content" ]; then
  trace "pyramid-tampering: no proposed content extractable; allowing"
  exit 0
fi

# Extract proposed pyramid shape + tag set from the spec content's
# **Pyramid shape:** preamble (per D3.2's §Spec template addition).
#
# Expected shape: a `**Pyramid shape:**` line followed by `- Strategy: <value>`
# and tag-set lines (required/optional/forbidden), then the §Failing-test seed
# section with `[<tag>]` annotations per entry.
#
# For shape-tampering detection we compare:
#   (a) The Strategy field — must match sealed.
#   (b) The full pyramid_shape block — must match sealed verbatim
#       (the strategy → shape catalog is the source of truth; the spec
#       writes the rendered form, which is deterministic from strategy).
#   (c) The set of [<tag>] values on each failing-test seed entry — must
#       be a subset of sealed required ∪ optional, and a superset of required.

proposed_strategy="$(echo "$proposed_content" \
  | grep -E '^\s*-\s+Strategy:' \
  | head -n 1 \
  | sed -E 's/^\s*-\s+Strategy:\s*([a-z-]+).*$/\1/')"

if [ -z "$proposed_strategy" ]; then
  # No Strategy line. May be a draft pre-step-1; conservative allow.
  trace "pyramid-tampering: no Strategy: line in proposed content; allowing"
  exit 0
fi

if [ "$proposed_strategy" != "$sealed_strategy" ]; then
  diagnostic="§pyramid-shape-violation/shape-tampering: spec at $file_path proposes Strategy: $proposed_strategy, but the sealed parent manifest at $parent_manifest carries Strategy: $sealed_strategy. Changing strategy post-seal is forbidden; the cascade halts. Recovery: /specify --unseal to re-seal under the new strategy (re-runs four-hat), OR revert the spec edit."
  log_halt "§pyramid-shape-violation/shape-tampering" "$diagnostic"

  # Emit hookSpecificOutput for v2.0.45+ + exit 2 for older versions
  emit_hook_specific_output "PreToolUse" \
    "$(jq -c -n --arg r "$diagnostic" '{permissionDecision: "deny", permissionDecisionReason: $r}')"
  exit 2
fi

# Compare the failing-test seed tag set
# The spec markdown has a §Failing-test seed section with bulleted entries
# of shape: `- test_name — \`[<tag>]\` — <description>`
# Extract the tag values from the proposed content.
proposed_tags="$(echo "$proposed_content" \
  | sed -n '/^##\s\+Failing-test seed/,/^##\s\+/p' \
  | grep -oE '\[(smoke|unit|integration|contract|perceptual|invariance)\]' \
  | sort -u \
  | tr '\n' ' ')"

# Sealed tag set
sealed_required="$(echo "$sealed_pyramid_shape" | jq -r '.required_tags[]?' 2>/dev/null | sort -u | tr '\n' ' ')"
sealed_optional="$(echo "$sealed_pyramid_shape" | jq -r '.optional_tags[]?' 2>/dev/null | sort -u | tr '\n' ' ')"
sealed_forbidden="$(echo "$sealed_pyramid_shape" | jq -r '.forbidden_tags[]?' 2>/dev/null | sort -u | tr '\n' ' ')"

# Check each proposed tag is in required ∪ optional and not in forbidden
violation=""
for tag in $proposed_tags; do
  bare_tag="${tag#[}"
  bare_tag="${bare_tag%]}"
  if echo " $sealed_forbidden " | grep -q " $bare_tag "; then
    violation="${violation}forbidden tag $bare_tag present; "
    continue
  fi
  if ! echo " $sealed_required $sealed_optional " | grep -q " $bare_tag "; then
    violation="${violation}tag $bare_tag not in required/optional set; "
  fi
done

# Check every required tag is present in proposed
for tag in $sealed_required; do
  if ! echo " $proposed_tags " | grep -q " \[$tag\] "; then
    violation="${violation}required tag $tag missing; "
  fi
done

if [ -n "$violation" ]; then
  diagnostic="§pyramid-shape-violation/shape-tampering: spec at $file_path proposes a tag set that violates the sealed pyramid_shape for Strategy: $sealed_strategy. Violations: $violation. Sealed required: [$sealed_required], optional: [$sealed_optional], forbidden: [$sealed_forbidden]. Recovery: re-tag the failing-test seed entries to match the sealed shape, OR /specify --unseal if the shape itself needs to change."
  log_halt "§pyramid-shape-violation/shape-tampering" "$diagnostic"

  emit_hook_specific_output "PreToolUse" \
    "$(jq -c -n --arg r "$diagnostic" '{permissionDecision: "deny", permissionDecisionReason: $r}')"
  exit 2
fi

# All checks pass; allow the write
trace "pyramid-tampering: proposed write matches sealed pyramid; exit 0"
exit 0
```

---

## Design notes

### Why narrow by path inside the script vs in the settings matcher

D2.2's tool-name regex matcher works on tool names (`Write`, `Edit`, etc.), not on file paths. The matcher catches all spec writes; the script's case statement narrows to `docs/specs/*/spec.md`. This split keeps `.claude/settings.json` simple (one matcher entry) and the script's narrowing logic explicit (one case statement).

### Why Write and Edit but not MultiEdit (v0.2)

MultiEdit applies a sequence of edits; predicting the post-MultiEdit content requires replaying the edit sequence against the current file. The bash replay logic is fragile (multiple sequential `${var/old/new}` replacements; ordering matters; no good error surface). v0.2 conservatively lets MultiEdit through — the at-write gate in `/specify` catches shape violations regardless.

**Surfaced item:** v0.2.x should handle MultiEdit by spawning a Python helper that uses string-replace semantics. Defer to v0.2.x.

### Why allow writes when run-state or parent manifest is absent

The hook is a pre-flight defense; the at-write gate inside `/specify` (Gate 1, per the Child 0001-B continuation 0 `/specify` amendment) is the authoritative shape-check. If this hook can't validate (no run-state, no parent manifest), it allows the write and trusts the at-write gate to catch violations.

This is consistent with the "hooks are auto-fire convenience; CLI/skill is authoritative" framing per D2.2 §Critical caveats #1.

### Diagnostic in `permissionDecisionReason` is factual

Per D2.2 §Critical caveats #3 + D2.3 v1.2 four-hat review §F-Int-2: the diagnostic describes the violation; the block is enforced by `permissionDecision: "deny"`, not by the prose. Recovery options are listed as informational suffixes ("Recovery: ..."), not commands.

### Halt-code naming: `§pyramid-shape-violation/shape-tampering`

The hash-mark prefix (`§`) matches v0.1's halt-code convention. The sub-case suffix (`shape-tampering`) distinguishes this from `/specify`'s at-seal violations (`§pyramid-shape-violation/artifact-path-invalid`, `§pyramid-shape-violation/refactor-spike-non-empty-seed`, etc.). The full halt-code is the apply-time identifier in `halt-messages.md`.

The halt-card content for `§pyramid-shape-violation` already exists in Child A's `halt-messages-append.md` per the F-2 fix; the sub-case `shape-tampering` is a refinement of the existing card. **Surfaced item:** verify Child A's append covers this sub-case at apply time; add a sub-case stanza if not.

---

## Failing-test seed

Per `decomposition.md` Child 0001-C failing-test-seed list:

```python
def test_pyramid_tampering_blocks_mutated_seed(tmp_cascade_repo):
    """
    asserts the script exits 2 when given a seed file whose tags don't match
    the sealed parent; covers AC-14.
    """
    # Seal a parent with walking-skeleton shape (required: smoke, perceptual)
    write_specify_manifest(tmp_cascade_repo, "TST-42", {
        "outputs": {
            "spec_path": "docs/specs/0042-login/spec.md",
            "decomposition_strategy": "walking-skeleton",
            "pyramid_shape": {
                "required_tags": ["smoke", "perceptual"],
                "optional_tags": ["unit", "integration"],
                "forbidden_tags": ["contract", "invariance"],
            },
        }
    })
    # Propose a write that introduces a forbidden tag
    proposed_content = """
# Spec

**Pyramid shape:**
- Strategy: walking-skeleton

## Failing-test seed

- test_x — `[smoke]` — description
- test_y — `[contract]` — description  ← forbidden!
"""
    result = run_hook(
        "pyramid-tampering.sh",
        payload={
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmp_cascade_repo / "docs/specs/0042-login/spec.md"),
                "content": proposed_content,
            },
        },
        project_dir=tmp_cascade_repo,
    )
    assert result.exit_code == 2
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "§pyramid-shape-violation/shape-tampering" in output["hookSpecificOutput"]["permissionDecisionReason"]
    assert "forbidden tag contract" in output["hookSpecificOutput"]["permissionDecisionReason"]

def test_pyramid_tampering_allows_intact_write(tmp_cascade_repo):
    """asserts exit 0 silent when the proposed write matches the sealed shape."""
    # Same setup as above, but the write keeps tags within required/optional
    write_specify_manifest(tmp_cascade_repo, "TST-42", {
        "outputs": {
            "spec_path": "docs/specs/0042-login/spec.md",
            "decomposition_strategy": "walking-skeleton",
            "pyramid_shape": {
                "required_tags": ["smoke", "perceptual"],
                "optional_tags": ["unit"],
                "forbidden_tags": ["contract", "invariance"],
            },
        }
    })
    proposed_content = """
# Spec

**Pyramid shape:**
- Strategy: walking-skeleton

## Failing-test seed

- test_x — `[smoke]` — description
- test_y — `[perceptual]` — description
- test_z — `[unit]` — description
"""
    result = run_hook("pyramid-tampering.sh", payload={
        "tool_name": "Write",
        "tool_input": {
            "file_path": str(tmp_cascade_repo / "docs/specs/0042-login/spec.md"),
            "content": proposed_content,
        },
    }, project_dir=tmp_cascade_repo)
    assert result.exit_code == 0
    assert result.stdout == ""
```

---

## Cross-references

- **D2.2 §Hook events table** — `PreToolUse` event semantics + matcher mechanics.
- **D2.2 §Hook events table** PreToolUse row's v2.0.45+ `permissionDecision` field.
- **D2.2 §Critical caveats #4** — "PostToolUse cannot undo the tool call" reinforces that pyramid-tampering must be a PreToolUse check.
- **D2.3 v1.2 four-hat review §F-Int-2** — factual-phrasing for the `permissionDecisionReason` string.
- **D3.2 §Downstream consumer touch-points** — `/build`'s pre-flight reads pyramid_shape from the parent manifest and rejects a seed file that mutates tags; this hook is one realization of that.
- **D3.2 §Spec template addition** — the `**Pyramid shape:**` preamble + tag-annotation conventions this hook parses.
- **D3.2 §Halt conditions** — `§pyramid-shape-violation` halt-card; this hook surfaces the `/shape-tampering` sub-case.
- **D3.4 §`/build` row** — the `build.pyramid-tampering` gate; this hook is the PreToolUse realization for `/build`'s pre-flight.
- **`build-SKILL-amendments.md`** (Child 0001-B continuation 1) Gate 2 — the predicate spec this hook implements at the hook level (the skill carries the at-write version).
- **`specify-SKILL-amendments.md`** (Child 0001-B continuation 0) Gate 1 — the at-write gate in /specify that this hook composes with.
- **Child A `halt-messages-append.md`** — `§pyramid-shape-violation` parent card; this hook's `/shape-tampering` sub-case may need an apply-time stanza addition.
- **`.claude/hooks/_lib.sh`** — sourced for IO and emitter helpers.
- **Parent spec AC-14** — covered by this script + the other six in this session.
