# ADR-002: ESP32-S3-WROOM-1-N4 (C2913197) is the module

**Date:** 2026-08-07 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

During the Rev 1.3 order review, the key-parts table in `CLAUDE.md` listed
C2913202, which is the **N16R8** (16 MB flash, 8 MB octal PSRAM, rated
-40~65 °C). The schematic used C2913197, the **N4** (4 MB quad flash, no PSRAM,
-40~85 °C). One of the two had to be wrong.

The N16R8's octal PSRAM takes IO35/IO36/IO37 (datasheet Table 3, footnote b:
"cannot be used for other functions"). This design uses those pins for
`ISO_STBY` and two Shade-2 control lines, so the N16R8 would lose a shade
channel and motor-driver standby. Its 65 °C rating is also below what a hot
attic reaches.

## Decision

Keep the **N4, LCSC C2913197**. The documentation was wrong, not the board.

If the part is ever re-sourced:

- **Never an R8 / R16V (octal PSRAM) variant.**
- R2 (quad PSRAM) parts are pin-compatible and 85 °C, but PSRAM buys nothing here.
- The H4 (105 °C, no PSRAM) would be the ideal attic part, but JLCPCB does not
  stock it (checked 2026-08-07). Every non-PSRAM part JLCPCB carries is 85 °C.

## Consequences

- 85 °C is the module's ambient rating, and a sealed printed box in an attic
  runs above attic air. The enclosure has to keep its ventilation (ADR-019).
- Verify the variant on the first board of every order with
  `esptool flash-id`. Rev 1.3 board 1 reported 4 MB, eFuse quad, QFN56 v0.2,
  which confirms the N4.
- This choice is also behind ADR-013: Tasmota's generic S3 module assumes
  octal PSRAM and hides GPIO33-37.
