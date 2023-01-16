import time

import RPi.GPIO as GPIO

# Full GPIO Keyboard Matrix (no shift registers)
class GPIOMatrix:
    ROW_PINS = (14, 15, 18)
    COL_PINS = (17, 27, 22)

    def __init__(self):
        GPIO.setup(self.ROW_PINS, GPIO.OUT)
        GPIO.setup(self.COL_PINS, GPIO.IN)

    def read(self, keymap_matrix):
        keys = []
        for i, row_pin in enumerate(self.ROW_PINS):
            row_keys = keymap_matrix[i]
            GPIO.output(row_pin, GPIO.HIGH)
            time.sleep(0.1)
            for j, col_pin in enumerate(self.COL_PINS):
                key = row_keys[j]
                if GPIO.input(col_pin):
                    keys.append(key)
            GPIO.output(row_pin, GPIO.LOW)
            time.sleep(0.1)
        GPIO.cleanup()
        return keys

if __name__ == "__main__":

    import json

    keyboard = json.load(open('../keyboards/Corsair/Vengeance K65/default_keymap.json'))
    keymap = keyboard['keymap']

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    kb = GPIOMatrix()

    print(kb.read(keymap))