# JLCPCB Export from KiCad

## Prerequisites

- Fabrication Toolkit plugin installed (Plugin and Content Manager > search "JLC")
- LCSC part numbers in the `LCSC` field of each schematic symbol

## U1 — hybrid DC-DC footprint, needs a manual assembly note

`DCDC_HYBRID_SLC03_TEC2` (used by U1) is **one footprint that shares holes across three pin-compatible isolated DC-DC modules** — Mean Well SLC03A-05, Traco TBA 2-1211, and Heniper B1205S-3WR2L — silkscreened with per-hole `M`/`H`/`T` letters and a "POPULATE ONE" note. **This run uses the Heniper (LCSC C20622657, in your JLCPCB inventory) — populate only the holes marked `H`.**

- Electrically this is safe either way: pads sharing a number (2/2, 3/3, 4/4) are tied to the same net regardless of which physical hole is used, so there's no shorting/miswiring risk. Lead spacing is also part-specific, so the wrong holes likely won't physically accept the part's leads.
- What it *doesn't* do automatically: the BOM/CPL only carry one reference position + rotation for the whole footprint — there's no standard field for "populate this subset of holes." JLCPCB's assembly team won't know to use the `H` holes unless you tell them.
- **Action: add an order remark/special-instruction when submitting for assembly** — e.g. "U1 is a shared multi-footprint THT pattern; populate only the 4 holes marked H (Heniper) on the top silkscreen; leave M and T holes empty."
- The `H` hole spacing in the footprint (2.54mm input pair, then 5.08mm-spaced output pins) reads as a standard isolated-DC-DC SIP-4 layout — consistent with what's expected, but I couldn't pull a clean copy of Heniper's mechanical drawing to confirm byte-exact, so do a quick visual check against the datasheet (or the physical part) before it goes out.

## Steps

### 1. Sync schematic to PCB

Press **F8** in PCBnew to push any schematic changes to the board before generating files.

### 2. Run the plugin

Click the Fabrication Toolkit button in the PCBnew toolbar.

Recommended options:
- **Archive name**: `${TITLE}_${REVISION}` (produces a versioned zip)
- **Apply automatic translations**: checked
- **Apply automatic fill for all zones**: checked
- **Exclude DNP components from BOM**: checked
- **Generate Backups**: checked

Click **Generate**. The plugin outputs gerbers, BOM, and CPL all at once into your project directory.

### 3. Upload to JLCPCB

1. Go to jlcpcb.com, click `Order Now`
2. Upload the generated gerber zip
3. Set board specs (qty, color, thickness, layers)
4. Enable `PCB Assembly`, select side(s)
5. Upload the BOM CSV
6. Upload the CPL CSV
7. Review component matches — confirm LCSC part numbers are correct
8. **Check the placement preview carefully** — rotation issues are common. Fix any obviously wrong orientations before confirming.

### 4. Fixing rotation issues

If the placement preview shows a component rotated wrong, add an `FT Rotation Offset` field to that symbol in the schematic with the correction in degrees (positive = counter-clockwise). Then re-sync (F8) and regenerate.

Use this table to determine the correction needed based on what you see in the JLCPCB preview:

| KiCad footprint | X arrow | Y arrow |
|---|---|---|
| 0 deg, Front | right | up |
| 0 deg, Back | left | down |
| 180 deg, Front | left | down |
| 180 deg, Back | right | up |
| 90 deg, Front or Back | up | left |
| -90 deg, Front or Back | down | right |

## Notes

- The `LCSC` field name is a recognized fallback — no renaming needed
- Always verify the JLCPCB placement preview before confirming the order

---

## OLD MANUAL METHOD (kept for reference)

### 1. Gerbers

1. Open PCBnew, `File > Fabrication Outputs > Gerbers`
2. Set output folder
3. Layers to include:
   - F.Cu, B.Cu, In1.Cu, In2.Cu
   - F.Paste, B.Paste
   - F.Silkscreen, B.Silkscreen
   - F.Mask, B.Mask
   - Edge.Cuts
4. Settings:
   - Check `Plot footprint values` and `Plot reference designators`
   - Check `Use Protel filename extensions`
   - Coordinate format: 4.6, metric
5. Click `Plot`
6. Click `Generate Drill Files` — use excellon format, metric, minimal header, PTH and NPTH in separate files
7. Zip all generated files together

## 2. BOM

1. `File > Fabrication Outputs > BOM`
2. Use the bom_csv_grouped_by_value_with_fp plugin, or export as CSV
3. The raw KiCad BOM needs reformatting for JLCPCB — required columns are:
   - `Comment` (value)
   - `Designator`
   - `Footprint`
   - `LCSC` (your LCSC/JLCPCB part numbers from the BOM field)
4. Easiest approach — open the CSV in a spreadsheet and rename/reorder columns to match JLCPCB's template, or use the [KiCad JLCPCB tools plugin](https://github.com/Bouni/kicad-jlcpcb-tools) to automate this

## 3. CPL (Component Placement List)

1. `File > Fabrication Outputs > Component Placement`
2. Export as CSV, both front and back
3. JLCPCB requires specific column names — the raw KiCad export won't match
4. Rename columns:
   - `Ref` → `Designator`
   - `PosX` → `Mid X`
   - `PosY` → `Mid Y`
   - `Rot` → `Rotation`
   - `Side` → `Layer`
5. `Layer` values must be `top` or `bottom` (lowercase)
6. Double-check rotation values for any non-standard footprints — JLCPCB and KiCad sometimes differ by 90 or 180 degrees for certain packages. Check the JLCPCB preview after upload and correct any obviously rotated parts before ordering.

## 4. Upload to JLCPCB

1. Go to jlcpcb.com, click `Order Now`
2. Upload the gerber zip
3. Set board specs (qty, color, thickness, layers etc.)
4. Enable `PCB Assembly`, select side(s)
5. Upload BOM CSV
6. Upload CPL CSV
7. Review component matches — confirm LCSC part numbers are correct
8. Review the placement viewer carefully — fix any rotation issues before confirming
9. Mark hand-solder / DNP parts as needed

## Notes

- The KiCad JLCPCB tools plugin (Bouni) automates BOM and CPL conversion and is worth installing if doing multiple revisions
- Always check the JLCPCB placement preview — rotation issues are common and easier to fix before fabrication than after
