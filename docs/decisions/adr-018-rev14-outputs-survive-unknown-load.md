# ADR-018: Rev 1.4's governing requirement: the outputs survive an unknown load

**Date:** 2026-09-03 (recorded retroactively 2026-10-12)
**Status:** Accepted (design direction; no driver chosen yet)

## Context

The shade motors are characterised and are not the design case. What
destroyed board 1's U8 was a **non-shade** motor on the bench: inrush sagged
`+12V_RAW`, the ESP32 browned out (ADR-008), the bridge shut off with energy
in the windings, and the flyback killed the driver. A general-purpose product
cannot know what gets plugged in, whether a stalled motor, the wrong motor, a
shorted lead or a large inductive load.

The current output stage cannot hold against that:

- TB6612FNG: VM absolute max is 15 V on a 12 V rail, 1.2 A continuous /
  3.2 A peak, and thermal shutdown is its only self-protection.
- D6-D9 (SMAJ15CA) clamp around 24 V, **above** the driver's absolute max.
- F1-F4 polyfuses act in seconds; the driver dies in microseconds.
- One rail-level current sensor cannot attribute a fault to a channel.

## Decision

Rev 1.4 is designed so the **output stage survives whatever is connected**,
not merely the known-good motors. The work items are in `docs/todo.md`
under "Rev 1.4 PCB Changes". The two that carry real design weight:

1. A driver with real current regulation and headroom (candidates: DRV8871,
   6.5-45 V with a resistor-set current limit; DRV8873, DRV8243), hard output
   short protection, clamping below the driver's absolute max, and
   per-channel current sense.
2. Hold-up for U1, so motor inrush cannot brown out the MCU (a series diode
   plus local bulk on U1's input, or a regulated isolated converter in U1's
   footprint).

Firmware soft-start is required regardless of hardware: never energize a
bridge at 100 % duty from rest.

The fuse stays the catastrophic backstop and the current reading stays the
stall protection (ADR-005).

## Consequences

- Rev 1.4 is a real design cycle, not a patch. Ride-along items: the net
  rename (ADR-012), test points silkscreened with their net names, and U7
  thermal.
- It does not block Rev 1.3 production (ADR-017).
