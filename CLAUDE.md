# Barn Blinds Controller — Claude Context

## What this is
Vesprio VSP-WSC-4: 4-channel motorized window shade controller, ESP32-S3-WROOM-1-N4, dual firmware track (ESPHome personal use / Tasmota product). See `docs/project-context/vsp-wsc4-handover.md` for full hardware detail and GPIO map.

## Current state (as of 2026-09-03)
- **STATUS: Rev 1.3 boards received 2026-08-27. Bring-up in progress — read `docs/project-context/vsp-wsc4-rev13-bringup-status.md` FIRST.** That file is the live "where did I leave off" log: what is verified on hardware, what is still open, and the single next action. Boots, flashes over native USB, WiFi/web UI up, all 3 LEDs and SW1 confirmed. **The channel-cross fix is now CONFIRMED ON HARDWARE (2026-09-03): Shade 1→1, 2→2, 4→4 all drive the correct terminal.** SHADE3 is still untested. **Board 1 is out of service — its U8 was destroyed by an unsuitable test motor (see the failure post-mortem in the status log). NO MOTOR goes on any board until the real shade motor's inrush and stall current are measured against the TB6612FNG's 1.2 A continuous / 3.2 A peak rating; use a 22-27 Ω / 10 W resistor for bring-up.** Work the "Firmware bring-up checklist" in `docs/project-context/vsp-wsc4-todo.md`. The **ACS725 formula change** (`amps = (Vout - 1.65) / 0.264`, was `/0.4` for the ACS723) is required before current sensing reads correctly — update the stall-detection threshold with it.
- **Flash via native USB (J2 Micro-USB, GPIO19/20) — that is the only path on these boards, because J3 is DNP'd.** See PICK UP HERE below.
- **PCB:** Rev 1.3, **fab-ready.** All PICK UP HERE items from the 2026-08-05 QA pass are done: C40-C43 placed (~1.8-2.6mm from U12-U15 pin 4), +5V_OR/USB_VBUS widened, U16 moved closer to J2, D10/D11 silkscreen fixed, LCSC added for J2 (C397452) and J4 (C6652293 — pre-purchased JLCPCB inventory part, number needed so JLCPCB places it). DRC: 0 unconnected pads, 0 real errors, 114 footprints. Rev 1.2 was assembled and working (ESPHome only; Tasmota broken on Shades 3&4 due to GPIO43/44 = U0TX/RX conflict — fixed in Rev 1.3).
- **Fabrication Toolkit run 2026-08-07** — archive `VSP-WSC-4_1.3`. These are the outputs the boards were built from; re-run the toolkit only if the PCB changes.
- **Schematic:** Rev 1.3 passed a full pre-fab QA review (2026-07-07) plus two physical/layout QA passes (2026-08-05 and 2026-08-06/07, see below). ERC errors steady at 5, all benign (4× missing PWR_FLAG, 1× J2-GND/U1-(-Vout) both-power-output which is correct by design).
- **Also in Rev 1.3:** D4/D5 LEDs software-controllable (GPIO6/7, hardware-default-ON; D5 crosses isolation via spare U5 channel); RTS/DTR auto-reset on 7-pin J3 (Espressif reference two-transistor circuit); Micro-USB (not USB-C); switch inputs wired to ESP32 — see todo.md "Rev 1.3 GPIO Map" for pinout and "Firmware bring-up checklist" before first flash
- **Enclosure:** FreeCAD Rev 2 (`project-case-rev2.FCStd`), 3D printed, test print 2 in progress

## PICK UP HERE — bring-up in progress (live log: `docs/project-context/vsp-wsc4-rev13-bringup-status.md`)
**Rev 1.3 boards arrived 2026-08-27.** Ordered from JLCPCB 2026-08-07: gerber `VSP-WSC-4_1.3_Y18`, 5 boards, PCBA both sides, S1000H TG155 / ENIG, Confirm Parts Placement + Photo Confirmation both on.

