# VSP-WSC-4 Architecture (living document)

Current state of the hardware and firmware. This file changes as the design
does; the *why* behind each choice is in [`decisions/`](decisions/README.md)
and is linked inline. Updated 2026-10-12.

## What it is

Vesprio VSP-WSC-4: a 4-channel motorized window-shade controller for 12 V
tubular shade motors (Rollerhouse ES2512 in the barn), with 8 wall-switch
inputs. ESP32-S3-WROOM-1-N4 ([ADR-002](decisions/adr-002-esp32-s3-wroom-1-n4.md)),
two TB6612FNG dual H-bridges, galvanic isolation between logic and motor sides
([ADR-004](decisions/adr-004-functional-isolation.md)). Two firmware tracks,
ESPHome and Tasmota ([ADR-003](decisions/adr-003-dual-firmware-track.md)).

## Revisions

| Rev | State | Notes |
|---|---|---|
| 1.0/1.1 | Retired | First build, 8-pin spring terminal block |
| 1.2 | Retired | Assembled and working under ESPHome; Tasmota Shutters 3/4 failed (cause: [ADR-013](decisions/adr-013-tasmota-by-template.md)). Detail: [`handover-rev1.2.md`](handover-rev1.2.md) |
| **1.3** | **Production** | Fabbed 2026-08-07, 5 boards. Motor-less bring-up complete 2026-10-11. Reorder as-is ([ADR-017](decisions/adr-017-rev13-to-production-as-is.md)). Branch `release/v1.3`, tag `v1.3-fab` |
| 1.4 | Open on `main` | Only needed to go general-purpose ([ADR-018](decisions/adr-018-rev14-outputs-survive-unknown-load.md)). Change list: [`todo.md`](todo.md) "Rev 1.4 PCB Changes" |

Branch and tag conventions: [ADR-016](decisions/adr-016-release-branch-and-fab-tag.md), [ADR-020](decisions/adr-020-repo-layout-and-branch-roles.md).

## Power

```
J1 12 V barrel ──D1 (SS54, series reverse-polarity)── +12V_RAW ──┬── U11 ACS725 (IP+/IP-) ── +12V ── C33/C34 2×1000 µF ── TB6612FNG VM
                                                                 │                                └── U7 AMS1117 ── +3.3V_MOTOR
                                                                 ├── D5 (blue LED, bypasses the ACS725)
                                                                 └── U1 B1205S isolated DC-DC (unregulated) ── +5V_ISO ──D11──┐
                                                      J2 Micro-USB VBUS ──────────────────────────────────────────────D10──┴── +5V_OR ── U2 AP2112K ── +3.3V_ISO
```

- U1 is **unregulated**: `+5V_ISO` ≈ 0.42 × `+12V_RAW`. The ESP32 browns out
  below ~8.5 V on `+12V_RAW` ([ADR-008](decisions/adr-008-usb-power-diode-or.md)).
- U1 footprint takes Mean Well / Heniper / Traco; Rev 1.3 uses Heniper on the
  `H` holes ([ADR-014](decisions/adr-014-shared-u1-footprint-no-assembly-remark.md)).
- Probing tip: J1 pin 1 → GND_MOTOR reads open even with a hard 12 V short,
  because D1 is in series. Probe at C33/C34.

## Firmware rules (every config, both tracks)

1. **Outputs are named for the physical J4 terminal** and use this map, not
   the net names ([ADR-012](decisions/adr-012-channel-cross-fixed-in-firmware.md)):

   | J4 shade | UP / DOWN | OPEN | CLOSED | PWM |
   |---|---|---|---|---|
   | SHADE1 | 7 / 17 | GPIO48 | GPIO47 | GPIO21 |
   | SHADE2 | 8 / 18 | GPIO36 | GPIO37 | GPIO38 |
   | SHADE3 | 9 / 19 | GPIO41 | GPIO40 | GPIO39 |
   | SHADE4 | 10 / 20 | GPIO42 | GPIO2 | GPIO1 |

   STBY is GPIO35 (both drivers, defaults off). The TB6612FNG needs PWM
   **high** to drive: at 0 % duty it sits in short brake, so a direction pin
   alone does nothing (bring-up Finding 8).
2. **Current:** `amps = (Vout - 1.65) / 0.264` on GPIO5, `attenuation: 12db`
   (proven within +2.5 %). Stall threshold: 1.4 A placeholder, set it from the
   measured motor stall current ([ADR-005](decisions/adr-005-stall-protection-is-current-sensing.md)).
3. **Temperature:** TMP235 on GPIO4, `(x - 0.5) / 0.01` °C. Reads U7's heat,
   not enclosure air.
4. **Switch inputs:** internal pull-ups on GPIO 3, 46, 9, 10, 11, 12, 13, 14,
   set GPIO46's explicitly. Software debounce is required, and no config has
   one yet ([ADR-007](decisions/adr-007-switch-input-protection.md)).
