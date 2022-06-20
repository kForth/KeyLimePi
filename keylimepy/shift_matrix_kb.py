# import pigpio

from shift import ShiftOut
from piso import PISO

class ShiftRegisterMatrix:
    def __init__(self, pi):
        self._pi = pi
        self.shift_out = ShiftOut(pi) # TODO: Pins
        self.shift_in = PISO(pi, SH_LD=16, SPI_device=PISO.SPI.MAIN, chips=2)  # Pins 16, 9, 11

    def read(self, keymap):
        for row_keys in keymap:
            self.shift_out.write(1 << 8)
            row_state = self.shift_in.read()
            for key, state in zip(row_keys, row_state):
                if state:
                    yield key
        self.shift_out.write(0)

    def read_bytes(self, keymap):
        byte_val = 0
        for row_keys in keymap:
            self.shift_out.write(1 << 8)
            row_state = self.shift_in.read()
            for key, state in zip(row_keys, row_state):
                byte_val |= state << key
        self.shift_out.write(0)
        return byte_val