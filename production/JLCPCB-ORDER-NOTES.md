# JLCPCB order notes — VSP-WSC-4 Rev 1.3

Working checklist for the Rev 1.3 order. Tick items off as they're set in the JLCPCB UI.

## Assembly remark — paste this into the "Assembly remark" field

> U1 uses a shared multi-part footprint (DCDC_HYBRID_SLC03_TEC2) that overlays the
> hole patterns for three different isolated DC-DC modules. The silkscreen marks the
> three hole sets with the letters M / H / T next to "POPULATE ONE".
>
> For this order, populate U1 with the Heniper B1205S-3WR2L (LCSC C20622657, supplied
> from our JLCPCB parts inventory) using the "H" hole set only. Leave the M and T
> holes empty.
>
> The BOM and CPL carry a single position and rotation for the whole footprint, so
> please use this note to select the correct holes.
>
> J3 is intentionally DNP (not in the BOM) — please leave it unpopulated.

## Order settings to change from the current draft

| Setting | Current | Change to | Why |
|---|---|---|---|
| Assembly remark | No | **Paste the text above** | U1 hole-set ambiguity; JLCPCB cannot infer it from BOM/CPL |
| Confirm Parts Placement | No | **Yes** | First run of a revision with newly placed parts + the U1 ambiguity |
| Surface Finish | HASL (with lead) | **ENIG** | Pad flatness for SOT-143 / 0402 / module LGA pad; RoHS for the product track |
| Base Material | JLC-1 Nan Ya NP-140F | **JLC-4 Shengyi S1000-2M TG170** (best) or **JLC-1 NP-155F** (minimal change) | Thermal-cycling margin in an attic; 96 of 177 vias are in-pad. Lowest-impact of the changes — see CLAUDE.md "Hot-attic reliability notes". Board is 4-layer, so only JLC-1 and JLC-4 are valid certification types; JLC-2/3 are single/two-layer only |
| Product Description | `jlcpcb_missing_text/...` | **Fill it in** | Unfilled field; usually feeds the customs declaration |
| BOM file | `bom.xls` (had 16 duplicate designators) | **`bom.xlsx`** (corrected) | See below |

## Which files to upload (toolkit re-run 2026-08-07 12:40)

Upload the **Fabrication Toolkit** outputs, all verified clean:

| File | Status |
|---|---|
| `VSP-WSC-4_1.3.zip` | gerbers — 11 layers + PTH/NPTH drills, verified |
| `VSP-WSC-4_1.3_bom.csv` | 40 lines, 106 placements, zero duplicates |
| `VSP-WSC-4_1.3_positions.csv` | 106 rows, matches BOM exactly (H1-H4 removed) |

**Correction to earlier guidance in this file.** The 16 duplicate designators found on
2026-08-07 were **not** produced by the Fabrication Toolkit. The toolkit's own
`VSP-WSC-4_1.3_bom.csv` has never contained duplicates — checked against the previously
committed copy. The duplicated file was `bom.xls`, whose header is
`Comment | Designator | Footprint | JLCPCB Part #` — the **JLCPCB Assembly Order** format,
i.e. a file that came back from JLCPCB's own parts-matching flow after upload.

So the earlier note here saying "re-run the toolkit and it will likely reappear" was
wrong. What to actually watch: **if you download and re-upload JLCPCB's own assembly-order
BOM, re-check it for duplicate designators.** Uploading the toolkit's CSV directly avoids
the problem entirely.

Superseded files kept only for reference: `bom.xls`, `bom.xlsx`, `bom.csv`,
`bom-ORIGINAL-with-dupes.xls`. **Do not upload these** — use the `VSP-WSC-4_1.3_*` set.

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

## Placement preview — what to actually look at

You have "Confirm Parts Placement" turned on, so use it deliberately. The toolkit applied
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
