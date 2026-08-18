# VEGA firmware reverse-engineering report

## Scope

Target: Dark Project KD85 Vega / GK8480M-RGB-QMK, MCU `WB32FQ95RCT4`.

The device was initially referred to as CM85; current physical identification is KD85.

The hardware includes a separate daughterboard with the volume encoder, an approximately 128×64 display, and the USB connector. This is important because the display and USB wiring may not be on the main keyboard PCB.

## Recorded board markings

The following markings were read from the main PCB. They are evidence, not yet verified part identifications:

| Marking | Current interpretation |
|---|---|
| `CHMC D8563F S2461` | Unknown component; identify from package and surrounding circuit. |
| `PY25Q128HA` | Likely 128-Mbit SPI NOR flash. |
| `2E1TH1D` | Unknown component. |
| `P25D80SH 3J1PC2F` | Likely 128-Mbit SPI NOR flash; confirm exact vendor and density. |
| `HFD80CP100 229GNWD0a` | External-flash candidate; confirm datasheet, package and bus wiring. |
| Two very small-marking ICs | Unreadable for now; photographs/microscope reading pending. |

## Component identification update

### `CHMC D8563F S2461` — RTC, high confidence

This is a CHMC D8563-compatible real-time clock/calendar IC, functionally close to the NXP PCF8563. It uses a two-wire I2C interface, a 32.768 kHz crystal, open-drain interrupt and clock-output pins. The suffix/date-like text is probably production or lot information, not a different device.

### `PY25Q128HA` — 128-Mbit SPI NOR flash, confirmed

Puya's PY25Q128HA is a 128-Mbit (16 MiB) serial NOR flash with single/dual/quad SPI and QPI support, normally in an 8-pin package. It is a strong candidate for firmware, configuration, display assets or other persistent data storage.

### `P25D80SH 3J1PC2F` — 8-Mbit SPI NOR flash, high confidence

The device marking matches Puya P25D80SH: 8 Mbit (1 MiB), 2.3–3.6 V SPI NOR flash, up to 120 MHz. `3J1PC2F` is likely lot/date/traceability marking. This is distinct from the 128-Mbit PY25Q128HA.

### `HFD80CP100 229GNWD0a` — additional controller, role unresolved

Independent teardown reports identify HFD80CP100 as a Huafenda keyboard/mouse controller, commonly associated with the Sonix SN32F299 family or a compatible/derivative device. It is described as an integrated keyboard controller with RGB and wireless-oriented functions. This identification is not backed by an official public HFD datasheet, so the exact role, core, flash size and peripheral map on this board remain unconfirmed.

The main keyboard MCU is confirmed separately as `WB32FQ95RCT4`; therefore HFD80CP100 must be treated as an additional controller or subsystem IC, not as the primary MCU. Its connection to the display daughterboard, wireless subsystem, RGB, RTC or auxiliary functions is still open.

### `2E1TH1D` — unresolved

No reliable public match was found. It may be a power-management, USB, display or other small-package IC marking. Package outline, pin count, nearby passives and the connected nets are required before assigning a function.

### `HFD 5501? CQ 2347TWC0a` — unresolved HFD-marked IC

This is a preliminary reading; the character after `5501` may not be `L`. No reliable public datasheet or catalog match was found for the partial marking. `CQ` and `2347TWC0a` are likely package/lot/date or internal traceability markings. Because the same board also contains `HFD80CP100`, this may be another Huafenda subsystem IC, but its function cannot be inferred from the marking alone. The display daughterboard location, package size, pin count and nearby buses will be decisive.

### Two unreadable ICs

Do not infer these from the firmware yet. A sharp perpendicular macro photograph, package dimensions and pin-1 indication should be enough to narrow them down.

Input image: `firmware/original/VEGA_vial_v1_01_20231201.bin`.

## Firm findings

### Image layout

- Raw ARM Cortex-M application image.
- Likely flash base: `0x08000000`.
- Initial stack pointer: `0x20000400`.
- Reset handler: `0x080001B9`.
- Vector table contains ChibiOS-style default handlers plus active SVC/SysTick and peripheral handlers.
- Bootloader is not present in this file; the image begins at the application vector table.

Notable vector targets include `0x08008349` (SVC), `0x08009199` (SysTick), `0x08009959`, `0x08008BD1`, `0x08009601`, `0x08009741`, `0x08009DB1`, `0x08009DC5` and `0x08008BD5`.

### USB

The descriptor block identifies:

