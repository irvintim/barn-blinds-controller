# VSP-WSC-4 Rev 1.3 — Bring-up STATUS LOG

**Live status of the physical Rev 1.3 boards.** Updated 2026-10-11.

This is the "where did I leave off" file. The step-by-step test plan is
`vsp-wsc4-rev13-bringup-procedure.md`; the config is
`firmware/esphome/vsp-wsc4-rev13-bringup.yaml`. Everything needed is git-tracked — nothing
important lives only on one machine.

---

## THE NEXT THING TO DO

**Bench bring-up without motors is COMPLETE (2026-10-11).** Every board
function has now been verified on board 2 with resistive loads, under both
ESPHome and Tasmota. Nothing found requires a board change for the shade
controller use case — **verdict: no Rev 1.4 needed for the next order; reorder
Rev 1.3 as-is if more boards are needed.** Rev 1.4 is only justified if the
product goes general-purpose (Rev 1.4 items 2 + 4 together, a real design cycle).

**Both barn units are flashed and on the bench network (2026-10-11):**

| Unit | Board | Config | Web page (bench LAN) | Shades on J4 7/17, 8/18, 9/19, 10/20 |
|---|---|---|---|---|
| `barn-overhead` | 2 | `firmware/esphome/barn-overhead.yaml` | http://10.10.0.101/ | Front, Middle, Back, Workshop |
| `barn-windows` | 3 | `firmware/esphome/barn-windows.yaml` | http://10.10.0.141/ | Bar, Back, Front, Workshop |

At the barn they join the barn WiFi (container secrets) and get new IPs; the
fallback AP is "Barn Overhead Shades Fallback" / "Barn Window Shades
Fallback" (password = `ap_password`). Both web pages answered on the bench
with Reset Reason `power-on event`; **neither has had the resistive bench check
through the production firmware yet**, and covers read 50 % until their first
full run.

**D3 (red) slow-blinking is expected at the barn, not a fault.** It's ESPHome's
`status_led`. A slow blink (one short flash every 1.5 s) is a *warning*: WiFi
down, or no Home Assistant client on the API, which is the normal state while
the barn has no network. A fast blink (4×/s) is an *error* (a component failed
setup) and is worth investigating. Off = all OK.

### Barn motor test — in this order
1. **Measure each shade motor's inrush and stall current OFF-board first**
   (clamp meter, or a bench supply with a current readout, motor held stalled
   for 1-2 s). Pass: stall well under the TB6612FNG's **3.2 A peak**, running
   current under its **1.2 A continuous**. If any motor exceeds that, stop —
   it does not go on these boards.
2. **Set `stall_amps`** in both configs between the highest running current
   and the lowest stall current (it is a 1.4 A placeholder), rebuild, flash.
3. **One motor on one channel first**, on the 12 V supply the boards will run
   from. Command Open from the web page and watch **Reset Reason** — anything
   other than `power-on event` / `software` (especially `brownout`) means motor
   inrush is pulling `+12V_RAW` below ~8.5 V (Finding 11). Note which way
   "Open" physically moves the shade; fix any reversed shade in software.
4. Then the wall switches (press = start, press again = stop), then all four
   motors, then the "All Shades" group buttons.
5. **Calibrate `open_duration` / `close_duration`** per shade (60 s
   placeholder) and rebuild.

Firmware items found today (not board items): switch debounce in all configs,
soft-start, Tasmota switch inputs + stall detection. See the Product Track list
in `docs/todo.md`.

---

## Board inventory

| Board | State | Notes |
|---|---|---|
| **1** | **FAULTY — U8 destroyed** | VM and 3 of 4 output legs shorted to PGND. Repairable: replace U8 (SSOP-24), confirm VM->PGND open before applying 12 V. Nothing else on it is damaged. |
| **2** | Healthy — **`barn-overhead`** (ESPHome, production) | Full resistance baseline taken 2026-09-03 — every reading open. **Use board 2 as the reference when a board is suspect.** 2026-10-11: ran Tasmota for the shutter test, then flashed `barn-overhead` over J3. |
| **3** | Healthy — **`barn-windows`** (ESPHome, production) | First powered 2026-10-11. esptool: ESP32-S3 QFN56 v0.2, 4 MB, eFuse quad = **N4 confirmed**. Flashed over J3. Not yet resistive-load tested |
| 4-5 | Unopened | |

---

## Status at a glance

