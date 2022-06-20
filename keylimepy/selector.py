import pigpio

class SelectorSwitch:
    def __init__(self, pi, pins):
        self._pi = pi
        self._pins = pins

        for pin in pins:
            pi.set_mode(pin, pigpio.INPUT)

    def read(self):
        val = 0
        for i, pin in enumerate(self._pins):
            val |= self._pi.read(pin) << i
        return val