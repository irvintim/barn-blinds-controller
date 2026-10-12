# VSP-WSC-4 main board (KiCad 10)

Open `barn-blinds-controller.kicad_pro`. Everything the project needs is under
this folder: `lib/New_Library.kicad_sym` (U1, J4, TMP235),
`lib/barn_shade_controller.pretty/`, and `lib/3dmodels/` (referenced as
`${KIPRJMOD}/lib/3dmodels/...`). Standard KiCad libraries plus the Espressif
and JLCPCB PCM add-ons supply the rest.

- `fab/vsp-wsc4-rev1.2/`, `fab/vsp-wsc4-rev1.3/`: the files each order was
  built from. Rev 1.3 order notes: `fab/vsp-wsc4-rev1.3/JLCPCB-ORDER-NOTES.md`.
- `jlcpcb-export-steps.md`: how to generate and archive a fab set.
- `barn-blinds-controller.kicad_dru`: isolation-barrier audit rule, warning
  severity (ADR-004).
- `lib/artwork/`: silkscreen graphics sources.

Checks (from WSL, run in this folder):

```bash
K="/mnt/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
"$K" sch erc --output erc.rpt --severity-error --severity-warning barn-blinds-controller.kicad_sch   # 92 violations, 5 errors, all known
"$K" pcb drc --output drc.rpt --severity-error barn-blinds-controller.kicad_pcb                      # 0 / 0
git status   # kicad-cli can rewrite files, so check after every run
```

Branches: Rev 1.3 fixes go on `release/v1.3`; Rev 1.4 work on `main` (ADR-020).
Never move a `vX.Y-fab` tag (ADR-016).
