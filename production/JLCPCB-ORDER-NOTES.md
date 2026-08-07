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

## BOM correction (done 2026-08-07)

The Fabrication Toolkit export contained **16 duplicate designator entries** — the source
files are clean, every refdes is unique in both schematic and PCB, so this was purely an
export artifact:

- `0.1uF` / C1590 — 29 entries for 15 real parts (C11, C15, C18, C21-C27, C30, C31, C38, C39 each listed twice)
- `RESET` / C51927445 — 4 entries for 2 real parts (SW1, SW2 each twice)

Also corrected the stale Comment on C10, which read `100uF25V` while both schematic and
PCB say `100uF 16V`. The LCSC (C7432790) was already the correct 16 V part, so this was
description-only — JLCPCB places by part number.

Files:
- `bom.xlsx` / `bom.csv` — **corrected, upload one of these**
- `bom-ORIGINAL-with-dupes.xls` — the original, kept for reference
- Verified: 38 lines, **106 placements**, zero duplicate designators, exactly matching the
  106 populated refs on the board. Correctly excluded: H1-H4 (mounting holes), J3 (DNP),
  TP1-TP7 (test points).

**If you re-run Fabrication Toolkit, re-check for this duplication before uploading** —
it will likely reappear.

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

## Open item — C33/C34 electrolytics

Not blocking this PCB order (footprint is unchanged either way), but decide before the
boards are populated. `Capacitor_SMD:CP_Elec_10x10.5`, 1000 µF 25 V, currently C7471896,
+12 V motor-rail bulk.

**First check whether C7471896 is 85 °C or 105 °C.** If 85 °C, swap it — that's the actual
risk. If already 105 °C, the upgrade is optional. Target: same 10 × 10.5 mm can, ≥ 25 V,
~1000 µF, **105 °C, load life ≥ 2000 h (prefer 5000 h+)**. Life math and duty-cycle
reasoning in CLAUDE.md → "Hot-attic reliability notes".

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
