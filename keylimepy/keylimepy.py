#!/usr/bin/env python
import time
import json

import pigpio

from shift_matrix_kb import ShiftRegisterMatrix
from usb_kb_output import UsbKeyboardOutput

# KEYMAP_FILE = "/home/pi/KeyLimePi/usbdisk.d/keymap.json"
KEYMAP_FILE = "../keyboards/Corsair/Vengeance K65/default_keymap.json"

if __name__ == "__main__":
    # Setup GPIO
    pi = pigpio.pi()
    if not pi.connected:
        exit()

    # GPIO.setwarnings(False)
    # GPIO.setmode(GPIO.BCM)

    keyboard_matrix = ShiftRegisterMatrix(pi)
    usb_keyboard = UsbKeyboardOutput()

    # Load Keymap file
    keymap_file = open(KEYMAP_FILE)
    keyboard = json.load(keymap_file)
    keymap = keyboard['keymap']
    keymap_file.close()

    while True:
        start_time = time.time()

        # Scan the keyboard matrix using shift registers
        active_keys = keyboard_matrix.read(keymap)

        # Write the key state to the usb
        usb_keyboard.write_nkro(active_keys)

        # print(time.time() - start_time)
        time.sleep(max(0, (1/125) - (time.time() - start_time))) # ~125Hz