### Verified working on hardware
| Item | Notes |
|---|---|
| Native USB flashing (J2) | Works on a blank chip |
| **UART flashing via J3 holes** | 2026-10-11: a USB-TTL adapter on the unpopulated J3 holes flashed Tasmota (full erase + factory image). The DNP decision holds up |
| Boot / ESPHome runtime | Boots and runs. Reset Reason `power-on event` through every test |
| WiFi + web UI | LAN via secrets, AP fallback |
| D3 / D4 / D5 LEDs | All three respond |
| **All 8 switch inputs** | 2026-10-11, jumper to GND_ISO: each pin turns on only its own entity, all OFF at rest, incl. strapping pins GPIO46 and GPIO3. See Finding 13 (debounce) |
| ESP32 module identity | 4 MB, eFuse **quad**, 3.3 V strapping = **N4 confirmed**, not an R8 |
| 12 V supply | 12 V / 3 A bench supply; ~0.22 ohm source resistance |
| J4 orientation | Pad 1 is **square, leftmost/top**. Confirmed by SW1 working |
| **Motor channel mapping** | **CONFIRMED ON HARDWARE — ALL FOUR**, under ESPHome (2026-09-03) and Tasmota (2026-10-11). See Finding 1 |
| **All 4 output channels** | Both directions, ±11.1-11.5 V at the terminals |
| **All 4 channels at once** | 2026-10-11: 1.93 A total for 2+ min, no reboot. U8 102 °F, U9 104.5 °F |
| **ACS725 current sense** | **Proven 2026-10-11.** 5-point calibration 0-1.83 A: 0.271 V/A, 1.647 V offset, linear within ±2 mV; firmware `/0.264` reads within +2.5 %. Noise ±0.04 A. See Finding 10 |
| **TMP235** | Matches an IR thermometer within 0.2 °C — but it reads U7's hot spot, not board air. See Finding 12 |
| **Power rails** | All in range idle and loaded. See Finding 11 |
| **Tasmota, all 4 shutters** | **2026-10-11 — THE POINT OF REV 1.3, PASSED.** Each shutter drives only its own pair, opposite polarity open/close, Stop works. See Finding 14 |

### NOT yet verified — open
| Item | Notes |
|---|---|
| **Any motor actually turning** | Still never seen to run under control. A motor *was* briefly energised on board 1 and destroyed U8. All output verification is resistive-load / DMM only. Needs the real shade motors |
| Shade motor inrush / stall current | Sets the stall threshold. Never recorded; the "well under 1 A" figure is a recollection, not data |
| Motor direction ↔ UP/DOWN | Which way "OPEN" physically drives is unconfirmed |
| Tasmota switch inputs / stall / soft-start | Not configured yet — firmware work, see the Product Track list |

---

## Findings this session (all fixed in the repo, all worth remembering)

### 1. Motor channel cross — the big one
`ISO_SHn_*` net names **do not match** the SHADEn terminal they drive. On both
TB6612FNGs the A/B channels are crossed with the outputs, swapped within each
pair. **Use this table, never the net names:**

| J4 shade | UP / DOWN pins | OPEN | CLOSED | PWM |
|---|---|---|---|---|
| SHADE1 | 7 / 17 | GPIO48 | GPIO47 | GPIO21 |
| SHADE2 | 8 / 18 | GPIO36 | GPIO37 | GPIO38 |
| SHADE3 | 9 / 19 | GPIO41 | GPIO40 | GPIO39 |
| SHADE4 | 10 / 20 | GPIO42 | GPIO2 | GPIO1 |

Failure mode is silent: correctly-wired motor, no movement, no current, no log
message — because the command energizes a different, empty channel.

**CONFIRMED ON HARDWARE 2026-09-03 — all four channels.** 1 -> 1, 2 -> 2,
3 -> 3 and 4 -> 4 all drive the right terminal, both directions, with the table
above applied. The table is correct; do not "fix" it back toward the net names.

**Root cause (user, 2026-09-03):** when the pin order was reworked for the new
J4 terminal block, the labels on the TB6612FNG **output** side were re-pointed
but the **input** side was not. So on U8, `AIN1/AIN2/PWMA` carry `SH4_*` while
`AO1/AO2` go to SHADE3. Same 1<->2 swap on U9. Verified end to end against the
netlist:

```
GPIO42 -> U3.35 -> ISO_SH3_OPEN -> U4.4 (INC) -> U4.13 (OUTC)
       -> SH3_IN1 -> U8.17 (BIN1) -> ch B -> BO1/BO2 -> SHADE4 -> J4.10/20
```

