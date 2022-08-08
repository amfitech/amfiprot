***************
Getting started
***************

What is Amfiprot?
=================
Amfiprot is a communication protocol used to transmit data between embedded devices and host computers. The protocol is
developed at `Amfitech <https://www.amfitech.dk/>`_, originally intended for the `AmfiTrack <https://www.amfitrack.com/>`_
system, but is now also used in several other devices.


Installation
============
Before installing the package, please make sure that `libusb <https://libusb.info/>`_ (v???) is installed on your machine.

The package can be installed either for normal usage or for development. Note that Python 3.6 or higher is required.

For users
---------
Simply install the package using pip (upgrading if necessary):

.. code-block::

    pip install -U amfiprot

For developers
--------------
After cloning the repository, create a virtual environment and activate it:

.. code-block::

    python -m venv .\venv
    .\venv\Scripts\activate.bat

In the virtual environment, install packages from `requirements.txt` and then install the `amfiprot` package itself
with the 'editable' option:

.. code-block::

    pip install -r requirements.txt
    pip install -e .

Now you can edit the source code and try out the changes immediately in your virtual environment without needing to
reinstall the package.

Usage example
=============

To connect to an Amfiprot-compatible device, the general process is:

- Create a connection
- Search for nodes on that connection
- Create device instances using the nodes
- Start the connection

Now the created devices are ready to use. Below is a minimal example creating a USB connection to a generic Amfiprot
device and reading its configuration:

.. code-block::

    import amfiprot

    if __name__ == '__main__':
        conn = amfiprot.UsbConnection(0xc17, 0xd12)
        nodes = conn.find_nodes()
        dev = amfiprot.Device(nodes[0])  # Assuming find_nodes() returns only our device

        conn.start()  # Sending/receiving packets is now handled in separate subprocesses

        # Reading and printing the configuration from the device
        cfg = dev.read_config()

        for category in cfg:
            print(category['category'])
            for param in category['parameters']:
                print(param)

        conn.stop()