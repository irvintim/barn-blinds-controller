# Architecture Decision Records

Short records of the significant design decisions on the VSP-WSC-4: the
context at the time, what was decided, and the consequences. They exist so a
settled question doesn't get re-litigated, and so the open ones are visible.

Rules:

- One ADR per genuine fork in the road. Routine choices don't get one.
- Accepted ADRs are immutable. If a decision changes, write a new ADR that
  supersedes the old one, and touch the old one only to update its Status line.
- Keep them short: context, decision, consequences.

ADR or living doc? Ask whether it will be wrong later or superseded. Decision
rationale is never wrong later, so it goes in an ADR. Content that will simply
be different later (the GPIO map, verified status, part stock) goes in
[`../architecture.md`](../architecture.md), which links back here.

ADR-002 to ADR-019 were back-filled on 2026-10-12. Their dates are when the
decision was made.

## Index

| ID | Title | Status | Date |
|---|---|---|---|
| [ADR-001](adr-001-record-architecture-decisions.md) | Record design decisions as ADRs | Accepted | 2026-10-12 |
| [ADR-002](adr-002-esp32-s3-wroom-1-n4.md) | ESP32-S3-WROOM-1-N4 (C2913197) is the module | Accepted | 2026-08-07 |
| [ADR-003](adr-003-dual-firmware-track.md) | Two firmware tracks: ESPHome for personal units, Tasmota for the product | Accepted | 2026-06 |
| [ADR-004](adr-004-functional-isolation.md) | Galvanic isolation between logic and motor domains, as a functional barrier | Accepted | 2026-04-17 |
| [ADR-005](adr-005-stall-protection-is-current-sensing.md) | Stall protection is the current reading, not the fuse | Accepted | 2026-04 |
| [ADR-006](adr-006-analog-sensors-on-adc1.md) | All analog sensing on ADC1 | Accepted | 2026-06-27 |
| [ADR-007](adr-007-switch-input-protection.md) | Wall-switch inputs: 1 kΩ series, RC, TVS on the MCU side, internal pull-ups only | Accepted | 2026-07-07 |
| [ADR-008](adr-008-usb-power-diode-or.md) | USB power diode-ORed into the single isolated logic rail | Accepted | 2026-06-30 |
| [ADR-009](adr-009-micro-usb.md) | Micro-USB instead of USB-C | Accepted | 2026-06-30 |
| [ADR-010](adr-010-native-usb-flash-path-j3-dnp.md) | Native USB is the flash path; J3 stays DNP | Accepted | 2026-08-07 |
| [ADR-011](adr-011-one-terminal-block-both-domains.md) | One 20-pin Phoenix 1786918 block carries motors and switches | Accepted | 2026-07-05 |
| [ADR-012](adr-012-channel-cross-fixed-in-firmware.md) | The Rev 1.3 motor channel cross is fixed in firmware; nets renamed in Rev 1.4 | Accepted | 2026-08-28 |
| [ADR-013](adr-013-tasmota-by-template.md) | Tasmota is configured by Template, not the Module page | Accepted | 2026-10-11 |
| [ADR-014](adr-014-shared-u1-footprint-no-assembly-remark.md) | One shared U1 footprint for three DC-DCs; no JLCPCB assembly remark | Accepted | 2026-08-07 |
| [ADR-015](adr-015-fab-spec.md) | Fab spec: 4-layer, ENIG, S1000H TG155 | Accepted | 2026-08-07 |
| [ADR-016](adr-016-release-branch-and-fab-tag.md) | Every fabbed revision gets a release branch and a frozen -fab tag | Accepted (extended by ADR-020) | 2026-08-27 |
| [ADR-017](adr-017-rev13-to-production-as-is.md) | Rev 1.3 goes to production as-is for the shade controller | Accepted | 2026-10-11 |
| [ADR-018](adr-018-rev14-outputs-survive-unknown-load.md) | Rev 1.4's governing requirement: the outputs survive an unknown load | Accepted (design direction; no driver chosen yet) | 2026-09-03 |
| [ADR-019](adr-019-enclosure-rev3-wall-and-din.md) | Enclosure Rev 3: wall keyholes and DIN rail from one box, sized for Rev 1.3 | Accepted | 2026-06-29 |
| [ADR-020](adr-020-repo-layout-and-branch-roles.md) | Repository layout, and main as the next-revision line | Accepted (extends ADR-016) | 2026-10-12 |

## Template

```markdown
# ADR-NNN: Title

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Superseded by ADR-XXX

## Context

## Decision

## Consequences
```
