#!/usr/bin/env python3
"""Find Thumb PC-relative loads that resolve to MCU peripheral bases."""

from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x08000000
PERIPHERALS = {
    0x40000000: "GPIOA", 0x40000400: "GPIOB", 0x40000800: "GPIOC",
    0x40000C00: "GPIOD", 0x40003000: "QSPI", 0x40003800: "UART1",
    0x40008400: "UART3", 0x40008800: "I2C2", 0x40010C00: "RCC",
    0x40014000: "USB",
}


def literal_xrefs(data: bytes):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    for offset in range(0, len(data) - 4, 2):
        for insn in md.disasm(data[offset : offset + 4], BASE + offset):
            if insn.mnemonic != "ldr" or "[pc" not in insn.op_str:
                continue
            match = re.search(r"#([+-]?0x[0-9a-f]+|[+-]?\d+)", insn.op_str)
            if not match:
                continue
            literal_address = ((insn.address + 4) & ~3) + int(match.group(1), 0)
            literal_offset = literal_address - BASE
            if 0 <= literal_offset <= len(data) - 4:
                value = struct.unpack_from("<I", data, literal_offset)[0]
                if value in PERIPHERALS:
                    yield insn.address, literal_address, value, insn.op_str
            break


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    data = args.image.read_bytes()
    rows = sorted(set(literal_xrefs(data)))
    print(f"image={args.image}")
    print(f"peripheral_literal_xrefs={len(rows)}")
    for instruction, literal, value, operands in rows:
        print(f"0x{instruction:08X} {PERIPHERALS[value]:<6} literal=0x{literal:08X} {operands}")


if __name__ == "__main__":
    main()