U4/U5/U6 are **ISO7760DBQ** and pair cleanly 1:1 (INA pin2->OUTA pin15 ...
INF pin7->OUTF pin10) — the isolators add no cross of their own.

Firmware-fixable, no board change. **The same swap must be applied to Tasmota
and to the production ESPHome config.** Rev 1.4 should rename the nets — see
"For Rev 1.4", it is a pure rename with zero copper change.

### 2. A brand-new board looks like a broken USB port
Blank flash → ROM finds no image → RTC watchdog resets → USB drops → repeat
every ~2.67 s. **Not a fault.** Tells it apart from real USB trouble: every
enumeration *completes*, the period is metronomic, and `dmesg` has **zero** USB
errors. Full triage table in the procedure doc.

### 3. J3 DNP costs you the ROM console
The ROM's `invalid header: 0xffffffff` goes to UART0 (GPIO43/44), which is
unpopulated. So a board that will not boot **cannot tell you why** — the USB CDC
port enumerates but carries zero bytes. Not a reason to reverse the DNP, but if
J3 is ever populated, fix its LCSC field first (still the wrong 5-pin part).

### 4. Chrome can hold the serial port
A Web Serial tab (ESPHome/Tasmota web installer) claims `/dev/ttyACM0`
exclusively → `[Errno 16] Device or resource busy`. `lsof /dev/ttyACM0` finds
it. ModemManager was checked and was **not** involved.

### 5. D5 does not prove the 12 V rail reached the drivers
D5 (blue) is on `+12V_RAW`, **upstream** of the ACS725. The sensor sits in
series in the 12 V path, and `+3.3V_MOTOR` (which powers the driver logic *and*
the isolator output side) is derived downstream of it. So D5 can be lit while
`+12V` is absent. Probe **TP6 (STBY)** against **GND_MOTOR** — not ISO ground.

*(This was the leading hypothesis before the netlist showed the channel cross.
It turned out not to be the cause here, but the reasoning stands and matters if
a genuine power fault ever appears.)*

### 6. U8 destroyed by the test motor — post-mortem (board 1, 2026-09-03)
**The test motor was an "Mrosnail 280" DC motor: 12 V, 0.9 A no-load,
43000 RPM no-load.** Every number about it is wrong for this board:

| | Motor | Board limit |
|---|---|---|
| Running current, no load | **0.9 A** | F1-F4 polyfuse holds at **1.1 A** |
| Startup inrush (= stall current) | **~6-8 A** typical for a 280 frame at 12 V | TB6612FNG peak **3.2 A**, continuous **1.2 A** |
| Demand at start | ~6-8 A | wall wart **3 A** |

Sequence: inrush collapsed the 12 V rail -> ESP32 browned out (U1 has only C9,
22 uF, on its input and the ISO side has ~1-2 ms of hold-up) -> the bridge shut
off instantly with energy still in the windings -> flyback into U8. Repeated
brownout/retry cycles finished it.

**Final state of board 1's U8: three of four output legs (AO2, BO1, BO2)
shorted to PGND.** Only AO1 survived. `SHADE3_DOWN` reaches only D8, J4.19 and
U8's AO2 — and J4.9 reads open, so D8 is not the path and the short is inside
U8. Same argument for BO1/BO2. U9's outputs are clean (J4 7/17 and 8/18 both
open to ground).

Also on board 1: **`+12V` is shorted to `GND_MOTOR`.** This is what put the
wall wart into hiccup mode and stopped the board booting on 12 V at all — while
USB still powered the ESP32 fine, because `USB_VBUS -> D10 -> +5V_OR` bypasses
the 12 V rail entirely.

**That 12 V short is NOT yet localized, and one obvious test does not localize
it:** U8 pins 13/14/24 and U9 pins 13/14/24 are all on `+12V`, and U8/U9 pins
3/4/9/10 are all on `GND_MOTOR` — so "VM->PGND at U8" and "VM->PGND at U9" are
the *same measurement taken at two places*, and a single rail short reads short
at both. Candidates include C33/C34, C36-C39, U7, U11 and the ACS725 as well as
U8. To localize: read **resistance, not continuity**, at C33/C34 and compare
against board 2, then lift U8 and re-read.

**Reading the J4 pair measurements correctly:** `10<->20` reads short because
pins 10 and 20 are each *independently* grounded — they are shorted through
ground, not to each other. `9<->19` reads open because pin 19 is grounded but
pin 9 is not, so you are measuring across an intact bridge leg. A pair-to-pair
test cannot reveal damage when only one leg of the pair is bad; always probe
each pin to GND_MOTOR separately.

