"""
Packet module docstring
"""
import array
import enum
import crcmod
from .payload import Payload, PayloadType, UndefinedPayload
from .common_payload import create_common_payload
from .response_payload import *


class PacketType(enum.IntEnum):
    NO_ACK = 0
    REQUEST_ACK = 1
    ACK = 2
    REPLY = 3


class PacketDestination(enum.IntEnum):
    PC = 0
    BROADCAST = 255


class Packet:
    class HeaderIndex(enum.IntEnum):
        PAYLOAD_LENGTH = 0
        """
        Length of payload including CRC, in bytes.
        """
        PACKET_TYPE = 1
        """
        | Bits [7:6]: 0 = NoAck, 1 = Request Ack, 2 = Ack, 3 = Reply.
        | Bits [5:0]: Time to live for packet routing.
        """
        PACKET_NUMBER = 2
        """
        Sequentially increasing packet number, used when sending back ack.
        """
        PAYLOAD_TYPE = 3
        """
        See :class:`amfitrack.amfiprot.payload.PayloadType`
        """
        SOURCE_TX_ID = 4
        DESTINATION_TX_ID = 5
        HEADER_CRC = 6
        """
        CRC of the data header (not including the two byte USB header)
        """

    def __init__(self, byte_data: array.array):  # Using array.array('B') since it's faster than bytearray()
        """ Init docstring """
        self.data: array.array = byte_data
        self.header = self.data[:len(self.HeaderIndex)]

        if self.header[self.HeaderIndex.PAYLOAD_LENGTH] == 0:
            self.payload = None
        else:
            self.payload_data = self.data[len(self.HeaderIndex):len(self.HeaderIndex)+self.payload_length]

            # Create payload object that corresponds to payload_type
            self.payload = create_payload_from_type(self.payload_data, self.payload_type)

    @classmethod
    def from_payload(cls, payload, destination_id, source_id=0, packet_type=PacketType.NO_ACK, packet_number: int = 0):
        data = array.array('B', [len(payload),
                                 packet_type,
                                 packet_number,
                                 payload.type,
                                 source_id,
                                 destination_id])

        # Append header CRC (not including report_id and packet_length)
        header_crc = calculate_crc(data[:])
        data.append(header_crc)

        # Append payload and CRC
        payload_data = payload.to_bytes()
        payload_crc = calculate_crc(payload_data)
        data.extend(payload_data)
        data.append(payload_crc)

        return Packet(data)

    def __len__(self):
        return len(self.data)

    @property
    def packet_type(self):
        return self.data[self.HeaderIndex.PACKET_TYPE]

    @packet_type.setter
    def packet_type(self, message_type):
        self.data[self.HeaderIndex.PACKET_TYPE] = message_type

    @property
    def payload_length(self):
        return self.data[self.HeaderIndex.PAYLOAD_LENGTH]

    @property
    def payload_type(self) -> PayloadType:
        return self.data[self.HeaderIndex.PAYLOAD_TYPE]

    @property
    def source_id(self):
        return self.data[self.HeaderIndex.SOURCE_TX_ID]

    @property
    def destination_id(self):
        return self.data[self.HeaderIndex.DESTINATION_TX_ID]

    @destination_id.setter
    def destination_id(self, identifier):
        self.data[self.HeaderIndex.DESTINATION_TX_ID] = identifier

    def __str__(self):
        return f"Dest: {self.destination_id}, Src: {self.source_id}, Payload_type: {self.payload_type}: {self.payload}"

    def to_bytes(self):
        """
        Convert packet to array.array('B') for transmission
        """
        return self.data

    def header_crc_good(self) -> bool:
        header_crc = self.header[self.HeaderIndex.HEADER_CRC]
        new_crc = calculate_crc(self.header[:self.HeaderIndex.HEADER_CRC])
        return new_crc == header_crc

    def payload_crc_good(self) -> bool:
        if self.payload is None or self.header[self.HeaderIndex.PAYLOAD_LENGTH] == 0:
            return True

        payload_crc_index = len(self.HeaderIndex) + self.header[self.HeaderIndex.PAYLOAD_LENGTH]
        payload_crc = self.data[payload_crc_index]
        new_crc = calculate_crc(self.payload_data)
        return new_crc == payload_crc


amfiprot_payload_mappings = {
        PayloadType.COMMON: create_common_payload,  # type: ignore
        PayloadType.SUCCESS: SuccessPayload,
        PayloadType.NOT_IMPLEMENTED: NotImplementedPayload,
        PayloadType.FAILURE: FailurePayload,
        PayloadType.INVALID_REQUEST: InvalidRequestPayload
    }


def create_payload_from_type(payload_data: array.array, payload_type: PayloadType):
    if payload_type in amfiprot_payload_mappings:
        return amfiprot_payload_mappings[payload_type](payload_data)  # type: ignore
    else:
        return UndefinedPayload(payload_data, payload_type)


def calculate_crc(data):
    crc8 = crcmod.Crc(0x12F, initCrc=0, rev=False)
    crc8.update(data[:])
    return crc8.crcValue
