# Barn Blinds Controller — Claude Context

## What this is
Vesprio VSP-WSC-4: 4-channel motorized window shade controller, ESP32-S3-WROOM-1-N4, dual firmware track (ESPHome personal use / Tasmota product). See `docs/project-context/vsp-wsc4-handover.md` for full hardware detail and GPIO map.

## Current state (as of 2026-07-06)
- **PCB:** Rev 1.2 assembled and working (ESPHome only; Tasmota broken on Shades 3&4 due to GPIO43/44 = U0TX/RX conflict — fixed in Rev 1.3 schematic)
- **Schematic:** Rev 1.3 in progress on branch `feature/new-inputs`; USB is now Micro-USB (not USB-C); switch inputs wired to ESP32; full GPIO reassignment done to avoid crossed leads on layout — see `docs/project-context/vsp-wsc4-todo.md` "Rev 1.3 GPIO Map" for the current pinout
- **Enclosure:** FreeCAD Rev 2 (`project-case-rev2.FCStd`), 3D printed, test print 2 in progress

## Rev 1.3 schematic work already done
- ACS723 on GPIO5 (ADC1_CH4), TMP235 on GPIO4 (ADC1_CH3) — both moved off ADC2 to avoid WiFi noise, then relocated again during the layout-driven GPIO reshuffle (see full map in vsp-wsc4-todo.md)
- Terminal block J3/J4: replaced JL271R-35008G01 (8-pin) with **Phoenix Contact 1054070** (20-pin dual-row, 3.5mm pitch, JLCPCB C20306292) in `motor_outputs.kicad_sch`; 3D model now included in the project-local `1054070/` library folder
  - Mating plug (wire side): 42mm W × 23.35mm L × 13.25mm H; header installed height 10mm above PCB; total mated stack 26.75mm above PCB
  - Pinout: pos 1-4 = motors M1-4, pos 5/7/8/10 = SW_UP, pos 6/9 = SW_COM (GND_ISO), pos 15/17/18/20 = SW_DOWN
- `switch_inputs.kicad_sch` created (page 9): 8-channel RC+TVS protection, 4× PRTR5V0U2X + 8× 10kΩ R0402 + 8× 100nF C0402; wired through to ESP32 GPIOs (function-named labels, e.g. `SW1_UP_IN`, not raw pin numbers)
- USB-C swapped to Micro-USB; native USB on GPIO19/20
- Smaller footprints for the tight terminal-block area: F1-F4 fuses 1812→1206 (1206L110/16NR), D6-D9 TVS SMBJ15CA→SMAJ15CA, C2 bulk cap electrolytic→ceramic (C11/C12 motor bulk caps intentionally left as-is)
- UART debug header (J3) moved from GPIO17/18 (U1TX/RX) to GPIO43/44 (U0TX/RX); GPIO43/44's prior signals relocated elsewhere in the GPIO reshuffle
- 1054070 library added to sym-lib-table and fp-lib-table
- All connection bugs fixed; schematic loads and connects correctly

## Rev 1.3 schematic work still needed
- **MANUAL:** Annotate refs (all show as R?/C?/U?), ERC, cosmetic TVS wire cleanup in `switch_inputs.kicad_sch`
- Add auto-reset circuit (2-transistor RTS/DTR for esptool)
- Make all LEDs software-controllable
- Fix test point copper (pads exist, no copper on Rev 1.2)
- Update silkscreen: revision → 1.3, copyright → 2026
- PCB layout: apply the schematic-only footprint swaps above (F1-F4, C2, D6-D9) and re-route to match the final GPIO map

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