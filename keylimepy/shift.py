import pigpio
    
# Shift-Out Registers for Keyboard Matrix
class ShiftOut:
    DATA_PIN = 16
    LATCH_PIN = 17  # 2x 8-Bit Registers
    CLOCK_PIN = 18
    NUM_BITS = 8

    def __init__(self, pi):
        self._pi = pi
        
        pi.set_mode(self.DATA_PIN, pigpio.OUTPUT)
        pi.set_mode(self.LATCH_PIN, pigpio.OUTPUT)
        pi.set_mode(self.CLOCK_PIN, pigpio.OUTPUT)

    def write(self, data):
        self._pi.write(self.CLOCK_PIN, 0)
        self._pi.write(self.LATCH_PIN, 0)
        self._pi.write(self.CLOCK_PIN, 1)
        # Write in reverse order
        for i in range(self.NUM_BITS, -1, -1):
            self._pi.write(self.CLOCK_PIN, 0)
            self._pi.write(self.DATA_PIN, data & 1 << i)
            self._pi.write(self.CLOCK_PIN, 1)
        self._pi.write(self.CLOCK_PIN, 0)
        self._pi.write(self.LATCH_PIN, 1)
        self._pi.write(self.CLOCK_PIN, 1)

# Shift-In Registers for Keyboard Matrix
class ShiftIn:
    DATA_PIN = 19
    LATCH_PINS = (20, 21)  # 2x 8-Bit Registers
    CLOCK_PIN = 22
    NUM_BITS = 16

    def __init__(self, pi):
        self._pi = pi

        pi.set_mode(self.DATA_PIN, pigpio.INPUT)
        pi.set_mode(self.LATCH_PINS, pigpio.OUTPUT)
        pi.set_mode(self.CLOCK_PIN, pigpio.OUTPUT)

    def read(self):
        for latch_pin in self.LATCH_PINS:
            self._pi.write(self.CLOCK_PIN, 0)
            self._pi.write(latch_pin, 0)
            self._pi.write(self.CLOCK_PIN, 1)
            for _ in range(self.NUM_BITS, -1, -1):
                self._pi.write(self.CLOCK_PIN, 0)
                yield self._pi.read(self.DATA_PIN)
                self._pi.write(self.CLOCK_PIN, 1)
            self._pi.write(self.CLOCK_PIN, 0)
            self._pi.write(latch_pin, 1)
            self._pi.write(self.CLOCK_PIN, 1)