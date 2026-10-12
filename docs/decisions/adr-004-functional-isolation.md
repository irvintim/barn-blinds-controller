# ADR-004: Galvanic isolation between logic and motor domains, as a functional barrier

**Date:** 2026-04-17 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

Four brushed shade motors on 12 V, switched by H-bridges, put inductive kicks
and ground bounce on the motor ground. The ESP32 needs a quiet ground for
WiFi and ADC readings, and the wall switches run back to it over long cable.

## Decision

Split the board into two domains, `GND_ISO` (ESP32, switches, sensors) and
`GND_MOTOR` (drivers, motors). Only these parts cross the barrier:

- **U1**, an isolated DC-DC (12 V → 5 V_ISO, unregulated)
- **U4/U5/U6**, ISO7760DBQ digital isolators, for every control line
- **U11**, the ACS725, a galvanically isolated Hall sensor: IP+/IP- on
  `+12V_RAW`, signal and supply on the ISO side

The barrier is **functional** (noise and ground-loop rejection), **not a
safety barrier**. The whole system is 12 V SELV.

## Consequences

- No dedicated creepage keep-out is required. The minimum ISO-to-MOTOR copper
  gap is the global 0.20 mm clearance, on Rev 1.2 and Rev 1.3 alike. Rev 1.3 has
  more close approaches (222 → 506 under 2.5 mm) because the switch nets
  cross the motor region to reach J4 (ADR-011).
- `barn-blinds-controller.kicad_dru` carries an audit rule for barrier
  clearance at **warning** severity, so it never blocks fab.
- Anything that needs power on the motor side gets it from the motor side.
  For example, U7 must never be fed from `+5V_ISO`.
- The motor-side status LED D5 is gated across the barrier through a spare
  U5 channel.
