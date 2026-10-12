# ADR-017: Rev 1.3 goes to production as-is for the shade controller

**Date:** 2026-10-11 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

Motor-less bench bring-up of Rev 1.3 finished on 2026-10-11 on board 2 with
resistive loads. All four channels passed (singly and together, 1.93 A), as
did all eight switch inputs, the ACS725 calibration, the TMP235, every power
rail idle and loaded, and Tasmota driving all four shutters. Nothing found
needs copper for the shade-controller use case. Every open item is firmware
(debounce, soft-start, Tasmota switch inputs and stall detection) or the
motor test.

Board 1 lost its U8 to an unsuitable, non-shade test motor (bring-up Finding 6).
That is a robustness gap for unknown loads, not a defect with the shade motors.

## Decision

**Reorder Rev 1.3 as-is** when more boards are needed. No Rev 1.4 is required
for the shade controller. Rev 1.4 is for making the board general-purpose
(ADR-018).

## Consequences

- `release/v1.3` is the production line. `main` carries Rev 1.4 work (ADR-020).
- Before any motor goes on a Rev 1.3 board, measure the real shade motor's
  inrush and stall current against the TB6612FNG's 1.2 A continuous / 3.2 A
  peak rating. Bench loads are 20-33 Ω / 10 W resistors, never below 20 Ω.
- The firmware rules (ACS725 `/0.264`, pull-ups, terminal-named outputs,
  debounce, soft-start) carry the remaining risk, so they go in every config.