- VID `0xFFFE`, PID `0x0030`.
- USB 2.00, device revision `0x0100`.
- Three HID interfaces:
  - boot keyboard, endpoint `0x81`, 8-byte report;
  - vendor HID, endpoints `0x82` / `0x02`, 32-byte reports;
  - vendor HID, endpoint `0x83`, 32-byte report.
- Visible strings: `USB Keyboard` and `vial:f64c2b3c`.

This is strong evidence for a QMK/Vial-style firmware. The two vendor HID channels likely cover configuration and a second Vial/protocol or device-specific channel; their exact semantics should be confirmed by USB capture.

### WB32 peripheral references

The code contains references consistent with the WB32FQ95xx memory map:

| Peripheral | Address |
|---|---:|
| GPIOA | `0x40000000` |
| GPIOB | `0x40000400` |
| GPIOC | `0x40000800` |
| GPIOD | `0x40000C00` |
| AFIO | `0x40001400` |
| EXTI | `0x40001800` |
| QSPI | `0x40003000` |
| UART1 | `0x40003800` |
| UART3 | `0x40008400` |
| I2C2 | `0x40008800` |
| RCC | `0x40010C00` |
| USB | `0x40014000` |

The QSPI base is actively referenced by initialization code, but the image alone does not prove the exact external-memory protocol or contents.

## Probable but not yet proven

### Matrix, GPIO and debounce

There are GPIO configuration and repeated periodic control-flow regions compatible with ChibiOS/QMK startup and keyboard scanning. The exact row/column pin assignment, scan direction, diode orientation and debounce algorithm cannot yet be named confidently from constants alone.

### Keymap and layers

Data around approximately `0xBA30–0xBA90` and `0xB5D8–0xB768` resembles compact QMK/HID keycode tables and configuration data. These regions may contain dynamic Vial keymap material or defaults, but exact layer boundaries and physical positions require cross-checking against Vial protocol reads and a known keymap.

### RGB

Structured lookup/gamma-like tables occur around `0xAA78` and `0xABB4`. They are consistent with RGB effects or color conversion support, but the actual LED driver, timing peripheral and pin mapping remain unresolved.

### OLED and external flash

No unambiguous SSD1306/SH1106 initialization sequence was recovered in the first pass. An OLED may use another controller, indirect tables, or be handled by code paths not obvious from the static scan. HFD80CP100 support is plausible because QSPI infrastructure is present, but flash commands, JEDEC ID and chip-select GPIO still need dynamic or hardware confirmation.

## Recovery assessment

### Can be recovered with high confidence

- MCU family and application base address.
- Vector table and interrupt entry points.
- USB VID/PID, interfaces, endpoints and report sizes.
- Vial signature/UID string.
- Broad QMK/ChibiOS runtime identification.
- Peripheral address map and major code/data regions.

### Recoverable with analysis plus hardware/USB traces

- Matrix pinout and scan timing.
- Debounce behavior.
- Vial keymap/layers, if the device exposes readable configuration.
- RGB protocol, LED count and effect table.
- OLED bus pins, controller and framebuffer format.
- External HFD80CP100 wiring and contents.
- Firmware update transport and bootloader boundary.

### Unlikely from this binary alone

- Original QMK source names and build configuration.
- Exact physical matrix layout without PCB photos or continuity measurements.
- Full original Vial JSON/configuration metadata.
- Reliable recovery of all high-level feature semantics after compiler optimization.

## Public references

- [WB32FQ95xx Reference Manual](https://www.westberrytech.com/uploads/file/WB32FQ95xx/EN_RM2905025_WB32FQ95xx_V01.pdf)
- [Westberry QMK board definition](https://raw.githubusercontent.com/WestberryTech/qmk_westberry/master/platforms/chibios/boards/GENERIC_WB32_FQ95XX/board/board.h)
- [Westberry QMK board startup code](https://raw.githubusercontent.com/WestberryTech/qmk_westberry/master/platforms/chibios/boards/GENERIC_WB32_FQ95XX/board/board.c)
- [Westberry QMK MCU configuration](https://raw.githubusercontent.com/WestberryTech/qmk_westberry/master/platforms/chibios/boards/GENERIC_WB32_FQ95XX/configs/mcuconf.h)
- [QMK compatible microcontrollers](https://develop-docs.qmk.fm/compatible_microcontrollers)
- [QMK flashing documentation](https://github.com/qmk/qmk_firmware/blob/master/docs/flashing.md)
- [Vial firmware size notes](https://get.vial.today/docs/firmware-size.html)
- [Vial porting documentation](https://get.vial.today/docs/porting-to-via.html)
