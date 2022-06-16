#!/usr/bin/env python
import time
import json

import RPi.GPIO as GPIO

# USB Keyboard Output
DEVICE = '/dev/hidg0'
NULL = chr(0)
    
# Keyboard Matrix Pin Numbers
LINE_PINS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
COL_PINS = [17, 18, 19, 20, 21, 22, 23, 24]

def write(str):
    with open(DEVICE, 'rb+') as kb:
        kb.write(str.encode())

def write_code(code, shift=False):
    write((chr(32) if shift else NULL) + NULL + chr(code) + NULL * 5)

def write_char(char, shift=False):
    write_code(ord(char[0].lower()) - 93, shift=shift)

if __name__ == "__main__":
    # Setup RPi GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for line in LINE_PINS:
        GPIO.setup(line, GPIO.OUT)
    for col in COL_PINS:
        GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Load Keymap file
    keymap_file = open("/home/pi/KeyLimePi/usbdisk.d/keymap.json")
    keymap = json.load(keymap_file)
    matrix = keymap['keymap']
    keymap_file.close()

    last_state = [[0] * len(matrix[0])] * len(matrix)

    while True:
        # Scan the keyboard matrix
        for i, (line, keys) in enumerate(zip(LINE_PINS, matrix)):
            GPIO.output(line, GPIO.HIGH)
            for j, (col, key) in enumerate(zip(COL_PINS, keys)):
                state = GPIO.input(col)
                if state != last_state[i][j]:
                    print(i, j, key, state)
                    # write_key_event(key, state)
            GPIO.output(line, GPIO.LOW)

        time.sleep(0.001) # ~1kHz