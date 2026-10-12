# ADR-012: The Rev 1.3 motor channel cross is fixed in firmware; nets renamed in Rev 1.4

**Date:** 2026-08-28 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

During the J4 pin rework (ADR-011), the labels on the TB6612FNG **output**
side were re-pointed but the **input** side was not. On both drivers the A/B
control nets are swapped within each pair: `SH2_*` drives SHADE1, `SH1_*`
drives SHADE2, `SH4_*` drives SHADE3, `SH3_*` drives SHADE4. The isolators
add no cross of their own. The symptom is silent: a motor on a correctly
wired terminal never moves, because the command energizes a different, empty
channel. Found 2026-08-28, confirmed on hardware for all four channels under
ESPHome (2026-09-03) and Tasmota (2026-10-11).

## Decision

**Rev 1.3: fix it in firmware.** Every config names its outputs for the
physical J4 terminal and uses this map, never the net names:

| J4 shade | UP / DOWN | OPEN | CLOSED | PWM |
|---|---|---|---|---|
| SHADE1 | 7 / 17 | GPIO48 | GPIO47 | GPIO21 |
| SHADE2 | 8 / 18 | GPIO36 | GPIO37 | GPIO38 |
| SHADE3 | 9 / 19 | GPIO41 | GPIO40 | GPIO39 |
| SHADE4 | 10 / 20 | GPIO42 | GPIO2 | GPIO1 |

**Rev 1.4: rename the nets**, swapping the label pairs 1↔2 and 3↔4 along the
whole path, so `ISO_SH1_*` reaches SHADE1. It is a pure rename with zero
copper changes and the same GPIO assignments. Do not re-route `OUTx`→`xIN`
instead, which costs real B.Cu routing for an identical result.

## Consequences

- Until Rev 1.4 ships, the net names in the schematic and the Rev 1.3 GPIO map
  in `docs/todo.md` mislead. Firmware must not "fix" its ids back to match them.
- After the rename, the table above stays correct unchanged.
