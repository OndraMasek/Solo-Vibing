# Decision records

This directory holds Architectural Decision Records (ADRs) — `NNNN-slug.md` files numbered continuously across both strategic and build-time decisions.

## Conventions

- **Numbering:** continuous `D-0001`, `D-0002`, … shared across strategic and build-time classes.
- **Naming:** `NNNN-short-slug.md` where slug matches the decision title in kebab-case.
- **Linear back-references:** for strategic decisions, include the originating Linear issue (e.g. `SOL-9`) in the front-matter and body.
- **Permanence:** ADRs are append-only. Use Status field for lifecycle (Active / Superseded by D-NNNN / Deprecated). Do NOT rewrite resolved ADRs.

## Index

| ID | Title | Status |
|---|---|---|
| D-0001 | Meta-project Linear setup | Active |
