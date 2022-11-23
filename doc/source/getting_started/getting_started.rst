What is Amfiprot?
=================
Amfiprot is a communication protocol for embedded devices used and developed by `Amfitech <https://www.amfitech.dk/>`_.
The protocol can be extended with plugins for specific devices implementing the Amfiprot protocol (e.g. the
`AmfiTrack <https://www.amfitrack.com/>`_).

Installation
============

Prerequisites
-------------

- Python 3.6 or higher.
- `libusb <https://libusb.info/>`_ in order to communicate with USB devices through :code:`pyusb`


Windows
-------

Get a libusb Windows binary from https://libusb.info/.

Install (or update) :code:`amfiprot` with :code:`pip`:

.. code-block:: shell

    pip install -U amfiprot

Linux (Ubuntu)
--------------

Install :code:`libusb`:

.. code-block:: shell

    sudo apt install libusb-1.0-0-dev


Make sure that your user has access to USB devices. For example, give the :code:`plugdev` group access to USB devices by creating a udev rule:

.. code-block:: shell

    echo 'SUBSYSTEM=="usb", MODE="660", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/50-pyusb.rules
    sudo udevadm control --reload
    sudo udevadm trigger

Check whether you are a member of :code:`plugdev` with:

.. code-block:: shell

    groups <username>

If not, add yourself to the group with:

.. code-block:: shell

    sudo usermod -aG plugdev <username>

Finally, install (or update) :code:`amfiprot` with :code:`pip`:

.. code-block:: shell

    pip install -U amfiprot


Basic usage
=============

The basic workflow when using the library is:

1. Create a :code:`Connection` to a device connected directly to the host machine (we call this the "root node").
2. Search for :code:`Node`\ s on the :code:`Connection` (i.e. nodes connected through the root node)
3. Create a :code:`Device` using one of the discovered :code:`Node`\ s.
4. Start the :code:`Connection`.
5. Communicate with the :code:`Device`.

Example:

.. code-block:: python

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

.. The following sections provide a more in-depth explanation.