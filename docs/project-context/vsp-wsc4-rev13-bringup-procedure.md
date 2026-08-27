# VSP-WSC-4 Rev 1.3 — Bring-up procedure

Companion to `vsp-wsc4-rev13-bringup.yaml`. Written 2026-08-27, boards received same day.

Split into **Stage 1 (bench, nothing connected)** and **Stage 2 (lab, I/O connected)**.
Stage 1 needs only a USB cable and can be done at a desk. Do not skip to Stage 2 —
if Stage 1 fails, connecting 12 V and motors only adds variables.

---

## Before you plug anything in

**Flash path: native USB only.** J3 is DNP'd on this run, so there is no UART
fallback. If native USB does not enumerate, you have no second way in short of
soldering a header onto J3 — and its LCSC field is still the wrong 5-pin part.

**Power:** USB alone powers the 3.3 V ISO side (ESP32, isolators, TMP235,
ACS725 signal side). It does **not** power the 12 V motor rail. That is fine and
expected for Stage 1 — it means D5 (blue, +12V_RAW) will be **dark** on USB
power alone, and motor current will read ~0 A. Neither is a fault.

**Setup:**
```bash
python3 -m venv ~/.venvs/esphome && ~/.venvs/esphome/bin/pip install esphome
```
Create `docs/project-context/secrets.yaml` (see `secrets.yaml.example`, and note
it is gitignored — do not commit real credentials):
```yaml
wifi_ssid: "your-ssid"
wifi_password: "your-password"
```

---

## Stage 1 — Bench, nothing connected

### 1.1 Flash

```bash
esphome run docs/project-context/vsp-wsc4-rev13-bringup.yaml
```

Hold **BOOT (SW2)**, tap **RESET (SW1)**, release BOOT if it does not enter
download mode on its own. The S3's USB-Serial-JTAG normally auto-resets without
this.

**Pass:** flashes and reboots.

**If the port never appears:** this is the single highest-risk failure on this
build, because there is no fallback path. Check U16 (USB ESD protection) first —
it sits on B.Cu while J2 is on F.Cu, so D+/D− cross layers through a ~2 mm via
stub each side. That was an accepted trade-off, not a known defect, but it is
the first thing to suspect if enumeration is flaky rather than absent.

### 1.1a Expected build figures

The config was compiled clean on 2026-08-27 with ESPHome 2026.8.1. Compare
against these — a large deviation means your toolchain resolved something
differently:

```
RAM:   31.6% (108111 / 341760 bytes)
Flash: 48.0% (881035 / 1835008 bytes)
```

**That 1835008-byte flash figure is the useful one.** It is the app partition
size for a 4 MB flash with OTA, which confirms `flash_size: 4MB` took effect.
If you see roughly double that, the override did not apply and the image will
not fit the N4. RAM at 341760 bytes total likewise confirms no PSRAM was
brought in.

### 1.2 Console

Logs come over the same USB port via the S3's USB-Serial-JTAG peripheral
(`hardware_uart: USB_SERIAL_JTAG` in the config — without it you get silence).

```bash
esphome logs docs/project-context/vsp-wsc4-rev13-bringup.yaml
```

**Pass:** you see `=== VSP-WSC-4 Rev 1.3 bring-up firmware booted ===` followed
by `Motor drivers held in STANDBY.`

### 1.3 Flash size sanity

Confirm in the boot log that the partition table matches **4 MB**. The N4 module
has 4 MB and no PSRAM; the `esp32-s3-devkitc-1` board definition assumes 8 MB,
which is why the config sets `flash_size: 4MB`. A boot loop right after flashing
is the classic symptom of that override being missing or wrong.

There should be **no PSRAM line** in the log. If you see PSRAM being initialised,
the wrong module got placed — see CLAUDE.md "ESP32 variant selection" before
touching anything.

### 1.4 WiFi + web UI

**Pass:** joins WiFi, log prints an IP. Open `http://<ip>/` for the full entity
list. If credentials are wrong it falls back to the **"WSC4 Bringup"** AP
(password `bringup1234`).

### 1.5 LEDs — first real proof of life

Press **"TEST: Blink all LEDs"** in the web UI. It cycles D3 → D4 → D5 three
times, then restores D4/D5 to on.

