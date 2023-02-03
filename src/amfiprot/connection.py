from abc import ABC, abstractmethod
from typing import List
from .packet import Packet
from .node import Node


class Connection(ABC):
    """Interface for connecting to a root node."""

    @abstractmethod
    def find_nodes(self) -> List[Node]:
        """ Searches for Amfiprot-compatible nodes on the Connection and returns a list of Node objects. """
        pass

    @abstractmethod
    def start(self):
        """ Starts one or more subprocesses that asynchronously sends enqueued packets and receives incoming packets
        (and route them to the correct Node). """
        pass

    @abstractmethod
    def stop(self):
        """ Stops the subprocesses that were created when invoking start(). """
        pass

    @abstractmethod
    def refresh(self):
        """ Inform the connection that e.g. a previously registered node has changed """
        pass

    @abstractmethod
    def enqueue_packet(self, packet: Packet):
        """ Enqueue a packet for transmission. """
        pass

    @abstractmethod
    def max_payload_size(self) -> int:
        """ Returns the maximum size (in bytes) of the payload (not the entire packet) for the connection. """
        pass

