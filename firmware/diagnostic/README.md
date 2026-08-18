# KD85 VEGA diagnostic firmware — iteration 1

This is the first code iteration for the WB32FQ95RCT4 controller. It is a
small QMK/Vial overlay, not a complete KD85 keyboard target: the real matrix
pins, RGB pins, display bus, and secondary-controller bus still need to be
confirmed from the PCB.

## What it does

It adds a private command range (`0xE0`–`0xE5`) to QMK's existing Raw HID/VIA
transport while preserving the normal keyboard and Vial handlers.

Implemented:

- `0xE0 PING`: returns status, sequence, and a 32-bit QMK uptime value.
- `0xE1 INFO`: returns protocol revision and the `KD85 VEGA` signature.
- `0xE2`–`0xE5`: return `NOT_IMPLEMENTED`; they are placeholders for a
  read-only I²C scan/read and SPI JEDEC/read phase.

The code performs no GPIO writes outside normal QMK board startup and does
not access I²C, SPI, TFT, RGB drivers, or external flash. This is intentional:
the next bus probe must use verified pins and a recovery plan.

## Integrating into the local QMK tree

Copy `diag_protocol.h` and `diag_raw_hid.c` into the selected KD85-derived
QMK keyboard target, add `RAW_ENABLE = yes`, and include the C file in that
target's `SRC`. The sibling local QMK checkout already contains generic
WB32FQ95 support and the `wb32-dfu` bootloader definition.

Do not flash this overlay yet. It does not contain the KD85 matrix definition
and therefore is not itself a safe, complete keyboard image. The next step is
to create a dedicated KD85 target from the original matrix/RGB configuration,
then build and inspect the descriptor and image layout before using DFU.

## Packet examples

Request `E0 07` (remaining bytes zeroed):

```text
e0 07 00 00 00 00 00 ...
```

Response begins:

```text
e0 00 07 <uptime big-endian, 4 bytes> ...
```
