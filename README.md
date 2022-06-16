# KeyLimePi

KeyLimePi lets you use your Raspberry Pi as a USB keyboard on another device.

## Prerequisites

Install Raspberry Pi OS and connect to your Pi's terminal.
See [raspberrypi.com](https://www.raspberrypi.com/software/) for help getting setup.

Be sure to enable ssh and setup your WiFi credentials if you're 
planning on using those.

## Setup

1. 
    Clone this repository:
    ```bash
    git clone http://github.com/kforth/KeyLimePi.git ~/KeyLimePi
    ```

2. 
    Run the setup script:
    ```bash
    cd ~/KeyLimePi & ./setup
    ```

3.
    Reboot the pi:
    ```bash
    sudo reboot now
    ```

4.
    That's it, you just have to figure out the rest.

---

[This guide](https://www.isticktoit.net/?p=1383) was very helpful in getting this project started.
[Also this file](https://github.com/ckuethe/usbarmory/wiki/USB-Gadgets) was helpful.