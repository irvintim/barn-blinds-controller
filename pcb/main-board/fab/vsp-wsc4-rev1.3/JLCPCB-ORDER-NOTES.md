# JLCPCB order notes — VSP-WSC-4 Rev 1.3

**Order placed 2026-08-07 (gerber `VSP-WSC-4_1.3_Y18`). Nothing outstanding — waiting on boards.**

## Two things deliberately NOT done — do not re-flag these

Both were reviewed and closed by the user from direct experience with this vendor. They
are settled, not oversights. A future session should not re-raise them.

**1. Assembly remark left empty — intentional.** The concern was that U1's footprint
(`DCDC_HYBRID_SLC03_TEC2`) overlays three DC-DC hole patterns (silkscreen `M`/`H`/`T`,
"POPULATE ONE") and the BOM/CPL can't express which set to use. In practice **JLCPCB's
engineer reaches out with questions on every run of this board anyway**, and it has been
placed several times without a remark. The hole-set question gets handled in that
conversation. Keep the text below on hand for answering them, but there is no need to set
the field.

> U1 uses a shared multi-part footprint (DCDC_HYBRID_SLC03_TEC2) that overlays the
> hole patterns for three different isolated DC-DC modules. The silkscreen marks the
> three hole sets with the letters M / H / T next to "POPULATE ONE".
>
> For this order, populate U1 with the Heniper B1205S-3WR2L (LCSC C20622657, supplied
> from our JLCPCB parts inventory) using the "H" hole set only. Leave the M and T
> holes empty.
>
> J3 is intentionally DNP (not in the BOM) — please leave it unpopulated.

**2. Duplicate designators in JLCPCB's BOM — handled in their UI, not worth engineering
around.** JLCPCB's parts-matching flow duplicates designators when one LCSC part number
appears on more than one BOM line; it merges the lines but concatenates the designator
lists wrongly. Two part numbers trip it here — C1590 (`0.1uF` ×11 and `0.1uF 25V` ×4) and
C51927445 (`RESET`/SW1 and `BOOT`/SW2) — accounting for all 16 duplicates.

**Their BOM tool prompts about the duplicates at upload time and the user approves them,
so it resolves itself every run.** No file surgery needed.

`VSP-WSC-4_1.3_bom-UPLOAD.csv` (every LCSC collapsed to one line) exists in this folder if
a pre-merged BOM is ever wanted, but it is **not required** and was not used for this
order. The permanent fix, if it ever becomes worth it, is to normalise the Value strings in
the schematic so the toolkit emits one line per part number to begin with.

## Order settings as placed (gerber Y18)

| Setting | Value |
|---|---|
| Base Material | S1000H TG155 (JLC-4) — Tg155, good thermal-cycling margin |
| Surface Finish | ENIG, 1 U" gold |
| Confirm Parts Placement | Yes |
| Photo Confirmation | Yes |
| UL Type | JLC-4, consistent with the laminate |
| Layers / copper | 4 layer, 1 oz outer / 0.5 oz inner |
| Via Covering | Plugged |
| Qty | 5 PCB + 5 PCBA, both sides |

## Files used for this order

| File | Verified |
|---|---|
| `VSP-WSC-4_1.3.zip` | 11 layers + PTH/NPTH drills, outline 65.004 × 73.935 mm, PTH min drill 0.300 mm |
| `VSP-WSC-4_1.3_bom.csv` | 40 lines, 106 placements, matches the board |
| `VSP-WSC-4_1.3_positions.csv` | 106 rows, matches the BOM exactly (H1-H4 excluded) |

## ESP32 variant — RESOLVED 2026-08-07, no action

**C2913197 = ESP32-S3-WROOM-1-N4. The board is correct, leave it alone.**

The docs were what was wrong: CLAUDE.md's key-parts table listed C2913202, which is the
**N16R8** — Octal PSRAM (consumes IO35/36/37, which this design drives as ISO_STBY /
ISO_SH1_OPEN / ISO_SH1_CLOSED) and rated only –40~65 °C. Had anyone "fixed" the schematic
to match the docs, it would have broken Shade 1 and the driver standby line and put the
module below attic temperature. Table now corrected.

H4 (105 °C) would be the ideal attic part but **JLCPCB does not stock it** — every
non-PSRAM ESP32-S3-WROOM-1 they carry is 85 °C. N4 is the best available and also the
cheapest ($4.13/1, ~4700 in stock).

## C33/C34 electrolytics — CHECKED 2026-08-07, no action

C7471896 is **already a 105 °C part**: 1000 µF 25 V, –55~+105 °C, 2000 h @ 105 °C,
60 mΩ ESR, 1.19 A ripple, D10×L10.5 mm. Duty-cycle-weighted for an attic that works out
to **~15 year service life**, and ripple self-heating is negligible because these only
see current during the brief motor runs. **Leave them in.** Full reasoning in
CLAUDE.md → "Hot-attic reliability notes".

## Placement preview / photo confirmation — what to actually look at

Both "Confirm Parts Placement" and "Photo Confirmation" are on, so use them. The toolkit applied
JLCPCB rotation corrections to **20 of 36 polarity-critical parts** (`AUTO TRANSLATE: true`).
Those corrections are internally consistent — every part sharing an LCSC number got the
same delta — and the same toolkit produced the Rev 1.2 boards that assembled correctly, so
the mechanism is proven. What can't be verified offline is absolute correctness against
JLCPCB's own orientation library.

Focus the review on parts whose **LCSC number was not in the proven Rev 1.2 build**, since
those have no track record with this workflow:

| Part | Why it matters |
|---|---|
| **D1** (SS54, C22452) | Input protection diode, new PN. Reversed = board never powers up |
| **Q1, Q2** (2N7002, C8545) | LED drive MOSFETs |
| **Q3, Q4** (S8050, C2146) | RTS/DTR auto-reset transistors, new circuit |
| **U11** (ACS725, C3684552) | Current sensor, changed from ACS723 |
| **U12-U16** (PRTR5V0U2X, C5158049) | ESD arrays — never built before, and the PN changed |
| **J2, J4** | Connectors; orientation is visually obvious, easy win |

Lower risk, no need to dwell: **D6-D9 (SMAJ15CA) are bidirectional TVS** — the `CA` suffix
means rotation is electrically harmless. **D10/D11** use C8678, which *was* in the Rev 1.2
build. **C40-C43** and the other new ceramics are non-polarised.

## Verified correct — no action needed

- Board is 65.00 × 73.93 mm; the order's 75 mm width is JLCPCB's edge rails (added by
  JLCPCB, depaneled before delivery). Height matches exactly.
- Assembly Side "Both Sides" is right — parts on F.Cu and B.Cu.
- Inner copper 0.5 oz is fine: **no current-carrying traces on inner layers at all**,
  inner copper is ground pour only. Every power trace is on 1 oz outer copper.
- Via Covering "Plugged" is well justified — 96 of 177 vias land in SMD pads. Rev 1.2
  assembled successfully with 68, so it is a proven configuration for this design.
- J3 is DNP in schematic (`dnp yes`), PCB (`attr through_hole dnp`) and absent from the
  BOM — the wrong 5-pin part cannot get placed.
- TP1-TP7 carry `exclude_from_pos_files exclude_from_bom` on the PCB.
