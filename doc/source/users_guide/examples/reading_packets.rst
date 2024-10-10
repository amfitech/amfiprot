***************************
Reading and writing packets
***************************
All of these examples assume that you have already established a connection (:code:`conn`), created a device
(:code:`dev`) and started the connection (see the :doc:`usb_connection` section).

Reading all packets from a device
---------------------------------
.. code-block::

    if dev.packet_available():
        packet = dev.get_packet():
        print(packet)

Reading packets with specific payload type
------------------------------------------
.. code-block::

    if dev.packet_available():
        packet = dev.get_packet():

        if type(packet.payload) == amfiprot.common_payload.ReplyDeviceIdPayload:
            print(packet)

Reading all packets on a USB connection
---------------------------------------
.. code-block::

    if not conn.global_receive_queue.empty():
        packet = global_receive_queue.get()
        print(packet)

Write a specific payload to a device
------------------------------------
.. code-block::

    payload = amfiprot.common_payload.RequestDeviceIdPayload()
    dev.node.send_payload(payload)

Broadcast a packet on a connection
-----------------------------------
.. code-block::

    payload = amfiprot.common_payload.RequestDeviceIdPayload()
    broadcast_packet = amfiprot.Packet.from_payload(payload)
    conn.enqueue_packet(broadcast_packet)

