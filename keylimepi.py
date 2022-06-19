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
    # MOD_BYTES = 2
    KEY_BYTES = 6

    DEVICE = '/dev/hidg0'
    DEVICE = '.dev.hidg0'
    NONE_KEY = scancodes['KEY_NONE']
    MOD_KEYS = ("KEY_MOD_LCTRL", "KEY_MOD_LSHIFT", "KEY_MOD_LALT", "KEY_MOD_LMETA", "KEY_MOD_RCTRL", "KEY_MOD_RSHIFT", "KEY_MOD_RALT", "KEY_MOD_RMETA")

    def write(self, key_bytes):
        print(key_bytes)
        with open(self.DEVICE, 'wb+') as kb:
            kb.write(''.join([chr(e) for e in key_bytes]).encode())

    def write_keys(self, active_keys):
        keys = []
        mods = []
        for key in active_keys:
            (mods if key in self.MOD_KEYS else keys).append(eval(key, scancodes))
        if len(keys) > self.KEY_BYTES:
            key_bytes = [scancodes['KEY_ERR_OVF']] * self.KEY_BYTES
        else:
            key_bytes = [sum(mods), self.NONE_KEY]
            key_bytes += [keys[i] if i < len(keys) else self.NONE_KEY for i in range(self.KEY_BYTES)]
        self.write([sum(mods), self.NONE_KEY] + key_bytes)

# Full GPIO Keyboard Matrix (no shift registers)
class GPIOMatrix:
    ROW_PINS = (17, 18, 19, 20, 21, 22, 23, 24)
    COL_PINS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)

    def __init__(self):
        GPIO.setup(self.ROW_PINS, GPIO.OUT)
        GPIO.setup(self.COL_PINS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read(self, keymap_matrix):
        keys = []
        for i, (row_keys) in enumerate(keymap_matrix):
            GPIO.output(self.ROW_PINS[i], GPIO.HIGH)
            for j, key in enumerate(row_keys):
                if GPIO.input(self.COL_PINS[j]):
                    keys.append(key)
            GPIO.output(self.ROW_PINS[i], GPIO.LOW)
        GPIO.cleanup()
        return keys
    
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

class ShiftRegisterMatrix:
    def __init__(self):
        shift_in = ShiftIn()
        shift_out = ShiftOut()

    def read(self):
        keys = []
        for i, (row_keys) in enumerate(keymap):
            self.shift_out.write(1 << 8)
            row_state = self.shift_in.read()
            for j, (key, state) in enumerate(zip(row_keys, row_state)):
                if state:
                    keys.append(key)
        self.shift_out(0)
        GPIO.cleanup()
        return keys

if __name__ == "__main__":
    # Setup RPi GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    keyboard_matrix = ShiftRegisterMatrix()
    usb_keyboard = UsbKeyboardOutput()

    # Load Keymap file
    keymap_file = open(KEYMAP_FILE)
    keyboard = json.load(keymap_file)
    keymap = keyboard['keymap']
    keymap_file.close()

    while True:
        start_time = time.time()

        # Scan the keyboard matrix using shift registers
        active_keys = keyboard_matrix.read()

        # Write the key state to the usb
        usb_keyboard.write_keys(set(active_keys))

        time.sleep(max(0, 0.001 - (time.time() - start_time))) # ~1kHz