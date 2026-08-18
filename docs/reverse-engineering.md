# VEGA firmware reverse-engineering report

## Scope

Target: Dark Project CM85 Vega / GK8480M-RGB-QMK, MCU `WB32FQ95RCT4`.

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

