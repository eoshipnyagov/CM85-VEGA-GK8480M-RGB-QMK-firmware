#!/usr/bin/env python3
"""Small reproducible first-pass analyzer for the KD85 VEGA image."""

from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x08000000
PERIPHERALS = {
    0x40000000: "GPIOA",
    0x40000400: "GPIOB",
    0x40000800: "GPIOC",
    0x40000C00: "GPIOD",
    0x40001400: "AFIO",
    0x40001800: "EXTI",
    0x40003000: "QSPI",
    0x40003800: "UART1",
    0x40008400: "UART3",
    0x40008800: "I2C2",
    0x40010C00: "RCC",
    0x40014000: "USB",
}


def read_words(data: bytes, start: int, count: int) -> list[int]:
    return [struct.unpack_from("<I", data, start + i * 4)[0] for i in range(count)]


def find_word_offsets(data: bytes, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    return [m.start() for m in re.finditer(re.escape(needle), data)]


def printable_strings(data: bytes, minimum: int = 4) -> list[tuple[int, str]]:
    result = []
    for match in re.finditer(rb"[ -~]{%d,}" % minimum, data):
        result.append((match.start(), match.group().decode("ascii", "replace")))
    return result


def disassemble_window(data: bytes, offset: int, radius: int = 24) -> list[str]:
    start = max(0, offset - radius)
    code = data[start : min(len(data), offset + radius + 32)]
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    lines = []
    for insn in md.disasm(code, BASE + start):
        lines.append(f"0x{insn.address:08X}: {insn.mnemonic:<7} {insn.op_str}".rstrip())
        if len(lines) >= 12:
            break
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--strings", action="store_true")
    args = parser.parse_args()

    data = args.image.read_bytes()
    print(f"image={args.image}")
    print(f"size={len(data)} bytes (0x{len(data):X})")
    print(f"sha256={__import__('hashlib').sha256(data).hexdigest()}")

    print("\nvector_table:")
    for index, value in enumerate(read_words(data, 0, min(64, len(data) // 4))):
        label = "initial_sp" if index == 0 else "reset" if index == 1 else "handler"
        print(f"  [{index:02d}] {label:<9} 0x{value:08X}")

    print("\nperipheral_references:")
    for address, name in PERIPHERALS.items():
        offsets = find_word_offsets(data, address)
        if offsets:
            shown = ", ".join(f"0x{x:X}" for x in offsets[:12])
            suffix = " ..." if len(offsets) > 12 else ""
            print(f"  {name:<6} 0x{address:08X}: {len(offsets)} refs at {shown}{suffix}")

    print("\nselected_strings:")
    for offset, value in printable_strings(data):
        if any(token in value.lower() for token in ("usb", "vial", "keyboard", "qmk", "hid", "dark", "vega")):
            print(f"  0x{offset:04X}: {value}")

    print("\nperipheral_context:")
    seen = set()
    for address, name in PERIPHERALS.items():
        for offset in find_word_offsets(data, address):
            key = (name, offset)
            if key in seen:
                continue
            seen.add(key)
            print(f"\n  [{name} @ file+0x{offset:X}]")
            for line in disassemble_window(data, offset):
                print(f"    {line}")
            if len(seen) >= 24:
                break

    if args.strings:
        print("\nall_strings:")
        for offset, value in printable_strings(data):
            print(f"  0x{offset:04X}: {value}")


if __name__ == "__main__":
    main()
