#!/bin/bash
set -e

modprobe loop

echo "Setting Up KeyLimePi Directory..."
mkdir -p ~/KeyLimePi && cd ~/KeyLimePi
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

echo "Creating Startup Service..."
SERVICE="keylimepi.service"
SERVICE_FILE="/lib/systemd/system/${SERVICE}"
sudo test -f $SERVICE_FILE && sudo rm $SERVICE_FILE
sudo cp keylimepi.service $SERVICE_FILE
sudo chmod +x $SERVICE_FILE
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE

echo "Setting Up USB Disk Image..."
DISKFILE="usbdisk.img"
DISKDIR="usbdisk.d/"
sudo test -f $DISKFILE && sudo rm $DISKFILE
sudo test -d $DISKDIR && sudo rm -r $DISKDIR
dd if=/dev/zero of=~/KeyLimePi/${DISKFILE} bs=1 count=0 seek=1G
mkfs.exfat -n KeyLimePi ~/KeyLimePi/${DISKFILE}
mkdir -p $DISKDIR

echo "Writing Defaults to USB Disk"
sudo mount -o loop -t exfat /home/pi/KeyLimePi/${DISKFILE} /home/pi/KeyLimePi/${DISKDIR}
sudo cp default_keymap.json /home/pi/KeyLimePi/$DISKDIR
sudo umount /home/pi/KeyLimePi/${DISKDIR}

echo "Done."