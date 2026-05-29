#!/usr/bin/env python3
# .claude/hooks/_lib.py — shared Python helpers for Solo-Vibing cascade hooks.
#
# Python parity with the bash lib at .claude/hooks/lib/common.sh, for the
# command-type Python hooks (currently four-hat-objection-coverage.py). Provides:
#   - read_hook_payload(): read stdin JSON, return the parsed dict
#   - trace(msg): env-gated stderr trace (SOLO_HOOK_TRACE=1)
#   - log_halt(code, diagnostic): append a halt record to .cascade/halt/<code>.txt
#   - emit_stop_block(reason): emit the top-level Stop/SubagentStop quirk JSON
#
# Output and side-effect shapes match common.sh exactly so the bash and Python
# hooks behave identically. CLAUDE_PROJECT_DIR is resolved the same way
# common.sh does (env var, else walk up from cwd for .cascade/).
#
# 3.9-compatible on purpose: hooks run via `#!/usr/bin/env python3`, which on
# some hosts is <3.10. No match statements, no runtime PEP-604 unions.
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def project_dir() -> Path:
    """Resolve CLAUDE_PROJECT_DIR like common.sh: env var, else walk up from
    cwd looking for a .cascade/ directory, else fall back to cwd."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    d = Path.cwd().resolve()
    for candidate in [d, *d.parents]:
        if (candidate / ".cascade").is_dir():
            return candidate
    return d


def read_hook_payload() -> dict:
    """Read stdin and return the parsed JSON payload dict.

    Mirrors common.sh read_hook_payload: exit 4 on empty stdin or invalid JSON.
    """
    raw = sys.stdin.read()
    if not raw.strip():
        sys.stderr.write("hook-lib: empty stdin; expected hook payload JSON\n")
        sys.exit(4)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        sys.stderr.write("hook-lib: stdin is not valid JSON\n")
        sys.exit(4)
    if not isinstance(payload, dict):
        sys.stderr.write("hook-lib: stdin JSON is not an object\n")
        sys.exit(4)
    return payload


def trace(msg: str) -> None:
    """Env-gated stderr trace. Silent unless SOLO_HOOK_TRACE=1, matching
    common.sh's trace()."""
    if os.environ.get("SOLO_HOOK_TRACE") == "1":
        tag = os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else "hook"
        sys.stderr.write("[{}] {}\n".format(tag, msg))


def log_halt(code: str, diagnostic: str) -> None:
    """Append a halt record to .cascade/halt/<safe_name>.txt.

    Byte-for-byte parity with common.sh log_halt: strip § and / from the
    filename (keep them in the content), append the same five-line block.
    The caller decides whether to also emit a block decision; this only records.
    """
    halt_dir = project_dir() / ".cascade" / "halt"
    halt_dir.mkdir(parents=True, exist_ok=True)
    safe_name = code.replace("§", "").replace("/", "")
    path = halt_dir / "{}.txt".format(safe_name)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    block = "## {}\nTimestamp: {}\nDiagnostic:\n{}\n---\n".format(code, timestamp, diagnostic)
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)


def emit_stop_block(reason: str) -> None:
    """Emit the Stop / SubagentStop top-level-fields-only output per D2.2
    §Stop / SubagentStop output schema quirk. NO hookSpecificOutput wrapper.
    Matches common.sh emit_stop_block: compact JSON {"decision","reason"}."""
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}, separators=(",", ":")) + "\n")
