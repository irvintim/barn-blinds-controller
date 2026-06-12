# VSP-WSC-4 Window Shade Controller — Project Handover

## Project Overview

Vesprio VSP-WSC-4 is a 4-channel motorized window shade controller built around the ESP32-S3-WROOM-1-N4. It controls Rollerhouse ES2512 tubular motors via two TB6612FNG H-bridge drivers, with digital isolation (ISO7760DBQ) between the ESP32 logic side and the motor power side. The board is Rev 1.2, assembled by JLCPCB.

There are two parallel firmware tracks:
- **ESPHome** — personal installation in barn, fully working
- **Tasmota** — product/marketplace track, partially working (see status below)

---

## Hardware

### Board: VSP-WSC-4 Rev 1.2

**Power:**
- Input: 12V DC, 3A, center positive, 2mm barrel jack (DC005-T20, JLCPCB C111567)
- DC-DC converter: Heniper B1205S-3WR2L (JLCPCB C20622657), 12V→5V isolated
- LDO: AP2112K-3.3, 5V→3.3V for ESP32 side
- Two ground domains: GND_ISO (ESP32/logic), GND_MOTOR (motor power)

**MCU:** ESP32-S3-WROOM-1-N4 (4MB flash, no PSRAM)

**Motor drivers:** 2x TB6612FNG, each driving 2 motors
- U8: Shades 1 & 2
- U9: Shades 3 & 4

**Digital isolators:** 3x ISO7760DBQ (U4, U5, U6)

**Sensors:**
- ACS723LLCTR-05AB current sense (GPIO14, ADC2_CH3) — NOTE: move to GPIO10/ADC1_CH9 in Rev 1.3
- TMP235 temperature sensor (GPIO15, ADC2_CH4) — NOTE: move to GPIO7/ADC1_CH6 in Rev 1.3

**LEDs:**
- D8: ESP32 power/status LED (GPIO16, red, 330R)
- D9: 12V power LED (blue, 1.8K to GND_MOTOR)
- D3: Status LED (GPIO16 driven, red)

### Confirmed GPIO Map

| GPIO | Function | Notes |
|------|----------|-------|
| GPIO2 | Shade 1 close (M2_BIN2) | |
| GPIO14 | ACS723 VIOUT | ADC2_CH3, WiFi noise risk |
| GPIO15 | TMP235 Vout | ADC2_CH4, WiFi noise risk |
| GPIO16 | Status LED | Active high |
| GPIO17 | UART TX (U1TXD) | On UART header J4 |
| GPIO18 | UART RX (U1RXD) | On UART header J4 |
| GPIO19 | USB D- | |
| GPIO20 | USB D+ | |
| GPIO35 | Shade 3 close (M3_AIN2) | Red/PSRAM warning — safe on N4 |
| GPIO36 | Shade 3 open (M3_AIN1) | Red/PSRAM warning — safe on N4 |
| GPIO37 | STBY (TB6612 standby) | Must be HIGH for motors to run |
| GPIO38 | Shade 4 open (M4_BIN1) | |
| GPIO39 | Shade 4 close (M4_BIN2) | |
| GPIO42 | Shade 2 close (M1_AIN2) | |
| GPIO43 | Shade 2 open (M1_AIN1) | U0TXD — conflicts with serial console in Tasmota |
| GPIO44 | Shade 1 open (M2_BIN1) | U0RXD — conflicts with serial console in Tasmota |

**UART header J4 (Conn_01x05):**
Pin 1=TX, 2=RX, 3=3.3V, 4=GND, 5=GPIO0 (BOOT)
Note: Connected to U1TX/U1RX not U0TX/U0RX — this is a known bug for Rev 1.3.

---

## ESPHome Firmware (Personal Track)

**Status: Fully working on dedicated board**

**File:** `barn-shades-pcb.yaml`

