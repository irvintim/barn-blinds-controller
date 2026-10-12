# ADR-013: Tasmota is configured by Template, not the Module page

**Date:** 2026-10-11 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

On Rev 1.2, Tasmota Shutters 3 and 4 never worked. At the time this was blamed
on GPIO43/44 being UART0, but those pins carried Shades 1 and 2, which worked,
so the explanation never fit. Tasmota's generic ESP32-S3 module reserves
GPIO33-37 for octal PSRAM (`GPIO_NONE`) and **hides them on the Module page**.
The N4 has no PSRAM (ADR-002), so the pins are free. Tasmota simply won't
offer them. Rev 1.3 uses GPIO35/36/37 for STBY and Shade 2.

## Decision

Configure the board by applying a **Template** that assigns every pin,
including 35-37, using the command sequence in
`firmware/tasmota/tasmota-setup-commands.txt`. No Berry scripts. No board
change was needed.

## Consequences

- All four shutters verified on Rev 1.3 under Tasmota (2026-10-11), which was
  the point of Rev 1.3 (ADR-003).
- `Interlock` must be set **after** the template is active, then switched `ON`
  separately.
- The template is the artifact to submit to the Tasmota templates repository
  for the product track.
