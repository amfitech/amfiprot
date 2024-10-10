Connecting to a USB device
==========================

Discover USB devices
--------------------
Amfiprot devices connected directly to the host machine are referred to as :emphasis:`root nodes`. Root nodes connected
via USB can be discovered using the :meth:`amfiprot.USBConnection.discover` method:

.. code-block::

    import amfiprot

    if __name__ == '__main__':
        usb_devices = amfiprot.USBConnection.discover()
        usb_device = None

        for dev in usb_devices:
            if "amfitech" in usb_device['manufacturer'].lower():
                usb_device = dev
                break

        if dev is None:
            raise ConnectionError("USB device not found.")

Root node connection
--------------------
After finding a USB device to use as a root node, create a connection to it by passing the vendor ID, product ID and
serial number of the device into the :class:`amfiprot.USBConnection` constructor:

.. code-block::

    conn = amfiprot.USBConnection(usb_device['vid'],
                                  usb_device['pid'],
                                  serial_number=usb_device['serial_number'])


Searching for nodes
-------------------
With the connection created, we can now search for nodes that are connected indirectly to the host machine through the
root node (e.g. other devices connected to the root node via RF or serial connection):

.. code-block::

    nodes = conn.find_nodes()

This returns a list of :code:`Node`\ s that we can use to create a :code:`Device`.

Creating a device
-----------------
To create a :code:`Device` pick a :code:`Node` from the list and inject it into the :code:`Device` constructor.

.. code-block::

    dev = None

    for node in nodes:
        if "amfitrack" in node.name.lower():
            dev = amfiprot.Device(node)
            break

    if dev is None:
        raise ConnectionError("No AmfiTrack nodes found.")


If you want to communicate with several nodes, simply create a :code:`Device` instance for each of them.

.. admonition:: Tip

    When creating an :class:`amfiprot.Device` you only get the most basic Amfiprot functionality.

    If the device is an AmfiTrack device, create an :code:`amfitrack.Device` from the
    `amfiprot-amfitrack <https://pypi.org/project/amfiprot-amfitrack/>`_ package instead. This will give you access to
    AmfiTrack specific functionality such as making the device to perform startup calibration, enable/disable phase
    modulation and to interpret AmfiTrack specific payloads.

Starting the connection and interacting with the devices
--------------------------------------------------------
After creating your :code:`Device` instances you are almost ready to start interacting with them. However, to start
sending and receiving packets through the root node, you must first start the connection:

.. code-block::

    conn.start()

This creates a subprocess that processes incoming and outgoing packets and makes sure that they get routed to the
correct node/device.