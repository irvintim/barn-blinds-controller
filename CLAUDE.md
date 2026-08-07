# Barn Blinds Controller — Claude Context

## What this is
Vesprio VSP-WSC-4: 4-channel motorized window shade controller, ESP32-S3-WROOM-1-N4, dual firmware track (ESPHome personal use / Tasmota product). See `docs/project-context/vsp-wsc4-handover.md` for full hardware detail and GPIO map.

## Current state (as of 2026-08-07)
- **PCB:** Rev 1.3, **fab-ready.** All PICK UP HERE items from the 2026-08-05 QA pass are done: C40-C43 placed (~1.8-2.6mm from U12-U15 pin 4), +5V_OR/USB_VBUS widened, U16 moved closer to J2, D10/D11 silkscreen fixed, LCSC added for J2 (C397452) and J4 (C6652293 — pre-purchased JLCPCB inventory part, number needed so JLCPCB places it). DRC: 0 unconnected pads, 0 real errors, 114 footprints. Rev 1.2 was assembled and working (ESPHome only; Tasmota broken on Shades 3&4 due to GPIO43/44 = U0TX/RX conflict — fixed in Rev 1.3).
- **Fabrication Toolkit run 2026-08-07** — archive `VSP-WSC-4_1.3`. See "Before submitting the JLCPCB order" below for one manual step still needed at order time.
- **Schematic:** Rev 1.3 passed a full pre-fab QA review (2026-07-07) plus two physical/layout QA passes (2026-08-05 and 2026-08-06/07, see below). ERC errors steady at 5, all benign (4× missing PWR_FLAG, 1× J2-GND/U1-(-Vout) both-power-output which is correct by design).
- **Also in Rev 1.3:** D4/D5 LEDs software-controllable (GPIO6/7, hardware-default-ON; D5 crosses isolation via spare U5 channel); RTS/DTR auto-reset on 7-pin J3 (Espressif reference two-transistor circuit); Micro-USB (not USB-C); switch inputs wired to ESP32 — see todo.md "Rev 1.3 GPIO Map" for pinout and "Firmware bring-up checklist" before first flash
- **Enclosure:** FreeCAD Rev 2 (`project-case-rev2.FCStd`), 3D printed, test print 2 in progress

## PICK UP HERE — before submitting the JLCPCB order
Board and schematic are done. One manual step remains, plus a few accepted trade-offs/decisions to know about:

