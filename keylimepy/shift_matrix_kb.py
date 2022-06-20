import platform
if any([e in platform.platform().lower() for e in ["darwin", "macos", "windows"]]):
    import fake_gpio as GPIO
else:
    import RPi.GPIO as GPIO

from shift import ShiftIn, ShiftOut

class ShiftRegisterMatrix:
    def __init__(self):
        self.shift_in = ShiftIn()
        self.shift_out = ShiftOut()

    def read(self, keymap):
        for row_keys in keymap:
            self.shift_out.write(1 << 8)
            row_state = self.shift_in.read()
            for key, state in zip(row_keys, row_state):
                if state:
                    yield key
        self.shift_out.write(0)
        GPIO.cleanup()

    def read_bytes(self, keymap):
        byte_val = 0
        for row_keys in keymap:
            self.shift_out.write(1 << 8)
            row_state = self.shift_in.read()
            for key, state in zip(row_keys, row_state):
                if state:
                    byte_val += 1 << key
        self.shift_out.write(0)
        GPIO.cleanup()
        return byte_val