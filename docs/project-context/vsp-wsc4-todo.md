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
- [x] Swapped C2 (isolated 5V bulk cap) from 100uF electrolytic (CP_Elec_6.3x5.4) to 100uF 10V ceramic (C_1210_3225Metric) in power_input.kicad_sch — C11/C12 (1000uF/25V motor rail bulk caps) intentionally left as electrolytic (2026-07-05)
- [x] Swapped F1-F4 fuses from 1812 (Polyfuse mSMD110, 24V) to 1206 (1206L110/16NR, 16V, LCSC C7542961) in motor_outputs.kicad_sch — same 1.1A hold/2.2A trip rating, smaller footprint to clear the narrower 1054070 terminal block gap (2026-07-05)
- [x] Swapped D6-D9 TVS diodes from SMBJ15CA (SMB) to SMAJ15CA (SMA, LCSC C223985) in motor_outputs.kicad_sch — same 15V standoff/24.4V clamp, smaller footprint (2026-07-05)
- [x] Fixed 1054070 terminal block library: added missing 3D STEP model to the project-local `1054070/` library folder (`1054070/3D/1054070.stp`), fixed the model path in `1054070/KiCad/1054070.kicad_mod` to use `${KIPRJMOD}` so it resolves on any machine (2026-07-05)
- [x] esp32-s3.kicad_sch: wired GPIO4/5/6/8/9/11/12/13 as switch inputs (previously only existed as orphaned labels in switch_inputs.kicad_sch, never reaching the MCU); renamed switch_inputs.kicad_sch labels from pin-number style (`GPIO4`...) to function names (`SW1_UP_IN`...) (2026-07-05)
- [x] Fixed a mislabeled net: GPIO35/36 were both wired as `ISO_SH2_CLOSED`/`ISO_SH2_OPEN` (duplicate of the real Shade 2 pins), leaving `ISO_SH1_CLOSED`/`ISO_SH1_OPEN` orphaned — corrected to reference Shade 1 (2026-07-05)
- [x] Fixed UART header: moved J3 (debug header) from GPIO17/U1TXD, GPIO18/U1RXD to GPIO43/U0TXD, GPIO44/U0RXD; freed GPIO43/44 by moving what was on them elsewhere (2026-07-05)
- [x] Full Rev 1.3 GPIO reassignment completed to eliminate crossed leads during layout — see "Rev 1.3 GPIO Map" below for the final pinout (2026-07-06)
- [x] Annotated all refs in switch_inputs.kicad_sch and usb-c-5v.kicad_sch — zero unannotated (R?/C?/U?) refs remain in either sheet (confirmed 2026-07-06)
- [x] PCB footprint: J2 swapped to Connector_USB:USB_Micro-B_XKB_U254-051T-4BH83-F1S on the actual board layout (2026-07-06)
- [x] PCB layout: F1-F4 (Fuse_1206_3216Metric), C2 (C_1210_3225Metric), D6-D9 (D_SMA) footprint swaps present on barn-blinds-controller.kicad_pcb; C11/C12 correctly still CP_Elec_10x10.5 (2026-07-06)
- [x] PCB fully routed and re-routed to match the final Rev 1.3 GPIO map; DRC clean (only 4 non-blocking `lib_footprint_mismatch` warnings on U4/U5/U6/U10 — local footprint edits differ from library copy, zero errors, zero unconnected pads) (2026-07-06)
- [x] Update silkscreen revision to 1.3 (confirmed on board: "rev: 1.3") (2026-07-06)
- [x] Update silkscreen copyright year (confirmed on board: "© Vesprio.io 2026") (2026-07-06)
- [x] Fixed test point copper — removed the TestPoint footprint that was suppressing solder mask over the TP pads; copper now renders correctly in 3D view (2026-07-06)

