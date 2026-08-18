#!/usr/bin/env python3
"""Small reproducible first-pass analyzer for the KD85 VEGA image."""

from __future__ import annotations

import argparse
import hashlib
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


def disassemble_range(data: bytes, start: int, end: int) -> list[str]:
    """Disassemble a bounded Thumb range, retaining undecoded bytes as data."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    md.skipdata = True
    result = []
    for insn in md.disasm(data[start:end], BASE + start):
        result.append(f"0x{insn.address:08X}: {insn.mnemonic:<7} {insn.op_str}".rstrip())
    return result


def literal_ldr_xrefs(data: bytes, start: int, end: int) -> list[tuple[int, int, int, str]]:
    """Find Thumb LDR (PC-relative) instructions and resolve their literal values."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    result = []
    for insn in md.disasm(data[start:end], BASE + start):
        if insn.mnemonic != "ldr" or "[pc" not in insn.op_str:
            continue
        match = re.search(r"#([+-]?0x[0-9a-f]+|[+-]?\d+)", insn.op_str)
        if not match:
            continue
        immediate = int(match.group(1), 0)
        literal_address = ((insn.address + 4) & ~3) + immediate
        literal_offset = literal_address - BASE
        if 0 <= literal_offset <= len(data) - 4:
            value = struct.unpack_from("<I", data, literal_offset)[0]
            result.append((insn.address, literal_address, value, insn.op_str))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--strings", action="store_true")
    args = parser.parse_args()

    data = args.image.read_bytes()
    print(f"image={args.image}")
    print(f"size={len(data)} bytes (0x{len(data):X})")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")

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

    print("\nstartup_path:")
    print("  Reset vector enters a branch at 0x080001B8, targeting 0x080000E0.")
    for line in disassemble_range(data, 0xE0, 0x17A):
        print(f"  {line}")

    print("\nliteral_ldr_xrefs_in_startup_and_handlers:")
    for address, literal, value, operands in literal_ldr_xrefs(data, 0xE0, 0x9F00):
        peripheral = PERIPHERALS.get(value)
        tag = f" ({peripheral})" if peripheral else ""
        print(f"  0x{address:08X}: {operands:<18} -> [0x{literal:08X}] = 0x{value:08X}{tag}")


if __name__ == "__main__":
    main()
