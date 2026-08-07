# Barn Blinds Controller — Claude Context

## What this is
Vesprio VSP-WSC-4: 4-channel motorized window shade controller, ESP32-S3-WROOM-1-N4, dual firmware track (ESPHome personal use / Tasmota product). See `docs/project-context/vsp-wsc4-handover.md` for full hardware detail and GPIO map.

## Current state (as of 2026-08-05)
- **PCB:** Rev 1.3, **F8 sync from schematic is DONE** — D2 removed, D10/D11/U16 placed and routed, R1-R8/D1/C10/U11 values updated in place. DRC: **0 errors, 0 unconnected pads**, 114 footprints. Rev 1.2 was assembled and working (ESPHome only; Tasmota broken on Shades 3&4 due to GPIO43/44 = U0TX/RX conflict — fixed in Rev 1.3)
- **Schematic:** Rev 1.3 passed a full pre-fab QA review (2026-07-07) plus a second physical/layout QA pass (2026-08-05, see below). ERC errors down to 5, all benign (4× missing PWR_FLAG, 1× J2-GND/U1-(-Vout) both-power-output which is correct by design).
- **Also in Rev 1.3:** D4/D5 LEDs software-controllable (GPIO6/7, hardware-default-ON; D5 crosses isolation via spare U5 channel); RTS/DTR auto-reset on 7-pin J3 (Espressif reference two-transistor circuit); Micro-USB (not USB-C); switch inputs wired to ESP32 — see todo.md "Rev 1.3 GPIO Map" for pinout and "Firmware bring-up checklist" before first flash
- **Enclosure:** FreeCAD Rev 2 (`project-case-rev2.FCStd`), 3D printed, test print 2 in progress

## PICK UP HERE — remaining work before sending Rev 1.3 to JLCPCB
Schematic-side items from the 2026-08-05 QA pass are **done and committed**. What is left is all PCB/GUI work:

1. **Place C40-C43** (new, 100nF 0402, LCSC C1525) — TVS VCC decoupling, one per PRTR5V0U2X. They exist in `switch_inputs.kicad_sch` (bottom of sheet, ~Y=190) but have no board position yet. Run F8, then place **each within ~2mm of its device's VCC pin (pin 4)**: C40→U12, C41→U13, C42→U14, C43→U15. Reason: U12-U15 currently have their nearest +3.3V_ISO bypass **18-23mm away**; the PRTR5V0U2X shunts ESD into VCC and has nowhere local to dump it. This is the highest-value fix left — the switch inputs are new in Rev 1.3 and have never been validated on hardware.
2. **Widen `+5V_OR`** — 8.1mm of its 14mm run is 0.20mm (default signal width); the rest is 0.50mm. This is the ESP32's entire supply (500mA WiFi bursts). Bump to 0.50mm. Not a failure at 0.20mm (~1A capable, ~20mV drop) but it has no margin and is inconsistent with the other rails (+5V_ISO 0.50mm, +12V_RAW 1.00mm). Optional: `USB_VBUS` is 26.3mm all at 0.20mm — 0.40mm would be better.
3. **Move U16 closer to J2** — currently **9.2-9.4mm** from J2's D+/D- pads and on the opposite copper layer (U16 B.Cu / J2 F.Cu). Topology is right (it IS on the connector side of R9/R10, which sit 37mm away near the ESP32), but a 9mm stub plus a layer change badly undercuts ESD performance. Ideally sits directly under J2 on B.Cu.
4. **Decide J2 LCSC** — J2 (Micro-USB) has no LCSC part number. Hand-solder, or pick a part? J4 having no LCSC is intentional (pre-purchased inventory part).
5. Cosmetic: D11's reference field overlaps D10's silkscreen outline.

Then: regenerate gerbers/BOM/CPL (`docs/project-context/jlcpcb-export-steps.md`) — the `gerbers/` and `gerbers-v1.1/` folders are both stale (v1.1 era).

## Rev 1.3 schematic work already done
- ACS723 on GPIO5 (ADC1_CH4), TMP235 on GPIO4 (ADC1_CH3) — both moved off ADC2 to avoid WiFi noise, then relocated again during the layout-driven GPIO reshuffle (see full map in vsp-wsc4-todo.md)
- Terminal block J4: **Phoenix Contact 1786918** (20-pin dual-row 3.5mm, right-angle — cable exits sideways, not up); mating terminal block is 1790182; both ECAD/3D libraries committed in project-local `1786918/` and `1790182/` folders
  - Pinout (final, layout-driven): top row 1=SW1_UP, 2=GND_ISO, 3=SW2_UP, 4=SW3_UP, 5=GND_ISO, 6=SW4_UP, 7-10=SHADE1-4_UP; bottom row 11=SW1_DOWN, 12=GND_ISO, 13=SW2_DOWN, 14=SW3_DOWN, 15=GND_ISO, 16=SW4_DOWN, 17-20=SHADE1-4_DOWN (motors and switches connect across vertical pairs)