**D6-D9 were NOT the problem.** D8 sits directly across J4 9/19; that pair read
**open**, so D8 is fine. All four polyfuses are fine too (a healthy PTC reads
short across its poles).

**Diagnostic gotcha:** probing J1 pin 1 -> GND_MOTOR reads **open even on a
board with a hard 12 V short**, because `Net-(D1-A)` shows D1 is a *series*
reverse-polarity diode between J1 and `+12V_RAW`. Probe at **C33/C34** instead.

**Rule going forward: no motor on any board until the real shade motor's
inrush and stall current are measured.** Use a 20-33 ohm / 10 W resistor for
bring-up.

### 7. `api:` reboots the board every 15 minutes on the bench
`[api:129] No clients; rebooting`. ESPHome's API watchdog defaults to a 15 min
`reboot_timeout`, and on a bench config there is never a Home Assistant client.
Every reboot silently resets **STBY to off, all four PWM sliders to 0, and every
direction switch to off** — which looks exactly like a channel dying, and made
several hours of channel-mapping observations untrustworthy.
**Fixed:** `reboot_timeout: 0s` in the config.

### 8. PWM at 0 = short brake, and the sliders used to default there
The TB6612FNG needs PWM **high** to drive; at 0 % duty it sits in short brake
with both outputs pulled low (~38 mV across the terminal pair — steady, which
is the tell that the bridge is alive rather than high-Z). The four PWM sliders
defaulted to 0, so toggling a direction pin did nothing at all.
**Fixed:** `initial_value: 100` plus an explicit `output.set_level` for all four
in `on_boot`, because an optimistic template number does not necessarily push
its initial value to the LEDC channel.

