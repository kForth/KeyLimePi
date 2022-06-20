import platform
if any([e in platform.platform().lower() for e in ["darwin", "macos", "windows"]]):
    import fake_gpio as GPIO
else:
    import RPi.GPIO as GPIO

# Full GPIO Keyboard Matrix (no shift registers)
class GPIOMatrix:
    ROW_PINS = (17, 18, 19, 20, 21, 22, 23, 24)
    COL_PINS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)

    def __init__(self):
        GPIO.setup(self.ROW_PINS, GPIO.OUT)
        GPIO.setup(self.COL_PINS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read(self, keymap_matrix):
        for i, (row_keys) in enumerate(keymap_matrix):
            GPIO.output(self.ROW_PINS[i], GPIO.HIGH)
            for j, key in enumerate(row_keys):
                if GPIO.input(self.COL_PINS[j]):
                    yield key
            GPIO.output(self.ROW_PINS[i], GPIO.LOW)
        GPIO.cleanup()