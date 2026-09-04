# VSP-WSC-4 Rev 1.3 — Bring-up STATUS LOG

**Live status of the physical Rev 1.3 boards.** Updated 2026-09-03 (evening).

This is the "where did I leave off" file. The step-by-step test plan is
`vsp-wsc4-rev13-bringup-procedure.md`; the config is
`vsp-wsc4-rev13-bringup.yaml`. Everything needed is git-tracked — nothing
important lives only on one machine.

---

## THE NEXT THING TO DO

**Continue bring-up on board 2, using a RESISTOR as the load — not a motor.**
Board 1 is out of service with a destroyed U8 (see "Board inventory" below).

Use a **22-27 ohm / 10 W wirewound resistor** across a shade terminal pair:
~0.45-0.55 A, no inrush, no back-EMF, clean sign flip on the meter when the
direction reverses, and a known current that doubles as a calibration check on
the ACS725 divisor. **Do not connect a motor to any board** until the real
shade motor's inrush and stall current have been measured against the driver's
1.2 A continuous / 3.2 A peak rating. A motor destroyed board 1's U8.

**All four output channels are now proven** (DMM, board 2, both directions,
2026-09-03 evening) — the channel mapping question is fully closed.

Remaining unverified items, in order: **ACS725 divisor against a known
resistive load** (the next thing to do, and the cheapest chance to prove the
`/0.264` change before any motor is involved), SW2/SW3/SW4 inputs, TMP235
sanity check against room ambient, all four channels driven together, then
Tasmota.

---

## Board inventory

| Board | State | Notes |
|---|---|---|
| **1** | **FAULTY — U8 destroyed** | VM and 3 of 4 output legs shorted to PGND. Repairable: replace U8 (SSOP-24), confirm VM->PGND open before applying 12 V. Nothing else on it is damaged. |
| **2** | Healthy | Full resistance baseline taken 2026-09-03 — every reading open. **Use board 2 as the reference when a board is suspect.** |
| 3-5 | Unopened | |

---

## Status at a glance

### Verified working on hardware
| Item | Notes |
|---|---|
| Native USB flashing (J2) | Works on a blank chip. J3 DNP'd and **not needed** |
| Boot / ESPHome runtime | Boots and runs |
| WiFi AP + web UI | AP-only config, no credentials required |
| D3 / D4 / D5 LEDs | All three respond |
| SW1 UP and SW1 DOWN | Read correctly, incl. **GPIO46**, the pin most at risk |
| ESP32 module identity | 4 MB, eFuse **quad**, 3.3 V strapping = **N4 confirmed**, not an R8 |
| 12 V supply | 12 V / 3 A bench transformer connected |
| J4 orientation | Pad 1 is **square, leftmost/top**. Confirmed by SW1 working |
| **Motor channel mapping** | **CONFIRMED ON HARDWARE 2026-09-03 — ALL FOUR.** 1->1, 2->2, 3->3, 4->4 with the config's swap applied. See Finding 1 |
| **All 4 output channels** | **All four drive both directions and produce ±12 V at their terminals (DMM, board 2).** SHADE3 included — it had never been driven on any board before this |

### NOT yet verified — open
| Item | Notes |
|---|---|
| **Any motor actually turning** | Still never seen to run under control. A motor *was* briefly energised on board 1 and destroyed U8. All output verification so far is DMM-only |
| SW2, SW3, SW4 (6 inputs) | Only SW1 exercised so far |
| TMP235 board temperature | Reading not yet sanity-checked against room ambient |
| ACS725 current sense | Never seen a real load. Divisor `0.264` **unproven** — check against a clamp meter |
| `+12V` / `+3.3V_MOTOR` rails | Never measured. No test point exists on either (see Rev 1.4 list) |
| Motor direction ↔ UP/DOWN | Which way "OPEN" physically drives is unconfirmed |
| All 4 channels together | Only single-channel attempted |
| **Tasmota** | Untouched. Deliberately deferred — see below |

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
inrush and stall current are measured.** Use a 22-27 ohm / 10 W resistor for
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

## Working on a different machine

**Normal path (what is actually used):** `git pull`, open
`vsp-wsc4-rev13-bringup.yaml` in the IDE, copy the whole file, paste it into the
ESPHome Docker dashboard's web editor, Save + Install. See Finding 9 for the
traps that come with this.

**CLI path**, if ever needed:

```bash
git pull
python3 -m venv ~/.venvs/esphome && ~/.venvs/esphome/bin/pip install esphome
cp docs/project-context/secrets.yaml.example docs/project-context/secrets.yaml  # then edit
~/.venvs/esphome/bin/esphome run docs/project-context/vsp-wsc4-rev13-bringup.yaml
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

- **Tasmota.** Explicitly parked 2026-08-27: get ESPHome working and fully
  tested first, then circle back. Remember Rev 1.3's *reason for existing* is
  the Tasmota Shutters 3 & 4 fix (GPIO43/44 = U0TX/RX on Rev 1.2), and
  **ESPHome passing proves nothing about it** — that pairing has to be retested
  under Tasmota. The channel cross above may also be a factor there.

## For Rev 1.4

**The canonical Rev 1.4 list lives in `vsp-wsc4-todo.md` under
"Rev 1.4 PCB Changes".** Everything this bring-up turned up is written there
with its evidence — the net rename, driver protection, fuse/stall-threshold
sizing, U1 hold-up, test points, J3, via-in-pad. Add new items there, not here,
so the two do not drift.
