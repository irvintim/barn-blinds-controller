# Barn Blinds Controller — Claude Context

## What this is
Vesprio VSP-WSC-4: 4-channel motorized window shade controller, ESP32-S3-WROOM-1-N4, dual firmware track (ESPHome personal use / Tasmota product). See `docs/project-context/vsp-wsc4-handover.md` for full hardware detail and GPIO map.

## Current state (as of 2026-07-07)
- **PCB:** Rev 1.3 routed and DRC-clean (silkscreen "rev: 1.3"); Rev 1.2 was assembled and working (ESPHome only; Tasmota broken on Shades 3&4 due to GPIO43/44 = U0TX/RX conflict — fixed in Rev 1.3)
- **Schematic:** Rev 1.3 passed a full pre-fab QA review (2026-07-07). Review-driven changes, schematic done: R1-R8 10k→1k (switch input logic levels), ACS723→ACS725 (3.3V-native current sensor, firmware formula change needed), D1 SS34→SS54 (5A, same SMA footprint), D2 BAT54C→D10/D11 SS34 pair (power-path OR diodes were undersized), U16 PRTR5V0U2X added (USB ESD), all missing LCSC BOM fields filled. **PCB placement still pending for D10/D11/U16** (D2 removal + 2×SMA + 1×SOT-143), then F8 sync — see "Pre-fab QA review changes" in `docs/project-context/vsp-wsc4-todo.md`
- **Also in Rev 1.3:** D4/D5 LEDs software-controllable (GPIO6/7, hardware-default-ON; D5 crosses isolation via spare U5 channel); RTS/DTR auto-reset on 7-pin J3 (Espressif reference two-transistor circuit); Micro-USB (not USB-C); switch inputs wired to ESP32 — see todo.md "Rev 1.3 GPIO Map" for pinout and "Firmware bring-up checklist" before first flash
- **Enclosure:** FreeCAD Rev 2 (`project-case-rev2.FCStd`), 3D printed, test print 2 in progress

## Rev 1.3 schematic work already done
- ACS723 on GPIO5 (ADC1_CH4), TMP235 on GPIO4 (ADC1_CH3) — both moved off ADC2 to avoid WiFi noise, then relocated again during the layout-driven GPIO reshuffle (see full map in vsp-wsc4-todo.md)
- Terminal block J4: **Phoenix Contact 1786918** (20-pin dual-row 3.5mm, right-angle — cable exits sideways, not up); mating terminal block is 1790182; both ECAD/3D libraries committed in project-local `1786918/` and `1790182/` folders
  - Pinout (final, layout-driven): top row 1=SW1_UP, 2=GND_ISO, 3=SW2_UP, 4=SW3_UP, 5=GND_ISO, 6=SW4_UP, 7-10=SHADE1-4_UP; bottom row 11=SW1_DOWN, 12=GND_ISO, 13=SW2_DOWN, 14=SW3_DOWN, 15=GND_ISO, 16=SW4_DOWN, 17-20=SHADE1-4_DOWN (motors and switches connect across vertical pairs)
- `switch_inputs.kicad_sch` created (page 9): 8-channel RC+TVS protection, 4× PRTR5V0U2X + 8× 10kΩ R0402 + 8× 100nF C0402; wired through to ESP32 GPIOs (function-named labels, e.g. `SW1_UP_IN`, not raw pin numbers)
- USB-C swapped to Micro-USB; native USB on GPIO19/20
- Smaller footprints for the tight terminal-block area: F1-F4 fuses 1812→1206 (1206L110/16NR), D6-D9 TVS SMBJ15CA→SMAJ15CA, C2 bulk cap electrolytic→ceramic (C11/C12 motor bulk caps intentionally left as-is)
- UART debug header (J3) moved from GPIO17/18 (U1TX/RX) to GPIO43/44 (U0TX/RX); GPIO43/44's prior signals relocated elsewhere in the GPIO reshuffle
- 1054070 library added to sym-lib-table and fp-lib-table
- All connection bugs fixed; schematic loads and connects correctly

## Rev 1.3 schematic work still needed
- **PCB placement/routing for the pre-fab review parts** (exact wiring below), then Update PCB from Schematic (F8). Everything else from the review was value/part-number-only on unchanged footprints — F8 updates those in place.

### Placement guide: D10, D11, U16 (the only 3 new footprints)
- **D2 (BAT54C, SOT-23) is deleted** — its board location near the USB/5V area frees up; D10/D11 replace its function.
- **D10 — SS34, SMA (D_SMA footprint):** anode → `USB_VBUS` net (J2 pin 1 / VBUS), cathode → `+5V_OR`. This is the USB-power leg of the OR.
- **D11 — SS34, SMA (D_SMA footprint):** anode → `+5V_ISO` (DC-DC U1 +Vout side, C10/C11 rail), cathode → `+5V_OR`. This is the main-power leg. **Both cathodes join on +5V_OR** which feeds U2 (AP2112K VIN+EN) and C12. Keep both on short, wide traces — this is the ESP32's entire supply path (WiFi bursts to ~500mA).
- **U16 — PRTR5V0U2X, SOT-143 (Package_TO_SOT_SMD:SOT-143):** pin 1 → `GND_ISO`, pin 2 (I/O1) → `USB_IN_DP`, pin 3 (I/O2) → `USB_IN_DN`, pin 4 (VCC) → `USB_VBUS`. Place tight against J2, on the connector side of the 22Ω series resistors (R9/R10), stubs as short as possible — same placement pattern as U12-U15 on the switch inputs.
- After F8: R1-R8 become 1k, D1 becomes SS54, C10 becomes 25V-rated, U11 becomes ACS725 — all same footprints, no moves needed. Verify DRC returns to 0/0.
- MANUAL: cosmetic TVS wire cleanup in `switch_inputs.kicad_sch` (annotation is done, just needs a tidy pass)

Done in Rev 1.3 (previously listed here): RTS/DTR auto-reset (J3 grown to 7 pins, Q3/Q4 S8050 per Espressif reference, C21 1µF on EN; native USB auto-resets on its own — no hardware needed for that path). D4/D5 software-controllable LEDs (GPIO6/GPIO7 via Q1/Q2 2N7002, hardware-default-ON; D5 gate crosses the isolation barrier through spare U5 channel A; D5 feeds from +12V_RAW so its current bypasses the ACS725 measurement).

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
| Terminal block header J4 (PCB) | Phoenix Contact 1786918 | in user's JLCPCB parts inventory (pre-purchased) | 20-pin dual-row 3.5mm right-angle THR; assembled by JLCPCB |
| Mating terminal block (wire side) | Phoenix Contact 1790182 | — (Mouser, user has stock) | plugs into J4, not board-mounted |
| DIN rail clip | Phoenix Contact USA 10 1201578 | — | Ordered 2026-06-29, screw-on |
| ESP32 module | ESP32-S3-WROOM-1-N4 | C2913202 | |
| DC-DC isolated | Heniper B1205S-3WR2L | C20622657 | |

## Key files
- `docs/project-context/vsp-wsc4-handover.md` — full Rev 1.2 hardware/firmware detail
- `docs/project-context/vsp-wsc4-todo.md` — full TODO list
- `motor_outputs.kicad_sch` — terminal block and motor output circuits
- `switch_inputs.kicad_sch` — new switch input protection circuit (Rev 1.3)
- `project-case-rev2.FCStd` — current enclosure FreeCAD file