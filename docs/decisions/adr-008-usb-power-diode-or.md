# ADR-008: USB power diode-ORed into the single isolated logic rail

**Date:** 2026-06-30, diode parts revised 2026-07-07 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

The ESP32 side should run from USB alone, for flashing and bench work with no
12 V present, as well as from the isolated DC-DC in service. U1 (Heniper
B1205S-3WR2L) is **unregulated**, so it cannot be paralleled directly with
USB VBUS. A second, USB-only regulator was considered.

## Decision

Diode-OR `+5V_ISO` (from U1) and `USB_VBUS` into `+5V_OR`, which feeds one
AP2112K-3.3 LDO for the whole `+3.3V_ISO` rail (ESP32, isolators, sensors).
No second regulator.

Rev 1.3 replaced the BAT54C (200 mA, carrying the entire ESP32 load including
350-500 mA WiFi bursts) with **two SS34 Schottkys (D10 = VBUS, D11 = 5V_ISO,
3 A each)**.

## Consequences

- USB alone powers the logic side, enough to flash and run firmware with the
  motor side dead.
- Because U1 is unregulated, `+5V_ISO` ≈ 0.42 × `+12V_RAW` (measured). The
  ESP32 browns out when `+12V_RAW` falls below ~8.5 V. Motor inrush that sags
  the 12 V rail takes the MCU down with it, which is Rev 1.4's hold-up item
  (ADR-018).
- A USB-TTL adapter's 3.3 V pin cannot power the board through WiFi start-up.
  It brownout-loops (bring-up Finding 16).
