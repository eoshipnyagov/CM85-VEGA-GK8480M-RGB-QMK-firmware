#!/usr/bin/env python3
"""Passive raw-HID capture for the KD85 reverse-engineering work.

This tool enumerates the Vial raw-HID collection, opens it for reading only,
and prints non-empty input reports. It never calls write(), send_feature_report,
or any reset/flash operation.
"""

from __future__ import annotations

import argparse
import json
import time

import hid


VID = 0xFFFE
PID = 0x0030
USAGE_PAGE = 0xFF60


def main() -> int:
    parser = argparse.ArgumentParser(description="Passive read-only HID capture")
    parser.add_argument("--seconds", type=float, default=60.0)
    parser.add_argument("--timeout-ms", type=int, default=250)
    args = parser.parse_args()

    devices = [
        d
        for d in hid.enumerate(VID, PID)
        if d.get("usage_page") == USAGE_PAGE
    ]
    if len(devices) != 1:
        raise SystemExit(f"expected one raw-HID collection, found {len(devices)}")

    device = hid.device()
    device.open_path(devices[0]["path"])
    print(json.dumps({k: devices[0].get(k) for k in (
        "vendor_id", "product_id", "serial_number", "usage_page", "usage",
        "interface_number",
    )}, ensure_ascii=False), flush=True)
    print("PASSIVE_ONLY=1", flush=True)

    deadline = time.monotonic() + args.seconds
    try:
        while time.monotonic() < deadline:
            report = device.read(64, args.timeout_ms)
            if report:
                print(json.dumps({
                    "t": round(time.monotonic(), 3),
                    "length": len(report),
                    "data": list(report),
                    "hex": bytes(report).hex(" "),
                }), flush=True)
    finally:
        device.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
