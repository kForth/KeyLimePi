'''
MIT License

Copyright (c) 2022 Kestin Goforth

Based on work from:
Copyright (c) 2018 Kyle Kowalczyk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

https://github.com/superadm1n/ShiftLib165/
'''

import RPi.GPIO as GPIO

class ShiftRegister:
    '''
    This class handles the low level bit-banging needed to interface with the register.
    It takes care of loading and shifting the register, extend this class to handle reading 
    and writing data.
    '''

    DATA_PIN_MODE = None  # To be overridden

    def __init__(self, serial_out, load_pin, clock_pin, clock_enable_pin=None, n_bits=8, data_pull_up_down=GPIO.PUD_OFF):
        '''
        :param serial_out: BCM GPIO pin that's connected to chip pin 9 (Serial Out)
        :param load_pin: BCM GPIO pin that's connected to chip pin 1 (PL)
        :param clock_enable_pin: BCM GPIO pin that's connected to chip pin 15 (Clock enable) not required
        :param clock_pin: BCM GPIO pin that's connected to chip pin 2 (Clock Pin)
        :param n_bits: Total number of bits to shift
        '''
        self._data_pin = serial_out
        self._load_pin = load_pin
        self._clock_pin = clock_pin
        self._clock_enable_pin = clock_enable_pin
        self._n_bits = n_bits
        self._data_pud = data_pull_up_down

        self._gpio_init()

    def _gpio_init(self):
        '''
        Sets up GPIO pins for output and gives them their default value

        :return: Nothing
        '''
        assert self.DATA_PIN_MODE is not None and self.DATA_PIN_MODE in (GPIO.IN, GPIO.OUT)
        assert self._data_pud is not None and self._data_pud in (GPIO.PUD_DOWN, GPIO.PUD_UP, GPIO.PUD_OFF)

        # Setup GPIO pin modes and set intitial states
        GPIO.setup(self._data_pin, self.DATA_PIN_MODE, pull_up_down=self._data_pud)
        GPIO.setup(self._clock_pin, GPIO.OUT, initial=0)
        if self._clock_enable_pin is not None:
            GPIO.setup(self._clock_enable_pin, GPIO.OUT, initial=0)
        GPIO.setup(self._load_pin, GPIO.OUT, initial=1)

    def _cycle_clock(self, n=1):
        '''
        This method will cycle the clock pin high and low to shift
        the data down the register

        :param n: Number of times to cycle clock (Default 1 time)
        :return:
        '''

        self._shift_register(n)

    def _shift_register(self, n=1):
        '''
        This method cycles the clock pin high and low which
        shifts the register down.

        :param n: number of times to cycle the clock pin (default 1 time)
        :return:
        '''

        for _ in range(n):
            GPIO.output(self._clock_pin, 1)
            GPIO.output(self._clock_pin, 0)

    def _load_register(self):
        '''
        This method takes the values on the input pins of the register and loads
        them into the internal storage register in preperation to be shifted out of the
        serial port

        :return: Nothing
        '''

        GPIO.output(self._load_pin, 0)
        GPIO.output(self._load_pin, 1)


class OutputShiftReg(ShiftRegister):
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


    DATA_PIN_MODE = GPIO.OUT
    _data_pud = GPIO.PUD_OFF

    def _write_output(self, val):
        '''
        This method will write the value to the serial in pin of the register

        :param val: Value to write to the register.
        '''

        return GPIO.output(self._data_pin, GPIO.HIGH if val else GPIO.LOW)

    def write_register(self, data):
        '''
        This method handles writing the data in to the register.
        It writes the values to the register from the data starting
        with the first bit and Pin 0.

        :param data: An integer with bits representing output states.
        '''

        # Loads the status of the input pins into the internal register
        self._load_register()

        # shifts out each bit and stores the value
        for i in range(self._n_bits):
            # Stores the value of the pin
            self._write_output(data & 1 << i)

            # Cycles the clock causing the register to shift
            self._shift_register()


class InputShiftReg(ShiftRegister):
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

    DATA_PIN_MODE = GPIO.IN
    _data_pud = GPIO.PUD_UP

    def _read_input(self):
        '''
        This method will read the value on the serial out pin from the
        register

        :return: Value read from the register
        '''

        return GPIO.input(self._data_pin)

    def read_register(self):
        '''This method handles reading the data out of the entire register.
        It loads the values into the register, shifts all of the values out of the
        register and reads the values storing them in a list left to right starting
        at Pin 0 going to the highest pin in your chain

        :return: List of pin values from the register lowest to highest pin.
        '''

        register = []

        # Loads the status of the input pins into the internal register
        self._load_register()

        # shifts out each bit and stores the value
        for _ in range(self._n_bits):
            # Stores the value of the pin
            register.append(self._read_input())

            # Cycles the clock causing the register to shift
            self._shift_register()

        # reverses the list so it reads from left to right pin0 - pin7
        return register[::-1]

if __name__ == '__main__':
    import time

    GPIO.setmode(GPIO.BCM)

    osr = OutputShiftReg(16, 20, 21)
    isr = InputShiftReg(9, 25, 11, n_bits=16)
    while True:
        try:
            for i in range(8):
                osr.write_register(1 << i)
                time.sleep(0.001)
                print(isr.read_register())
            print()
            time.sleep(1)
        except KeyboardInterrupt:
            break

    GPIO.cleanup()