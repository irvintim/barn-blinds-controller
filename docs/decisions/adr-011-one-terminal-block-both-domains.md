# ADR-011: One 20-pin Phoenix 1786918 block carries motors and switches

**Date:** 2026-07-05 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

Rev 1.2 had an 8-pin spring terminal block for the four motors. Rev 1.3 adds
eight wall-switch inputs with their returns. A second connector would cost
board edge and enclosure openings. (The Phoenix 1054070 was used briefly
during the Rev 1.3 layout before this part replaced it.)

## Decision

A single **Phoenix Contact 1786918** (20-pin, dual-row, 3.5 mm pitch,
right-angle, so cable exits sideways), mating plug **1790182**. JLCPCB places
it from pre-purchased inventory (LCSC C6652293). Each motor and each switch
connects across a **vertical pair**:

| Pin pair | Function |
|---|---|
| 1 / 11 | SW1 UP / DOWN |
| 2, 5 / 12, 15 | GND_ISO (switch commons) |
| 3 / 13 | SW2 UP / DOWN |
| 4 / 14 | SW3 UP / DOWN |
| 6 / 16 | SW4 UP / DOWN |
| 7-10 / 17-20 | SHADE1-4 UP / DOWN |

## Consequences

- The connector deliberately carries **both isolation domains** (ISO switch
  returns beside 12 V motor pins, with SW4_UP next to SHADE1_UP). That is fine
  at 3.5 mm pitch for 12 V SELV (ADR-004), but it raises the number of close
  ISO/MOTOR copper approaches.
- The mated height (header 13.5 mm + plug 13.25 mm = 26.75 mm) drives the
  enclosure's Z height (ADR-019).
- The pin rework for this block is where the A/B control-net cross came from
  (ADR-012).
