# Enclosure

FreeCAD, 3D printed, two-piece (bottom tray + top lid).

- `rev3/`: **current design, for the Rev 1.3 board.** Generated,
  spreadsheet-driven model plus a fit checker. Start with `rev3/README.md`.
- `rev2/project-case-rev2.FCStd`: previous design, sized for the Rev 1.2
  board. `rev2/exports/` holds its print exports.
- `archive/rev1/`: first case and its exports.
- `reference/vsp-wsc4-rev1.3-board.step`: the as-fabbed Rev 1.3 board with all
  components, exported 2026-10-12. Use this for Rev 3.
- `reference/barn-blinds-controller.FCStd`: older board import (Rev 1.2 era).
- `reference/1597DIN2GY.stp`: DIN-rail enclosure reference model.

Rev 3 requirements: ADR-019, with two numbers corrected by ADR-021 (DIN
holes 12.5 mm pitch; no extra Z height needed).
