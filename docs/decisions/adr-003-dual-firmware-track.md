# ADR-003: Two firmware tracks: ESPHome for personal units, Tasmota for the product

**Date:** 2026-06 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

The board serves two purposes. One is the owner's barn installation, which
lives in Home Assistant. The other is a possible Vesprio product, where buyers
expect a familiar open firmware with app onboarding and MQTT, and no build
toolchain.

## Decision

Maintain both:

- **ESPHome** (esp-idf framework) for personal installations: `barn-overhead`
  and `barn-windows`, plus the bench bring-up config.
- **Tasmota** (stock release binary plus a device Template, no Berry) is the
  product track, using the Shutter module with interlocked relay pairs.

The hardware has to be fully usable from both. A pin or feature that only
works under one of them is a hardware bug.

## Consequences

- Every firmware rule (ACS725 formula, pull-ups, channel swap per ADR-012,
  debounce, soft-start) has to be applied in both config sets.
- The Tasmota failure on Rev 1.2 (Shutters 3 and 4) was treated as a board
  problem, and fixing it was the main purpose of Rev 1.3. It is resolved on
  Rev 1.3 (ADR-013).
- Product-track work items include a hosted generic ESPHome factory image for
  users who migrate off Tasmota.
