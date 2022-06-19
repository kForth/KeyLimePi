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
echo 0x1d6b > idVendor # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB # USB2

echo "Writing Product Info..."
mkdir -p strings/0x409
echo $PRODUCT > strings/0x409/product
echo $MANUFACTURER > strings/0x409/manufacturer
echo $SERIALNUMBER > strings/0x409/serialnumber

echo "Writing MaxPower Flag..."
mkdir -p configs/c.1/strings/0x409
echo 250 > configs/c.1/MaxPower

echo "Setting Up USB Input Device Functions..."
DESC = \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length
echo -ne $DESC > functions/hid.usb0/report_desc
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

echo "Running KeyLimePi..."
python /home/pi/KeyLimePi/keylimepi.py >> /home/pi/KeyLimePi/keylimepi.py.log

echo "Done."