Key config notes:
- Framework: esp-idf (required for ESP32-S3 in ESPHome 2026.x)
- STBY set HIGH at on_boot, stays permanently HIGH
- Stall detection threshold: 1.4A (after ACS723 voltage-to-amps conversion)
- ACS723 formula: `(x - 1.65) / 0.4` (zero current = 1.65V, 400mV/A sensitivity)
- TMP235 formula: `(x - 0.5) / 0.01` (500mV at 0C, 10mV/C)
- Open/close durations: 60s placeholder — update after motor timing calibration
- device_class: current on motor sensor
- attenuation: 12db (not 11db)
- Group buttons use 200ms stagger between cover.control calls

**Known ADC2 issue:** GPIO14/15 are on ADC2 which can have noise when WiFi is active. Watch for false stall triggers. Rev 1.3 moves these to ADC1.

---

## Tasmota Firmware (Product Track)

**Status: Shutters 1 & 2 working, Shutters 3 & 4 not working**

**Root cause of Shutters 3 & 4 failure:**
GPIO43 (Shade 2 open) and GPIO44 (Shade 1 open) are U0TX/U0RX. Tasmota's serial console holds these pins even with SerialLog 0 and SetOption65 1. They cannot be used as relay outputs while Tasmota serial is active.

Workaround attempted: SetOption65 1 — partial improvement but pins still not reliably driven.

**Files:**
- `tasmota-autoexec.be` — Berry script (STBY control only, motor GPIOs driven by Tasmota relay system)
- `tasmota-setup-commands.txt` — full setup command sequence
- `vsp-wsc4-standalone.yaml` — ESPHome standalone config for product use

**Confirmed working Tasmota template (35-position array, skips GPIO22-32):**
```json
{"NAME":"Vesprio WSC-4","GPIO":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,416,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,225,224,0,0,0],"FLAG":0,"BASE":1}
```
Note: Template array positions 22+ correspond to GPIO33+ (skipping GPIO22-32 which are internal/reserved on ESP32-S3).

**Working relay map (empirically verified):**
| POWER | GPIO | Shade function |
|-------|------|----------------|
| 1 | GPIO44 | Shade 1 open |
| 2 | GPIO2 | Shade 1 close |
| 3 | GPIO43 | Shade 2 open |
| 4 | GPIO42 | Shade 2 close |
| 5 | GPIO36 | Shade 3 open |
| 6 | GPIO35 | Shade 3 close |
| 7 | GPIO38 | Shade 4 open |
| 8 | GPIO39 | Shade 4 close |

**ShutterRelay assignments:**
```
ShutterRelay1 1
ShutterRelay2 3
ShutterRelay3 5
ShutterRelay4 7
```

**Setup command order (critical):**
1. SetOption80 1 + Restart
2. Interlock 1 (enable)
3. Interlock 1,2 3,4 5,6 7,8 (define groups)
4. ShutterMode 1
5. ShutterRelay1-4
6. ShutterOpenDuration/ShutterCloseDuration (60s placeholder)
7. FriendlyName1-8
8. Upload autoexec.be via file manager
9. Restart

---

## Rev 1.3 PCB Changes

### Already done in schematic:
- [x] ACS723 moved to GPIO10 (ADC1_CH9)
- [x] TMP235 moved to GPIO7 (ADC1_CH6)

### Still needed:
- [ ] Fix UART header — currently U1TX/U1RX (GPIO17/18), needs to be U0TX/U0RX (GPIO43/44)
- [ ] Move Shade 2 open and Shade 1 open away from GPIO43/44 (U0TX/U0RX) to free those pins for serial console in Tasmota
- [ ] Add auto-reset circuit (two-transistor RTS/DTR circuit for reliable esptool flashing)
- [ ] Troubleshoot USB-C orientation issue — /dev/ttyACM0 only enumerates in one cable orientation (likely CC1/CC2 asymmetry)
- [ ] Make all LEDs software-controllable (currently some are always-on)
- [ ] Fix test point copper — pads exist but no copper on Rev 1.2 boards
- [ ] Update silkscreen revision to 1.3
- [ ] Update silkscreen copyright year to 2026

