from __future__ import annotations
import multiprocessing as mp
import time
import typing
from .packet import Packet, PacketType
from .payload import Payload

if typing.TYPE_CHECKING:
    from .connection import Connection


class Node:
    """ A `Node` represents a single endpoint on a `Connection`. One `Connection` can
    have multiple nodes, e.g. if the PC connects via USB to a device which in turn is connected
    to additional devices via RF """
    def __init__(self, tx_id, uuid, connection: Connection):
        self.connection = connection
        self.tx_id = tx_id
        self.uuid = uuid
        self.receive_queue: mp.Queue = mp.Queue(maxsize=128)

    def available_packets(self) -> int:
        return self.receive_queue.qsize()

    def get_packet(self, blocking=False, timeout_ms=1000) -> Packet:
        if self.receive_queue.empty() and not blocking:
            return None

        # start_time = time.time_ns() / 1000
        # while self.receive_queue.empty() and (time.time_ns()/1000) - start_time < timeout_ms:
        #     self.connection.process()
        #
        # if self.receive_queue.empty():
        #     return None

        return self.receive_queue.get()

    def send_packet(self, packet: Packet):
        self.connection.enqueue_packet(packet)

    def send_payload(self,
                     payload: Payload,
                     source_id: int = 0,
                     packet_type: PacketType = PacketType.NO_ACK):
        packet = Packet.from_payload(payload,
                                     destination_id=self.tx_id,
                                     source_id=source_id,
                                     packet_type=packet_type)
        self.send_packet(packet)

    def flush_receive_queue(self):
        while not self.receive_queue.empty():
            self.receive_queue.get_nowait()

    def __str__(self):
        return f"<Node> tx_id: {self.tx_id}, uuid: {self.uuid:024x}"
