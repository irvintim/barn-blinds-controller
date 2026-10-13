# ADR-022: DIN mounting: two clips on the back, or one on the -X side

**Date:** 2026-10-12
**Status:** Accepted (supersedes ADR-021 decision point 5's single DIN clip)

## Context

ADR-021 placed one DIN clip in the middle of the tray floor (y = −8 mm). The
clips actually bought are the generic copy of the Phoenix USA 10 (42.6 × 10 mm,
19.3 mm tall, three screw holes with 25 mm across the outer two, for 35 mm
TS 35 rail). Their hole pattern matches Rev 3 as built. The supplier's own
mounting photo uses two clips per device, one near each end. A single clip on
a 79 mm box can rock, especially with field wiring pulling on the terminal
block.

## Decision

- **Two clips**, both on the **tray floor** (the back of the box), each running
  across the rail along X. The rail runs along Y.
- Clip centres at **y = −8 and y = +31 mm** (`din_cy` = 11.5 midpoint,
  `din_spacing` = 39). They sit either side of the wall-mount keyholes, so
  neither clip covers one.
- The second clip goes on the +Y side, not near −Y: a boss at y ≈ −30 would hit
  U1's pins, which hang 2.5 mm below the board.
- **Side mount, terminal block facing out:** one clip on the **−X wall** (lid
  part), three holes along Y centred at y = +5, z = 10 mm, with bosses inside.
  The rail runs along Z. The terminal block faces the installer and D5 (power,
  on +X) stays visible. D3/D4 and USB face the panel, which is acceptable
  because USB is only for initial programming. All vents stay open.
  One clip only: the wall is 24 mm tall, too short for two 10 mm clips at a
  useful spacing.
- **Rejected:** side mounting on a ±Y wall (terminal block up or down). It
  puts that wall's vents against the panel, and the +Y wall has the
  1000 µF bulk caps right behind it, leaving no room for bosses.
- Holes stay Ø2.75 for self-cutting M3, with 1.5 mm inside bosses; the fit
  checker gates boss clearance to the board's underside parts.

## Consequences

- Screw length = clip base thickness + up to 4 mm into the case. Measure the
  clip's base when it arrives.
- **Stand-off from the rail is less than the clip's 19.3 mm height**, because
  the rail sits inside the clip's channel. Neither drawing dimensions it
  directly, so measure it with a clip on a rail. ADR-019's "adds only 7.4 mm"
  came from a spec-table value and should not be relied on either.
- The middle side-mount boss sits beside the unpopulated J3 holes. Debugging
  through J3 means taking the lid off anyway, so it doesn't get in the way.
- Any clip with three M3 holes at 12.5 mm pitch fits. Others need
  `din_pitch` / `din_hole_d` changes; the three-holes-per-clip count is
  fixed in the build script.
