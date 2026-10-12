# ADR-020: Repository layout, and main as the next-revision line

**Date:** 2026-10-12
**Status:** Accepted (extends ADR-016)

## Context

The repo had grown flat: ~60 top-level files mixing the KiCad project,
vendor library downloads for six parts, two generations of enclosure exports,
stale gerbers, datasheets, and firmware configs filed under
`docs/project-context/`. Rev 1.3 is going to production while Rev 1.4 work
starts, so two lines of board development have to coexist.

## Decision

1. **Layout** follows `vesprio-thermostat`:
   `pcb/main-board/` (KiCad project, `lib/` for project symbols, footprints and
   3D models, `fab/<rev>/` for the files each order was built from),
   `enclosure/`, `firmware/esphome/` + `firmware/tasmota/`, `docs/`
   (`decisions/`, `architecture.md`, `bringup/`, `datasheets/`), `purchasing/`.
   Fabrication Toolkit's `production/` output is scratch and gitignored.
2. **Branch roles:** `release/v1.3` is the production line for Rev 1.3
   (fixes, firmware and docs for boards in the field). **`main` is Rev 1.4
   development.** A change that applies to both goes on `release/v1.3` and is
   brought to `main` by rebase or cherry-pick, never by a merge commit.
3. Stale outputs are deleted, not archived. Git history and the `-fab` tags
   keep them.

## Consequences

- `release/v1.3` and `main` were fast-forwarded together through the
  reorganization, so both have the new layout and diverge only from here.
- `release/v1.0` and `release/v1.2` are left at their fab commits, in the old
  layout. Those revisions are retired; their tags are the record.
- The old `feature/new-inputs` branch is fully merged into `main` and can be
  pruned.