### Still needed — schematic:
- [ ] **Auto-reset circuit — needs a research/discussion pass next session before any hardware decision. Do not add circuitry yet.**
  - Goal: let esptool/ESPHome/Tasmota flash and reset the board without the user manually holding BOOT and tapping RESET.
  - Board has two flashing paths by design: native Micro-USB (GPIO19/20, USB-Serial-JTAG peripheral) and a 5-pin UART header J3 (`U0TXD`, `U0RXD`, `+3.3V_ISO`, `GND_ISO`, `BOOT`/GPIO0 — no RTS/DTR pins currently). Board also has physical BOOT and RESET buttons (SW2, SW1) for manual flashing.
  - **Open question raised 2026-07-06:** the user's own TTY/USB bridge adapter has no RTS/DTR pins — they only ever connect RX/TX/3.3V/GND and manually ground BOOT, using the existing buttons. They haven't encountered the RTS/DTR auto-reset workflow before and want to understand it better before deciding whether to add any circuitry (transistors, and/or expanding J3 to 7 pins to expose RTS/DTR for adapters that do have them).
  - Next session should: explain how the classic RTS/DTR auto-reset handshake works and why/when it matters (e.g. relevant mainly for the product track, where random customers' adapters — many common FTDI/CP2102/CH340 boards — do expose RTS/DTR, vs. the user's personal dev adapter which doesn't need it since buttons already work); confirm whether the native USB path already auto-resets on its own (untested so far); then let the user decide whether J3 needs to grow to 7 pins at all, given the answer may simply be "no, buttons are fine."
- [ ] **Make D4 (ESP32 power, white) and D5 (12V power, blue) LEDs software-controllable — confirmed in scope for Rev 1.3, next session should implement this.**
  - Current state: D3 (status, red) is already GPIO16-driven — that one's done.
  - D4 is hardwired directly to `+3.3V_ISO` via R_LED2 (always on whenever 3.3V rail is up) — needs a GPIO-driven switch (transistor/MOSFET or direct GPIO drive through the LED resistor, whichever this design's LED drive convention already uses for D3) instead of a direct tie to the rail.
  - D5 is hardwired directly to `+12V` via R_LED3 (always on whenever 12V input is present) — same fix needed, referenced to `GND_MOTOR` since it's on the motor-side rail.
  - Free GPIOs available per the Rev 1.3 GPIO map below: GPIO6, GPIO7, GPIO8, GPIO15, GPIO17, GPIO18, GPIO45 (note GPIO45 is a strapping pin, only use it if the strapping behavior is confirmed harmless the way it was for other signals sharing it before).
- [ ] MANUAL: cosmetic TVS wire cleanup in switch_inputs.kicad_sch (still worth a tidy pass even though annotation is done)

---

## Rev 1.3 GPIO Map (final, as of 2026-07-06)

Reassigned to eliminate crossed leads during PCB layout. Verified against the ESP32-S3-WROOM-1 module pinout with no duplicate assignments, no WiFi/ADC2 conflicts (only TMP235/ACS723 do real analog sensing, both on ADC1), and no strapping-pin or input-only-pin misuse.

| Pin | GPIO | Function | Notes |
|---|---|---|---|
| 3 | EN | Reset button | |
| 4 | GPIO4 | TMP235 Vout | ADC1_CH3 |
| 5 | GPIO5 | ACS723 VIOUT | ADC1_CH4 |
| 6 | GPIO6 | *(empty)* | |
| 7 | GPIO7 | *(empty)* | |
| 8 | GPIO15 | *(empty)* | |
| 9 | GPIO16 | Status LED | |
| 10 | GPIO17 | *(empty)* | freed from old UART header |
| 11 | GPIO18 | *(empty)* | freed from old UART header |
| 12 | GPIO8 | *(empty)* | |
| 13 | GPIO19 | USB D- | native USB |
| 14 | GPIO20 | USB D+ | native USB |
| 15 | GPIO3 | SW1_DOWN_IN | switch input |
| 16 | GPIO46 | SW1_UP_IN | switch input — input-only pin, OK for a switch |
| 17 | GPIO9 | SW2_DOWN_IN | switch input |
| 18 | GPIO10 | SW2_UP_IN | switch input |
| 19 | GPIO11 | SW3_DOWN_IN | switch input |
| 20 | GPIO12 | SW3_UP_IN | switch input |
| 21 | GPIO13 | SW4_DOWN_IN | switch input |
| 22 | GPIO14 | SW4_UP_IN | switch input |
| 23 | GPIO21 | ISO_SH2_PWM | to isolator U6 |
| 24 | GPIO47 | ISO_SH2_CLOSED | to isolator U6 |
| 25 | GPIO48 | ISO_SH2_OPEN | to isolator U6 |
| 26 | GPIO45 | *(empty)* | strapping pin (VDD_SPI voltage) — deliberately left free |
| 27 | GPIO0 | BOOT | strapping pin |
| 28 | GPIO35 | ISO_STBY | to isolator U6 |
| 29 | GPIO36 | ISO_SH1_OPEN | to isolator U6 |
| 30 | GPIO37 | ISO_SH1_CLOSED | to isolator U6 |
| 31 | GPIO38 | ISO_SH1_PWM | to isolator U5 |
| 32 | GPIO39 | ISO_SH4_PWM | to isolator U4 |
| 33 | GPIO40 | ISO_SH4_CLOSE | to isolator U4 |
| 34 | GPIO41 | ISO_SH4_OPEN | to isolator U4 |
| 35 | GPIO42 | ISO_SH3_OPEN | to isolator U4 |
| 36 | GPIO44 | U0RXD | debug/UART header J3 |
| 37 | GPIO43 | U0TXD | debug/UART header J3 |
| 38 | GPIO2 | ISO_SH3_CLOSED | to isolator U4 — unchanged, not part of this reshuffle |
| 39 | GPIO1 | ISO_SH3_PWM | to isolator U4 — unchanged, not part of this reshuffle |

GND (pins 1, 40, 41) and 3V3 (pin 2) not listed above.

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
