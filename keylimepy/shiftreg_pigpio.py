import pigpio

class OutputShiftReg:
    
    '''
    This class handles writing the values to one or more output shift registers, like a SN75HC595.

    Example wiring for a single SN75HC595 chip:

                   First chip

                Qb  |1 U 16| Vcc ------ 3V3
                Qc  |2   15| Qa
                Qd  |3   14| SER ------ Pi GPIO (Data Pin)
                Qe  |4   13| OE ------- Ground
                Qf  |5   12| RCLK  ---- Pi GPIO (Latch Pin)
                Qg  |6   11| SRCLK ---- Pi GPIO (Clock Pin)
                Qh  |7   10| SRCLR ---- 3V3
    Ground ---- GND |8    9| Qh' ------ not connected

    Example wiring for chain of SN75HC595 chips:

                   First chip

                Qb  |1 U 16| Vcc ------ 3V3
                Qc  |2   15| Qa
                Qd  |3   14| SER ------ Pi GPIO (Data Pin)
                Qe  |4   13| OE ------- Ground
                Qf  |5   12| RCLK  ---- Pi GPIO (Latch Pin)
                Qg  |6   11| SRCLK ---- Pi GPIO (Clock Pin)
                Qh  |7   10| SRCLR ---- 3V3
    Ground ---- GND |8    9| Qh' ------ next SER


                  Middle chips

                Qb  |1 U 16| Vcc ------ 3V3
                Qc  |2   15| Qa
                Qd  |3   14| SER ------ prior Qh'
                Qe  |4   13| OE ------- Ground
                Qf  |5   12| RCLK  ---- prior RCLK
                Qg  |6   11| SRCLK ---- prior SRCLK
                Qh  |7   10| SRCLR ---- 3V3
    Ground ---- GND |8    9| Qh' ------ next SER


                    Last chip

                Qb  |1 U 16| Vcc ------ 3V3
                Qc  |2   15| Qa
                Qd  |3   14| SER ------ prior Qh'
                Qe  |4   13| OE ------- Ground
                Qf  |5   12| RCLK  ---- prior RCLK
                Qg  |6   11| SRCLK ---- prior SRCLK
                Qh  |7   10| SRCLR ---- 3V3
    Ground ---- GND |8    9| Qh' ------ not connected

    '''

    DATA_PIN = 16
    LATCH_PIN = 20
    CLOCK_PIN = 21
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
            self._pi.write(self.DATA_PIN, 1 if (data & (1 << i)) else 0)
            self._pi.write(self.CLOCK_PIN, 1)
        self._pi.write(self.CLOCK_PIN, 0)
        self._pi.write(self.LATCH_PIN, 1)
        self._pi.write(self.CLOCK_PIN, 1)


class InputShiftReg:

    '''
    This class handles reading the values from one or more input shift registers, like a SN74HC165.

    Example wiring for SN74HC165 chain:
    
                        First chip

    Pi GPIO ------- SH/LD |1 U 16| Vcc ------ 3V3
    Pi GPIO ------- CLK   |2   15| CLK INH -- Ground
                    E     |3   14| D
                    F     |4   13| C
                    G     |5   12| B
                    H     |6   11| A
    not connected - /Qh   |7   10| SER ------ Ground
    Ground -------- GND   |8    9| Qh ------- next SER


                        Middle chips

    prior SH/LD --- SH/LD |1 U 16| Vcc ------ 3V3
    prior CLK ----- CLK   |2   15| CLK INH -- Ground
                    E     |3   14| D
                    F     |4   13| C
                    G     |5   12| B
                    H     |6   11| A
    not connected - /Qh   |7   10| SER ------ prior Qh
    Ground -------- GND   |8    9| Qh ------- next SER


                        Last chip

    prior SH/LD --- SH/LD |1 U 16| Vcc ------ 3V3
    prior CLK ----- CLK   |2   15| CLK INH -- Ground
                    E     |3   14| D
                    F     |4   13| C
                    G     |5   12| B
                    H     |6   11| A
    not connected - /Qh   |7   10| SER ------ prior Qh
    Ground -------- GND   |8    9| Qh ------- Pi GPIO

    '''

    DATA_PIN = 21
    LATCH_PIN = 24
    CLOCK_PIN = 23
    NUM_BITS = 16  # 2x 8-Bit Registers

    def __init__(self, pi):
        self._pi = pi

        pi.set_mode(self.DATA_PIN, pigpio.INPUT)
        pi.set_mode(self.LATCH_PIN, pigpio.OUTPUT)
        pi.set_mode(self.CLOCK_PIN, pigpio.OUTPUT)

    def read(self):
        bits = []
        self._pi.write(self.CLOCK_PIN, 0)
        self._pi.write(self.LATCH_PIN, 0)
        self._pi.write(self.CLOCK_PIN, 1)
        for _ in range(self.NUM_BITS, -1, -1):
            self._pi.write(self.CLOCK_PIN, 0)
            bits.append(self._pi.read(self.DATA_PIN))
            self._pi.write(self.CLOCK_PIN, 1)
        self._pi.write(self.CLOCK_PIN, 0)
        self._pi.write(self.LATCH_PIN, 1)
        self._pi.write(self.CLOCK_PIN, 1)
        return bits

if __name__ == "__main__":
    import time

    import pigpio

    pi = pigpio.pi()

    if not pi.connected:
        exit()
    
    sri = InputShiftReg(pi)
    sro = OutputShiftReg(pi)

    for i in range(8):
        sro.write(1 << i)
        r = sri.read()
        print(r)
    sro.write(0)