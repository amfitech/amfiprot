This package is used to interact with devices via the Amfiprot protocol developed by Amfitech.

# Prerequisites

The package requires [libusb](https://libusb.info/) to communicate with USB devices.

# Install

## Windows

Install with `pip`:

```shell
pip install amfiprot
```

Import, create connection, search for nodes and register device:

```
import amfiprot

conn = amfiprot.UsbConnection(0xC17, 0xD12)
nodes = conn.find_nodes()

print(f"Found {len(nodes)} node(s).")
for node in nodes:
	print(f"[{node.id}] {node.name}")
	
dev = amfiprot.Device(nodes[0])
conn.start()

while True:
	if dev.packet_available():
		print(dev.get_packet())
```



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