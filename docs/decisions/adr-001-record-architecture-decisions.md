# ADR-001: Record design decisions as ADRs

**Date:** 2026-10-12
**Status:** Accepted

## Context

Six months of design decisions on the VSP-WSC-4 lived in `CLAUDE.md` and the
bring-up/todo docs, mixed in with current status. They were marked "settled",
"CLOSED" and "do not re-flag" because they kept getting re-raised: the fuse
rating, the J3 DNP, the empty JLCPCB assembly remark, via-in-pad. A status file
is the wrong home for them. It is supposed to change, and a decision's
rationale is not.

## Decision

Keep decisions in `docs/decisions/` as numbered ADRs (`adr-NNN-slug.md`), the
same convention as the hourarc repo:

- One ADR per genuine fork in the road. Routine choices don't get one.
- Accepted ADRs are immutable. A changed decision gets a new ADR that
  supersedes the old one; the old one changes only its Status line.
- Context, decision, consequences. Short.

Current state (the GPIO map, the rails, what has been verified) lives in the
living `docs/architecture.md`, which links back to the ADRs.

ADR-002 to ADR-019 were back-filled on 2026-10-12 from `CLAUDE.md`, the todo
list and the bring-up log. Each one carries the date the decision was made,
not the date it was written down.

## Consequences

- "Do not re-flag this" becomes "see ADR-NNN". Re-opening a decision means
  writing a superseding ADR, which forces the new argument to be made.
- `CLAUDE.md` can shrink to a repo map, the current status and the working rules.
