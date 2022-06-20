#!/usr/bin/env python

import time
from enum import Enum

import pigpio

class PISO:
    class SPI(Enum):
        MAIN = 0
        AUX = 1

    """
    A class to read multiple inputs from one or more
    SN74HC165 PISO (Parallel In Serial Out) shift
    registers.

    Either the main SPI or auxiliary SPI peripheral
    is used to clock the data off the chip.  SPI is
    used for performance reasons.

    Connect a GPIO (referred to as SH_LD) to pin 1 of
    the first chip.

    Connect SPI SCLK to pin 2 of the first chip.  SCLK
    will be GPIO 11 if the main SPI is being used and
    GPIO 21 if the auxiliary SPI is being used.

    Connect SPI MISO to pin 9 of the last chip.  MISO
    will be GPIO 9 if the main SPI is being used and
    GPIO 19 if the auxiliary SPI is being used.

                        First chip

    Pi GPIO ------> SH/LD 1 o 16 Vcc ------ 3V3
    Pi SPI clock -> CLK   2   15 CLK INH -- Ground
                    E     3   14 D
                    F     4   13 C
                    G     5   12 B
                    H     6   11 A
    Don't connect   /Qh   7   10 SER ------ Ground
    Ground -------- GND   8    9 Qh ------> next SER


                        Middle chips

    prior SH/LD --> SH/LD 1 o 16 Vcc ------ 3V3
    prior CLK ----> CLK   2   15 CLK INH -- Ground
                    E     3   14 D
                    F     4   13 C
                    G     5   12 B
                    H     6   11 A
    Don't connect   /Qh   7   10 SER <----- prior Qh
    Ground -------- GND   8    9 Qh ------> next SER


                        Last chip

    prior SH/LD --> SH/LD 1 o 16 Vcc ------ 3V3
    prior CLK ----> CLK   2   15 CLK INH -- Ground
                    E     3   14 D
                    F     4   13 C
                    G     5   12 B
                    H     6   11 A
    Don't connect   /Qh   7   10 SER <----- prior Qh
    Ground -------- GND   8    9 Qh ------> Pi SPI MISO

    https://forums.raspberrypi.com/viewtopic.php?t=254053#p1551154
    """

    SPI_FLAGS_AUX = 256   # use auxiliary SPI device
    SPI_FLAGS_NO_CE0 = 32  # don't use CE0

    def __init__(self, pi, SH_LD, SPI_device=SPI.MAIN, chips=1):
      """
      Instantiate with the connection to the Pi.

      SL_LD is the GPIO connected to the shift/load pin
      of the shift register.

      SPI_device is either MAIN_SPI (default) or AUX_SPI.

      chips is the number of SN74HC165 being used (defaults
      to 1).
      """

      self._pi = pi

      assert 0 <= SH_LD <= 53
      self._SH_LD = SH_LD

      assert 0 <= SPI_device <= 1
      flags = self.SPI_FLAGS_NO_CE0
      if SPI_device == PISO.SPI.AUX:
         flags |= self.SPI_FLAGS_AUX
      self._h = pi.spi_open(0, 5000000, flags)

      assert 1 <= chips
      self._chips = chips

    def read(self):
      """
      Reads the shift registers and returns the readings as a byte array (one byte per chip).
      """
      data = None
      with self._lock:
         if self._exiting:
            return data
         self._pi.gpio_trigger(self._SH_LD, 1, 0)
         count, data = self._pi.spi_read(self._h, self._chips)
      return data

if __name__ == "__main__":

   import time
   import pigpio

   def cbf(pin, level, tick):
      print(pin, level, tick)

   pi = pigpio.pi()
   if not pi.connected:
      exit()

   run_for = 30

   sr = PISO(pi, SH_LD=16, SPI_device=PISO.SPI.AUX, chips=2)

   time.sleep(run_for)

   # read all registers
   r = sr.read()
   # and print each value
   for i in range(len(r)):
      print(r[i])

   sr.cancel()

   pi.stop()
