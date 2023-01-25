Amfiprot is a communication protocol for embedded devices used and developed by Amfitech. The protocol can be extended with plugins for specific devices implementing the Amfiprot protocol (e.g. the AmfiTrack).

# Prerequisites

- Python 3.6 or higher.
- [libusb](https://libusb.info/) in order to communicate with USB devices through `pyusb`

# Installation

## Windows

Get a libusb Windows binary from https://libusb.info/. From the downloaded archive, copy the following two files:

- `VS2015-x64\dll\libusb-1.0.dll` to `C:\Windows\System32`
- `VS2015-Win32\dll\libusb-1.0.dll` to `C:\Windows\SysWOW64`

Install (or update) `amfiprot` with `pip`:

```shell
pip install -U amfiprot
```

## Linux (Ubuntu)

Install `libusb`:

```shell
sudo apt install libusb-1.0-0-dev
```

Make sure that your user has access to USB devices. For example, give the `plugdev` group access to USB devices by creating a udev rule:

```shell
echo 'SUBSYSTEM=="usb", MODE="660", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/50-pyusb.rules
sudo udevadm control --reload
sudo udevadm trigger
```

Check whether you are a member of `plugdev` with:

```shell
groups <username>
```

If not, add yourself to the group with:

``` shell
sudo usermod -aG plugdev <username>
```

Finally, install (or update) `amfiprot` with `pip`:

```shell
pip install -U amfiprot
```

# Quick start

The basic workflow when using the library is:

1. Create a `Connection` to a device connected directly to the host machine (we call this the "root node").
2. Search for `Node`s on the `Connection` (i.e. nodes connected through the root node)
3. Create a `Device` using one of the discovered `Node`s.
4. Start the `Connection`.
5. Communicate with the `Device`.

Example:

```python
import amfiprot

VENDOR_ID = 0xC17
PRODUCT_ID = 0xD12

if __name__ == "__main__":
    conn = amfiprot.UsbConnection(VENDOR_ID, PRODUCT_ID)
    nodes = conn.find_nodes()

    print(f"Found {len(nodes)} node(s).")
    for node in nodes:
        print(f"[{node.tx_id}] {node.name}")

    dev = amfiprot.Device(nodes[0])
    conn.start()
    
    cfg = dev.config.read_all()

    while True:
        if dev.packet_available():
            print(dev.get_packet())
```

The following sections provide a more in-depth explanation.

## Discovering and connecting to a root node

After attaching a device to your host machine, you can scan for connected devices (e.g. connected via USB) with:

```python
phys_devs = amfiprot.UsbConnection.scan_physical_devices()

for dev in phys_devs:
    print(dev)
```

A connection can then be created using a specific physical device:

```python
conn = amfiprot.UsbConnection(dev['vid'], dev['pid'], dev['serial_number'])
```

Using `serial_number` is optional. If none is given, the first device matching the given vendor and product ID is used.

## Finding nodes

After creating a connection, we can search for nodes that are connected to the root node (e.g. via RF or UART):

```python
nodes = conn.find_nodes()
```

`find_nodes()` returns a list of `Node` instances. A `Node` provides a low-level interface to the physical device and can be used to retrieve the `uuid`, `tx_id` and `name` of the device, and send/receive raw packets. It is not recommended to use the `Node` directly, but rather attach it to a `Device` instance.

## Creating a device

A `Device` is an abstraction layer on top of a `Node` and is created by injecting a `Node` in the constructor:

```python
dev = amfiprot.Device(node)
```

The `Device` provides a higher-level interface allowing the user to easily:

- Update the firmware
- Reboot the device
- Read/write configurations
- Read decoded packets

We are still able to access the `Node` through the `Device` if necessary:

```python
tx_id = dev.node.tx_id
```

## Starting the connection and interacting with the device

Before interacting with the `Device`, the `Connection` must be started:

```python
conn.start()
```

This creates a child process that asynchronously sends and receives packets on the specified interface. We can now interact with the `Device` in the main process without worrying about blocking:

```python
device_name = dev.name()
print(f"Reading packets from {device_name}...")

while True:
	if dev.packet_available():
		print(dev.get_packet())
```

We can access the device configuration through a `Configurator` instance which is automatically created as a member (`dev.config`) of the `Device`:

```python
# Read the entire configuration as a JSON-like object (a list of dicts)
cfg = dev.config.read_all()

# Print all parameters
for category in cfg:
    print(f"CATEGORY: {category['name']}")
    for parameter in category['parameters']:
        print(parameter)
```

The configuration can be easily saved to and loaded from a `.json` file:

```python
import json

# Write configuration to file
with open("config.json", "w") as outfile:
	json.dump(cfg, outfile, indent=4)

# Read configuration from file and send to device
with open("config.json", "r") as infile:
    new_cfg = json.load(infile)
    dev.config.write_all(new_cfg)
```

# Contributions and bug reporting

The Amfiprot Python package is open-source and the source code can be found on our [Github repository](https://github.com/amfitech/amfiprot). Contributions can be made through pull requests to the `development` branch. Bug reports and feature requests can be created in the [Issues](https://github.com/amfitech/amfiprot/issues) tab.