Next action: work the **"Firmware bring-up checklist"** in `docs/project-context/vsp-wsc4-todo.md`. The four things that will bite first, in order:

1. **ACS725 formula:** `amps = (Vout - 1.65) / 0.264`. The old ACS723 divisor was `0.4` — current sensing reads wrong until this changes, and the stall threshold moves with it.
2. **Internal pull-ups on all 8 switch GPIOs** (3, 46, 9, 10, 11, 12, 13, 14). There are no external pull-ups; switches short to GND_ISO. GPIO46 is a strapping pin defaulting to pull-*down*, so its pull-up must be set explicitly.
3. **D4 (GPIO6, white) and D5 (GPIO7, blue) are hardware-default-ON** and stay on until firmware drives them LOW. That is by design — they track raw power.
4. **Tasmota is the thing actually being validated here.** Rev 1.2 worked under ESPHome but Tasmota's Shutters 3 & 4 were broken by the GPIO43/44 = U0TX/RX conflict. Rev 1.3 moved those signals, so confirming all four shutters work under Tasmota is the point of this build.

### First board powered up 2026-08-27 — the USB "fault" was a blank chip
A virgin board **boot-loops and looks exactly like a failing USB port**: clean
enumeration as `303a:1001 USB JTAG/serial debug unit`, then `USB disconnect`
~2.4 s later, forever. Flash ships erased, the ROM finds no image, the RTC
watchdog resets the chip, and each reset drops the USB peripheral.

**It is not a fault, and it will happen on every board from every fab run.**
Tells: every enumeration *completes*, the period is metronomic (measured
2.673 s ±ms), and `dmesg` has **zero** USB errors. A real USB problem gives
`-71`/`-110` and failed descriptor reads.

Proven on the first board: `esptool flash-id` connected and ran a stub flasher
over native USB, which clears the entire USB path — connector, D+/D−, **U16 and
its via-stub trade-off**, cable, host port. Flash at `0x0` read back all `0xFF`.

That readout also independently confirmed the module: **`Detected flash size:
4MB`, `Flash type set in eFuse: quad`, 3.3V strapping, ESP32-S3 QFN56 rev v0.2**
— i.e. the N4 was placed, not an octal-PSRAM R8. Worth running on the first
board of every future order as a cheap variant check.

**Native USB is sufficient for first programming — J3/UART0 is never required.**
The USB-Serial-JTAG is a ROM peripheral and works on a blank chip. Hold BOOT
(SW2) + tap RESET (SW1) to park it in download mode, or let esptool's
`--before default-reset` do it (verified, first attempt, no buttons).

**Cost of the J3 DNP, now concrete:** the ROM's `invalid header: 0xffffffff`
explanation goes to UART0 (GPIO43/44), which is unpopulated — so the USB CDC
port enumerates but carries zero bytes and the board cannot tell you why it
won't boot. Not a reason to reverse the DNP, but if J3 is ever populated, fix
its LCSC field first (still the wrong 5-pin part).

**Watch out:** a Chrome tab holding the port via the Web Serial API (ESPHome or
Tasmota web installer) causes `[Errno 16] Device or resource busy` and blocks
esptool. `lsof /dev/ttyACM0` finds it. ModemManager was checked and was *not*
involved.

Full detail and the ten-second triage table: `vsp-wsc4-rev13-bringup-procedure.md`.

### Motor channel cross — ISO_SHn_* net names do NOT match the SHADEn terminal
**Found 2026-08-28 during first motor bring-up. Verified against the netlist,
and CONFIRMED ON HARDWARE 2026-09-03 (Shade 1→1, 2→2, 4→4).**

**Root cause:** when the pin order was reworked for the new J4 terminal block,
the labels on the TB6612FNG **output** side were re-pointed but the **input**
side was not. The isolators (U4/U5/U6, ISO7760DBQ) pair cleanly 1:1 and add no
cross of their own.
On **both** TB6612FNGs the A/B channel control signals are crossed with the
output terminals, swapped within each pair:

