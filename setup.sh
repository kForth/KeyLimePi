#!/bin/bash
set -e

# Enable I2C
# Enable SPI

echo "Installing Prerequisites"
sudo apt-get install python3 libopenjp2-7 python3-pip pigpiod
python3 -m pip install -r requirements.txt

echo "Loading Required Modules"
sudo modprobe libcomposite
sudo modprobe loop

KEYBOARD_MANUFACTURER="Corsair"
KEYBOARD_MODEL="Vengrance K65"

BASE_DIR="/home/pi/KeyLimePi"

echo "Setting Up KeyLimePi Directory..."
mkdir -p $BASE_DIR && cd $BASE_DIR
touch keylimepi.log
touch keylimepi.py.log
chmod +x keylimepi.sh

echo "Enabling Device Tree Overlay..."
if ! [ $(sudo grep -Fxc "dtoverlay=dwc2" /boot/config.txt) ]; then
    echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
fi
if ! [ $(sudo grep -Fxc "dwc2" /etc/modules) ]; then
    echo "dwc2" | sudo tee -a /etc/modules
fi

echo "Enabling libcomposite Driver..."
if ! [ $(sudo grep -Fxc "libcomposite" /etc/modules) ]; then
    echo "libcomposite" | sudo tee -a /etc/modules
fi

echo "Enabling loop Driver..."
if ! [ $(sudo grep -Fxc "loop" /etc/modules) ]; then
    echo "loop" | sudo tee -a /etc/modules
fi

echo "Creating Startup Services..."
SERVICE="keylimepi.service"
SERVICE_FILE="/lib/systemd/system/${SERVICE}"
sudo test -f $SERVICE_FILE && sudo rm $SERVICE_FILE
sudo cp keylimepi.service $SERVICE_FILE
sudo chmod +x $SERVICE_FILE
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE
sudo systemctl enable pigpiod

echo "Setting Up USB Disk Image..."
DISKFILE="usbdisk.img"
DISKDIR="usbdisk.d/"
sudo test -f $DISKFILE && sudo rm $DISKFILE
sudo test -d $DISKDIR && sudo rm -r $DISKDIR
dd if=/dev/zero of=${BASE_DIR}/${DISKFILE} bs=1 count=0 seek=1G
mkfs.exfat -n KeyLimePi ${BASE_DIR}/${DISKFILE}
mkdir -p $DISKDIR

echo "Writing Defaults to USB Disk"
DEFAULT_CONFIG="${BASE_DIR}/keyboards/${KEYBOARD_MANUFACTURER}/${KEYBOARD_MODEL}/default_keymap.json"
sudo mount -o loop -t exfat ${BASE_DIR}/${DISKFILE} ${BASE_DIR}/${DISKDIR}
sudo cp ${DEFAULT_CONFIG} ${BASE_DIR}/${DISKDIR}
sudo umount ${BASE_DIR}/${DISKDIR}

echo "Done."