#!/usr/bin/env python3
"""Evaluator for the cascade-control write denylist (build-agent-scoped).

Called by .claude/hooks/pretool-write-denylist.sh ONLY in build-agent context.
Reads the PreToolUse payload and the denylist, decides whether the tool call is
a write to a denylisted cascade-control path, and prints an explicit-deny JSON
({"decision":"block","reason":"..."}) on a match. Prints nothing on a pass.
Always exits 0 so the calling hook's `set -e` is safe.

Inputs (env):
  CLAUDE_PROJECT_DIR  repo root (paths normalized relative to it)
  DENYLIST            path to .claude/agents/build-write-denylist.txt
  HOOK_PAYLOAD_RAW    the raw PreToolUse payload JSON

Inspects Write/Edit/MultiEdit file_path AND Bash WRITE targets (redirection,
tee, cp/mv/install/rsync dest, dd of=, sed -i, truncate) — reads are ignored,
so a `cat <denylisted>` is not blocked. The Bash arm closes the
shell-redirection bypass (the build agent runs --dangerously-skip-permissions).
"""
import os
import sys
import json
import re
import fnmatch

HALT = "§cascade-control-write-blocked"


def main():
    repo = os.environ.get("CLAUDE_PROJECT_DIR", "").rstrip("/")
    denylist_path = os.environ.get("DENYLIST", "")
    raw = os.environ.get("HOOK_PAYLOAD_RAW", "")

    try:
        payload = json.loads(raw)
    except Exception:
        return  # unparseable → soft-pass

    try:
        patterns = []
        with open(denylist_path, encoding="utf-8") as fh:
            for line in fh:
                s = line.strip()
                if s and not s.startswith("#"):
                    patterns.append(s)
    except OSError:
        return
    if not patterns:
        return

    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input", {}) or {}

    if tool in ("Write", "Edit", "MultiEdit"):
        fp = ti.get("file_path") or ti.get("filePath") or ""
        candidates = [fp] if fp else []
    elif tool == "Bash":
        candidates = bash_write_targets(ti.get("command", "") or "")
    else:
        return  # not a write-capable tool this guard inspects

    for cand in candidates:
        rel = normalize(cand, repo)
        if not rel:
            continue
        for pat in patterns:
            if fnmatch.fnmatch(rel, pat):
                print(json.dumps({"decision": "block", "reason": reason(tool, rel, pat)}))
                return


def normalize(p, repo):
    p = p.strip().strip('"').strip("'")
    if not p:
        return ""
    if repo and p.startswith(repo + "/"):
        p = p[len(repo) + 1:]
    while p.startswith("./"):
        p = p[2:]
    return p


def bash_write_targets(cmd):
    """Extract WRITE-target tokens from a shell command. Reads are ignored, so a
    legitimate `cat docs/.solo-config.json` is not blocked — only writes."""
    targets = []
    # redirection: optional fd, > or >> or &> / &>>  → target token
    for m in re.finditer(r'(?:\d*&?>>?|&>>?)\s*(["\']?)([^\s"\';|&()<>]+)', cmd):
        targets.append(m.group(2))
    # tee [flags] file...  (writes each file arg up to a shell operator)
    for m in re.finditer(r'\btee\b((?:\s+-{1,2}[A-Za-z-]+)*)((?:\s+[^\s|;&()<>]+)+)', cmd):
        targets += [t for t in m.group(2).split() if not t.startswith("-")]
    # cp / mv / install / rsync  → destination is the last positional arg
    for m in re.finditer(r'\b(?:cp|mv|install|rsync)\b([^|;&]*)', cmd):
        toks = [t for t in m.group(1).split() if not t.startswith("-")]
        if toks:
            targets.append(toks[-1])
    # dd of=PATH
    for m in re.finditer(r'\bdd\b[^|;&]*?\bof=(["\']?)([^\s"\';|&()]+)', cmd):
        targets.append(m.group(2))
    # sed -i / --in-place  → following non-flag file tokens
    for m in re.finditer(r'\bsed\b[^|;&]*?(?:-i\S*|--in-place\S*)\s+([^|;&]+)', cmd):
        targets += [t for t in m.group(1).split() if not t.startswith("-")]
    # truncate [flags] file...
    for m in re.finditer(r'\btruncate\b((?:\s+-{1,2}[A-Za-z=]+\S*|\s+-s\s*\S+)*)((?:\s+[^\s|;&()<>]+)+)', cmd):
        targets += [t for t in m.group(2).split() if not t.startswith("-")]
    return targets


def reason(tool, rel, pat):
    return (
        f"{HALT}: build-agent-context {tool} write to '{rel}' matches denylist "
        f"pattern '{pat}' (.claude/agents/build-write-denylist.txt, per D4.1.7 / "
        "spec AC-21). The autonomous Ralph build loop (SOLO_BUILD_AGENT=1) may not "
        "mutate cascade-control files. Recovery: make this change from the founder "
        "session via the responsible orchestration stage — e.g. /config or /onboard "
        "for docs/.solo-config.json, /constitution for the constitution, the sealing "
        "stage (/build --finalize, /wrap, …) for a .cascade manifest. Those run "
        "outside build-agent context and are the authoritative writers; the build "
        "agent does not edit governance files directly."
    )


if __name__ == "__main__":
    main()
    sys.exit(0)
