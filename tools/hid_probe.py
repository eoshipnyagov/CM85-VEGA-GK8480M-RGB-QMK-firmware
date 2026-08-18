#!/usr/bin/env python3
"""Safe HID inventory for the KD85 Vega reverse-engineering work.

The default action only calls hid.enumerate(). It does not open a device and
does not send reports, feature reports, reset commands, or flash commands.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import hid


TARGET_USAGE_PAGE = 0xFF60


def printable(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.hex()
    return value


def compact(item: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "path",
        "vendor_id",
        "product_id",
        "release_number",
        "serial_number",
        "manufacturer_string",
        "product_string",
        "usage_page",
        "usage",
        "interface_number",
    )
    return {key: printable(item.get(key)) for key in keys if key in item}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enumerate HID interfaces without opening or writing to them."
    )
    parser.add_argument(
        "--json", action="store_true", help="print machine-readable JSON"
    )
    parser.add_argument(
        "--all", action="store_true", help="show all HID interfaces, not only raw HID"
    )
    args = parser.parse_args()

    try:
        devices = [compact(item) for item in hid.enumerate()]
    except Exception as exc:  # pragma: no cover - platform/backend dependent
        print(f"HID enumeration failed: {exc}", file=sys.stderr)
        return 1

    if not args.all:
        devices = [
            item
            for item in devices
            if item.get("usage_page") == TARGET_USAGE_PAGE
            or "vial:" in str(item.get("product_string", "")).lower()
        ]

    if args.json:
        print(json.dumps(devices, ensure_ascii=False, indent=2, default=str))
        return 0

    print(f"Found {len(devices)} matching HID interface(s).")
    for index, item in enumerate(devices, 1):
        print(f"\n[{index}]")
        for key, value in item.items():
            if key == "path":
                # Paths can contain backend-specific opaque details; retain them
                # because they are needed for a later explicit probe.
                value = str(value)
            print(f"{key}: {value}")
    print("\nNo device was opened and no HID report was sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
