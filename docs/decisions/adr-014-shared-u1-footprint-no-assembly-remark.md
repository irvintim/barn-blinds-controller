# ADR-014: One shared U1 footprint for three DC-DCs; no JLCPCB assembly remark

**Date:** 2026-08-07 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

U1's footprint `DCDC_HYBRID_SLC03_TEC2` shares holes across three isolated
DC-DC converters (Mean Well SLC03A-05, Traco TBA 2-1211 and Heniper
B1205S-3WR2L), silkscreened `M` / `H` / `T` with "POPULATE ONE", so stock
problems don't force a re-layout. JLCPCB's BOM/CPL carries only one position
and rotation for the footprint. The obvious fix is an assembly remark naming
the hole set.

## Decision

Leave the assembly remark **empty**. JLCPCB's engineer contacts us about this
board on every run regardless, and the hole set is settled in that exchange.
It has been placed correctly several times without a remark. The answer text
is kept in `pcb/main-board/fab/vsp-wsc4-rev1.3/JLCPCB-ORDER-NOTES.md`.

Rev 1.3 uses the **Heniper B1205S-3WR2L (C20622657) on the `H` holes**.

## Consequences

- Electrically safe whichever hole set is used, since same-numbered pads
  share nets.
- Related standing practice: JLCPCB's parts matcher duplicates designators
  when one LCSC spans two BOM lines (C1590, C51927445). Their tool prompts at
  upload and we approve. A pre-merged `_bom-UPLOAD.csv` exists but is not
  needed.
