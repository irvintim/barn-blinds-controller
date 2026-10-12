# Firmware

Rules every config must follow (terminal-named outputs, ACS725 `/0.264`,
pull-ups, debounce, soft-start) are in `docs/architecture.md`, "Firmware rules".

## ESPHome (`esphome/`)

| File | Board | Use |
|---|---|---|
| `barn-overhead.yaml` | Rev 1.3, board 2 | Barn overhead/skylight shades |
| `barn-windows.yaml` | Rev 1.3, board 3 | Barn window shades (differs from overhead only in its top block) |
| `vsp-wsc4-rev13-bringup.yaml` | Rev 1.3 | Bench bring-up, AP-only fallback, no motors |
| `vsp-wsc4-standalone.yaml` | still Rev 1.2 pins | Product-track ESPHome config, needs porting |
| `legacy/barn-shades-pcb-rev1.2.yaml` | **Rev 1.2 only** | Never flash onto Rev 1.3 |

Copy `secrets.yaml.example` to `secrets.yaml` here (gitignored). Builds run
on an ESPHome Docker dashboard (bring-up Finding 9); flash over native USB (J2).

## Tasmota (`tasmota/`)

`tasmota-setup-commands.txt`: stock `tasmota32s3.factory.bin` plus a Template
(never the Module page, ADR-013), then interlock and shutter setup in order.
