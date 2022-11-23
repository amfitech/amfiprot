********
Overview
********

In order to use the library, it is important to first understand which components it contains and how they relate to
each other.

To communicate with a device, the steps necessary are:

- Create a :code:`Connection` (e.g. a `USBConnection`) to a device connected directly to the host. This is called the "root node"
- Search for :code:`Node`\ s on the :code:`Connection`, i.e. devices connected indirectly to the host through the root node
- Create a :code:`Device` (e.g a generic :code:`amfiprot.Device`) using one of the discovered :code:`Node`\ s
- Start the :code:`Connection`
- Interact with the :code:`Device` by calling high-level methods or by manually sending and receiving :code:`Packet`\ s through its :code:`Node`.


**********
Connection
**********
The connection to a root node is handled using the :code:`Connection` interface:

.. autoclass:: amfiprot.Connection
    :members:

This interface is implemented by concrete classes for different connection types, such as USB, Bluetooth or UART.
Currently, only USB connection is supported

USB
===
USB (HID) connection is established using the :code:`UsbConnection` class. The class implements the :code:`Connection`
interface and USB specific parameters are given in the constructor:

.. autoclass:: amfiprot.UsbConnection

****
Node
****

.. autoclass:: amfiprot.Node
    :members:
    :undoc-members:


******
Device
******

.. autoclass:: amfiprot.Device
    :members:
    :undoc-members:

******
Packet
******

.. autoclass:: amfiprot.Packet
    :members:
    :undoc-members:

.. autoclass:: amfiprot.packet.Header
    :members:
    :undoc-members:

.. autoclass:: amfiprot.Payload
    :members:
    :undoc-members:



Connecting to a USB device
==========================

After attaching a device to your host machine, you can scan for connected devices (e.g. connected via USB) with:

.. code-block::

    phys_devs = amfiprot.UsbConnection.scan_physical_devices()

    for dev in phys_devs:
        print(dev)

A connection can then be created using a specific physical device:

.. code-block::

    conn = amfiprot.UsbConnection(dev['vid'], dev['pid'], dev['serial_number'])


Using :code:`serial_number` is optional. If none is given, the first device matching the given vendor and product ID
is used.

Finding nodes
=============

After creating a connection, we can search for nodes that are connected to the root node (e.g. via RF or UART):

.. code-block::

    nodes = conn.find_nodes()

:code:`find_nodes()` returns a list of :code:`Node` instances. A :code:`Node` provides a low-level interface to the
physical device and can be used to retrieve the :code:`uuid`, :code:`tx_id` and :code:`name` of the device, and
send/receive raw packets. It is not recommended to use the :code:`Node` directly, but rather attach it to a `Device`
instance.

Creating a device
=================

A :code:`Device` is an abstraction layer on top of a :code:`Node` and is created by injecting a :code:`Node` in the constructor:

.. code-block::

    dev = amfiprot.Device(node)

The :code:`Device` provides a higher-level interface allowing the user to easily:

- Update the firmware
- Reboot the device
- Read/write configurations
- Read decoded packets

We are still able to access the :code:`Node` through the :code:`Device` if necessary:

.. code-block::

    tx_id = dev.node.tx_id

## Starting the connection and interacting with the device

Before interacting with the :code:`Device`, the :code:`Connection` must be started:

.. code-block::

    conn.start()

This creates a child process that asynchronously sends and receives packets on the specified interface. We can now
interact with the :code:`Device` in the main process without worrying about blocking:

.. code-block::

    device_name = dev.name()
    print(f"Reading packets from {device_name}...")

    while True:
        if dev.packet_available():
            print(dev.get_packet())

We can access the device configuration through a :code:`Configurator` instance which is automatically created as a
member (:code:`dev.config`) of the :code:`Device`:

.. code-block::

    # Read the entire configuration as a JSON-like object (a list of dicts)
    cfg = dev.config.read_all()

    # Print all parameters
    for category in cfg:
        print(f"CATEGORY: {category['name']}")
        for parameter in category['parameters']:
            print(parameter)

The configuration can be easily saved to and loaded from a :code:`.json` file:

.. code-block::

    import json

    # Write configuration to file
    with open("config.json", "w") as outfile:
        json.dump(cfg, outfile, indent=4)

    # Read configuration from file and send to device
    with open("config.json", "r") as infile:
        new_cfg = json.load(infile)
        dev.config.write_all(new_cfg)
