# Barn Blinds Controller — Claude Context

## What this is
Vesprio VSP-WSC-4: 4-channel motorized window shade controller, ESP32-S3-WROOM-1-N4, dual firmware track (ESPHome personal use / Tasmota product). See `docs/project-context/vsp-wsc4-handover.md` for full hardware detail and GPIO map.

## Current state (as of 2026-06-29)
- **PCB:** Rev 1.2 assembled and working (ESPHome only; Tasmota broken on Shades 3&4 due to GPIO43/44 = U0TX/RX conflict)
- **Schematic:** Rev 1.3 in progress on branch `feature/new-inputs`
- **Enclosure:** FreeCAD Rev 2 (`project-case-rev2.FCStd`), 3D printed, test print 2 in progress

## Rev 1.3 schematic work already done
- ACS723 moved to GPIO10 (ADC1_CH9), TMP235 moved to GPIO7 (ADC1_CH6)
- Terminal block J3: replaced JL271R-35008G01 (8-pin) with **Phoenix Contact 1054070** (20-pin dual-row, 3.5mm pitch, JLCPCB C20306292) in `motor_outputs.kicad_sch`
  - Mating plug (wire side): 42mm W × 23.35mm L × 13.25mm H; header installed height 10mm above PCB; total mated stack 26.75mm above PCB
  - Pinout: pos 1-4 = motors M1-4, pos 5/7/8/10 = SW_UP, pos 6/9 = SW_COM (GND_ISO), pos 15/17/18/20 = SW_DOWN
- `switch_inputs.kicad_sch` created (page 9): 8-channel RC+TVS protection, 4× PRTR5V0U2X + 8× 10kΩ R0402 + 8× 100nF C0402
- 1054070 library added to sym-lib-table and fp-lib-table
- All connection bugs fixed; schematic loads and connects correctly

## Rev 1.3 schematic work still needed
- **MANUAL:** Annotate refs (all show as R?/C?/U?), ERC, cosmetic TVS wire cleanup in `switch_inputs.kicad_sch`
- `esp32-s3.kicad_sch`: add GPIO4/5/6/8/9/11/12/13 as switch inputs; remap GPIO43→GPIO1, GPIO44→GPIO3 for motors; assign GPIO43=U0TXD, GPIO44=U0RXD
- Fix UART header: U1TX/U1RX (GPIO17/18) → U0TX/U0RX (GPIO43/44)
- USB-C CC1/CC2 fix (only works in one orientation — likely missing pull-down)
- Add auto-reset circuit (2-transistor RTS/DTR for esptool)
- Make all LEDs software-controllable
- Fix test point copper (pads exist, no copper on Rev 1.2)
- Update silkscreen: revision → 1.3, copyright → 2026

## Enclosure Rev 3 direction (decided 2026-06-29)
Redesign the 3D printed box to support **two mounting options**:
1. **Existing wall-mount keyholes** — keep as-is on back plate
2. **DIN rail mount** — Phoenix Contact USA 10 (1201578) clip, snaps onto 35mm TS 35 DIN rail

**DIN clip mounting (1201578):**
- 3× M3 self-cutting screws, Ø2.75mm holes, 25mm center-to-center spacing (50mm total span)
- Clip is 43mm long × 27.5mm tall × 7.4mm deep (adds only 7.4mm to enclosure depth)
- Add 3 boss holes on back plate to match

**Other enclosure changes needed:**
- Make taller (Z) to fit 26.75mm mated terminal block height (currently ~25mm deep)
- Move USB-C from DIN-rail-side wall to top or bottom edge
- Move LEDs accordingly
- Terminal block cutout stays on same face, same orientation — no PCB layout change needed for it

## Key parts
| Part | PN | JLCPCB | Notes |
|------|----|--------|-------|
| Terminal block header (PCB) | Phoenix Contact 1054070 | C20306292 | 20-pin dual-row 3.5mm THR |
| DIN rail clip | Phoenix Contact USA 10 1201578 | — | Ordered 2026-06-29, screw-on |
| ESP32 module | ESP32-S3-WROOM-1-N4 | C2913202 | |
| DC-DC isolated | Heniper B1205S-3WR2L | C20622657 | |

## Key files
- `docs/project-context/vsp-wsc4-handover.md` — full Rev 1.2 hardware/firmware detail
- `docs/project-context/vsp-wsc4-todo.md` — full TODO list
- `motor_outputs.kicad_sch` — terminal block and motor output circuits
- `switch_inputs.kicad_sch` — new switch input protection circuit (Rev 1.3)
- `project-case-rev2.FCStd` — current enclosure FreeCAD file