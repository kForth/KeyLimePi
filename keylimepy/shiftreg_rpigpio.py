import RPi.GPIO as GPIO

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
    LATCH_PIN = 20
    CLOCK_PIN = 21
    NUM_BITS = 8

    def __init__(self):
        GPIO.setup(self.DATA_PIN, GPIO.OUT)
        GPIO.setup(self.LATCH_PIN, GPIO.OUT)
        GPIO.setup(self.CLOCK_PIN, GPIO.OUT)

    def write(self, data):
        GPIO.output(self.CLOCK_PIN, 0)
        GPIO.output(self.LATCH_PIN, 0)
        GPIO.output(self.CLOCK_PIN, 1)
        # Write in reverse order
        for i in range(self.NUM_BITS, -1, -1):
            GPIO.output(self.CLOCK_PIN, 0)
            GPIO.output(self.DATA_PIN, 1 if (data & (1 << i)) else 0)
            GPIO.output(self.CLOCK_PIN, 1)
        GPIO.output(self.CLOCK_PIN, 0)
        GPIO.output(self.LATCH_PIN, 1)
        GPIO.output(self.CLOCK_PIN, 1)


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

    DATA_PIN = 9 #19
    LATCH_PIN = 25 # (20, 21)  # 2x 8-Bit Registers
    CLOCK_PIN = 11 #22
    NUM_BITS = 16

    def __init__(self):
        GPIO.setup(self.DATA_PIN, GPIO.IN)
        GPIO.setup(self.LATCH_PIN, GPIO.OUT)
        GPIO.setup(self.CLOCK_PIN, GPIO.OUT)

        # GPIO.set_pull_up_down(self.DATA_PIN, pigpio.PUD_UP)

    def read(self):
        bits = []
        # for latch_pin in self.LATCH_PIN:
        GPIO.output(self.CLOCK_PIN, 0)
        GPIO.output(self.LATCH_PIN, 0)
        GPIO.output(self.CLOCK_PIN, 1)
        for _ in range(self.NUM_BITS, -1, -1):
            GPIO.output(self.CLOCK_PIN, 0)
            bits.append(GPIO.INPUT(self.DATA_PIN))
            GPIO.output(self.CLOCK_PIN, 1)
        GPIO.output(self.CLOCK_PIN, 0)
        GPIO.output(self.LATCH_PIN, 1)
        GPIO.output(self.CLOCK_PIN, 1)
        return bits