### 9. The build machine is an ESPHome Docker dashboard, not the CLI
Config is copy-pasted from the IDE into the dashboard's web editor, then
Save + Install. Consequences:
- **`secrets.yaml` lives inside the container** and never comes from this repo
  (the repo's copy is gitignored). `!secret wifi_ssid` resolves there.
- **No git on that container.** Every paste overwrites the previous config with
  no history. Hand-edits made in the web editor are silently reverted by the
  next paste — this is how the wifi lines kept re-commenting themselves.
  **Make every edit in this repo, never in the web editor.**
- The config's `ssid`/`password` lines are now **uncommented** so a paste works
  against the container's secrets. The `ap:` block remains as fallback.
- To confirm a paste took, look for the **"Reset Reason"** entity in the web UI.

---

### 10. ACS725 calibration — the `/0.264` formula is right (2026-10-11)
Resistive loads on board 2, current from DMM volts ÷ DMM-measured ohms (lead
resistance 0.2 ohm subtracted), channels added one at a time:

| Load | True current | ACS725 raw (mean) | Firmware reads | Error |
|---|---|---|---|---|
| Idle | 0 | 1.647 V | −0.01 A | — |
| SHADE1 20.1 ohm | 0.564 A | 1.801 V | 0.572 A | +1.5 % |
| + SHADE2 30.0 ohm | 0.939 A | 1.900 V | 0.947 A | +0.9 % |
| + SHADE3 20.0 ohm | 1.470 A | 2.047 V | 1.505 A | +2.4 % |
| + SHADE4 30.2 ohm | 1.827 A | 2.140 V | 1.857 A | +1.7 % |

Least-squares fit: **0.271 V/A, 1.647 V offset, every point within ±2 mV.**
That is 2.5 % above the datasheet 0.264 V/A — inside part + ADC tolerance.
**Keep `/0.264`; per-board calibration is not worth it.** Noise (5-sample
average) ±10 mV ≈ ±0.04 A idle and loaded, so a 0.7 A stall (~185 mV) is ~30×
the noise floor: **one rail-level sensor CAN detect a shade stall.** A
single-point check on 30.2 ohm earlier the same day suggested 0.285 V/A — that
was too few samples; the 5-point fit supersedes it.

The sensor sits in the supply rail, so it reads the same positive current in
both drive directions — do not expect a sign flip on reversal.

### 11. Power rails, idle vs 1.93 A load (2026-10-11)
GND_MOTOR reference = C33 negative; GND_ISO reference = J4 pin 2.

| Rail | Probe | Idle | Loaded | Δ |
|---|---|---|---|---|
| 12 V input (before D1) | TP1 | 12.27 | 11.85 | −0.42 |
| `+12V` | C33 + | 11.98 | 11.42 | −0.56 |
| `+3.3V_MOTOR` | U7 tab | 3.292 | 3.292 | 0 |
| STBY | TP6 | 0 | 3.282 | — |
| `+5V_ISO` | TP2 | 5.040 | 4.835 | **−0.205** |
| `+3.3V_ISO` | TP3 | 3.305 | 3.305 | 0 |

`+5V_ISO` moving is **not a fault**: U1 (B1205S) is an **unregulated** isolated
converter, so its output is a fixed fraction of its input — `+5V_ISO` ÷
`+12V_RAW` was 0.421 idle and 0.423 loaded. U2 absorbs it, so `+3.3V_ISO` is
rock steady. **Consequence, now quantified:** the ESP32 holds as long as
`+5V_ISO` > ~3.55 V (3.3 V + U2 dropout), i.e. **`+12V_RAW` above ~8.5 V**. A
3 A wall wart facing a 6-8 A motor inrush goes far below that — which is the
board 1 failure sequence. Feeds Rev 1.4 item 4.

Note TP1 is `Net-(D1-A)` (the raw input, *before* D1), not `+12V`.

### 12. U7 (AMS1117, 12 V → `+3.3V_MOTOR`) is the board's hot spot (2026-10-11)
IR thermometer, open air, 75 °F room, **no load**: U7 **94 °F**, ACS725 91.5 °F,
U1 87 °F, U2 84 °F, ESP32 can 82 °F (a metal can reads low on IR; its die
sensor said 90 °F). A linear drop of ~8.7 V × the motor-side logic load.
- **TMP235 (U10) sits beside U7**, so "Board Temperature" reports U7's local hot
  spot, not enclosure air. It agreed with the IR reading of the ACS725 within
  0.2 °C. Fine as a warning; any thermal-shutdown logic must know this.
- Board runs ~9 °C over ambient at idle with no enclosure — relevant to the
  enclosure Rev 3 ventilation check (70 °C attic + 9 °C ≈ 80 °C vs the module's
  85 °C rating, before the enclosure adds anything).
- U2 is *not* the hot spot, so swapping it for a buck would buy little.
- **Do not "fix" U7 by feeding it from 5 V** — the only 5 V is `+5V_ISO`, on the
  other side of the isolation barrier. Logged as a Rev 1.4 nice-to-have.

### 13. Switch inputs need firmware debounce (2026-10-11)
With a hand-held jumper, SW3 Up logged ON three times in ~3 s and SW2 Down
chattered. The 1 k / 100 nF filter has τ ≈ 0.1 ms; mechanical contacts bounce
for milliseconds. **No config has a debounce filter yet** (bring-up, standalone,
Tasmota). Firmware item — `delayed_on_off: 50ms` in ESPHome, `SwitchDebounce`
in Tasmota. Not a board item.

### 14. Tasmota on Rev 1.3 — all four shutters work, and why Rev 1.2's didn't (2026-10-11)
**Passed:** Shade 1 ±11.31 V, 2 ±11.47 V, 3 ±11.10 V, 4 ±11.36 V, each driving
only its own J4 pair, opposite polarity open/close, `ShutterStop` works, no
restarts. Tasmota 15.6.0.3. Full procedure and template:
`firmware/tasmota/tasmota-setup-commands.txt`. Things that cost time, in order:

1. **Cannot OTA from ESPHome to Tasmota** — partition layout mismatch (ESPHome
   app slots ~1.75 MB, Tasmota needs safeboot + app + FS). Serial flash only.
2. **GPIO35/36/37 are hidden on Tasmota's Module page.** Its generic ESP32S3
   module defines GPIO33-37 as `GPIO_NONE` (reserved for octal PSRAM on R8
   modules; `tasmota_template.h`). The N4 has no PSRAM, so they are normal
   GPIOs — **apply a Template** (`Template {...}` + `Module 0`) instead; the
   Template page shows them in red as a warning only. **No board change.**
   This is very likely the real reason Rev 1.2's Shutter 3 failed (it was on
   GPIO35/36) — the old GPIO43/44 explanation never fit, since 43/44 carried
   Shades 1 and 2, which worked.
3. **"Relay_i" ≠ "Relay".** Inverted relays idle HIGH and drive the opposite
   direction. Must be plain Relay.
4. **The PWM pins must be "Output Hi"** or the channel sits in short brake (same
   trap as Finding 8).
