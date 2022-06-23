import RPi.GPIO as GPIO
    
# Shift-Out Registers for Keyboard Matrix
class OutputShiftReg:
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

# Shift-In Registers for Keyboard Matrix
class ShiftIn:
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
