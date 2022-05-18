Packet
======
An AmfiProt packet has a fixed length of 64 bytes and contains the following:

- 2 byte USB header
    - byte 0: Report ID
    - byte 1: Packet length
- 7 byte data header
    - byte 2: Payload length
    - byte 3: Message type
    - byte 4: Packet number
    - byte 5: Payload type
    - byte 6: Source TX ID
    - byte 7: Destination TX ID
    - byte 8: Header CRC
- 55 bytes data payload (including data CRC byte), zero-padded if necessary

Header
------
The header indices are defined in the Packet.HeaderIndex enum:

.. autoclass:: amfitrack.amfiprot.packet.Packet.HeaderIndex
    :members:
    :undoc-members:

Payload
-------
The interpretation of the payload data depends on the payload type and the payload ID,
which is the first byte of the payload. The different payload types are defined here:

.. autoclass:: amfitrack.amfiprot.payload.PayloadType
    :members:
    :undoc-members:
