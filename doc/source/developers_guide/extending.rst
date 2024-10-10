******************************************
Extending the protocol for a custom device
******************************************

The :code:`amfiprot` package can be extended to support additional types of :code:`Connection`\ s and :code:`Device`\ s
(with accompanying :code:`Payload`\ s).

Implementing a new Connection
=============================
Adding additional connections is done by creating a subclass of :class:`amfiprot.Connection` that implements all
its abstract methods.

Implementing a new Device
=========================
In order to inherit all the basic Amfiprot functionality, specialized devices should be implemented as a subclass of
:class:`amfiprot.Device`.

If a new :code:`Device` also features new payload types (which is often the case), the device must watch for
:code:`Packet`\ s containing :code:`UndefinedPayload`\ s and then attempt to reinterpret these payloads for any newly
implemented payload types. This should be done by overriding the :meth:`amfiprot.Device.get_packet` function.

Implementing a new Payload
==========================

To create a new payload type, you must create a subclass of the :code:`Payload` interface, implementing all its
abstract methods:

.. autoclass:: amfiprot.payload.Payload
        :members:
        :undoc-members:
        :special-members: __str__, __len__

After creating this subclass, you are now able to *send* packets containing your new payload type:

.. code-block::

    payload = MyNewPayload(some_variable)
    dev.node.send_payload(payload, source_id=252)

As long as the new payload type is a subclass of :code:`Payload` (and thus implements the
:meth:`amfiprot.Payload.to_bytes()` method), it can be converted to an array of bytes for transmission, and thus the
specific payload type does not matter.

When receiving packets, any payload type that is not defined in the core Amfiprot package will be created as an
:code:`UndefinedPayload`. If the packet's payload type matches your newly implemented payload, it is your responsibility
to reinterpret the packet. If you have also implemented a new :code:`Device` then it should be done by overriding
:meth:`amfiprot.Device.get_packet`.

Select a payload type identifier between 0-255 that is not already in use. The built-in Amfiprot payload types are
defined here:

.. autoclass:: amfiprot.payload.PayloadType
        :members:
        :undoc-members:

