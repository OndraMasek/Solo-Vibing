# Code markers

In-code markers Claude can leave behind when it wants the founder's attention without halting the cascade. Each marker is a Unicode glyph followed by a one-line note; downstream scans (`grep -rn 🤔` / `📝` / `☣️`) surface them for triage.

## Vocabulary

| Glyph | Name | Meaning |
|---|---|---|
| `🤔` | clarify question | The model needed clarification but proceeded with its best guess. The marker names the assumption made and the question the founder should answer. /retro surfaces a count per session. |
| `📝` | copy pending | Final product copy was not in scope at the moment of writing. Placeholder text is in place; the marker names what copy is needed and any constraints (length, tone, references). |
| `☣️` | tainted code region | Implementation was written against a manifest that has since been marked `is_tainted: true` per AC-18. The code may be correct, but provenance is broken; a `--reconcile` re-evaluation of the responsible stage is required before this region is trusted. The marker names the tainted manifest and the responsible stage. |

## Placement

Markers go in source code (or markdown) as comments, single-line:

```python
# 🤔 Assuming this rate-limit is per-IP not per-API-key — confirm with founder.
```

```markdown
<!-- 📝 Hero copy: 1–2 lines, "you ship; we don't" angle. -->
```

```typescript
// ☣️ Tainted: written against /plan manifest sha:abc12345 before it was marked is_tainted (reason: decomposition skipped the kill-handler). Run `solo-cascade --reconcile=plan SOL-12` before relying on this block.
```

These glyphs live in source code and on the chat surface only. They are **never** written into Linear content — titles, descriptions, comments, labels, or documents — per `write-discipline.md` §No emoji or icons in Linear content. `/retro` surfaces marker counts in chat; it does not mirror the glyphs into the Linear retro doc.

## Lifecycle

- **Add.** The producing skill writes the marker as part of the artifact it seals. Markers are first-class evidence; they are not a workaround.
- **Surface.** `/retro` scans the worktree for `🤔` / `📝` / `☣️` counts and lists locations; `/audit-self` may sweep older sessions for stale markers.
- **Remove.** The founder removes the marker when the underlying issue resolves — answering the clarify, writing the copy, or re-running the responsible stage with `--reconcile` (for `☣️`).

## Why glyphs and not text tags

The v0.1 markers (`🤔`, `📝`) are deliberately atypical so they don't collide with the surrounding codebase's TODO/FIXME/XXX/NOTE conventions. Each consumer repo has its own taxonomy; glyphs sidestep that. `☣️` extends the family.

## Provenance

Convention deferred in D4.2 §D4.4 ("code-markers convention for skipping mid-build clarification cycles"). Promoted to v0.2 with the `☣️` addition per SOL-HANDOFF-008 decision 1b and `D2_1_revision_decisions.md` decision 5.
