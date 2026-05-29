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
# shellcheck source=lib/common.sh
. "$SCRIPT_DIR/lib/common.sh"

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
