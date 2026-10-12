# ADR-009: Micro-USB instead of USB-C

**Date:** 2026-06-30 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

Rev 1.2 used a USB-C receptacle (Kinghelm KH-TYPE-C-16P). `/dev/ttyACM0` only
enumerated in one cable orientation, which points to a CC1/CC2 asymmetry. The
port carries only USB 2.0 Full-Speed for flashing, plus 5 V.

## Decision

Use **Micro-USB** (LCSC C397452, footprint
`USB_Micro-B_XKB_U254-051T-4BH83-F1S`, the same part as `zen32-esphome`).
Micro-USB has no CC lines, so the orientation problem disappears along with
the CC pull-downs.

## Consequences

- One DRC `hole_clearance` exclusion at J2's own NPTH (0.20 vs 0.25 mm) is
  accepted. It is set by the connector's pad geometry and cannot be fixed
  without a different footprint.
- U16 (USB ESD) is on B.Cu and J2 on F.Cu, so D+/D- cross layers through a
  ~2 mm via stub on each side. That is acceptable for an occasional-use
  Full-Speed port. A proper fix moves U16 to F.Cu.
- The enclosure needs a Micro-USB cutout, not USB-C (ADR-019).
