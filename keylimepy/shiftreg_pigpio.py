import pigpio

class OutputShiftReg:
    
    '''
    This class handles writing the values to one or more output shift registers, like a SN75HC595.

    Example wiring for SN75HC595 chain:
    TODO
                        First chip

    Pi GPIO ------> SH/LD |1 U 16| Vcc ------ 3V3
    Pi GPIO ------> CLK   |2   15| CLK INH -- Ground
                    E     |3   14| D
                    F     |4   13| C
                    G     |5   12| B
                    H     |6   11| A
    Don't connect   /Qh   |7   10| SER ------ Ground
    Ground -------- GND   |8    9| Qh ------> next SER


                        Middle chips

    prior SH/LD --> SH/LD |1 U 16| Vcc ------ 3V3
    prior CLK ----> CLK   |2   15| CLK INH -- Ground
                    E     |3   14| D
                    F     |4   13| C
                    G     |5   12| B
                    H     |6   11| A
    Don't connect   /Qh   |7   10| SER <----- prior Qh
    Ground -------- GND   |8    9| Qh ------> next SER


                        Last chip

    prior SH/LD --> SH/LD |1 U 16| Vcc ------ 3V3
    prior CLK ----> CLK   |2   15| CLK INH -- Ground
                    E     |3   14| D
                    F     |4   13| C
                    G     |5   12| B
                    H     |6   11| A
    Don't connect   /Qh   |7   10| SER <----- prior Qh
    Ground -------- GND   |8    9| Qh ------> Pi GPIO

    '''

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


class InputShiftReg:

    '''
    This class handles reading the values from one or more input shift registers, like a SN74HC165.

    Example wiring for SN74HC165 chain:
    
                        First chip

    Pi GPIO ------> SH/LD |1 U 16| Vcc ------ 3V3
    Pi GPIO ------> CLK   |2   15| CLK INH -- Ground
                    E     |3   14| D
                    F     |4   13| C
                    G     |5   12| B
                    H     |6   11| A
    Don't connect   /Qh   |7   10| SER ------ Ground
    Ground -------- GND   |8    9| Qh ------> next SER


                        Middle chips

    prior SH/LD --> SH/LD |1 U 16| Vcc ------ 3V3
    prior CLK ----> CLK   |2   15| CLK INH -- Ground
                    E     |3   14| D
                    F     |4   13| C
                    G     |5   12| B
                    H     |6   11| A
    Don't connect   /Qh   |7   10| SER <----- prior Qh
    Ground -------- GND   |8    9| Qh ------> next SER


                        Last chip

    prior SH/LD --> SH/LD |1 U 16| Vcc ------ 3V3
    prior CLK ----> CLK   |2   15| CLK INH -- Ground
                    E     |3   14| D
                    F     |4   13| C
                    G     |5   12| B
                    H     |6   11| A
    Don't connect   /Qh   |7   10| SER <----- prior Qh
    Ground -------- GND   |8    9| Qh ------> Pi GPIO

    '''

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