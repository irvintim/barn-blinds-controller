# VSP-WSC-4 Rev 1.3 — Bring-up STATUS LOG

**Live status of the physical Rev 1.3 boards.** Updated 2026-08-30.

This is the "where did I leave off" file. The step-by-step test plan is
`vsp-wsc4-rev13-bringup-procedure.md`; the config is
`vsp-wsc4-rev13-bringup.yaml`. Everything needed is git-tracked — nothing
important lives only on one machine.

---

## THE NEXT THING TO DO

**Confirm the motor channel-cross fix.** A motor was wired to SHADE4
(J4 pins 10/20) and would not run on any "Shade 4" command. Root cause found
and fixed in the config, **but the fix has not yet been confirmed on hardware.**

Fastest confirmation — **flash the current config first**, then:

1. **Motor Enable (STBY)** → ON
2. **Shade 4 PWM** → 100  *(must be > 0; it defaults to 0 and nothing moves at 0)*
3. **Shade 4 OPEN pin** → ON

Motor on J4 pins 10/20 should run. "Shade 4 CLOSED pin" reverses it.

<details>
<summary>If you are still on the OLD firmware (pre-2026-08-28 build)</summary>

The old build has the crossed mapping. Without reflashing, a motor on SHADE4
responds to the **"Shade 3"** entities. That was the diagnostic trick; the
corrected build makes the labels honest, so prefer flashing.
</details>

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

### NOT yet verified — open
| Item | Notes |
|---|---|
| **Any motor actually turning** | The whole point of the next step. Never yet seen to run |
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

Firmware-fixable, no board change. **The same swap must be applied to Tasmota
and to the production ESPHome config.** Rev 1.4 should rename the nets.

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

---

## Working on a different machine

```bash
git pull
python3 -m venv ~/.venvs/esphome && ~/.venvs/esphome/bin/pip install esphome
~/.venvs/esphome/bin/esphome run docs/project-context/vsp-wsc4-rev13-bringup.yaml
```

- **No `secrets.yaml` needed.** The config is AP-only: join **`WSC4 Bringup`**
  / `bringup1234`, then open **http://192.168.4.1/**. Every test is driven from
  that page.
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
- Rename `ISO_SHn_*` nets so they match the SHADEn terminal they drive.
- Add test points on **`+12V`** and **`+3.3V_MOTOR`** — the two rails most worth
  probing during bring-up both currently require touching an IC pin.
- Revisit J3: either populate it with the correct 7-pin part (e.g. C492406) for
  a ROM console, or drop it deliberately and document that there is no fallback.
