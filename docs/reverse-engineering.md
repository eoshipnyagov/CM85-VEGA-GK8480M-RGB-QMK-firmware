# VEGA firmware reverse-engineering report

## Scope

Target: Dark Project KD85 Vega / GK8480M-RGB-QMK, MCU `WB32FQ95RCT6`.

Physical marking: `WB32F Q95RCT6 AP3F154 2022`.

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
| `HFD80CP100 229GNWD0a` | Additional controller/IC; exact role unresolved. |
| Two `HFD5501L CQ` devices | Additional HFD-marked ICs; one is near USB and may be related to RGB/backlight control, the other is near `HFD80CP100` and `334PD45`. |
| `334PD45` (`U9`) | Small 16-pin IC; probably power-management or power-distribution controller, pending rail tracing. |
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

The main keyboard MCU is confirmed separately as `WB32FQ95RCT6`; therefore HFD80CP100 must be treated as an additional controller or subsystem IC, not as the primary MCU. Its connection to the display daughterboard, wireless subsystem, RGB, RTC or auxiliary functions is still open.

### `2E1TH1D` — unresolved

No reliable public match was found. It may be a power-management, USB, display or other small-package IC marking. Package outline, pin count, nearby passives and the connected nets are required before assigning a function.

### `HFD5501L CQ` — two devices, role unresolved

The marking is now read as `HFD5501L CQ`. No reliable public datasheet or catalog match was found. Two instances are present: one close to the USB connector, and one beside `HFD80CP100` and `334PD45`. The USB-side device is plausibly a power/RGB/backlight-related controller, but this remains a hypothesis until its high-current outputs, LED traces or PWM/control lines are identified. The duplicate device may indicate separate lighting zones, a second subsystem, or a reused platform controller.

The PCB photographs additionally show two identical devices with reference
designators `UL1` and `UL2`. Their duplicated placement and the `UL` prefix are
consistent with lighting units, possibly separate RGB zones. This is a board
reference hypothesis, not a confirmed component family or protocol.

### `334PD45` (`U9`) — probable power-management IC

This small 16-pin device, identified on the PCB as `U9`, sits beside `HFD80CP100` and the second `HFD5501L`. Based on its placement and the board architecture, a power-management or power-distribution role is plausible. This is not yet confirmed: check whether it connects to USB 5 V, battery/3.3 V rails, inductors, MOSFETs or multiple decoupling networks. The nearby 12 MHz crystal is now considered more likely to clock `HFD80CP100` than `334PD45`.

### Crystal inventory

The board has three crystal components with `XT` reference designators. One is reported as 12 MHz and is located beside the `HFD80CP100`/`334PD45`/`HFD5501L` cluster. The current working assignment is that this 12 MHz crystal belongs to `HFD80CP100`; the frequencies and consumers of the other two crystals remain to be recorded.

## Physical placement observations

The board has only four visibly labelled test points (`TP`) in total. This
does not rule out hidden test vias or service signals on the FFC connectors,
but it makes a complete exposed SWD/JTAG/UART header unlikely. Their nets
should be identified before assuming any one of them is a debug signal.

The main PCB has many vias between layers, so visual tracing is unreliable without continuity measurements or microscope photography.

| Region | Observed components | Current interpretation |
|---|---|---|
| Centre/lower side | `WB32FQ95RCT6`, physically separated from the dense component groups | Confirmed primary keyboard MCU; likely matrix/QMK/Vial/RGB coordination. |
| Near USB | First `HFD5501L` | Possible USB-adjacent power, RGB or backlight function; unconfirmed. |
| Right side under/near Backspace | `HFD80CP100`, `334PD45`, second `HFD5501L`, nearby 12 MHz `XT` crystal | Dense auxiliary-controller cluster; 12 MHz crystal probably clocks `HFD80CP100`. |
| Far right edge | `CHMC D8563F`, `PY25Q128HA`, two small 8-pin devices | RTC and 16 MB SPI flash are confirmed by marking; likely persistent data/display assets, but bus ownership needs tracing. |

The working architecture is therefore a split design: `WB32FQ95RCT6` is the primary keyboard MCU, while the right-side cluster likely handles one or more auxiliary functions (display, USB, storage, lighting or RTC). A radio function is not assumed for this keyboard. This is a working model, not a proven schematic.

## Current best candidate for the secondary controller

The strongest current candidate is the `HFD80CP100` paired with `PY25Q128HA`:

- `HFD80CP100` is the likely secondary digital controller;
- `PY25Q128HA` is its likely external 16 MB SPI storage;
- `CHMC D8563F` is likely connected to the same subsystem for time/date data;
- the 12 MHz `XT` crystal is likely the clock source for `HFD80CP100`;
- one or both `HFD5501L` devices may provide RGB or display-backlight control.