5. **LEDs:** D4 (GPIO6, white) and D5 (GPIO7, blue) are on until firmware
   drives them LOW. D3 status LED is GPIO16.
6. **Soft-start:** never energize a bridge at 100 % from rest. Not yet
   implemented anywhere.
7. **Tasmota:** apply the Template, never the Module page ([ADR-013](decisions/adr-013-tasmota-by-template.md)).

Wall-switch and motor wiring on J4: [ADR-011](decisions/adr-011-one-terminal-block-both-domains.md).
Full module-pin table (net names): [`todo.md`](todo.md) "Rev 1.3 GPIO Map".

## Flashing

Native USB on J2 (GPIO19/20) only, since J3 is DNP ([ADR-010](decisions/adr-010-native-usb-flash-path-j3-dnp.md)).
A blank board boot-loops with clean enumeration every ~2.7 s and no `dmesg`
errors. That is normal: flash it. Triage table:
[`bringup/vsp-wsc4-rev13-bringup-procedure.md`](bringup/vsp-wsc4-rev13-bringup-procedure.md).
A browser tab holding the port (Web Serial) gives `[Errno 16] busy`;
`lsof /dev/ttyACM0` finds it.

## Rev 1.3 as built

- Order of record: [ADR-015](decisions/adr-015-fab-spec.md). Fab files: `pcb/main-board/fab/vsp-wsc4-rev1.3/`.
  Outline 65.004 × 73.935 mm, 106 placements, 40 BOM lines.
- Stock substitutions at order time, same footprints: C10 = 100 µF 16 V
  (C7432790); U12-U16 = C5158049. When substituting PRTR5V0U2X-class parts,
  verify bidirectional + ~5 V working voltage, because several LCSC listings
  under that name are not.
- J3 DNP (wrong 5-pin LCSC C492404 still on it).
- Boards: 1 = U8 destroyed (repairable), 2 = `barn-overhead`, 3 =
  `barn-windows`, 4-5 unopened. Live detail:
  [`bringup/vsp-wsc4-rev13-bringup-status.md`](bringup/vsp-wsc4-rev13-bringup-status.md).

## Accepted layout margins (inherited from Rev 1.2, proven in service)

Do not "fix" these without a reason:

- U3 3V3 pin → nearest cap 12.0 mm (C15); U2 caps 3.8-5.5 mm; U1 output caps
  8.0-8.7 mm; `+12V_RAW` has only C9 (22 µF) at 7.1 mm and no HF bypass.
- ISO-to-MOTOR minimum copper gap 0.20 mm ([ADR-004](decisions/adr-004-functional-isolation.md)).
- J2 NPTH `hole_clearance` exclusion and the U16 via stub ([ADR-009](decisions/adr-009-micro-usb.md)).
- Vias: of 177, 104 have their centre over a pad, but these are pushed to pad
  edges, or sit on large pads, or on 0402s with as much clearance as the
  geometry allows. Via-in-pad is closed. Do not repeat the old
  "96 of 177 in pads" figure.
- Switch filter caps 3.4-5.9 mm from their TVS (position not critical at
  fc ≈ 1.6 kHz).
- 37 `endpoint_off_grid` ERC warnings come from the `Device:C` symbol variant
  and are cosmetic. ERC errors hold at 5, all benign (4× missing PWR_FLAG,
  J2-GND/U1 -Vout both power outputs, which is correct).

## Thermal (attic)

- Module rated 85 °C ambient ([ADR-002](decisions/adr-002-esp32-s3-wroom-1-n4.md)).
  The enclosure keeps its ventilation ([ADR-019](decisions/adr-019-enclosure-rev3-wall-and-din.md)).
- U7 (AMS1117) is the hot spot, +19 °F over ambient at idle. Within rating; a
  Rev 1.4 nice-to-have.
- C33/C34 are 105 °C / 2000 h, ~15-year estimated attic life ([ADR-015](decisions/adr-015-fab-spec.md)).

## Tooling

- KiCad 10 (Windows install; from WSL use
  `"/mnt/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"`, run from
  `pcb/main-board/`, and pass Windows paths via `wslpath -w` for output files).
- The PCB's ESP32 3D model path uses `${KICAD8_3RD_PARTY}`, which KiCad 10's
  CLI does not define. The model is at
  `C:/Users/irvin/Documents/KiCad/10.0/3dmodels/espressif.3dshapes/`.
- `kicad-cli sch export netlist` is **not read-only**: it has rewritten
  `usb-c-5v.kicad_sch` and the `.kicad_pro` before. Run `git status` after any
  kicad-cli call.
- A `.kicad_dru` `(condition "...")` must be on **one line**. Multi-line
  parses without error and matches nothing.
- FreeCAD for the enclosure. ESPHome builds on a Docker dashboard (bring-up
  Finding 9).