1. **U1's DC-DC footprint is a shared multi-part pattern — add an assembly order remark.** `DCDC_HYBRID_SLC03_TEC2` shares holes across Mean Well SLC03A-05 / Traco TBA 2-1211 / Heniper B1205S-3WR2L (silkscreen `M`/`H`/`T` letters + "POPULATE ONE"). This run uses the **Heniper (LCSC C20622657, in your JLCPCB inventory)**. BOM/CPL only carry one position+rotation for the whole footprint — there's no field for "use this subset of holes," so JLCPCB's assembly team needs an explicit note or they won't know to use the `H` holes. Full detail in `docs/project-context/jlcpcb-export-steps.md`. (Electrically safe regardless — same-numbered pads share nets — but do add the remark so the right physical part goes in the right holes.)
2. **Accepted trade-off — USB_VBUS/J2 hole clearance exclusion.** One `hole_clearance` DRC error (0.20mm vs 0.25mm rule, at J2's own NPTH mounting hole) is suppressed via exclusion. Confirmed it's capped by the connector's own pad geometry, not trace routing — same category as 4 other pre-existing accepted exclusions on this connector footprint. Not fixable without a different Micro-USB footprint.
3. **Accepted trade-off — U16 via stub.** U16 (USB ESD protection) sits on B.Cu while J2 is F.Cu, so its D+/D- routing crosses layers via a ~2mm stub each side rather than a direct trace. Fine for a Full-Speed, occasional-use flashing port; revisit only if it ever causes a field problem — fixing it properly means moving U16 to F.Cu, which is a bigger rework.
4. **J3 (backup UART/RTS-DTR header) is DNP'd (2026-08-07).** Its LCSC (C492404) turned out to be a leftover from before J3 grew from 5→7 pins for the RTS/DTR rework — that part is actually a **5-pin** header (PZ254V-11-05P), silently mismatched against the 7-pin footprint (confirmed via the JLCPCB assembly-order BOM: it auto-matched to another 5-pin substitute, "Select by System," rather than flagging the mismatch). A real 7-pin equivalent (e.g. C492406, PZ254V-11-07P) wasn't in the user's stock either, and J3 is only for emergency reflashing if native USB (GPIO19/20) fails — not needed day-to-day — so the call was to DNP it rather than chase a part. **If J3 is ever un-DNP'd, fix the LCSC field first** — it's still the wrong 5-pin part. Stale "01x05" Description text (same root cause) fixed to "01x07" while in there.
5. **C10 and U12-U16 parts swapped for stock (2026-08-07):** C10 was 100uF 25V (C2840614, out of stock) → now **100uF 16V** (C7432790, HGC1210R5107M160NSVK) — same 1210 footprint, no PCB change; 16V chosen over 10V/6.3V alternatives to keep DC-bias derating low on the ~5V rail. U12-U16 (PRTR5V0U2X ESD protection) LCSC C12333 → **C5158049** (UMW/Youtai) — same SOT-143 footprint, no PCB change. Note for future part swaps: several other "PRTR5V0U2X"-labeled LCSC listings had wrong specs (unidirectional, or 14-25V standoff instead of ~5V) despite sharing the part name — verify bidirectional + working voltage before trusting a name match alone.

Then: regenerate gerbers/BOM/CPL (`docs/project-context/jlcpcb-export-steps.md`) — the C10/U12-U16/J3 changes above aren't in the `VSP-WSC-4_1.3` archive yet, so re-run Fabrication Toolkit before ordering. `gerbers/` and `gerbers-v1.1/` folders are stale (v1.1 era) regardless.

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

## Hot-attic reliability notes (2026-08-07)
Ranked by how likely each is to actually bite, most-likely first:

1. **C33/C34 — 1000 µF 25 V aluminium electrolytics are the weak link.** The only electrolytics left on the board; everything else is ceramic. They are the +12 V motor-rail bulk/inrush reservoir (`+12V` / `GND_MOTOR`), SMD can, `Capacitor_SMD:CP_Elec_10x10.5`, currently **C7471896**. HF bypass on that rail is already covered by C32/C36/C37 (10 µF 0805) and C38/C39 (0.1 µF 0603), so these two are purely bulk — which means the selection is about **endurance, not ESR finesse**.

   **First step: check what C7471896 actually is.** If it's an 85 °C part, replace it — that's the real problem. If it's already 105 °C, the upgrade is optional.

   **Selection criteria for the replacement** (drop-in, no PCB change):
   - Same 10 × 10.5 mm SMD can, ≥ 25 V, ~1000 µF
   - **105 °C rated**, load life ≥ 2000 h, prefer 5000 h+
   - Polymer/hybrid would be better still but 1000 µF/25 V in a 10 mm can is expensive and hard to source — a good 105 °C long-life aluminium is the pragmatic pick

   **What the numbers actually say** (life doubles per 10 °C below rating). Assume the cap sees ~80 °C at attic peak (70 °C ambient + enclosure rise):
   - 105 °C / 2000 h part → 2000 × 2^2.5 ≈ **11,300 h** at a *sustained* 80 °C ≈ 1.3 years
   - 105 °C / 5000 h part → ≈ **28,000 h** ≈ 3.2 years

   But it is never sustained. Weighting a plausible duty cycle — say ~500 h/year at 80 °C and the rest near 30 °C — a 105 °C/2000 h part consumes roughly 7 %/year, i.e. **~15 year life**; a 5000 h part is comfortably beyond the rest of the design. So this is worth doing, but it is a "spend $1 for peace of mind" item, not a crisis. An 85 °C part under the same duty cycle is the one that would genuinely disappoint.
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
Diffing the netlist before/after an edit is the reliable way to prove connectivity was preserved — schematic geometry checks can miss pins whose position is far from the symbol origin.