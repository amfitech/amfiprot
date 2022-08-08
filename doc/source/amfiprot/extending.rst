******************************************
Extending the protocol for a custom device
******************************************

The :code:`amfiprot` package can be extended to support additional types of :code:`Connections` and :code:`Device`\ s
(with accompanying :code:`Payload`\ s).

Implementing a new Connection
=============================

Adding additional connections is done by creating a subclass of :code:`Connection` that implements all abstract
methods:

.. autoclass:: amfiprot.connection.Connection
        :members:
        :undoc-members:

Implementing a new Device
=========================
When implementing a new Device class, it is recommended to inherit all the basic Amfiprot functionality (such as
requesting device ID, reading and setting configuration parameters and updating firmware) by subclassing the
:code:`amfiprot.Device` class and then adding additional functionality on top of that. If the basic Amfiprot functionality
is not needed, subclassing the :code:`amfiprot.Device` is not strictly necessary but it may still be used for inspiration.

If a new :code:`Device` also features new payload types (which it most likely does), the device must watch for Packets
containing UndefinedPayloads and then attempt to reinterpret these payloads for the new payload types.

Implementing a new Payload
==========================

A new payload type is created as a class that implements the :code:`Payload` interface:

.. autoclass:: amfiprot.payload.Payload
        :members:
        :undoc-members:
        :special-members: __str__, __len__

Now you are able to *send* packets containing your new payload type. As long as the new payload type is a subclass of
:code:`Payload`, it can be converted to an array of bytes for transmission, and thus the specific payload type does not
matter.

However, when receiving packets with a payload type that is not defined in the Amfiprot built-in payload types, the
payload will be interpreted as an UndefinedPayload. This payload can then be reinterpreted as the newly created payload type
(given that the payload type in the packet header matches). This can be done manually by the user or (more elegantly) by
implementing a new Device class that has knowledge of this payload type.

Select a payload type identifier between 0-255 that is not already in use. The built-in Amfiprot payload types are
defined here:

.. autoclass:: amfiprot.payload.PayloadType
        :members:
        :undoc-members:

