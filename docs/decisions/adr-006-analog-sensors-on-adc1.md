# ADR-006: All analog sensing on ADC1

**Date:** 2026-06-27 (recorded retroactively 2026-10-12)
**Status:** Accepted

## Context

On Rev 1.2 the current sensor (GPIO14) and TMP235 (GPIO15) were on ADC2. The
ESP32-S3's ADC2 is shared with the WiFi radio and reads noisy, or not at all,
while WiFi is active. A noisy current reading means false stall trips
(ADR-005).

## Decision

Every pin doing real analog measurement goes on **ADC1**. On Rev 1.3 that is
TMP235 → GPIO4 (ADC1_CH3) and ACS725 → GPIO5 (ADC1_CH4).

## Consequences

- ESPHome configs use `attenuation: 12db` on both.
- The TMP235 sits beside U7, the board's hot spot, so "Board Temperature"
  reads U7 rather than enclosure air (bring-up Finding 12). This is
  placement, not ADC choice. See the Rev 1.4 list.
