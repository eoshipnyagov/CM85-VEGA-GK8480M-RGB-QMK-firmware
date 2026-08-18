# Dark Project CM85 Vega / GK8480M-RGB-QMK

Reverse-engineering workspace for the `WB32FQ95RCT4` keyboard firmware.

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

## Status

The first pass confirms a WB32/ChibiOS/QMK/Vial application image with USB keyboard and two vendor HID interfaces. GPIO roles, matrix wiring, OLED controller, RGB implementation and exact keymap still need hardware-assisted validation.

