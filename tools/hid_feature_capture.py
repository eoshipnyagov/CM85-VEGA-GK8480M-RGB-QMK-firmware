#!/usr/bin/env python3
"""Read-only Frida hook for HID feature reports in the vendor utility."""

from __future__ import annotations

import argparse
import json
import time

import frida


HOOK = r"""
function hookBufferFunction(moduleName, functionName, bufferArg, lengthArg) {
    const address = Process.getModuleByName(moduleName).getExportByName(functionName);
    send({hooked: functionName, address: address.toString()});
    Interceptor.attach(address, {
        onEnter(args) {
            const length = args[lengthArg].toInt32();
            if (length > 0 && length <= 4096 && !args[bufferArg].isNull()) {
                send({source: functionName, length: length}, args[bufferArg].readByteArray(length));
            }
        }
    });
}

hookBufferFunction('hid.dll', 'HidD_SetFeature', 1, 2);
hookBufferFunction('kernel32.dll', 'WriteFile', 1, 2);
hookBufferFunction('kernel32.dll', 'DeviceIoControl', 2, 3);
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture HidD_SetFeature calls")
    parser.add_argument("--process", default="Vega Screen Software.exe")
    parser.add_argument("--seconds", type=float, default=120.0)
    args = parser.parse_args()

    device = frida.get_local_device()
    matches = [p for p in device.enumerate_processes() if p.name.lower() == args.process.lower()]
    if len(matches) != 1:
        raise SystemExit(f"expected one process named {args.process!r}, found {len(matches)}")

    session = device.attach(matches[0].pid)

    def on_message(message, data):
        if message.get("type") == "send":
            payload = message["payload"]
            if data is not None:
                payload = dict(payload)
                payload["hex"] = bytes(data).hex(" ")
                payload["data"] = list(data)
            print(json.dumps(payload, ensure_ascii=False), flush=True)
        else:
            print(json.dumps(message, ensure_ascii=False), flush=True)

    script = session.create_script(HOOK)
    script.on("message", on_message)
    script.load()
    print(json.dumps({"attached_pid": matches[0].pid, "read_only": True}), flush=True)
    try:
        time.sleep(args.seconds)
    finally:
        session.detach()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
