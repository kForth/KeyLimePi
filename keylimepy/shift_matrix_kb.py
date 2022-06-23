from shiftreg_pigpio import InputShiftReg, OutputShiftReg

class ShiftRegisterMatrix:
    def __init__(self, pi):
        self._pi = pi
        self.shift_out = OutputShiftReg(pi, 16, 20, 21)
        self.shift_in = InputShiftReg(pi, SH_LD=25, chips=2)

    def read(self, rows, cols):
        for i in range(rows):
            self.shift_out.write(1 << i)
            row_state = self.shift_in.read()
            for j in range(len(row_state)):
                print(f"{i:02d}:{j:02d} -> {row_state[j]}")
        self.shift_out.write(0)

    # def read(self, keymap):
    #     for i, row_keys in enumerate(keymap):
    #         self.shift_out.write(1 << i)
    #         row_state = self.shift_in.read()
    #         for key, state in zip(row_keys, row_state):
    #             if state:
    #                 yield key
    #     self.shift_out.write(0)

    def read_bytes(self, keymap):
        byte_val = 0
        for i, row_keys in enumerate(keymap):
            self.shift_out.write(1 << i)
            row_state = self.shift_in.read()
            for key, state in zip(row_keys, row_state):
                byte_val |= state << key
        self.shift_out.write(0)
        return byte_val

if __name__ == "__main__":

    import pigpio

    print("Connecting to pigpiod")
    pi = pigpio.pi()
    if not pi.connected:
        exit()

    srm = ShiftRegisterMatrix(pi)

    print(srm.read(8, 8))