---

## Product Track TODO

### Firmware:
- [ ] Resolve Tasmota Shutters 3 & 4 — requires GPIO reassignment in Rev 1.3
- [ ] Validate full 4-shutter Tasmota operation on Rev 1.3 board
- [ ] Test Bluetooth onboarding via Tasmota app
- [ ] Test Home Assistant auto-discovery via MQTT
- [ ] Document motor calibration procedure (ShutterSetClose/ShutterSetOpen sequence)
- [ ] Submit device template to Tasmota templates repository (templates.blakadder.com)
- [ ] Build and host generic ESPHome factory .bin for OTA migration from Tasmota
- [ ] Set up firmware.vesprio.io hosting for OTA binary

### Hardware:
- [ ] Finalize Rev 1.3 PCB
- [ ] Finalize and test 3D printed enclosure (see enclosure section)
- [ ] Source production enclosure option

### Documentation:
- [ ] Quick start guide
- [ ] Motor calibration guide
- [ ] Home Assistant integration guide
- [ ] FCC Part 15 compliance research

### Business:
- [ ] Product page on Vesprio.io
- [ ] Product photography
- [ ] Pricing research
- [ ] Marketplace selection (Tindie, Etsy, own store)

---

## Enclosure (3D Printed, FreeCAD)

**Status: Rev 2 test print in progress**

Two-piece box, bottom tray + top lid, split at board surface level (Z=1.51mm).

**Dimensions:**
- Board: ~60x65mm
- Bottom tray: 7.16mm tall
- Top lid: 16.84mm tall
- Wall thickness: 2.5mm
- Corner fillets: 3mm outer, 2mm inner

**Mounting:**
- 4 countersunk holes in bottom floor for PM3 nylon screws
- 4 boss posts in top lid interior, 2.7mm self-tap holes
- Board rests on 3mm standoffs, held down by top lid posts

**Cutouts:**
- Barrel jack: bottom tray wall (rectangular)
- Terminal block: top lid wall (full height slot)
- USB-C: top lid wall (oval with outer recess — Gemini recessed design pending)
- 2x LED windows: top lid USB-C wall (3mm circles)
- Air vents: top face and side wall above motor drivers

**Alignment:** tongue and groove around perimeter of split line

**Known issues from test print 1 (fixes in progress):**
- Keyholes upside down — fixed
- USB cutout too small — redesigning with oval + outer recess
- Alignment ridge too tight — adjusted
- Bottom countersink missing center hole — fixed
- Post screw holes too large (3mm→2.9mm) — fixed
- Case too wide — narrowed 2.5mm
- Text on sides not legible (PLA sag) — removed, new approach TBD
- Top text color print didn't work — new approach TBD

---

## Key JLCPCB Part Numbers

| Part | JLCPCB # | Notes |
|------|----------|-------|
| Heniper B1205S-3WR2L DC-DC | C20622657 | Primary DCDC, replaces MeanWell |
| DC005-T20 barrel jack | C111567 | 2mm center, 3A |
| SMBJ15CA TVS diode | C19077570 | Bidirectional, motor protection |
| mSMD110 polyfuse | C69691 | Motor output fuses |
| 1000uF 25V bulk cap | C7471896 | C11, C12 |

---

## Tools & Files

- **EDA:** KiCad (PCB), FreeCAD (enclosure)
- **Fabrication:** JLCPCB, Fabrication Toolkit plugin for gerber/BOM/CPL
- **Firmware:** ESPHome (esp-idf), Tasmota 15.4.0 + Berry
- **Key docs in project:** barn-shades-pcb.yaml, vsp-wsc4-standalone.yaml, tasmota-autoexec.be, tasmota-setup-commands.txt, vsp-wsc4-todo.md
