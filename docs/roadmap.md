# Development roadmap

1. Add reproducible binary-analysis scripts and export a symbol/strings report.
2. Disassemble the reset path and annotate clock, GPIO, USB and QSPI initialization.
3. Capture USB traffic while using Vial; map vendor HID reports and test readable keymap/configuration commands.
4. Photograph both PCBs and identify MCU, OLED, RGB, USB and external-flash nets with continuity measurements.
5. Resolve the unreadable IC markings and verify the suspected SPI flash parts against package pinouts and datasheets.
6. Build a minimal WB32/QMK test firmware only after the recovery/update path is understood.
7. Add a host-side adapter for Steam/game context through a separate Raw HID protocol.

## Evidence policy

Every recovered fact should include an address, byte range, trace, photo or public-source reference. Keep original firmware immutable and place generated analysis under a separate directory.
