# ADR-005: Stall protection is the current reading, not the fuse

**Date:** 2026-04 (original design); sensor changed 2026-07-07 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

A shade motor that hits its end stop, or jams, stalls and draws stall current
until something stops it. Two mechanisms on the board could plausibly do that:
the per-channel polyfuses F1-F4 and the current sensor.

## Decision

**Stall protection is firmware acting on the current sensor.** A current
sensor was put in the circuit for exactly this. The fuses are the
**catastrophic-fault backstop**, for a short or a load the board was never
meant to drive.

F1-F4 (1.1 A hold / 2.2 A trip) sitting above the motors' stall current is
therefore correct by design. Do not lower the fuse rating to chase stalls.

The sensor is one rail-level Allegro Hall sensor on ADC1 (ADR-006). Rev 1.3
replaced the ACS723 (a 5 V part that had been running out of spec at 3.3 V on
Rev 1.2) with the **ACS725LLCTR-05AB-T**, the native 3.3 V version: same
SOIC-8 pinout, -40~150 °C. Firmware formula: `amps = (Vout - 1.65) / 0.264`.

## Consequences

- The `/0.264` divisor is proven on hardware (2026-10-11): within +2.5 % over
  0-1.83 A, with ±0.04 A noise, so a 0.7 A stall sits about 30× above the noise floor.
- The stall threshold (1.4 A placeholder) **has never been validated**. It
  needs the real shade motors' measured stall current, which is a firmware
  setting, not a board change.
- A single rail sensor cannot attribute a fault to a channel or see one
  channel stall while others run. Rev 1.4 may move to per-channel sensing
  (ADR-018).
- Polyfuses respond in seconds while a driver dies in microseconds, so the
  fuse cannot protect the driver either. That gap is ADR-018's subject.
