# from shiftreg_pigpio import InputShiftReg, OutputShiftReg
from shiftreg_rpigpio import InputShiftReg, OutputShiftReg
from usb_hid_scancodes import scancodes

class ShiftRegisterMatrix:
    def __init__(self):
        self.shift_out = OutputShiftReg()
        self.shift_in = InputShiftReg(n_bits=16)

    def read_bits(self, rows, cols):
        bits = []
        for i in range(rows):
            self.shift_out.write(1 << i)
            row_state = self.shift_in.read()
            bits.append(row_state)
        self.shift_out.write(0)
        return bits

    def read_keys(self, keymap):
        keys = []
        for i, row_keys in enumerate(keymap):
            self.shift_out.write(1 << i)
            row_state = self.shift_in.read()
            for key, state in zip(row_keys, row_state):
                if state:
                    keys.append(key)
        self.shift_out.write(0)
        return keys

    def read_bytes(self, keymap):
        byte_val = 0
        for i, row_keys in enumerate(keymap):
            self.shift_out.write(1 << i)
            row_state = self.shift_in.read()
            for key, state in zip(row_keys, row_state):
                byte_val |= state << scancodes.get(key, 0)
        self.shift_out.write(0)
        return byte_val

if __name__ == "__main__":

    import json
    import time

    keyboard = json.load(open('../keyboards/Corsair/Vengeance K65/default_keymap.json'))
    keymap = keyboard['keymap']

    # import pigpio

    # print("Connecting to pigpiod")
    # pi = pigpio.pi()
    # if not pi.connected:
    #     exit()

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    srm = ShiftRegisterMatrix()

    st = time.time()
    bits = srm.read_bits(8, 16)
    print(time.time() - st)
    for b in bits:
        print(b)
    print()

    st = time.time()
    bits = srm.read_keys(keymap)
    print(time.time() - st)
    print(bits)
    print()

    st = time.time()
    bits = srm.read_bytes(keymap)
    print(time.time() - st)
    print(hex(bits))
    print()