| Driver | Control nets | Output terminals | J4 pins |
|---|---|---|---|
| U9 ch A | `SH2_IN1/IN2/PWM` | **SHADE1**_UP/DOWN | 7 / 17 |
| U9 ch B | `SH1_IN1/IN2/PWM` | **SHADE2**_UP/DOWN | 8 / 18 |
| U8 ch A | `SH4_IN1/IN2/PWM` | **SHADE3**_UP/DOWN | 9 / 19 |
| U8 ch B | `SH3_IN1/IN2/PWM` | **SHADE4**_UP/DOWN | 10 / 20 |

**Correct GPIO → physical J4 terminal mapping (use this, not the net names):**

| J4 shade | UP / DOWN | OPEN | CLOSED | PWM |
|---|---|---|---|---|
| SHADE1 | 7 / 17 | GPIO48 | GPIO47 | GPIO21 |
| SHADE2 | 8 / 18 | GPIO36 | GPIO37 | GPIO38 |
| SHADE3 | 9 / 19 | GPIO41 | GPIO40 | GPIO39 |
| SHADE4 | 10 / 20 | GPIO42 | GPIO2 | GPIO1 |

Symptom if you get this wrong: a motor on a correctly-wired terminal simply
never moves, because the command energizes a different, empty channel. No
error, no current draw, nothing in the logs. Cost roughly an evening.

**This is firmware-fixable — no board change needed**, and the bring-up config
is already corrected. The ids there are named for the **physical J4 terminal**;
do not "fix" them back to match the net names. Any Tasmota or production
ESPHome config must apply the same 1↔2 / 3↔4 swap.

Rev 1.4 should rename the nets so `ISO_SH1_*` actually reaches SHADE1 — this is
a labelling trap that will keep costing time otherwise.

### As-built quirks of this specific run — check these before debugging anything
- **J3 (UART/RTS-DTR header) is DNP'd — not populated.** Native USB (GPIO19/20) is the only flash path as shipped. The RTS/DTR auto-reset circuit exists on the board but is unusable without J3. If J3 is ever populated, **fix its LCSC field first** — it still carries C492404, a 5-pin part against a 7-pin footprint.
- **U1 is the Heniper B1205S-3WR2L (C20622657), on the `H` hole set** of the shared `DCDC_HYBRID_SLC03_TEC2` footprint.
- **C10 is 100 µF 16 V (C7432790)** and **U12-U16 are C5158049**, both stock-driven substitutions made at order time. Same footprints, no board change.

