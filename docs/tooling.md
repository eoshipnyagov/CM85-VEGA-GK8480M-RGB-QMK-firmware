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
- User-level Python tools: `qmk 1.2.0`, `cmake 4.4.2`, `ninja 1.13.0`, `hid`, `pyusb` and `pyserial`.

QMK Toolbox runtime directory:

`C:\Users\eoshi\AppData\Local\QMK\QMK Toolbox\0.3.2`

## Not currently available on PATH

- ARM GNU Toolchain installation is in progress as a portable user-level download; system-wide installation was blocked by missing administrator rights.
- QMK CLI is installed, but reports that it requires an MSYS2 MinGW64 terminal for normal operation.
- Make/NMake are still absent.
- OpenOCD, SEGGER J-Link tools, ST-Link tools.
- HIDAPI command-line tester, sigrok-cli and serial-console utilities.

## Device detection

`wb32-dfu-updater_cli.exe --list` now detects `VID:PID 0x342D:0xDFA0`, bootloader version `0x0100`, device number `3`. `dfu-util -l` does not enumerate this device, so the WB32-specific updater is the confirmed flashing path.

## Recommended additions

1. Install an ARM GNU Embedded Toolchain.
2. Obtain a QMK/ChibiOS WB32 build tree or a minimal standalone WB32 project.
3. Add a HID capture/probe utility for the existing vendor HID interfaces.
4. Add a logic analyzer with I2C/SPI decoding before attempting custom firmware.
