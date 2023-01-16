#!/bin/bash
set -e
echo "Starting KeyLimePi..."

PRODUCT="KeyLimePi - Corsair K65"
MANUFACTURER="KeyLimePi"
SERIALNUMBER="793XiSqjuNuUicCJ"

echo "Mounting USB Disk Image"
DISKFILE=/home/pi/KeyLimePi/usbdisk.img
DISKDIR=/home/pi/KeyLimePi/usbdisk.d/
mount -o loop -t exfat $DISKFILE $DISKDIR

echo "Setting up USB Gadget Directory..."
GADGET_DIR="/sys/kernel/config/usb_gadget/keylimepi"
mkdir -p $GADGET_DIR
cd $GADGET_DIR

echo "Writing Basic USB Device Info..."
echo 0x1d6b > idVendor  # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB    # USB2

echo "Writing Product Info..."
mkdir -p strings/0x409
echo $PRODUCT > strings/0x409/product
echo $MANUFACTURER > strings/0x409/manufacturer
echo $SERIALNUMBER > strings/0x409/serialnumber

echo "Writing Config Info..."
mkdir -p configs/c.1/strings/0x409
echo 250 > configs/c.1/MaxPower

echo "Setting Up USB Ethernet Adapter..."
echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration 
mkdir -p functions/ecm.usb0
# first byte of address must be even
HOST="48:6f:73:74:50:43" # "HostPC"
# SELF="4b:65:79:4c:69:6d:65:50:69" # "KeyLimePi"
# SELF="4b:4c:50:55:53:42" # "KLPUSB"
SELF="42:61:64:55:53:42" # "BadUSB"
echo $HOST > functions/ecm.usb0/host_addr
echo $SELF > functions/ecm.usb0/dev_addr
ln -s functions/ecm.usb0 configs/c.1/

echo "Setting Up USB Input Device Functions..."
LOW_SPEED_DESC = \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0
HIGH_SPEED_DESC = \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x19\\x00\\x29\\x67\\x95\\x68\\x81\\x02\\x05\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x05\\x91\\x02\\x75\\x03\\x95\\x01\\x91\\x91\\xc0
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length
echo -ne $LOW_SPEED_DESC > functions/hid.usb0/report_desc
ln -s functions/hid.usb0 configs/c.1/

echo "Setting Up USB Mass Storage Device Functions"
mkdir -p functions/mass_storage.usb0
echo 1 > functions/mass_storage.usb0/stall
echo 0 > functions/mass_storage.usb0/lun.0/cdrom
echo 0 > functions/mass_storage.usb0/lun.0/ro
echo 0 > functions/mass_storage.usb0/lun.0/nofua
echo $DISKFILE > functions/mass_storage.usb0/lun.0/file
ln -s functions/mass_storage.usb0 configs/c.1/

echo "Enabling USB Device..."
ls /sys/class/udc > UDC

echo "Configuring Network..."
ifconfig usb0 10.0.0.1 netmask 255.255.255.252 up
route add -net default gw 10.0.0.2

echo "Running KeyLimePi..."
python /home/pi/KeyLimePi/keylimepi.py > /home/pi/KeyLimePi/keylimepi.py.log

echo "Done."
