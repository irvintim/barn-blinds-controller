# VSP-WSC-4 Project TODO Lists

## Rev 1.3 PCB Changes

### Already done in schematic:
- [x] ACS723 moved to GPIO10 (ADC1_CH9)
- [x] TMP235 moved to GPIO7 (ADC1_CH6)
- [x] Terminal block J3: replaced JL271R-35008G01 (8-pin) with Phoenix Contact 1054070 (20-pin dual-row, 3.5mm pitch, JLCPCB C20306292) in motor_outputs.kicad_sch
- [x] Pinout: pos 1-4 = motors M1-4, pos 5/7/8/10 = SW_UP, pos 6/9 = SW_COM (GND_ISO), pos 15/17/18/20 = SW_DOWN
- [x] switch_inputs.kicad_sch created (page 9): 8-ch RC+TVS, 4× PRTR5V0U2X + 8× 10kΩ + 8× 100nF
- [x] All schematic connection bugs fixed; loads and connects correctly
- [x] USB connector swapped from USB-C (Kinghelm KH-TYPE-C-16P) to Micro-USB in usb-c-5v.kicad_sch — same part/footprint/LCSC (C397452) as used in ../zen32-esphome; removes the CC1/CC2 orientation issue entirely (Micro-USB has no CC lines); CC pulldowns R1/R4 removed; verified via kicad-cli ERC/netlist (2026-06-30)
- [x] Decided to leave USB power diode-ORed into the single shared 3.3V_ISO rail (powers ESP32 + isolators/sensors) rather than adding a second regulator — see project memory for reasoning (2026-06-30)

### Still needed — schematic (do these first):
- [ ] MANUAL: Annotate all refs in switch_inputs.kicad_sch (currently R?/C?/U?), run ERC, cosmetic TVS wire cleanup
- [ ] MANUAL: Annotate new J2 (Micro-USB) reference and new #PWR? GND_ISO symbol in usb-c-5v.kicad_sch, cosmetic wire cleanup (new wiring was placed programmatically, needs a tidy pass in the GUI)
- [ ] esp32-s3.kicad_sch: add GPIO4/5/6/8/9/11/12/13 as switch inputs; remap GPIO43→GPIO1, GPIO44→GPIO3 for motors; assign GPIO43=U0TXD, GPIO44=U0RXD
- [ ] Fix UART header: U1TX/U1RX (GPIO17/18) → U0TX/U0RX (GPIO43/44)
- [ ] PCB footprint: swap J2 footprint from KINGHELM_KH-TYPE-C-16P to Connector_USB:USB_Micro-B_XKB_U254-051T-4BH83-F1S on the board layout (barn-blinds-controller.kicad_pcb still has the old footprint — schematic-only change so far)
- [ ] Add auto-reset circuit (two transistors + resistors on RTS/DTR lines for reliable flashing)
- [ ] Make all LEDs software-controllable (status LED, 12V power LED, ESP32 power LED)
- [ ] Fix test point copper (pads present but no copper on Rev 1.2 boards)
- [ ] Update silkscreen revision to 1.3
- [ ] Update silkscreen copyright year

---

## Product Track TODO (Vesprio WSC-4)

### Firmware:
- [ ] Test and validate Tasmota firmware on Rev 1.2 board
- [ ] Validate Berry script motor control
- [ ] Validate Shutter module with 4 shades
- [ ] Test Bluetooth onboarding via Tasmota app
- [ ] Test Home Assistant auto-discovery via MQTT
- [ ] Document open/close duration calibration procedure for end users
- [ ] Submit device template to Tasmota templates repository (templates.blakadder.com)
- [ ] Build and host generic ESPHome factory .bin for OTA migration from Tasmota
- [ ] Set up firmware.vesprio.io hosting for OTA binary

### Hardware:
- [ ] Finalize Rev 1.3 PCB with auto-reset circuit (required for end-user flashing/recovery)
- [ ] Enclosure Rev 3 redesign (see below)
- [ ] Source production enclosure (3D print vs injection mold vs off-shelf)
- [ ] Decide on packaging

---

## Enclosure Rev 3 TODO (decided 2026-06-29)

Goal: support two mounting options from one enclosure — wall mount (keyholes) and DIN rail mount.

**DIN rail clip:** Phoenix Contact USA 10 (1201578) — ordered 2026-06-29
- Snaps onto 35mm TS 35 rail, attaches to enclosure back with 3× M3 self-cutting screws
- Hole pattern: Ø2.75mm, 25mm center-to-center spacing (50mm total span), 3 holes in a line
- Clip is 43mm L × 27.5mm H × 7.4mm deep — adds only 7.4mm to enclosure depth

**FreeCAD changes needed in project-case-rev2.FCStd:**
- [ ] Increase Z height to accommodate 26.75mm mated terminal block (header 13.5mm + plug 13.25mm)
- [ ] Move USB (now Micro-USB, not USB-C — see Rev 1.3 schematic changes above) cutout from DIN-rail-side wall to top or bottom edge
- [ ] Move status LED cutouts accordingly
- [ ] Add 3× Ø2.75mm boss holes on back plate for DIN clip (25mm spacing)
- [ ] Keep existing wall-mount keyholes on back plate

### Documentation:
- [ ] Quick start guide (hardware install + app onboarding)
- [ ] Motor calibration guide (how to set open/close timing)
- [ ] Home Assistant integration guide (MQTT + ESPHome upgrade path)
- [ ] FCC/CE compliance research (required for marketplace sales)

### Business/Marketing:
- [ ] Product page on Vesprio.io
- [ ] Product photography
- [ ] Pricing research (BOM cost + enclosure + margin)
- [ ] Decide on marketplace (Etsy, Tindie, own store)
- [ ] Determine minimum viable batch size
- [ ] Research FCC Part 15 requirements for WiFi devices sold in US
