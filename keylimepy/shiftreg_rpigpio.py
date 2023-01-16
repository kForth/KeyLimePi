import time

import RPi.GPIO as GPIO

class _ShiftRegister:
    # DWELL_TIME = 0

    def __init__(self):
        pass

    def _dwell(self):
        time.sleep(self.DWELL_TIME)

class OutputShiftReg(_ShiftRegister):
    
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

    Datasheet Reference: https://www.ti.com/lit/ds/symlink/sn74hc595.pdf

    '''

    DWELL_TIME = 1e-3

    def __init__(self, ser=15, rclk=20, srclk=21, n_bits=8):
        self._data_pin = ser
        self._latch_pin = rclk
        self._clock_pin = srclk
        self._n_bits = n_bits
        GPIO.setup(self._data_pin, GPIO.OUT)
        GPIO.setup(self._latch_pin, GPIO.OUT)
        GPIO.setup(self._clock_pin, GPIO.OUT)
    
    def _clock(self):
        GPIO.output(self._clock_pin, 1)
        self._dwell()
        GPIO.output(self._clock_pin, 0)
        self._dwell()
    
    def _latch(self):
        GPIO.output(self._latch_pin, 1)
        self._dwell()
        GPIO.output(self._latch_pin, 0)
        self._dwell()

    def write(self, data):
        GPIO.output(self._clock_pin, 0)
        GPIO.output(self._latch_pin, 0)
        self._dwell()
        for i in range(self._n_bits, -1, -1): # Write bits in reverse order
            GPIO.output(self._data_pin, 1 if (data & (1 << i)) else 0)
            self._dwell()
            self._clock()
            self._latch()

    def write_bits(self, data):
        GPIO.output(self._clock_pin, 0)
        GPIO.output(self._latch_pin, 0)
        self._dwell()
        self._clock()
        for bit in data[::-1]: # Write bits in reverse order
            GPIO.output(self._data_pin, 1 if bit else 0)
            self._dwell()
            self._clock()
        self._latch()
        self._clock()


class InputShiftReg(_ShiftRegister):
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

    Datasheet Reference: https://www.ti.com/lit/ds/symlink/sn74hc165.pdf

    '''

    DWELL_TIME = 1e-5

    _data_pin = 9
    _load_pin = 8
    _clock_pin = 11
    _n_bits = 16  # 2x 8-Bit Registers

    def __init__(self, qh=9, sh_ld=8, clk=11, n_bits=8):
        self._data_pin = qh
        self._load_pin = sh_ld
        self._clock_pin = clk
        self._n_bits = n_bits

        GPIO.setup(self._data_pin, GPIO.IN)
        GPIO.setup(self._load_pin, GPIO.OUT)
        GPIO.setup(self._clock_pin, GPIO.OUT)

    def _clock(self):
        GPIO.output(self._clock_pin, 1)
        self._dwell()
        GPIO.output(self._clock_pin, 0)
        self._dwell()

    def _load(self):
        GPIO.output(self._clock_pin, 1)
        self._dwell()
        GPIO.output(self._load_pin, 0)
        self._dwell()
        GPIO.output(self._clock_pin, 0)
        self._dwell()
        GPIO.output(self._load_pin, 1)
        self._dwell()

    def read(self):
        bits = []
        self._clock()
        self._load()
        for _ in range(self._n_bits, -1, -1):
            self._clock()
            bits.append(GPIO.input(self._data_pin))
        self._clock()
        return bits


if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    sro = OutputShiftReg()
    sri = InputShiftReg(n_bits=16)

    while True:
        for i in range(8):
            bits = [0] * 8
            bits[i] = 1
            sro.write_bits(bits)
            # sro.write(1 << i)
            r = sri.read()
            print(r)
        sro.write(0)
        print()