- `switch_inputs.kicad_sch` created (page 9): 8-channel RC+TVS protection, 4× PRTR5V0U2X + 8× **1kΩ R0603** (note: 0603, not 0402 as previously recorded here; LCSC C14676) + 8× 100nF C0402, plus **C40-C43** 100nF TVS VCC decoupling added 2026-08-05; wired through to ESP32 GPIOs (function-named labels, e.g. `SW1_UP_IN`, not raw pin numbers)
  - Topology is connector → **1k series R** → node shared by 100nF cap + PRTR5V0U2X I/O + ESP32 GPIO. The TVS is on the **MCU side** of the series resistor (R limits surge current into the TVS; TVS clamps right at the pin being protected). Note this is the opposite convention from U16 on USB, which sits on the *connector* side of R9/R10 — both are valid, just be aware they differ.
  - **No external pull-ups.** Switches pull to GND_ISO, so firmware MUST enable internal pull-ups on all 8. Two land on strapping pins: **GPIO46** (SW1_UP) and **GPIO3** (SW1_DOWN). Both verified safe — GPIO46 is input-only on the S3 and reads LOW at boot whether the switch is open (internal pull-down) or closed (tied to GND); GPIO3's JTAG-select default is unaffected.
- USB-C swapped to Micro-USB; native USB on GPIO19/20
- Smaller footprints for the tight terminal-block area: F1-F4 fuses 1812→1206 (1206L110/16NR), D6-D9 TVS SMBJ15CA→SMAJ15CA, C2 bulk cap electrolytic→ceramic (C11/C12 motor bulk caps intentionally left as-is)
- UART debug header (J3) moved from GPIO17/18 (U1TX/RX) to GPIO43/44 (U0TX/RX); GPIO43/44's prior signals relocated elsewhere in the GPIO reshuffle
- 1054070 library added to sym-lib-table and fp-lib-table
- All connection bugs fixed; schematic loads and connects correctly

Done in Rev 1.3 (previously listed here): D10/D11/U16 placement + F8 sync (all complete, verified 2026-08-05). RTS/DTR auto-reset (J3 grown to 7 pins, Q3/Q4 S8050 per Espressif reference, C21 1µF on EN; native USB auto-resets on its own — no hardware needed for that path). D4/D5 software-controllable LEDs (GPIO6/GPIO7 via Q1/Q2 2N7002, hardware-default-ON; D5 gate crosses the isolation barrier through spare U5 channel A; D5 feeds from +12V_RAW so its current bypasses the ACS725 measurement).

## Physical QA pass findings (2026-08-05)
Full geometric audit of the synced board. Everything here was **measured**, not eyeballed.

**Accepted as-is — inherited Rev 1.2 layout that is proven to work.** Do not "fix" these without a reason; the Rev 1.2 board shipped with them:
- ESP32 U3 pin 2 (3V3) → nearest cap C15 is **12.0mm** (C16 bulk 11.3mm). Loose for 500mA WiFi bursts, but proven.
- U2 (AP2112K): Cin C12 3.8mm, Cout C13/C14 5.2-5.5mm. Datasheet wants tighter.
- U1 (DC-DC) +5V_ISO out: C11 8.0mm, C10 8.7mm.
- +12V_RAW: only C9 (22µF) at 7.1mm from U1's input; **no HF bypass on the 12V rail at all**.
- Switch filter caps C1-C8 sit 3.4-5.9mm from their TVS — fine, position is not critical for a 1k/100nF low-pass (fc ≈ 1.6kHz).

**Isolation barrier — known and accepted, do not be alarmed by it.**
- Minimum ISO-to-MOTOR copper gap is **0.20mm** (= the global default clearance; there is no dedicated barrier). **Rev 1.2 measured the same 0.20mm**, so this is inherited, not a Rev 1.3 regression. Rev 1.3 roughly doubles the *number* of close approaches (222 → 506 under 2.5mm) because the 8 switch nets must cross the motor region to reach J4.
- This is fine because the whole system is **12V SELV** — the isolation is functional (noise / ground-loop rejection), not a safety barrier.
- It is partly unavoidable by design: **J4 deliberately carries both domains** (switch returns are GND_ISO on pins 2/5/12/15; SHADE pins are motor-side 12V; pins 6 and 7 are adjacent SW4_UP / SHADE1_UP). At 3.5mm pitch that is fine for 12V.
- The barrier-crossing parts are U1 (isolated DC-DC), U4/U5/U6 (digital isolators) and **U11 (ACS725 — a galvanically isolated Hall sensor, so its IP+/IP- on +12V_RAW with signal/supply on the ISO side is correct, not a bug)**.
- `barn-blinds-controller.kicad_dru` (committed) contains an audit rule for this. Severity is **warning** so it never blocks fab. Read its header comments before using it.

**KiCad gotcha worth remembering:** a `(condition "...")` in a `.kicad_dru` **must be on one line**. Multi-line parses without error but matches nothing — silently zero violations.

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
- `barn-blinds-controller.kicad_dru` — isolation-barrier audit DRC rule (warning severity)
- `project-case-rev2.FCStd` — current enclosure FreeCAD file

## Useful verification commands (kicad-cli 10.x, works headless)
```bash
kicad-cli sch erc  --output /tmp/erc.rpt --severity-error --severity-warning barn-blinds-controller.kicad_sch
kicad-cli pcb drc  --output /tmp/drc.rpt --severity-error barn-blinds-controller.kicad_pcb
kicad-cli sch export netlist --format kicadsexpr --output /tmp/net.net barn-blinds-controller.kicad_sch
kicad-cli sch export bom --fields "Reference,Value,Footprint,LCSC" --group-by Value --output /tmp/bom.csv barn-blinds-controller.kicad_sch
```
Diffing the netlist before/after an edit is the reliable way to prove connectivity was preserved — schematic geometry checks can miss pins whose position is far from the symbol origin.