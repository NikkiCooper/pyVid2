#  ir_wifi.py Copyright (c) 2026 Nikki Cooper
#
#  This program and the accompanying materials are made available under the
#  terms of the GNU Lesser General Public License, version 3.0 which is available at
#  https://www.gnu.org/licenses/gpl-3.0.html#license-text
#
import network
import socket
import time
from ir_rx.nec import NEC_8  # or NEC_16 depending on your remote
from machine import Pin

# -----------------------------
# CONFIG
# -----------------------------
SSID = "ssid_of_machine_running_pyvid2"
PASSWORD = "change to the password of the SSID"
DEST_IP = "192.168.0.14"   # your Arch Linux machine
DEST_PORT = 5005            # UDP port
IR_PIN = 15                 # The pin the IR Receiver is connected to.
# -----------------------------

print("IR WiFi server starting...")

# WiFi connect
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(0.1)
    print("#", end="")
print(f"\nConnected:", wlan.ifconfig())

# UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# IR callback
def ir_callback(data, addr, ctrl):
    # NEC_8 gives you the command byte in "data"
    msg = str(data)
    print(f"IR:", hex(data))
    sock.sendto(msg.encode(), (DEST_IP, DEST_PORT))

# IR receiver
ir = NEC_8(Pin(IR_PIN, Pin.IN), ir_callback)

print("IR receiver active. Waiting for signals...")
while True:
    time.sleep(1)
