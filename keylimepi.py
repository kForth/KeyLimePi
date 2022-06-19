#!/usr/bin/env python
import time
import json

# import RPi.GPIO as GPIO
import fake_gpio as GPIO

from usb_hid_scancodes import scancodes

# KEYMAP_FILE = "/home/pi/KeyLimePi/usbdisk.d/keymap.json"
KEYMAP_FILE = "keyboards/Corsair/Vengeance K65/default_keymap.json"

# USB Keyboard Output
class UsbKeyboardOutput:
    DEVICE = '/dev/hidg0'
    NULL = chr(0)

    def write(self, str):
        print(str)
        # with open(self.DEVICE, 'rb+') as kb:
        #     kb.write(str.encode())

    def write_key(self, key, *mods):
        self.write(chr(sum(mods)) + self.NULL + chr(key) + self.NULL * 5)

# Full GPIO Keyboard Matrix (no shift registers)
class GPIOMatrix:
    ROW_PINS = (17, 18, 19, 20, 21, 22, 23, 24)
    COL_PINS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)

    def __init__(self):
        GPIO.setup(self.ROW_PINS, GPIO.OUT)
        GPIO.setup(self.COL_PINS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read(self):
        for i, (row_keys) in enumerate(matrix):
            GPIO.output(self.ROW_PINS[i], GPIO.HIGH)
            for j, key in enumerate(row_keys):
                state = GPIO.input(self.COL_PINS[j])
                if state != last_state[i][j]:
                    print(i, j, key, state)
                    # write_key_event(key, state)
            GPIO.output(self.ROW_PINS[i], GPIO.LOW)
        last_state = state
        GPIO.cleanup()

    
# Shift-Out Registers for Keyboard Matrix
class ShiftOut:
    DATA_PIN = 16
    LATCH_PIN = 17  # 2x 8-Bit Registers
    CLOCK_PIN = 18
    NUM_BITS = 8

    def __init__(self):
        GPIO.setup(self.DATA_PIN,GPIO.OUT)
        GPIO.setup(self.LATCH_PIN,GPIO.OUT)
        GPIO.setup(self.CLOCK_PIN,GPIO.OUT)

    def write(self, data):
        GPIO.output(self.CLOCK_PIN, 0)
        GPIO.output(self.LATCH_PIN, 0)
        GPIO.output(self.CLOCK_PIN, 1)
        # Write in reverse order
        for i in range(self.NUM_BITS, -1, -1):
            GPIO.output(self.CLOCK_PIN, 0)
            GPIO.output(self.DATA_PIN, GPIO.HIGH if (data & 1 << i) else GPIO.LOW)
            GPIO.output(self.CLOCK_PIN, 1)
        GPIO.output(self.CLOCK_PIN, 0)
        GPIO.output(self.LATCH_PIN, 1)
        GPIO.output(self.CLOCK_PIN, 1)

# Shift-In Registers for Keyboard Matrix
class ShiftIn:
    DATA_PIN = 19
    LATCH_PINS = (20, 21)  # 2x 8-Bit Registers
    CLOCK_PIN = 22
    NUM_BITS = 16

    def __init__(self):
        GPIO.setup(self.DATA_PIN,GPIO.IN)
        GPIO.setup(self.LATCH_PINS,GPIO.OUT)
        GPIO.setup(self.CLOCK_PIN,GPIO.OUT)

    def read(self):
        data = []
        for i in (0, 1):
            GPIO.output(self.CLOCK_PIN, 0)
            GPIO.output(self.LATCH_PINS[i], 0)
            GPIO.output(self.CLOCK_PIN, 1)
            for _ in range(self.NUM_BITS, -1, -1):
                GPIO.output(self.CLOCK_PIN, 0)
                data.insert(0, GPIO.input(self.DATA_PIN))  # append?
                GPIO.output(self.CLOCK_PIN, 1)
            GPIO.output(self.CLOCK_PIN, 0)
            GPIO.output(self.LATCH_PINS[i], 1)
            GPIO.output(self.CLOCK_PIN, 1)
        return data

shift_in = ShiftIn()
shift_out = ShiftOut()
usb_keyboard = UsbKeyboardOutput()

if __name__ == "__main__":
    # Setup RPi GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Load Keymap file
    keymap_file = open(KEYMAP_FILE)
    keymap = json.load(keymap_file)
    matrix = keymap['keymap']
    keymap_file.close()

    last_state = [[0] * len(matrix[0])] * len(matrix)

    while True:
        et = time.time()
        # Scan the keyboard matrix using shift registers
        for i, (row_keys) in enumerate(matrix):
            shift_out.write(1 << 8)
            row_state = shift_in.read()
            for j, (key, state) in enumerate(zip(row_keys, row_state)):
                if state != last_state[i][j]:
                    print(i, j, key, state)
                    usb_keyboard.write_key(eval(key, scancodes))
                    last_state[i][j] = state
        # shift_out(0)
        GPIO.cleanup()

        time.sleep(max(0, 0.001 - (time.time() - et))) # ~1kHz