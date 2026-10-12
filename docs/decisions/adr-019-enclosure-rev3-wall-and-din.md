# ADR-019: Enclosure Rev 3: wall keyholes and DIN rail from one box, sized for Rev 1.3

**Date:** 2026-06-29 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

The Rev 2 printed enclosure (`enclosure/rev2/`) was designed around the Rev 1.2
board. Rev 1.3 is larger (outline 65.004 × 73.935 mm), has a taller mated
terminal block, and moved from USB-C to Micro-USB. Installations differ:
some boards go on a wall or rafter, some in a panel on DIN rail.

## Decision

One Rev 3 enclosure supporting both mounts:

- **Wall:** keep the keyholes on the back plate.
- **DIN rail:** Phoenix Contact USA 10 (1201578) clip on 35 mm TS 35 rail,
  fixed with 3× M3 self-cutting screws in Ø2.75 mm bosses on 25 mm centers
  (50 mm span). The clip adds 7.4 mm depth.

Sized for the Rev 1.3 board, with Z height for the 26.75 mm mated terminal
block (ADR-011). The Micro-USB cutout moves off the DIN-rail-side wall to the
top or bottom edge, and the LED windows move with it. The terminal-block
cutout stays on the same face and orientation.

## Consequences

- Keep the existing ventilation and confirm it still works in the larger box:
  the N4 module is rated 85 °C ambient (ADR-002). Don't mount the box at the
  roof ridge.
- The board model for the redesign is
  `enclosure/reference/vsp-wsc4-rev1.3-board.step`, exported from the
  as-fabbed PCB.
