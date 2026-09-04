# VSP-WSC-4 Project TODO Lists

## Rev 1.3 PCB Changes

### Already done in schematic:
- [x] ACS723 moved to GPIO10 (ADC1_CH9)
- [x] TMP235 moved to GPIO7 (ADC1_CH6)
- [x] Terminal block J3: replaced JL271R-35008G01 (8-pin) with Phoenix Contact 1054070 (20-pin dual-row, 3.5mm pitch, JLCPCB C20306292) in motor_outputs.kicad_sch
- [x] J4 pinout (final, verified against netlist 2026-07-07 — layout-driven, intentional): top row pos 1=SW1_UP, 2=GND_ISO, 3=SW2_UP, 4=SW3_UP, 5=GND_ISO, 6=SW4_UP, 7-10=SHADE1-4_UP; bottom row pos 11=SW1_DOWN, 12=GND_ISO, 13=SW2_DOWN, 14=SW3_DOWN, 15=GND_ISO, 16=SW4_DOWN, 17-20=SHADE1-4_DOWN. Each motor connects across its vertical pair (e.g. Shade 1 = pos 7 + pos 17); each wall switch across its vertical pair with adjacent GND_ISO commons
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

### Pre-fab QA review changes (2026-07-07) — schematic done, PCB placement pending:
- [x] **R1-R8 (switch input series resistors): 10k → 1k.** Root cause: inputs rely on ESP32 internal ~45k pull-up; with 10k series, a closed switch divided to 0.6V at the pin vs 0.825V VIL — marginal. With 1k: ~0.1-0.23V worst case. Same 0603 footprint, no layout change.
  - ⚠️ **LCSC discrepancy — decide before ordering.** This line originally specified **C21190**, but the symbols had *no* LCSC field at all (the value change landed, the part number never did — they would have come back unpopulated). Set to **C14676** on 2026-08-05 because that is the exact part R14 already uses for 1K 0603 in this design, so it consolidates to one BOM line / one feeder. If C21190 was chosen deliberately, change R1-R8 in `switch_inputs.kicad_sch` back.
