# Local tooling inventory

Checked 2026-08-18 on Windows.

## Ready

- Git and GitHub CLI: installed and authenticated.
- QMK Toolbox: installed, version `0.3.2` runtime.
- Generic DFU utility: `dfu-util 0.11`.
- WB32 updater: `wb32-dfu-updater_cli.exe`, supports `--list`, `--upload`, `--download`, `--dfuse-address` and toolbox mode.
- `dfu-programmer 1.1.0` and other QMK Toolbox helper utilities.
- Python 3.13 and `capstone 5.0.9` for binary analysis.
- MinGW GCC: available for host-side tools only.

QMK Toolbox runtime directory:

`C:\Users\eoshi\AppData\Local\QMK\QMK Toolbox\0.3.2`

## Not currently available on PATH

- `arm-none-eabi-gcc`, `arm-none-eabi-objdump`, `arm-none-eabi-size`, `arm-none-eabi-gdb`.
- QMK CLI/source tree.
- CMake, Ninja, Make and NMake.
- OpenOCD, SEGGER J-Link tools, ST-Link tools.
- HIDAPI command-line tester, sigrok-cli and serial-console utilities.

## Device detection

`wb32-dfu-updater_cli.exe --list` reported `Not found device` during the check. `dfu-util -l` also found no DFU device, so the keyboard was not in bootloader/DFU mode at that time.

## Recommended additions

1. Install an ARM GNU Embedded Toolchain.
2. Obtain a QMK/ChibiOS WB32 build tree or a minimal standalone WB32 project.
3. Add a HID capture/probe utility for the existing vendor HID interfaces.
4. Add a logic analyzer with I2C/SPI decoding before attempting custom firmware.

