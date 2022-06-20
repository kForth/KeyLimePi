import platform
if any([e in platform.platform().lower() for e in ["darwin", "macos", "windows"]]):
    import fake_gpio as GPIO
else:
    import RPi.GPIO as GPIO
    
# Shift-Out Registers for Keyboard Matrix
class ShiftOut:
    DATA_PIN = 16
    LATCH_PIN = 17  # 2x 8-Bit Registers
    CLOCK_PIN = 18
    NUM_BITS = 8

    def __init__(self):
        GPIO.setup(self.DATA_PIN,GPIO.OUT)
        GPIO.setup(self.LATCH_PIN,GPIO.OUT)
        GPIO.setup(self.CLOCK_PIN,GPIO.OUT)

    def write(self, data):
        GPIO.output(self.CLOCK_PIN, 0)
        GPIO.output(self.LATCH_PIN, 0)
        GPIO.output(self.CLOCK_PIN, 1)
        # Write in reverse order
        for i in range(self.NUM_BITS, -1, -1):
            GPIO.output(self.CLOCK_PIN, 0)
            GPIO.output(self.DATA_PIN, GPIO.HIGH if (data & 1 << i) else GPIO.LOW)
            GPIO.output(self.CLOCK_PIN, 1)
        GPIO.output(self.CLOCK_PIN, 0)
        GPIO.output(self.LATCH_PIN, 1)
        GPIO.output(self.CLOCK_PIN, 1)

# Shift-In Registers for Keyboard Matrix
class ShiftIn:
    DATA_PIN = 19
    LATCH_PINS = (20, 21)  # 2x 8-Bit Registers
    CLOCK_PIN = 22
    NUM_BITS = 16

    def __init__(self):
        GPIO.setup(self.DATA_PIN,GPIO.IN)
        GPIO.setup(self.LATCH_PINS,GPIO.OUT)
        GPIO.setup(self.CLOCK_PIN,GPIO.OUT)

    def read(self):
        for latch_pin in self.LATCH_PINS:
            GPIO.output(self.CLOCK_PIN, 0)
            GPIO.output(latch_pin, 0)
            GPIO.output(self.CLOCK_PIN, 1)
            for _ in range(self.NUM_BITS, -1, -1):
                GPIO.output(self.CLOCK_PIN, 0)
                yield GPIO.input(self.DATA_PIN)
                GPIO.output(self.CLOCK_PIN, 1)
            GPIO.output(self.CLOCK_PIN, 0)
            GPIO.output(latch_pin, 1)
            GPIO.output(self.CLOCK_PIN, 1)