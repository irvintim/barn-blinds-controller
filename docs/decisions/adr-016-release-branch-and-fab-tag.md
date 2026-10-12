# ADR-016: Every fabbed revision gets a release branch and a frozen -fab tag

**Date:** 2026-08-27 (recorded retroactively 2026-10-12)
**Status:** Accepted (extended by ADR-020)

## Context

Bring-up keeps producing fixes and documentation for a revision after its
boards were ordered. We also need to recover exactly what a fab house built
from.

## Decision

Each shipped revision gets:

- **`release/vX.Y`**, a moving branch that absorbs later fixes for that revision
- **`vX.Y-fab`**, an annotated tag **frozen** at the commit the boards were
  built from. Never move a `-fab` tag.

| Revision | Branch | Tag | Commit |
|---|---|---|---|
| 1.0/1.1 | `release/v1.0` | `v1.0-fab` | `41bff59` (2026-04-24) |
| 1.2 | `release/v1.2` | `v1.2-fab` | `b2b59b3` (2026-06-11) |
| 1.3 | `release/v1.3` | `v1.3-fab` | `3bc6a34` (2026-08-07) |

History stays linear (no merge commits), so release branches fast-forward
cleanly.

## Consequences

- The fab outputs also live in `pcb/main-board/fab/<rev>/`, so they can be
  inspected without a checkout.
- `-fab` tags predate the 2026-10-12 reorganization and therefore have the old
  flat layout. That is intended, because they are the as-built record.
