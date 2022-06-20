# import pigpio

# from shift import ShiftOut, ShiftIn
from sipo import SIPO
from piso import PISO

class ShiftRegisterMatrix:
    def __init__(self, pi):
        self._pi = pi
        self.shift_out = SIPO(pi, SH_LD=17, SPI_device=SIPO.SPI.MAIN, chips=1)  # Pins 17, 9, 11
        self.shift_in = PISO(pi, SH_LD=16, SPI_device=PISO.SPI.AUX, chips=2)  # Pins 16, 19, 21
        # self.shift_out = ShiftOut(pi)
        # self.shift_in = ShiftIn(pi)

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