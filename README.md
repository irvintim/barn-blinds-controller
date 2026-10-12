# barn-blinds-controller (Vesprio VSP-WSC-4)

4-channel motorized window-shade controller: ESP32-S3-WROOM-1-N4, two TB6612FNG
H-bridges, isolated logic and motor domains, 8 wall-switch inputs. Runs ESPHome
(the owner's barn units) or Tasmota (product track).

**Rev 1.3 is the production board** (`release/v1.3`, tag `v1.3-fab`).
`main` carries Rev 1.4 development.

```
pcb/main-board/      KiCad project; lib/ (project symbols, footprints, 3D models); fab/<rev>/ (files each order was built from)
enclosure/           3D-printed case: rev2/ (current, Rev 1.2 board), archive/rev1/, reference/ (board STEP, DIN clip)
firmware/esphome/    barn-overhead, barn-windows, bench bring-up, standalone; legacy/ = Rev 1.2 pins
firmware/tasmota/    template + setup command sequence
docs/architecture.md current state: power, GPIO/terminal map, firmware rules
docs/decisions/      ADRs (why things are the way they are)
docs/bringup/        Rev 1.3 bring-up status log and procedure
docs/todo.md         TODO lists, including the Rev 1.4 change list
docs/datasheets/     part datasheets
purchasing/          JLCPCB parts inventory
```

Start with `docs/architecture.md`, then `docs/bringup/vsp-wsc4-rev13-bringup-status.md`.
