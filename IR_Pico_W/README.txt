Pico‑W IR Bridge Setup (Quick Instructions)

The Pico‑W runs a small MicroPython script that receives IR codes and forwards them to pyVid2 over UDP.
Requirements

    Raspberry Pi Pico‑W

    MicroPython firmware installed

    Thonny IDE

    ir_rx library by Peter Hinch

1. Open Thonny and connect to the Pico‑W

Select MicroPython (Raspberry Pi Pico) as the interpreter.
2. Upload the IR server files

Copy the following to the Pico’s filesystem:
Code

main.py
ir_wifi.py
ir_rx/   (directory)

Use Thonny’s View → Files panel and “Upload to /”.
3. Edit configuration

Open ir_wifi.py on the Pico and set:
python

SSID = "your_wifi"
PASSWORD = "your_password"

Select the IR protocol decoder you need:
python

from ir_rx.nec import NEC_8

4. Reboot the Pico

Press Ctrl+D in Thonny or power‑cycle the device.

The IR WiFi bridge starts automatically and sends decoded IR keycodes to pyVid2.

You will have to edit ir_keymaps.conf to match the codes sent by your remote control.
The ir_keymaps.conf file lives in ~/.local/share.pyVid/ on the computer running pyVid2.

