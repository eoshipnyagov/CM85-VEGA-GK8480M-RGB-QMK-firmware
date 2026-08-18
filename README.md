# Dark Project KD85 Vega / GK8480M-RGB-QMK

Reverse-engineering workspace for the `WB32FQ95RCT4` keyboard firmware.

The keyboard was initially identified as CM85; the current hardware identification is KD85.

## Contents

- `firmware/original/` — original firmware image and its checksum.
- `docs/reverse-engineering.md` — current binary analysis and confidence levels.
- `docs/roadmap.md` — next investigation steps.

## Reference image

`VEGA_vial_v1_01_20231201.bin`

- Size: 48,220 bytes (`0xBC5C`)
- SHA-256: `ADC61BBEA2A6A60629BB8AC69E7A44DCE2CAF4BBB8663A6CB28F68C0A76935CC7`
- Assumed flash base: `0x08000000`

The image is kept as evidence. Do not flash modified images to the keyboard without a recovery plan.

## Hardware inventory

The keyboard consists of a main PCB and a separate daughterboard containing the volume encoder, approximately 128×64 display, and USB connector.

Markings recorded from the main PCB:

- `CHMC D8563F S2461` — exact component role not yet identified.
- `PY25Q128HA` — likely SPI NOR flash, 128-Mbit class.
- `2E1TH1D` — exact component role not yet identified.
- `P25D80SH 3J1PC2F` — likely SPI NOR flash, 128-Mbit class; needs confirmation.
- `HFD80CP100 229GNWD0a` — additional controller/IC; role pending. The main keyboard MCU is confirmed as `WB32FQ95RCT4`.
- Two `HFD5501L CQ` devices — marking now read as `1L`; one is near USB and may be related to RGB/backlight control, the second is near `HFD80CP100` and `334PD45`.
- `334PD45` — small 16-pin IC, probably a power-management/power-distribution controller; located beside `HFD80CP100` and the second `HFD5501L`.
- Three crystal components are marked `XT`; the 12 MHz crystal beside the right-side controller cluster most likely clocks `HFD80CP100`.

Current auxiliary-controller hypothesis: `HFD80CP100` is paired with the nearby `PY25Q128HA` 16 MB SPI flash and `CHMC D8563F` RTC to operate the display/encoder subsystem. This remains to be confirmed by tracing the SPI/I2C and inter-board connections.

The retail box also lists `HFD80CP100` and `HFD582CHFS` alongside the TFT display. The keyboard is not specified as wireless, so `HFD582CHFS` is currently treated only as a platform/variant clue; it is not identified as an installed radio module without a matching physical chip and RF circuitry on this PCB.
- `U9` — small square IC, approximately four pins per side, located near a suspected crystal; marking not yet readable.
- Two additional ICs have markings too small to read reliably.

## Status

The first pass confirms a WB32/ChibiOS/QMK/Vial application image with USB keyboard and two vendor HID interfaces. GPIO roles, matrix wiring, OLED controller, RGB implementation and exact keymap still need hardware-assisted validation.