- [x] **U11: ACS723LLCTR-05AB → ACS725LLCTR-05AB-T (LCSC C3684552).** ACS723 requires 4.5-5.5V supply but was running at 3.3V (out of spec, though empirically working on Rev 1.2). ACS725 is the native 3.3V version, same SOIC-8 pinout, rated -40~+150°C (attic-safe). **FIRMWARE CHANGE REQUIRED:** sensitivity is 264mV/A (was 400mV/A) — formula becomes `(x - 1.65) / 0.264`; recompute stall threshold (1.4A → 1.65 + 1.4×0.264 ≈ 2.02V, within ADC range at 12dB).
- [x] **D1: SS34 → SS54 (LCSC C22452).** 3A → 5A input diode headroom for multi-motor load; C22452 is SS54 in the same SMA package — no layout change.
- [x] **D2 (BAT54C, 200mA) removed — replaced with D10 + D11 (SS34, 3A each, LCSC C8678).** The old BAT54C carried the entire ESP32 load permanently (WiFi bursts 350-500mA vs 200mA rating). Diode-OR topology retained (required: B1205S is unregulated, can't be paralleled with USB directly). D11 = 5V_ISO→5V_OR, D10 = USB VBUS→5V_OR. **PCB: remove D2 (SOT-23), place 2× SMA.**
- [x] **U16 (PRTR5V0U2X, LCSC C12333) added: USB D+/D- ESD protection.** I/O1→USB_IN_DP, I/O2→USB_IN_DN, VCC→USB_VBUS, GND→GND_ISO. **PCB: place SOT-143 near J2, keep stubs short.**
- [x] Filled all missing LCSC fields for assembly BOM: C1-C8 = C1525 (100nF 0402), C10 = C2840614 (100uF 25V 1210 — upgraded from 10V rating, same footprint), C17 = C15849 (1uF 0603), Q1/Q2 = C8545 (2N7002), Q3/Q4 = C2146 (S8050), U12-U15 = C12333 (PRTR5V0U2X)
- [x] **PCB work: DONE 2026-08-05.** D2 removed; D10, D11, U16 placed and routed; F8 sync applied all value changes in place. Verified by footprint-level diff: exactly the intended delta, nothing else moved. DRC 0 errors / 0 unconnected pads. Courtyard checks (normally disabled in this project) re-enabled in a scratch copy — no overlaps on any new part.

### Second QA pass (2026-08-05) — schematic items DONE, PCB items OPEN
Done and committed (schematic side):
- [x] R1-R8 given an LCSC part number (see discrepancy note above) — they had none, would have shipped unpopulated.
- [x] TP1-TP7 set `in_bom no` + `in_pos_files no` — were adding 7 junk lines to the JLCPCB BOM.
- [x] Removed 4 orphan dangling wire stubs in `switch_inputs.kicad_sch` (netlist verified byte-identical after).
- [x] Orphan `STBY` hierarchical label in `motor_drivers.kicad_sch` **converted to a global label** (not deleted). ⚠️ It looked like a free-floating orphan but its wire actually carried **U9 pin 19**; deleting it silently dropped U9.19 off the STBY net. Converting keeps the connection and clears the ERC `hier_label_mismatch`.
- [x] Added **C40-C43** (100nF 0402, C1525) for U12-U15 VCC decoupling.
- [x] Added `barn-blinds-controller.kicad_dru` isolation-barrier audit rule.

Done 2026-08-06/07 (PCB / GUI work):
- [x] Placed C40-C43, ~1.8-2.6mm from each TVS VCC pin (C40→U12, C41→U13, C42→U14, C43→U15).
- [x] Widened `+5V_OR` to 0.5mm (one negligible 0.565mm stub still at 0.2mm, not worth chasing) and `USB_VBUS` to 0.4mm.
- [x] Moved U16 nearer J2 (center-to-center 6.1mm→4.0mm). Still B.Cu vs J2's F.Cu — accepted trade-off, see "PICK UP HERE" above.
- [x] J2 LCSC set to C397452 (same Micro-USB part as zen32-esphome). J4 LCSC set to C6652293 — intentional: pre-purchased JLCPCB inventory part, number still needed so JLCPCB places it.
- [x] D10/D11 silkscreen reference overlap fixed.
- [x] Regenerated gerbers/BOM/CPL — Fabrication Toolkit re-run 2026-08-07 12:40 as `VSP-WSC-4_1.3`, fully verified (see below). `gerbers/` and `gerbers-v1.1/` remain stale v1.1-era folders.
- [x] **U1 assembly remark — deliberately skipped.** Not an oversight: JLCPCB's engineer reaches out with questions on every run of this board anyway, and it has been placed several times without one. Answer text kept in `production/JLCPCB-ORDER-NOTES.md`. **Do not re-flag this.**

### Stock-driven part swaps (2026-08-07) — schematic-only, same footprints, PICK UP HERE has full detail:
- [x] C10: 100uF 25V (C2840614, OOS) → 100uF 16V (C7432790, HGC1210R5107M160NSVK) — same 1210 footprint.
- [x] U12-U16: PRTR5V0U2X LCSC C12333 (OOS) → C5158049 (UMW/Youtai) — same SOT-143 footprint.
- [x] **J3 marked DNP.** Its LCSC (C492404) was a leftover 5-pin part mismatched against the 7-pin footprint since the RTS/DTR rework grew it from 5→7 pins; a real 7-pin part wasn't in stock either, and J3 is only a backup flashing path (native USB is primary) — not worth chasing for this run. Fix the LCSC before ever un-DNP'ing it. Stale "01x05" Description text (same root cause) corrected to "01x07."
- [x] Regenerated gerbers/BOM/CPL after these three changes — toolkit re-run 2026-08-07 12:40.

### Fabrication output verification (2026-08-07) — all clean, order placed
- **Gerbers** (`VSP-WSC-4_1.3.zip`): 11 layers (F/In1/In2/B copper, both masks, both silks, both pastes, Edge_Cuts) + PTH/NPTH drills and maps. Edge_Cuts parses to **65.004 × 73.935 mm**, matching the board. PTH min drill **0.300 mm**, matching the ordered spec. CPL shares the gerber coordinate frame.
- **BOM** (`VSP-WSC-4_1.3_bom.csv`): 40 lines, 106 placements, Quantity column consistent, no missing LCSC, matches the 106 populated board refs. J3 correctly dropped by `EXCLUDE DNP`.
- **CPL** (`VSP-WSC-4_1.3_positions.csv`): originally carried H1-H4 (mounting holes, nothing to place). **Fixed at the source** — H1-H4 given `in_pos_files no` in the schematic and `exclude_from_pos_files` in the PCB, same as TP1-TP7. Future runs emit 106 rows with no hand-editing; verified by simulating the toolkit's selection rules. DRC after the edit: 0 errors, 0 unconnected pads.
- **Duplicate designators in JLCPCB's own BOM export — accepted, not fixed.** Their parts-matching flow duplicates designators when one LCSC spans multiple BOM lines (C1590 as `0.1uF`+`0.1uF 25V`; C51927445 as `RESET`+`BOOT`). **Their tool prompts and the user approves the dups each run** — it self-resolves. Pre-merged `VSP-WSC-4_1.3_bom-UPLOAD.csv` exists if ever wanted. **Do not re-flag this.**

### Order placed 2026-08-07 — settings of record
Gerber `VSP-WSC-4_1.3_Y18` · 5 boards · PCBA both sides, qty 5 · 4-layer, 1 oz outer / 0.5 oz inner · **S1000H TG155 (JLC-4)** · **ENIG 1 U"** · Plugged vias · Confirm Parts Placement **Yes** · Photo Confirmation **Yes** · UL type JLC-4 · depanelled before delivery.

On the placement/photo confirmations, scrutinise the parts whose LCSC was *not* in the proven Rev 1.2 build: **D1, Q1-Q4, U11, U12-U16** (and J2/J4, visually obvious). D6-D9 are bidirectional TVS so rotation is harmless; D10/D11 use C8678 which was in the Rev 1.2 build.

### Firmware bring-up checklist (Rev 1.3 boards):
- Enable **internal pull-ups on all 8 switch input GPIOs**: 3, 46, 9, 10, 11, 12, 13, 14. There are no external pull-ups. Note GPIO46 is a strapping pin whose reset default is pull-*down* — the pull-up must be set explicitly in firmware; switches short to GND_ISO so a held switch can never create an invalid boot combination.
- **GPIO6 (D4 white LED) and GPIO7 (D5 blue LED): drive LOW to turn off, HIGH/floating = on.** Both LEDs are hardware-default-ON from power-up until firmware intervenes (by design — they track raw power).
- **ACS725 formula:** `amps = (Vout - 1.65) / 0.264` (was /0.4 for ACS723). Update stall detection threshold accordingly.
- **Serial terminal gotcha:** with the new RTS/DTR auto-reset circuit on J3, any terminal program that asserts DTR without RTS will hold the ESP32 in reset until DTR is released (identical behavior to NodeMCU-style dev boards). esptool/ESPHome/Tasmota flashers handle this correctly; if the board appears dead over a serial monitor, check the monitor's DTR/RTS settings. **Note: J3 is DNP'd on Rev 1.3 boards from this run — this only applies if it's populated later.** Native USB (GPIO19/20) is the primary/only flash path as shipped.

### Completed in Rev 1.3 — both shipped on the boards in hand
- [x] **Auto-reset circuit — DONE.** Resolved 2026-07-06/07: J3 grown from 5 to 7 pins exposing RTS/DTR, driven by the Espressif reference two-transistor circuit (Q3/Q4 S8050) with C21 1uF on EN. Confirmed the native USB path (GPIO19/20, USB-Serial-JTAG) auto-resets on its own with no hardware needed, so the circuit only matters for the UART path. **Caveat for these boards: J3 is DNP'd on the 2026-08-07 run**, so the auto-reset circuit is present but unreachable — native USB is the only flash path as shipped.
- [x] **D4/D5 software-controllable LEDs — DONE.** GPIO6 drives D4 (white, +3.3V_ISO) and GPIO7 drives D5 (blue) via Q1/Q2 2N7002. Both are hardware-default-ON from power-up until firmware pulls them low. D5's gate crosses the isolation barrier through spare U5 channel A, and D5 feeds from +12V_RAW so its current bypasses the ACS725 measurement.

- [x] MANUAL: TVS wire cleanup in switch_inputs.kicad_sch — 4 orphan dangling stubs removed 2026-08-05. Remaining 37 `endpoint_off_grid` ERC warnings are inherent to this project's `Device:C` symbol variant (pins at ±1.524mm cannot land on a 1.27mm grid) and affect C1-C8 equally; cosmetic only.

### Still needed — schematic:
- [ ] Nothing open for Rev 1.3. New items go here as bring-up finds them.


---

## Rev 1.4 PCB Changes

**Canonical list.** Opened 2026-09-03 from Rev 1.3 bring-up. Background and
evidence for most of these is in `vsp-wsc4-rev13-bringup-status.md`.

### 1. Rename `ISO_SHn_*` / `SHn_*` nets to match the SHADEn terminal — PURE RENAME, zero copper
Highest value for the least effort. Today the net names lie: `SH3_*` reaches
the SHADE4 terminal and `SH4_*` reaches SHADE3, with the same 1<->2 swap on U9.

**Root cause:** when the pin order was reworked for the new J4 terminal block,
the labels on the TB6612FNG **output** side were re-pointed but the **input**
side was not. The isolators (U4/U5/U6, ISO7760DBQ) pair cleanly 1:1 and add no
cross of their own — verified against the netlist, and confirmed on hardware
2026-09-03 (Shade 1->1, 2->2, 4->4).

**The fix:** the crossing is symmetric, so just swap the label pairs along the
whole path — **3 <-> 4** on the U4/U8 side and **1 <-> 2** on the U6/U9 side,
at both the `ISO_SHn_*` (ESP32->isolator) and `SHn_*` (isolator->driver) nets.
Nothing physical moves; the names simply start describing where the signal
actually goes. Afterwards the GPIO map reads naturally with the **same pin
assignments in use today**:

| Terminal | J4 | OPEN | CLOSED | PWM |
|---|---|---|---|---|
| SHADE1 | 7 / 17 | GPIO48 | GPIO47 | GPIO21 |
| SHADE2 | 8 / 18 | GPIO36 | GPIO37 | GPIO38 |
| SHADE3 | 9 / 19 | GPIO41 | GPIO40 | GPIO39 |
| SHADE4 | 10 / 20 | GPIO42 | GPIO2 | GPIO1 |

Do **not** "fix" it by rerouting `OUTC`->`AIN1` etc. — that costs real B.Cu
routing between U4/U8 and U6/U9 for an identical result.

Until this ships, every firmware config (bring-up, production ESPHome, and
Tasmota) must keep applying the swap by hand. That is a labelling trap that
will keep costing time.

### 2. Make the output stage survive an UNKNOWN load — the governing requirement
**Design target set 2026-09-03: the outputs must be robust against whatever
gets connected, not merely matched to the known-good shade motors.**

The shade motors were characterised early in the project and are not the design
case. What actually killed board 1's U8 was a *non-shade* motor connected during
bench testing. If this ever becomes a more general-purpose product, there is no
way to know what a user will plug in — a stalled motor, a wrong motor, a shorted
lead, a much larger inductive load. **The protection has to hold regardless.**

What the current design gets wrong:

| | Now | Problem |
|---|---|---|
| Driver | TB6612FNG | VM absolute max **15 V** on a 12 V rail — almost no headroom. 1.2 A continuous / 3.2 A peak. Its only self-protection is thermal shutdown, which demonstrably did not save it |
| Output clamp | D6-D9, SMAJ15CA | 15 V standoff, clamps around **24 V** — i.e. *above* the driver's absolute max. It cannot protect the part it sits beside |
| Fusing | F1-F4, 1.1 A hold / 2.2 A trip | Correctly scoped — the fuse is the *catastrophic fault* backstop, not the stall protection (see item 3). But polyfuses are slow: the driver dies in microseconds, the PTC responds in seconds, so the fuse cannot save the driver either |
| Fault attribution | one ACS725 on the whole 12 V rail | Cannot tell which channel is faulting, and cannot see a fault at all while several channels run |

Directions to evaluate (none chosen yet):
- **A driver with real current regulation**, so an overload is limited rather
  than fatal. E.g. **DRV8871** — 6.5-45 V (enormous headroom over 12 V), 3.6 A
  peak, and an **adjustable internal current limit set by one resistor**, plus
  thermal shutdown and UVLO. Single-channel, so four parts instead of two duals,
  and the PWM scheme changes (drive on IN1/IN2 rather than a separate PWM pin).
  Alternatives in the same family: DRV8873, DRV8243.
- **Hard output short protection** — short-to-ground and short-to-supply.
- **Clamping that engages below the driver's absolute max**, not above it.
- **Per-channel current sense** instead of one rail-level ACS725, so a fault can
  be attributed and shut down individually.
- **Firmware soft-start** regardless of hardware choice — never energise a bridge
  at 100 % duty from rest. Inrush equals stall current. See the firmware list.

### 3. Prove the stall-detection path — it is the designed protection and has never worked
**Settled design decision, not up for re-litigation:** the fuse is *not* the
stall protection. F1-F4 handle catastrophic faults (a short, or a load the board
was never meant to drive). **Stall protection is the current reading — that is
why the ACS723/ACS725 is in the circuit at all.** F1-F4 sitting above the
motors' stall current is therefore correct by design. Do not "fix" the fuse
rating to chase stalls.

The problem is that the mechanism which *is* supposed to do the job has never
been shown to work:

- **The divisor is wrong.** `/0.4` (ACS723) must become **`/0.264`** (ACS725).
  Until that is corrected the current reading is simply wrong.
- **The 1.4 A threshold is unvalidated and probably far too high.** A
  2026-09-03 recollection put a hand-held full stall on the shade motors "well
  under 1 A each" — but that is **fuzzy memory, not data**, and the original
  measurements were never recorded. The motors are on the job site now. If it is
  even roughly right, the threshold never fires and the designed stall
  protection has never functioned. **Re-measure; do not size from the
  recollection.**
- **The resolution may not support a low threshold.** At 0.264 V/A a 0.7 A stall
  is only ~185 mV above the 1.65 V quiescent — a small signal on a 12-bit ADC
  with WiFi running. Confirm the noise floor during the resistive-load
  calibration. If it is marginal, per-channel current sense (item 2) stops being
  a nice-to-have.
- **One rail-level sensor cannot attribute a fault to a channel**, nor see a
  single channel stall while others run. See item 2.

**Next action, needs no motor:** prove the `/0.264` divisor against a known
resistive load, and characterise the noise floor at the same time.

### 4. Hold-up for U1 so motor inrush cannot brown out the ESP32
U1's only input reservoir is **C9, 22 uF** on `+12V_RAW`, and the ISO side has
roughly **1-2 ms** of hold-up through `C10`. The 2x1000 uF bulk (C33/C34) is on
`+12V`, downstream, and buffers the *motors*, not the MCU. So a motor inrush
that sags the 12 V rail drops the ESP32 outright.

That is not just an uptime problem: **each brownout shut the bridge off
instantly with energy still in the windings, and the resulting flyback is what
killed U8.** Preventing MCU brownout is driver protection.

Proposed: a small series diode plus a local bulk cap on U1's input, so the
DC-DC feeds from a reservoir the motor rail cannot pull down.

### 5. Add test points on `+12V` and `+3.3V_MOTOR`, and label ALL test points with their net name
The two rails most worth probing during bring-up both currently require
touching an IC pin. TP1-TP7 already exist for other nets; extend the set.

**Silkscreen every test point with its net name, not just `TP1`/`TP4`.** As it
stands you have to open the schematic to find out what a test point is
connected to, which is exactly the wrong time to be doing that. Applies to the
existing TP1-TP7 as well as the new ones.

Also worth a labelled pad at C33/C34: probing **J1 pin 1 -> GND_MOTOR reads
open even on a board with a hard 12 V short**, because `Net-(D1-A)` shows D1 is
a *series* reverse-polarity diode between J1 and `+12V_RAW`, so the meter sees
its blocking direction. That cost real debugging time on 2026-09-03.

---

## Rev 1.3 GPIO Map (final, as of 2026-07-06; GPIO6/7 and the GPIO46 note corrected 2026-08-27)

Reassigned to eliminate crossed leads during PCB layout. Verified against the ESP32-S3-WROOM-1 module pinout with no duplicate assignments, no WiFi/ADC2 conflicts (only TMP235/ACS723 do real analog sensing, both on ADC1), and no strapping-pin or input-only-pin misuse.

> **WARNING (2026-08-28):** the `ISO_SHn_*` names below are the *net* names, and
> they do **not** match the SHADEn terminal each one drives. The A/B channels are
> crossed on both TB6612FNGs, swapped within each pair (1↔2, 3↔4). See "Motor
> channel cross" in CLAUDE.md for the correct GPIO → J4 terminal table. Firmware
> must use that table, not these names.

| Pin | GPIO | Function | Notes |
|---|---|---|---|
| 3 | EN | Reset button | |
| 4 | GPIO4 | TMP235 Vout | ADC1_CH3 |
| 5 | GPIO5 | ACS723 VIOUT | ADC1_CH4 |
| 6 | GPIO6 | D4 white LED | added after this map was written; hardware-default-ON, drive LOW to turn off |
| 7 | GPIO7 | D5 blue LED | added after this map was written; hardware-default-ON, gate crosses isolation via spare U5 ch A |
| 8 | GPIO15 | *(empty)* | |
| 9 | GPIO16 | Status LED | |
| 10 | GPIO17 | *(empty)* | freed from old UART header |
| 11 | GPIO18 | *(empty)* | freed from old UART header |
| 12 | GPIO8 | *(empty)* | |
| 13 | GPIO19 | USB D- | native USB |
| 14 | GPIO20 | USB D+ | native USB |
| 15 | GPIO3 | SW1_DOWN_IN | switch input |
| 16 | GPIO46 | SW1_UP_IN | switch input — strapping pin, reset default pull-*down*, so firmware must set the pull-up explicitly. **Not input-only** (datasheet Table 3 lists IO46 as I/O/T); an earlier note here said otherwise and was wrong. |
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
- [ ] **Soft-start PWM ramp on every motor start** — never energise a bridge at 100 % duty from rest. Inrush equals stall current, and on Rev 1.3 that is what browned out the ESP32 and killed board 1's U8 (Rev 1.4 item 2). Needed in the bring-up, production ESPHome and Tasmota configs.
- [ ] **Apply the SHADEn channel swap** in the production ESPHome config and in Tasmota until the Rev 1.4 net rename ships — see "Rev 1.4 PCB Changes" item 1 for the GPIO table.
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

**The Rev 1.3 board is physically larger than the one the current enclosure was
designed around, so the box has to be reworked regardless.** Do that work here,
not on the PCB list.

- [ ] Resize for the Rev 1.3 board outline (65.004 x 73.935 mm).
- [ ] **Thermal check, not a redesign — ventilation already exists in the current
      small enclosure.** Just confirm it still works once the box grows: the
      ESP32-S3-WROOM-1-N4 is rated to 85 °C *ambient around the module*, and a
      sealed printed box in an attic runs hotter inside than the attic air
      because of the board's own dissipation (LDO drop, DC-DC losses, driver
      quiescent, LEDs). Also worth not mounting at the peak-heat ridge line.


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
