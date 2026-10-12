# Barn Blinds Controller (Vesprio VSP-WSC-4)

4-channel motorized window-shade controller: ESP32-S3-WROOM-1-N4, two TB6612FNG
H-bridges, galvanically isolated logic/motor domains, 8 wall-switch inputs on one
20-pin Phoenix terminal block. Two firmware tracks: ESPHome (the owner's barn units)
and Tasmota (product).

## Where things are

```
pcb/main-board/          KiCad 10 project (open barn-blinds-controller.kicad_pro)
  lib/                   project symbols, footprints, 3D models (${KIPRJMOD}/lib/...)
  fab/vsp-wsc4-rev1.x/   the exact files each JLCPCB order was built from
  jlcpcb-export-steps.md how to generate and archive a fab set
enclosure/               FreeCAD case: rev2/ (current, fits Rev 1.2), archive/rev1/, reference/
firmware/esphome/        barn-overhead.yaml, barn-windows.yaml, bring-up, standalone; legacy/ = Rev 1.2
firmware/tasmota/        tasmota-setup-commands.txt (template-based, no Berry)
docs/architecture.md     LIVING current state: power tree, GPIO/J4 map, firmware rules, tooling
docs/decisions/          ADRs: why things are the way they are (immutable)
docs/bringup/            Rev 1.3 bring-up status log (read first for hardware work) + procedure
docs/todo.md             TODOs, incl. the canonical "Rev 1.4 PCB Changes" list
docs/handover-rev1.2.md  historical Rev 1.2 snapshot
```

## Status (2026-10-12)

- **Rev 1.3 is the production board**: motor-less bring-up complete 2026-10-11,
  reorder as-is (ADR-017). Board 2 = `barn-overhead`, board 3 = `barn-windows`,
  board 1 is out of service (U8 destroyed by a non-shade test motor).
- **Next hardware step: the barn motor test.** Order and pass criteria are in
  `docs/bringup/vsp-wsc4-rev13-bringup-status.md`, "THE NEXT THING TO DO".
- **Next design job: Enclosure Rev 3** for the Rev 1.3 board (ADR-019,
  `enclosure/README.md`, `docs/todo.md` "Enclosure Rev 3 TODO").
- Rev 1.4 is open on `main`, but only needed to go general-purpose (ADR-018).

## Branches

- `release/v1.3`: production line for Rev 1.3. `main`: Rev 1.4 development (ADR-020).
- Each fabbed revision has a `release/vX.Y` branch and a frozen `vX.Y-fab` tag.
  **Never move a `-fab` tag** (ADR-016). Keep history linear: rebase or
  cherry-pick, no merge commits.
- The `-fab` tags and `release/v1.0`/`v1.2` predate the 2026-10-12 reorganization
  and use the old flat layout. That is intended.

## Non-negotiable rules

- **No motor goes on any board** until the real shade motor's inrush and stall
  current are measured off-board against the TB6612FNG's 1.2 A continuous / 3.2 A
  peak. Bench loads are 20-33 Ω / 10 W resistors, never below 20 Ω.
- **Never flash `firmware/esphome/legacy/barn-shades-pcb-rev1.2.yaml` onto a Rev 1.3 board.**
- **Firmware outputs are named for the physical J4 terminal, not the net names.**
  The `ISO_SHn_*` nets are crossed 1↔2 / 3↔4 on Rev 1.3 (ADR-012). The correct
  GPIO table is in `docs/architecture.md`. Don't "fix" ids back to the net names.
- Every config: ACS725 `amps = (Vout - 1.65) / 0.264`; internal pull-ups on switch
  GPIOs 3, 46, 9, 10, 11, 12, 13, 14 (GPIO46 explicitly); software debounce;
  D4/D5 (GPIO6/7) are on until driven LOW. Full list: `docs/architecture.md`.
- Tasmota: apply the Template, never the Module page (it hides GPIO35-37), and set
  `Interlock` after the template is active (ADR-013).
- Flash over native USB (J2). A blank board boot-loops and *looks* like a bad USB
  port. It isn't; see the bring-up procedure's triage table.
- Never re-source the ESP32 as an R8/R16V (octal PSRAM) part (ADR-002).

## Settled. Read the ADR before raising any of these

The fuse is not the stall protection (ADR-005) · J3 stays DNP (ADR-010) · empty
JLCPCB assembly remark for U1 (ADR-014) · JLCPCB's duplicate BOM designators are
approved in their UI (ADR-014) · via-in-pad is closed (`docs/architecture.md`) ·
0.20 mm ISO-to-MOTOR gap is fine for 12 V SELV (ADR-004) · laminate/finish
(ADR-015) · the Rev 1.2-era layout margins listed in `docs/architecture.md`.

To change a settled decision, write a new ADR that supersedes it. New Rev 1.4
items go in `docs/todo.md` "Rev 1.4 PCB Changes", not the bring-up log.

## KiCad workflow

kicad-cli is the Windows install; run it from `pcb/main-board/`:

```bash
K="/mnt/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
"$K" sch erc --output "$(wslpath -w /tmp/erc.rpt)" --severity-error --severity-warning barn-blinds-controller.kicad_sch  # baseline 92 (5 errors, all benign)
"$K" pcb drc --output "$(wslpath -w /tmp/drc.rpt)" --severity-error barn-blinds-controller.kicad_pcb                   # baseline 0 / 0
"$K" sch export netlist --format kicadsexpr --output "$(wslpath -w /tmp/net.net)" barn-blinds-controller.kicad_sch
```

- **`sch export netlist` is not read-only**: it has rewritten `usb-c-5v.kicad_sch`
  and the `.kicad_pro`. Run `git status` after any kicad-cli call and
  `git checkout --` anything you didn't mean to change.
- Diffing the netlist before/after an edit is the reliable way to prove connectivity
  was preserved.
- A `.kicad_dru` `(condition "...")` must be on one line, or it silently matches nothing.
- Fabrication Toolkit writes to `pcb/main-board/production/` (gitignored scratch).
  Copy what you order from into `fab/vsp-wsc4-revX.Y/`.
