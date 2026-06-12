# VSP-WSC-4 Project TODO Lists

## Rev 1.3 PCB Changes

### Already done in schematic:
- [x] ACS723 moved to GPIO10 (ADC1_CH9)
- [x] TMP235 moved to GPIO7 (ADC1_CH6)

### Still needed in schematic/layout:
- [ ] Troubleshoot USB-C orientation issue -- /dev/ttyACM0 only appears with connector in one orientation, not the other. Likely CC1/CC2 asymmetry or missing pull-down on one CC line.
- [ ] Fix UART header — currently connected to U1TX/U1RX (GPIO17/18), should be U0TX/U0RX (GPIO43/44) for standard programming
- [ ] GPIO43 (U0TX) and GPIO44 (U0RX) are unusable as motor control outputs in Tasmota when serial console is active — move Shade 3 open and Shade 4 open signals to non-UART GPIOs
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
- [ ] Finalize and test 3D printed enclosure
- [ ] Source production enclosure (3D print vs injection mold vs off-shelf)
- [ ] Decide on packaging

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
