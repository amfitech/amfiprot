**********
Connection
**********
All connections (i.e. USB, UART, BLE, etc.) must implement the :class:`amfiprot.Connection` interface. All data specific
to the concrete implementation must be given in its constructor.

Currently, USB (HID) is the only supported connection.

.. autoclass:: amfiprot.Connection
    :members:

USB
===
.. autoclass:: amfiprot.USBConnection
