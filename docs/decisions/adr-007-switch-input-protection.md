# ADR-007: Wall-switch inputs: 1 kΩ series, RC, TVS on the MCU side, internal pull-ups only

**Date:** 2026-07-07 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

Rev 1.3 adds eight wall-switch inputs (up/down for each of the four shades).
The switches sit on long runs of building wire, so the inputs have to survive
ESD and induced surges and still give a clean logic level. The first pass used
10 kΩ series resistors. With the ESP32's internal ~45 kΩ pull-up, a closed
switch divided down to ~0.6 V at the pin, against a 0.825 V VIL, which is too
little margin.

## Decision

Each input (`switch_inputs.kicad_sch`) is: connector → **1 kΩ series R** → a
node shared by a **100 nF cap**, a **PRTR5V0U2X TVS** I/O and the ESP32 GPIO.

- The TVS sits on the **MCU side** of the series resistor. The resistor limits
  surge current into the TVS, and the TVS clamps right at the protected pin.
  (U16 on USB is the opposite way round, on the connector side of R9/R10. Both
  are valid; they just differ.)
- 1 kΩ + 100 nF gives fc ≈ 1.6 kHz, and a closed switch reads ~0.1-0.23 V
  worst case.
- **No external pull-ups.** Switches short to `GND_ISO`, and firmware enables
  the internal pull-up on all eight: GPIO 3, 46, 9, 10, 11, 12, 13, 14.
- Each TVS VCC gets 100 nF decoupling (C40-C43).

## Consequences

- GPIO46 is a strapping pin whose reset default is pull-*down*, so firmware
  must set its pull-up explicitly. Because the switch also pulls to ground,
  GPIO46 reads 0 at boot either way, and a held switch can never select an
  invalid boot mode. GPIO3 only selects the JTAG source, which this board does
  not use.
- The RC is too slow to need precise placement but does not debounce
  mechanical contacts. **Every firmware config needs a software debounce**
  (bounce seen on the bench 2026-10-11).
