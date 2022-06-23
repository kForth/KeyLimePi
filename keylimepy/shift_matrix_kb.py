from shiftreg_pigpio import InputShiftReg, OutputShiftReg

class ShiftRegisterMatrix:
    def __init__(self, pi):
        self._pi = pi
        self.shift_out = OutputShiftReg(pi, 16, 20, 21)
        self.shift_in = InputShiftReg(pi, SH_LD=25, chips=2)

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