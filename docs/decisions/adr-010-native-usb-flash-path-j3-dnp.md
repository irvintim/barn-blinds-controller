# ADR-010: Native USB is the flash path; J3 stays DNP

**Date:** 2026-08-07, closed 2026-09-03 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

Rev 1.3 grew J3 (UART0 debug header, GPIO43/44) from 5 to 7 pins to expose
RTS/DTR to an Espressif-reference auto-reset circuit (Q3/Q4 S8050, C21 on
EN). At order time its LCSC field (C492404) turned out to be a leftover
**5-pin** part, silently mismatched against the 7-pin footprint, and no 7-pin
part was in stock.

The ESP32-S3's USB-Serial-JTAG is a ROM peripheral. It flashes a blank chip
and auto-resets with no external circuitry.

## Decision

**J3 is DNP.** Native USB (J2, GPIO19/20) is the flash and console path. The
plated holes stay. For the rare debug session, solder in a header or push
jumper pins into the holes. Do not put J3 back on a fab list.

## Consequences

- The auto-reset circuit exists on the board but is only reachable through
  the bare J3 holes.
- The ROM's boot messages (`invalid header: 0xffffffff`) go to UART0, so a
  blank board's USB CDC port enumerates but stays silent, and a virgin board
  boot-loops while looking like a failing USB port. See the bring-up
  procedure's triage table.
- Proven 2026-10-11: a USB-TTL adapter on the J3 holes erased and flashed
  Tasmota.
- **If J3 is ever populated by the fab, fix its LCSC field first.** It still
  carries the 5-pin C492404.
