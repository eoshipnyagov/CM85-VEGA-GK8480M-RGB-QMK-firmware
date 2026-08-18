# Development roadmap

1. Add reproducible binary-analysis scripts and export a symbol/strings report.
2. Disassemble the reset path and annotate clock, GPIO, USB and QSPI initialization.
3. Capture USB traffic while using Vial; map vendor HID reports and test readable keymap/configuration commands.
4. Photograph both PCBs and identify MCU, OLED, RGB, USB and external-flash nets with continuity measurements.
5. Resolve the unreadable IC markings and verify the suspected SPI flash parts against package pinouts and datasheets.
6. Build a minimal WB32/QMK test firmware only after the recovery/update path is understood.
7. Add a host-side adapter for Steam/game context through a separate Raw HID protocol.

## Command recovery from the binary

The firmware contains almost no useful plain-text command names, so command recovery must be structural rather than string-based. The image exposes two 32-byte vendor HID report paths, making numeric HID/Vial dispatch tables and report handlers the primary targets. Search targets are:

- byte-0 command comparisons in vendor HID receive handlers;
- tables of small consecutive command IDs;
- fixed 32-byte copies and response builders;
- calls that follow HID commands into I2C2, QSPI, GPIO or display/RGB code;
- possible Vial/VIA commands for keymap, EEPROM, lighting, bootloader and device identification.

Static command identification should be correlated with captured USB reports. A command that causes I2C/SPI activity immediately afterward is the strongest evidence for communication with the secondary controller.

## Diagnostic bridge firmware

The proposed experimental firmware would turn the WB32 into a controlled USB-to-bus bridge:

```text
PC console
   ↓ USB vendor HID / Raw HID
WB32 diagnostic bridge
   ├─ I2C2 probe/read/write
   ├─ SPI/QSPI probe/read-only
   ├─ GPIO observation and safe control
   └─ response packet back to PC
```

Recommended packet shape:

```text
request:  [opcode, bus, address, register, length, payload...]
response: [status, bus, address, length, payload...]
```

The bridge should begin with identification and read-only operations: I2C bus scan, RTC register read, SPI JEDEC ID and bounded flash reads. Writes, arbitrary GPIO changes and display-controller commands should remain disabled until voltage levels, ownership and recovery are understood.

Because the original QMK source is not available, this cannot be added safely to the existing binary as a simple patch. The practical sequence is: first probe the original firmware through its existing HID interfaces; then confirm the bootloader/update and recovery path; only then build a minimal WB32/ChibiOS diagnostic image. A custom CDC serial port is unnecessary initially—vendor HID keeps the existing USB model and avoids changing descriptors.

## Iterative hardware probing

1. With power removed, identify only obvious ground, USB 5 V, 3.3 V and connector continuity points.
2. With the keyboard powered normally, observe candidate SDA/SCL lines using a high-impedance logic analyzer; do not inject signals.
3. Correlate traffic with display refresh, encoder rotation, RTC changes and Vial activity.
4. Compare idle, screen-update and encoder events to determine whether the second controller is on I2C, SPI, UART or a private GPIO protocol.
5. Only after the bus and voltage levels are known, investigate read-only identification commands or debug interfaces.

## Secondary firmware accessibility

The likely `HFD80CP100` is probably a programmable MCU/controller, not a simple one-function IC, especially because similar keyboard platforms pair this class of controller with external `PY25Q128HA` storage. However, the second controller's firmware is not automatically recoverable. Possible access paths include a vendor USB/bootloader mode, hidden test pads, SWD/JTAG/ISP, or reading an attached external flash. `334PD45` is currently treated as a power IC and would not have user firmware; `HFD5501L` may be a lighting/controller device and requires separate identification.

## Evidence policy

Every recovered fact should include an address, byte range, trace, photo or public-source reference. Keep original firmware immutable and place generated analysis under a separate directory.
