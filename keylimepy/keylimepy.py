#!/usr/bin/env python

# KEYMAP_FILE = "/home/pi/KeyLimePi/usbdisk.d/keymap.json"
KEYMAP_FILE = "../keyboards/Corsair/Vengeance K65/default_keymap.json"

if __name__ == "__main__":
    import time
    import json

    import pigpio
    # import RPi.GPIO as GPIO
    from PIL import ImageFont
    from cheap_oled import OLED_SH1106, OLED_Canvas

    from shift_matrix_kb import ShiftRegisterMatrix
    from usb_kb_output import UsbKeyboardOutput

    # Setup GPIO
    pi = pigpio.pi()
    if not pi.connected:
        exit()

    # GPIO.setwarnings(False)
    # GPIO.setmode(GPIO.BCM)

    font = ImageFont.truetype("/home/pi/KeyLimePi/keylimepy/oled/fonts/C&C Red Alert [INET].ttf", 24)
    oled = OLED_SH1106(port=1, address=0x3C)

    with OLED_Canvas(oled) as draw: 
        draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
        draw.text((0, 0), f"Initialzing", 255, font=font)
        draw.text((0, 20), f"KeyLimePi", 255, font=font)
        # draw.text((0, 40), f"", 255, font=font)

    keyboard_matrix = ShiftRegisterMatrix(pi)
    usb_keyboard = UsbKeyboardOutput()

    # Load Keymap file
    keymap_file = open(KEYMAP_FILE)
    keyboard = json.load(keymap_file)
    keymap = keyboard['keymap']
    keymap_file.close()

    with OLED_Canvas(oled) as draw: 
        draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    while True:
        start_time = time.time()

        # Scan the keyboard matrix using shift registers
        active_keys = keyboard_matrix.read(keymap)

        # Write the key state to the usb
        usb_keyboard.write_nkro(active_keys)

        # print(time.time() - start_time)
        time.sleep(max(0, (1/125) - (time.time() - start_time))) # ~125Hz