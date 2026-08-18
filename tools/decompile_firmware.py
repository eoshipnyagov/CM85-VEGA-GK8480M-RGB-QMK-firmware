#!/usr/bin/env python3
"""Build a reproducible function inventory and annotated Thumb listing."""

from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x08000000
DEFAULT_HANDLER = 0x080001BB
VECTOR_NAMES = {
    1: "reset_startup",
    11: "svc_rtos",
    15: "systick_rtos",
}


def words(data: bytes, count: int = 64) -> list[int]:
    return [struct.unpack_from("<I", data, i * 4)[0] for i in range(min(count, len(data) // 4))]


def direct_call_targets(data: bytes) -> set[int]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.skipdata = True
    targets: set[int] = set()
    for insn in md.disasm(data, BASE):
        if insn.mnemonic in {"bl", "blx"}:
            match = re.search(r"#0x([0-9a-f]+)", insn.op_str)
            if match:
                targets.add(int(match.group(1), 16) | 1)
    return targets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--max-calls", type=int, default=2000)
    args = parser.parse_args()
    data = args.image.read_bytes()
    vectors = words(data)
    starts: set[int] = {v for v in vectors[:56] if BASE <= (v & ~1) < BASE + len(data)}
    starts |= direct_call_targets(data)
    starts = set(sorted(starts)[: args.max_calls])

    names: dict[int, str] = {}
    for index, value in enumerate(vectors[:56]):
        if value == DEFAULT_HANDLER:
            continue
        if index in VECTOR_NAMES:
            names[value & ~1] = VECTOR_NAMES[index]
        elif BASE <= (value & ~1) < BASE + len(data):
            names.setdefault(value & ~1, f"irq_vector_{index:02d}")
    for address in starts:
        names.setdefault(address & ~1, f"sub_{address & ~1:08X}")

    print(f"image={args.image}")
    print(f"size={len(data)} bytes")
    print(f"candidate_function_starts={len(starts)}")
    print("\nfunction_catalog:")
    for address in sorted(starts):
        print(f"0x{address & ~1:08X} {names.get(address & ~1, 'sub_unknown')}")

    print("\nvector_labels:")
    for index, value in enumerate(vectors[:56]):
        if value != DEFAULT_HANDLER:
            print(f"vector[{index:02d}] 0x{value:08X} {names.get(value & ~1, 'candidate')}")

    print("\nnotes:")
    print("This is an annotated recovery pass, not original source reconstruction.")
    print("Names are hypotheses and must be promoted only after control-flow/xref confirmation.")


if __name__ == "__main__":
    main()