5. **Interlock must be set after the template is active, and switched ON
   separately.** Tasmota silently discards relay numbers above the current
   relay count, and `Interlock 1,2 3,4 ...` does not set the ON flag. Symptom:
   `SHT: ERROR: Shtr1 Relays are not in INTERLOCK ... Shutter DISABLE`.
6. Tasmota assumes every shutter starts at position 0 — send Open first.
7. The web UI "Restarting…" page can hang after a reboot that actually
   completed — just reload.

### 15. ESPHome safe mode after a reflash looks like a dead API (2026-10-11)
After reflashing, the dashboard got `Errno 111` on port 6053 and the web UI was
gone — but port 3232 (OTA) was open. That port pattern is **ESPHome safe mode**
(WiFi + OTA only), entered after 10 boots in a row that did not reach 60 s,
here from power cycling during the reflash. One clean power cycle fixed it;
Reset Reason was `power-on event`, so it was not a crash loop. If it comes back
after a clean power cycle, it *is* a crash loop — read the boot log over serial.

Related: with `name_add_mac_suffix: true` the mDNS name is
`wsc4-bringup-xxxxxx.local`, so the dashboard's `wsc4-bringup.local` lookup
always times out — use the IP. And a 40 s gap in the API log mid-test was the
board **roaming to a stronger WiFi AP**, not a reset (Uptime kept counting).

---

### 16. Powered from the USB-TTL adapter = brownout loop at WiFi start (2026-10-11)
With the 12 V supply unplugged, board 2 ran off the FTDI adapter's 3.3 V
through **J3 pin 3 (`+3.3V_ISO`)**. It boots, then browns out the moment WiFi
starts (`E BOD: Brownout detector was triggered`, then `rst:0x3
RTC_SW_SYS_RST`), about once a second, under **any** firmware — Tasmota
safeboot looped the same way. Looks exactly like a firmware crash. An FT232R's
3.3 V output is good for ~50 mA; WiFi start needs several hundred.
- **Always have 12 V connected when flashing or running over J3**, and leave
  **J3 pin 3 unconnected** (only pin 1 → adapter RX, 2 → TX, 4 → GND).
- Diagnosis trick that found it: this config logs to USB-Serial-JTAG, so with
  no USB cable a crash is invisible. A throwaway build with
  `logger: hardware_uart: UART0` put the app log on J3 and showed the brownout
  in one boot.
- In a fast reset loop, download mode is easier to catch by holding BOOT
  through RESET and ~2 s after it. esptool's "Invalid head of packet (0x45)"
  = it read the `E` of `ESP-ROM` — the chip was rebooting, not in download mode.

---

## Working on a different machine

**Normal path (what is actually used):** `git pull`, open
`firmware/esphome/vsp-wsc4-rev13-bringup.yaml` in the IDE, copy the whole file, paste it into the
ESPHome Docker dashboard's web editor, Save + Install. See Finding 9 for the
traps that come with this.

**CLI path**, if ever needed:

```bash
git pull
python3 -m venv ~/.venvs/esphome && ~/.venvs/esphome/bin/pip install esphome
cp firmware/esphome/secrets.yaml.example firmware/esphome/secrets.yaml  # then edit
~/.venvs/esphome/bin/esphome run firmware/esphome/vsp-wsc4-rev13-bringup.yaml
```

- The config now joins your LAN via `!secret`, with the **`WSC4 Bringup`** /
  `bringup1234` AP (http://192.168.4.1/) still there as fallback. `secrets.yaml`
  is gitignored, so it does **not** travel between machines via `git pull`.
- **First build on a new machine downloads the ESP-IDF toolchain** — hundreds of
  MB, several minutes. Do it before you are standing at the board if you can.
- If the port will not open: close any browser flasher tab (`lsof /dev/ttyACM0`).
- If the board is boot-looping: hold **BOOT (SW2)**, tap **RESET (SW1)**,
  release BOOT. Or let esptool's `--before default-reset` handle it.
- Safety: **STBY defaults OFF**, so the drivers are in high-Z until you arm them.

---

## Deferred by decision

- **Tasmota** — was parked 2026-08-27 until ESPHome was fully tested. **Done
  2026-10-11: all four shutters pass** (Finding 14). Remaining Tasmota work is
  firmware (switch inputs, debounce, soft-start, stall detection).

## For Rev 1.4

**The canonical Rev 1.4 list lives in `docs/todo.md` under
"Rev 1.4 PCB Changes".** Add new items there, not here, so the two do not
drift. As of 2026-10-11 none of them is required for the shade-controller use
case — see "THE NEXT THING TO DO" above.