### Rev 1.4 change list — canonical location
**`docs/project-context/vsp-wsc4-todo.md`, section "Rev 1.4 PCB Changes"** (opened 2026-09-03). Six items with evidence: the `ISO_SHn_*`/`SHn_*` net rename (pure rename, zero copper), motor-driver protection (D6-D9 SMAJ15CA clamp ~24 V vs the TB6612FNG's 15 V absolute-max VM), fuse and stall-threshold sizing, hold-up for U1 so motor inrush cannot brown out the ESP32, test points on `+12V`/`+3.3V_MOTOR` **plus net-name silkscreen on every TP**, and via-in-pad. Add new Rev 1.4 items there, not to the bring-up status log. **J3 is closed (stays DNP) and the enclosure work lives on the Enclosure Rev 3 list — do not re-add either.**

### Git state and release convention
Standardized 2026-08-27. Every shipped revision gets **both**:
- a `release/vX.Y` branch — a moving marker that may absorb later fixes for that revision
- an annotated `vX.Y-fab` tag — **frozen** at the exact commit the boards were built from

| Revision | Branch | Tag | Commit |
|---|---|---|---|
| 1.0/1.1 | `release/v1.0` | `v1.0-fab` | `41bff59` (2026-04-24) |
| 1.2 | `release/v1.2` | `v1.2-fab` | `b2b59b3` (2026-06-11) |
| 1.3 | `release/v1.3` | `v1.3-fab` | `3bc6a34` (2026-08-07) |

Bring-up fixes go on the branch — **never move a `-fab` tag**, or the as-fabbed state stops being recoverable. `main` was fast-forwarded to current on 2026-08-27; history is fully linear with no merge commits, so release branches fast-forward cleanly.

Pruned 2026-08-27: `feature/rework-vias` (fully merged, 0 unique commits vs `main`; its work is in `release/v1.2`'s history at `45e6a61`/`6322e81`). Note it enlarged vias and rerouted — it did **not** remove via-in-pad; 96 of 177 vias still sit inside SMD pads, which is why laminate Tg appears in the hot-attic notes.

### Three things deliberately NOT done — do not re-flag them
All were closed by the user. They are settled decisions, not oversights.

1. **Assembly remark left empty — intentional.** U1's footprint `DCDC_HYBRID_SLC03_TEC2` shares holes across Mean Well SLC03A-05 / Traco TBA 2-1211 / Heniper B1205S-3WR2L (silkscreen `M`/`H`/`T` + "POPULATE ONE"), and BOM/CPL carry only one position+rotation for the whole footprint. **JLCPCB's engineer reaches out with questions on every run of this board regardless**, and it has been placed several times without a remark — the hole-set question gets settled in that exchange. This run uses the **Heniper (LCSC C20622657)** → the `H` holes. Answer text kept in `production/JLCPCB-ORDER-NOTES.md` for when they ask. Electrically safe either way, since same-numbered pads share nets.
2. **J3 stays DNP — CLOSED 2026-09-03.** Do not put it back on a Rev 1.4 list. The plated through-holes are all that is needed: for the rare debugging session the user solders in their own connector, or just pushes pin-ended jumper wires into the holes to flash or read UART output. It is a debug path, not an everyday one, and native USB (GPIO19/20) covers normal use. The wrong LCSC field (C492404, a 5-pin part against the 7-pin footprint) only matters if J3 is ever populated by the fab — which it is not.
3. **Duplicate designators in JLCPCB's BOM — handled in their UI.** Their parts-matching flow duplicates designators when one LCSC appears on more than one BOM line (here: C1590 as `0.1uF`+`0.1uF 25V`, and C51927445 as `RESET`+`BOOT`). **Their tool prompts about it at upload and the user approves the duplicates each time**, so it self-resolves. A pre-merged `VSP-WSC-4_1.3_bom-UPLOAD.csv` exists if ever wanted but is not needed. See `production/JLCPCB-ORDER-NOTES.md`.

### Accepted trade-offs carried into this build
1. **USB_VBUS/J2 hole clearance exclusion.** One `hole_clearance` DRC error (0.20mm vs 0.25mm rule, at J2's own NPTH mounting hole) is suppressed via exclusion. Confirmed it's capped by the connector's own pad geometry, not trace routing — same category as 4 other pre-existing accepted exclusions on this connector footprint. Not fixable without a different Micro-USB footprint.
3. **Accepted trade-off — U16 via stub.** U16 (USB ESD protection) sits on B.Cu while J2 is F.Cu, so its D+/D- routing crosses layers via a ~2mm stub each side rather than a direct trace. Fine for a Full-Speed, occasional-use flashing port; revisit only if it ever causes a field problem — fixing it properly means moving U16 to F.Cu, which is a bigger rework.
4. **J3 (backup UART/RTS-DTR header) is DNP'd (2026-08-07).** Its LCSC (C492404) turned out to be a leftover from before J3 grew from 5→7 pins for the RTS/DTR rework — that part is actually a **5-pin** header (PZ254V-11-05P), silently mismatched against the 7-pin footprint (confirmed via the JLCPCB assembly-order BOM: it auto-matched to another 5-pin substitute, "Select by System," rather than flagging the mismatch). A real 7-pin equivalent (e.g. C492406, PZ254V-11-07P) wasn't in the user's stock either, and J3 is only for emergency reflashing if native USB (GPIO19/20) fails — not needed day-to-day — so the call was to DNP it rather than chase a part. **If J3 is ever un-DNP'd, fix the LCSC field first** — it's still the wrong 5-pin part. Stale "01x05" Description text (same root cause) fixed to "01x07" while in there.
5. **C10 and U12-U16 parts swapped for stock (2026-08-07):** C10 was 100uF 25V (C2840614, out of stock) → now **100uF 16V** (C7432790, HGC1210R5107M160NSVK) — same 1210 footprint, no PCB change; 16V chosen over 10V/6.3V alternatives to keep DC-bias derating low on the ~5V rail. U12-U16 (PRTR5V0U2X ESD protection) LCSC C12333 → **C5158049** (UMW/Youtai) — same SOT-143 footprint, no PCB change. Note for future part swaps: several other "PRTR5V0U2X"-labeled LCSC listings had wrong specs (unidirectional, or 14-25V standoff instead of ~5V) despite sharing the part name — verify bidirectional + working voltage before trusting a name match alone.

**Fabrication outputs: verified 2026-08-07 and used for the order.** The `VSP-WSC-4_1.3_*` set in `production/` — gerbers (11 layers + PTH/NPTH drills, outline 65.004 × 73.935 mm, PTH min drill 0.300 mm), `VSP-WSC-4_1.3_bom.csv` (40 lines / 106 placements) and `VSP-WSC-4_1.3_positions.csv` (106 rows, matches the BOM exactly, H1-H4 excluded). The older `bom.xls` / `bom.xlsx` / `bom.csv` in that folder are superseded; `gerbers/` and `gerbers-v1.1/` are stale v1.1-era folders.

**Source fix made while checking the CPL:** H1-H4 (mounting holes) were appearing in position files. They now carry `in_pos_files no` in the schematic and `exclude_from_pos_files` in the PCB, matching what TP1-TP7 already had — so future toolkit runs emit 106 CPL rows with no hand-editing. Verified by simulating the toolkit's own selection rules against the PCB.

## ESP32 variant selection — RESOLVED 2026-08-07, but read before changing the part
**Verdict: the board is correct. Keep C2913197. The documentation was the thing that was wrong.**

| LCSC | Variant | Flash | PSRAM | Ambient | |
|---|---|---|---|---|---|
| **C2913197** | **ESP32-S3-WROOM-1-N4** | 4 MB Quad | none | –40 ~ 85 °C | ✅ **what the design uses — correct** |
| C2913202 | ESP32-S3-WROOM-1-**N16R8** | 16 MB Quad | 8 MB **Octal** | –40 ~ 65 °C | ❌ what this file's key-parts table wrongly listed |

**Near-miss worth remembering.** Had anyone "corrected" the schematic to match the old docs, the N16R8 would have broken the board two ways: its Octal PSRAM consumes IO35/IO36/IO37 (datasheet Table 3 footnote b, p12 — *"connected to the module's internal Octal SPI PSRAM and cannot be used for other functions"*), which this design drives as `ISO_STBY`, `ISO_SH1_OPEN`, `ISO_SH1_CLOSED` on module pins 28/29/30 — losing Shade 1 and motor-driver standby — and it is rated only to **65 °C**, below what a hot attic reaches.

**Rules if the part is ever re-sourced:**
- **Never an R8 / R16V (Octal PSRAM) part** — steals IO35/36/37 *and* only 65 °C rated.
- R2 (Quad PSRAM) parts don't have the pin restriction and are 85 °C, but there's no reason to pay for PSRAM here.
- **H4** (4 MB, no PSRAM, –40~105 °C) would be the ideal attic part, but **JLCPCB does not stock it** (checked 2026-08-07 — no H4 in the ESP32-S3-WROOM-1 inventory at all). Every non-PSRAM option JLCPCB carries is 85 °C.
- So **N4 / C2913197 is the best available choice**, and it's also the cheapest at $4.13/1 with ~4700 in stock.

**Thermal caveat to carry into enclosure Rev 3:** the 85 °C figure is *ambient around the module*. Inside a sealed 3D-printed box in an attic, internal air runs hotter than attic ambient because of the board's own dissipation (LDO drop, DC-DC losses, driver quiescent, LEDs). A 60–70 °C attic plus enclosure rise eats into the 85 °C margin. Worth some ventilation in the Rev 3 design, and worth not mounting the box at the peak-heat ridge line.

## Hot-attic reliability notes (2026-08-07)
Ranked by how likely each is to actually bite, most-likely first:

1. **C33/C34 electrolytics — CHECKED 2026-08-07, no change needed.** The only electrolytics left on the board; everything else is ceramic. +12 V motor-rail bulk/inrush reservoir (`+12V` / `GND_MOTOR`), `Capacitor_SMD:CP_Elec_10x10.5`, **C7471896**.

   Actual spec: **1000 µF 25 V, –55 ~ +105 °C, 2000 h @ 105 °C, 60 mΩ ESR @ 100 kHz, 1.19 A ripple, D10×L10.5 mm.** Already a 105 °C part, so the thing that would have been a genuine problem (an 85 °C part) isn't present.

   Duty-cycle-weighted endurance for an attic (life doubles per 10 °C below rating; modelling 300 h/yr @ 80 °C, 800 @ 60 °C, 3000 @ 40 °C, 4660 @ 20 °C): consumes ~6.7 %/year → **~15 year service life**. A same-can 5000 h part would give ~37 years, which is past the useful life of everything else in the box.

   **Two reasons the ripple rating is not a concern here:** these caps see ripple only during the brief motor runs (a few tens of seconds a day), not continuously like an SMPS output cap — so ripple self-heating contributes essentially nothing to the thermal budget. And with two in parallel the combined 2.38 A rating (30 mΩ effective ESR) is well above anything the TB6612FNGs draw at the 1.4 A stall threshold.

   **Verdict: leave C7471896 in.** If a 105 °C / 5000 h part in the same 10 × 10.5 mm can happens to be in stock at similar cost, take it as free margin — but do not hold an order for it, and it does not justify any board change.
2. **ESP32 temperature grade** — resolved: N4 (85 °C) is the best JLCPCB stocks; H4 (105 °C) isn't available. See the section above, including the enclosure-ventilation caveat.
3. **Surface finish** — ENIG over HASL. Better pad flatness for the SOT-143 (U12-U16), the 0402s and the module's LGA thermal pad; also RoHS-compliant, which matters for the product track. Leaded HASL is fine electrically, this is about assembly yield and compliance.
4. **Laminate Tg — genuine but the smallest effect of the four.** At ~70 °C operating, every option on JLCPCB's list is far below its Tg, so this is not about surviving the heat. It is about *thermal-cycling fatigue* on plated through-hole barrels across daily attic swings, which matters a bit more here than usual because **96 of 177 vias sit inside SMD pads**. Higher Tg → lower z-axis CTE → less barrel strain per cycle. Board is 4-layer, so the valid choices are JLC-1 (Nan Ya NP-140F / NP-155F) or JLC-4 (up to Shengyi S1000-2M TG170). Best margin: **JLC-4 / S1000-2M TG170**. Minimal change: **JLC-1 / NP-155F**, staying in the already-selected certification family. Honest framing: Tg140 FR-4 ships in millions of hot-environment consumer products; this is cheap insurance, not a fix for a known problem.

## Rev 1.3 schematic work already done
- ACS723 on GPIO5 (ADC1_CH4), TMP235 on GPIO4 (ADC1_CH3) — both moved off ADC2 to avoid WiFi noise, then relocated again during the layout-driven GPIO reshuffle (see full map in vsp-wsc4-todo.md)
- Terminal block J4: **Phoenix Contact 1786918** (20-pin dual-row 3.5mm, right-angle — cable exits sideways, not up); mating terminal block is 1790182; both ECAD/3D libraries committed in project-local `1786918/` and `1790182/` folders
  - Pinout (final, layout-driven): top row 1=SW1_UP, 2=GND_ISO, 3=SW2_UP, 4=SW3_UP, 5=GND_ISO, 6=SW4_UP, 7-10=SHADE1-4_UP; bottom row 11=SW1_DOWN, 12=GND_ISO, 13=SW2_DOWN, 14=SW3_DOWN, 15=GND_ISO, 16=SW4_DOWN, 17-20=SHADE1-4_DOWN (motors and switches connect across vertical pairs)
- `switch_inputs.kicad_sch` created (page 9): 8-channel RC+TVS protection, 4× PRTR5V0U2X + 8× **1kΩ R0603** (note: 0603, not 0402 as previously recorded here; LCSC C14676) + 8× 100nF C0402, plus **C40-C43** 100nF TVS VCC decoupling added 2026-08-05; wired through to ESP32 GPIOs (function-named labels, e.g. `SW1_UP_IN`, not raw pin numbers)
  - Topology is connector → **1k series R** → node shared by 100nF cap + PRTR5V0U2X I/O + ESP32 GPIO. The TVS is on the **MCU side** of the series resistor (R limits surge current into the TVS; TVS clamps right at the pin being protected). Note this is the opposite convention from U16 on USB, which sits on the *connector* side of R9/R10 — both are valid, just be aware they differ.
  - **No external pull-ups.** Switches pull to GND_ISO, so firmware MUST enable internal pull-ups on all 8. Two land on strapping pins: **GPIO46** (SW1_UP) and **GPIO3** (SW1_DOWN). Both verified safe against the datasheet (Table 4, p13): GPIO46's reset default is **pull-down = 0**, and the switch also pulls to GND, so GPIO46 reads 0 at boot either way — a held switch can never produce an invalid boot-mode combination. GPIO3 defaults floating and only selects the JTAG signal source, which is unaffected.
    - Correction (2026-08-07): an earlier note here claimed GPIO46 is *input-only* on the ESP32-S3. That is **wrong** — datasheet Table 3 lists IO46 (pin 16) as type **I/O/T**, a full bidirectional GPIO. The safety conclusion above is unchanged, but GPIO46 can be driven as an output if ever needed.
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
| ESP32 module | ESP32-S3-WROOM-1-**N4** | **C2913197** ✅ correct — verified 2026-08-07 | –40~85 °C. **This table used to say C2913202, which is the N16R8** — see "ESP32 variant selection" below before ever changing it. |
| DC-DC isolated | Heniper B1205S-3WR2L | C20622657 | |

## Key files
- `docs/project-context/vsp-wsc4-handover.md` — full Rev 1.2 hardware/firmware detail
- `docs/project-context/vsp-wsc4-todo.md` — full TODO list
- `docs/project-context/vsp-wsc4-rev13-bringup-status.md` — **live bring-up status: start here**
- `docs/project-context/vsp-wsc4-rev13-bringup.yaml` — Rev 1.3 bench config (AP-only, no secrets needed)
- `docs/project-context/vsp-wsc4-rev13-bringup-procedure.md` — staged bench/lab test plan
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
**WARNING: `sch export netlist` is NOT read-only.** It rewrote `usb-c-5v.kicad_sch` (342 lines — junction coordinates shifted by a constant offset) and reordered `used_designators` in `barn-blinds-controller.kicad_pro` on 2026-09-03. Run `git status` after any `kicad-cli` invocation and `git checkout --` anything you did not mean to change.

Diffing the netlist before/after an edit is the reliable way to prove connectivity was preserved — schematic geometry checks can miss pins whose position is far from the symbol origin.