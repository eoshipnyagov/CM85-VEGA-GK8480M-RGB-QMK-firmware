#!/usr/bin/env python3
"""Dump the recovered 6x17 QMK keymap tables."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

ROWS, COLS, LAYER_BYTES = 6, 17, 6 * 17 * 2
KNOWN = {
    0x0000: "KC_NO", 0x0001: "KC_TRNS", 0x0029: "KC_ESC",
    0x0052: "KC_UP", 0x0050: "KC_LEFT", 0x0051: "KC_DOWN",
    0x004F: "KC_RGHT", 0x007E: "KC_MUTE", 0x00E0: "KC_LCTL",
    0x00E1: "KC_LSFT", 0x00E2: "KC_LALT", 0x00E3: "KC_LGUI",
    0x00E4: "KC_RCTL", 0x00E5: "KC_RSFT", 0x00E7: "KC_RGUI",
    0x5223: "QK_LAYER_ACTION_5223", 0x5240: "QK_LAYER_ACTION_5240",
    0x7823: "RGB_HUE_UP", 0x7827: "RGB_VALUE_UP",
    0x7828: "RGB_VALUE_DOWN", 0x7829: "RGB_SPEED_UP",
    0x782A: "RGB_SPEED_DOWN",
}


def fmt(value: int) -> str:
    return KNOWN.get(value, f"KC_0x{value:04X}")


def dump(data: bytes, offset: int, label: str) -> None:
    print(f"{label} file+0x{offset:X}")
    values = [struct.unpack_from("<H", data, offset + i * 2)[0] for i in range(ROWS * COLS)]
    for row in range(ROWS):
        row_values = values[row * COLS : (row + 1) * COLS]
        print(f"  row{row}: " + " | ".join(fmt(value) for value in row_values))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--offset", type=lambda value: int(value, 0), default=0xB5D8)
    parser.add_argument("--layers", type=int, default=2)
    args = parser.parse_args()
    data = args.image.read_bytes()
    for layer in range(args.layers):
        dump(data, args.offset + layer * LAYER_BYTES, f"layer{layer}")


if __name__ == "__main__":
    main()
