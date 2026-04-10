#!/usr/bin/env python
import socket
import json
import os


PORT = 5005
OUTFILE = "GE_ir_keymap.txt"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

print(f"Listening for IR codes on UDP port {PORT}...")

keymap = {}  # in-memory dictionary

while True:
    data, addr = sock.recvfrom(1024)
    code = data.decode().strip()
    code = str(hex(int(code)))
    # Ignore -1 (repeat or no-data)
    if code == "-0x1":
        continue

    print(f"\nReceived IR code: {code}")

    name = input("Enter button name (or 'save', 'quit'): ").strip()

    if name == "":
        print("Skipped.")
        continue

    if name.lower() == "save":
        with open(OUTFILE, "w") as f:
            for k, v in keymap.items():
                f.write(f"{k}:{v}\n")
        print(f"Dictionary saved to {OUTFILE}")
        continue

    if name.lower() == "quit":
        print("Exiting.")
        break

    # Normal entry
    keymap[name] = code
    print(f"Mapped: {name} → {code}")