| LED | GPIO | Expected on USB-only power |
|---|---|---|
| D3 red (status) | GPIO16 | blinks — driven directly by the ESP32 |
| D4 white (3V3) | GPIO6 | **lit at power-up before firmware runs**, then blinks |
| D5 blue (12V) | GPIO7 | **dark** — no 12 V rail present yet |

D4 and D5 are hardware-default-ON by design: their FET gates are pulled up to
their rails, so they light the instant power arrives and stay lit until firmware
pulls the GPIO low. **D4 being on before the ESP32 has booted is correct, not a
stuck output.**

### 1.6 Sensors

Both sensors are on-board and read with nothing connected. Each has a companion
"raw volts" entity — when a converted value looks wrong, the raw voltage tells
you whether it is the sensor or the formula.

| Entity | Expect | Raw volts |
|---|---|---|
| Board Temperature (TMP235) | room ambient, ±3 °C | ~0.70–0.80 V at 20–30 °C |
| Motor Current (ACS725) | ~0 A | **~1.65 V** (quiescent = zero current) |
| ESP32 Die Temperature | above ambient, typically +10–20 °C | — |

**The ACS725 divisor is `0.264`, not the ACS723's `0.4`.** If current reads
roughly 1.5× what you expect later in Stage 2, that formula is the reason.

A raw ACS725 reading far from 1.65 V at idle points at the sensor's supply or
offset, not at the formula.

### 1.7 Switch inputs — highest-risk area of Stage 1

All 8 must read **OFF** with nothing connected.

There are **no external pull-ups** on this board. Switches short to GND_ISO, so
the internal pull-ups the config enables are the only thing holding these inputs
high. Test each by jumpering its J4 pin to an adjacent GND_ISO pin (J4 pins 2, 5,
12, or 15) — the matching entity should flip ON.

**Watch GPIO46 (SW1 Up) specifically.** It is a strapping pin whose reset default
is pull-*down*, so the pull-up must be applied in software. That is safe for boot
— GPIO46 reads 0 at reset either way, and a held switch cannot create an invalid
boot-mode combination — but it does mean SW1 Up is the input most likely to float
or read inverted if something is off. If it misbehaves while the other seven are
fine, suspect the pin, not the wiring.

### 1.8 Motor pins — dry check

Leave **"Motor Enable (STBY)"** OFF. Press **"TEST: Walk motor direction pins"**
and probe each isolator output with a meter as the log names each pin. This
verifies the ESP32 → isolator path with no motors and no 12 V present.

Motor STBY defaults OFF at boot in this config, holding the TB6612FNG outputs in
high-Z. This is deliberately the **opposite** of the production config, which
enables STBY at boot.

---

## Stage 2 — Lab, I/O connected (Sunday)

Do Stage 1 first, on the same board, in the same session.

1. **12 V first, no motors.** Confirm D5 (blue) now lights. Confirm the ACS725
   still reads ~0 A with the rail up but nothing drawing.
2. **One motor, Shade 1.** Enable "Motor Enable (STBY)", set "Shade 1 PWM" to
   ~50%, then toggle "Shade 1 OPEN pin". Watch "Motor Current" respond.
   - Both OPEN and CLOSED high at once is short-brake on the TB6612FNG — a legal
     state, not damaging, but not a useful test.
3. **Check current magnitude against a clamp meter** before trusting the stall
   threshold. This is where the 0.264 divisor gets proven.
4. **Repeat per shade**, then all four.
5. **The actual point of this revision: Tasmota Shutters 3 & 4.** Rev 1.2 worked
   under ESPHome but Tasmota's shutters 3 and 4 were broken by the
   GPIO43/44 = U0TX/RX conflict. Rev 1.3 moved those signals. **ESPHome passing
   does not prove this is fixed** — it has to be retested under Tasmota, since
   that is the pairing that failed.

---

## What Stage 1 cannot tell you

- Anything about the 12 V rail, the DC-DC (U1), or the motor drivers under load.
- Whether the isolation barrier behaves under motor switching noise.
- Current-sense accuracy — 0 A proves the ADC path lives, not that the scale is right.
- **Whether the GPIO43/44 Tasmota conflict is actually fixed.**
- Thermal behaviour. The 85 °C module rating is *ambient around the module*, and
  a sealed box in an attic runs hotter than attic ambient. Comparing TMP235
  against the ESP32 die temperature over a long run starts to inform the
  enclosure Rev 3 ventilation question.