This arrangement naturally fits a display/encoder subsystem: the secondary controller can maintain the UI, read the encoder and RTC, and store images/animations in external flash, while `WB32FQ95RCT6` remains responsible for the keyboard matrix and QMK/Vial USB application. It is still a hypothesis until the SPI flash pins, RTC I2C lines and inter-board connector are traced to the controller.

## Box marking: `HFD582CHFS`

The retail box lists `HFD80CP100` and `HFD582CHFS` alongside the TFT display. The keyboard is not advertised as having Bluetooth, 2.4 GHz or another radio mode. Therefore `HFD582CHFS` must not be identified as a wireless controller solely from the box text or from similarly named parts in other keyboard platforms. It may refer to an alternate platform BOM, a different product variant, or a controller used for a non-radio subsystem. Confirmation requires locating the exact marking on the PCB and checking for RF matching components/antenna traces.

### Animation-control hypothesis

The additional controller may be responsible for scheduling and rendering TFT and/or lighting animations. The `PY25Q128HA` 16 MB flash is large enough to hold image assets, frame sequences and UI resources. In that model, `HFD80CP100` or the unidentified `HFD582CHFS`-class device would manage animation state and transport, while one or both `HFD5501L` devices would implement LED/PWM output. This remains a hypothesis until flash access patterns and LED-control traces are correlated with animation changes.

## Evidence for I2C communication

The binary contains a strong sign that the WB32 application configures the hardware `I2C2` peripheral:

- at image offset approximately `0x6206`, code loads the peripheral base `0x40008800`;
- the same early initialization block also references `0x40003800` (UART1), `0x40008400` (UART3) and `0x40003000` (QSPI), consistent with a ChibiOS/WB32 peripheral setup table;
- `0x40008800` matches the WB32FQ95xx `I2C2` address from the reference manual.

This proves I2C2 support/configuration exists in the image, but does not by itself prove a live exchange with `HFD80CP100`. The current static pass has not recovered a reliable 7-bit slave address, transaction buffer or device-specific register sequence. Candidate I2C users are `CHMC D8563F` RTC and the display/secondary-controller link; the latter remains unconfirmed. A USB/I2C or inter-board logic capture should resolve this quickly.

### Two unreadable ICs

Do not infer these from the firmware yet. A sharp perpendicular macro photograph, package dimensions and pin-1 indication should be enough to narrow them down.

### `U9` — board reference for `334PD45`

The PCB reference `U9` denotes the known 16-pin `334PD45` device. Its exact
electrical function remains unresolved; the current hypothesis is power
management or power distribution, pending rail tracing.

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

## Related public hardware references

No public schematic or board-level teardown for the exact KD85/`GK8480M-RGB-QMK` PCB was found in the current search. Product pages confirm the KD85 Vega exterior and 85-key layout, but do not expose PCB photographs or schematics.

The closest useful public references are the AJAZZ AK820 Pro and Epomaker TH80 V2 Pro reverse-engineering/teardown materials. They are not proven to be the same PCB, and their primary MCU is reported as HFD80CP100 rather than our confirmed WB32FQ95RCT6. However, they show a highly relevant platform pattern:

- separate display and encoder hardware connected through a board/FPC interface;
- `CHMC D8563F` RTC next to a dedicated 32.768 kHz crystal;
- `PY25Q128HA` 16 MB external SPI flash used for display assets, configuration and firmware data;
- display control over a small serial interface with power, reset, data/command, clock and chip-select signals;
- a multi-controller architecture where keyboard, wireless, display and storage functions are split.

This makes a separate display/USB controller on the KD85 plausible, but not yet proven. The decisive evidence will be continuity from USB D+/D− and the display FPC to `HFD80CP100`, `U9` and `WB32FQ95RCT6`.

Useful references:

- [AJAZZ AK820 Pro reverse-engineering README](https://github.com/fpb/ajazz-ak820-pro/blob/main/README.md) — public chip inventory, RTC, flash, display and encoder notes.
- [AK820 Pro Modder hardware reference](https://github.com/wsclx/ak820pro-modder) — protocol and architecture notes for the related platform.
- [Epomaker TH80 V2 Pro teardown](https://hwbusters.com/peripherals/epomaker-th80-v2-pro-mechanical-keyboard-review/4/) — photographs and component-level observations.
- [Dark Project KD85 Vega product reference](https://netbox.by/gaming-i-striming/igrovie-klaviaturi/dark-project-kd85-vega-dp-kd-85a-300101-gox-white/) — exterior/layout reference only.
