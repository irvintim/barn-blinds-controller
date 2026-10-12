# ADR-015: Fab spec: 4-layer, ENIG, S1000H TG155

**Date:** 2026-08-07 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

The board lives in an attic (60-70 °C summers) and may become a product.
Rev 1.3 has SOT-143 TVS parts, many 0402s and the module's LGA thermal pad.

## Decision

Rev 1.3 order of record: 4-layer, 1 oz outer / 0.5 oz inner, **S1000H TG155
(JLC-4)**, **ENIG 1 µ"**, plugged vias, PCBA both sides, Confirm Parts
Placement and Photo Confirmation both on.

- **ENIG over HASL** for pad flatness on the fine-pitch parts and the LGA pad,
  and because it is RoHS, which the product track needs. Leaded HASL would be
  fine electrically.
- The laminate choice is settled. At ~70 °C operating, every option is far
  below its Tg.

## Consequences

- C33/C34 (1000 µF 25 V, C7471896) are the only electrolytics. They are
  already 105 °C / 2000 h parts, giving an estimated ~15-year attic life.
  Leave them. A same-can 5000 h part is free margin if stocked, but don't hold
  an order for it.
- Via-in-pad was resolved long ago by moving vias to pad edges. It is not an
  open fab question.
