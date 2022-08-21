This package is used to interact with devices via the Amfiprot protocol developed by Amfitech.

The package requires [libusb](https://libusb.info/) to communicate with USB devices.

# Install

## Windows

## Linux
```
$ sudo apt install libusb-1.0-0-dev
```

To access USB devices from "plugdev" group without root privileges:
```
$ echo 'SUBSYSTEM=="usb", MODE="660", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/50-pyusb.rules
$ sudo udevadm control --reload
$ sudo udevadm trigger
```