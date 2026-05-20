# Capability-cluster `[perceptual]` artifact types

Read by `/specify` skill step 3 to resolve `artifact_type` and validate `artifact_path` extension for capability-cluster `[perceptual]` entries. Novel artifact types not in this table use founder-declared extensions recorded on the manifest.

## Canonical type table (v0.2)

| `artifact_type` (manifest value) | Description | Extension | Path example |
|---|---|---|---|
| `rendered-document` | Rendered document (PDF, generated report) | `.pdf` | `docs/specs/NNNN-<slug>/perceptual/invoice-2026-001.pdf` |
| `image` | Image (chart, diagram, generated graphic) | `.png` | `docs/specs/NNNN-<slug>/perceptual/dashboard-chart.png` |
| `scheduled-event` | Scheduled event (calendar invite) | `.ics` | `docs/specs/NNNN-<slug>/perceptual/team-sync-event.ics` |
| `share-post` | Share-post / social media body | `.md` | `docs/specs/NNNN-<slug>/perceptual/launch-announcement.md` |
| `email` | Email / message body | `.eml` or `.md` | `docs/specs/NNNN-<slug>/perceptual/welcome-email.eml` |
| `api-response` | API response capture (capability-internal; distinct from api-boundary's transcript) | `.json` | `docs/specs/NNNN-<slug>/perceptual/recommended-feed.json` |
| `plain-text` | Plain-text capture (logs, structured text outputs) | `.txt` | `docs/specs/NNNN-<slug>/perceptual/digest.txt` |

## Novel artifact types

For artifact types not in the table above, the founder declares the extension at `/specify` step 3. The chosen extension is recorded on the manifest's `artifact_type` field as a free-form lowercase-hyphenated string; the framework checks file existence at the documented `artifact_path` but does not validate the format. Per-extension format validators are a v0.2.x consideration.

## Implicit types (omit `artifact_type`)

- **Walking-skeleton `[perceptual]` entries** — `artifact_type` is omitted; the type is implicitly `image` and the extension is `.png`.
- **Api-boundary `[perceptual]` entries** — `artifact_type` is omitted; the type is implicitly `integration-transcript`, a singleton not in this table.
- **Refactor-spike specs** — the `[perceptual]` tag is forbidden; the invariance predicate replaces perceptual evidence. See D3.3 §Refactor-spike invariance predicate.

## Versioning

Versioned implicitly by D3.3's `schema_version`; v0.2.x can add rows without breaking sealed manifests.

## Cross-references

- D3.3 §Capability-cluster perceptual predicate — binding spec for this table.
- D3.3 §Manifest representation — binding spec for the `artifact_type` field on the manifest.
- `.claude/skills/specify/SKILL.md` step 3 — consumer; reads this file to resolve `artifact_type` and validate `artifact_path` extension at seal time.
- Parent spec `docs/specs/0001-v0.2-cascade-integration/spec.md` AC-4 — acceptance criterion this file satisfies.
