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


class Header:
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
        See :class:`amfiprot.payload.PayloadType`
        """
        SOURCE_TX_ID = 4
        DESTINATION_TX_ID = 5

    @classmethod
    def length(cls):
        return len(cls.HeaderIndex)

    def __init__(self, data):
        self.data = data
        self.payload_length = data[self.HeaderIndex.PAYLOAD_LENGTH]
        self.packet_type = data[self.HeaderIndex.PACKET_TYPE]
        self.packet_number = data[self.HeaderIndex.PACKET_NUMBER]
        self.payload_type = data[self.HeaderIndex.PAYLOAD_TYPE]
        self.source_tx_id = data[self.HeaderIndex.SOURCE_TX_ID]
        self.destination_tx_id = data[self.HeaderIndex.DESTINATION_TX_ID]

    def __len__(self):
        return self.length()

    def __str__(self):
        return f"<Header> src: {self.source_tx_id}, dest: {self.destination_tx_id}, payload_type: {self.payload_type}, packet_number: {self.packet_number}"

    def to_bytes(self):
        return array.array('B', self.data)


class Packet:
    def __init__(self, byte_data: array.array):  # Using array.array('B') since it's faster than bytearray()
        self.data: array.array = byte_data
        self.header = Header(self.data[:Header.length()])

        if self.header.payload_length == 0:
            self.payload = None
        else:
            payload_start_index = Header.length() + 1  # CRC
            payload_end_index = payload_start_index + self.header.payload_length
            payload_data = self.data[payload_start_index:payload_end_index]

            # Create payload object that corresponds to payload_type
            self.payload = create_payload_from_type(payload_data, self.header.payload_type)

    @classmethod
    def from_payload(cls, payload, destination_id=PacketDestination.BROADCAST, source_id=0, packet_type=PacketType.NO_ACK, packet_number: int = 0):
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
        return self.header.packet_type

    @packet_type.setter
    def packet_type(self, message_type):
        self.header.packet_type = message_type

    @property
    def payload_length(self):
        return self.header.payload_length

    @property
    def payload_type(self) -> PayloadType:
        return self.header.payload_type

    @property
    def source_id(self):
        return self.header.source_tx_id

    @property
    def destination_id(self):
        return self.header.destination_tx_id

    @property
    def header_crc(self):
        return self.data[Header.length()]

    @property
    def payload_crc(self):
        if self.header.payload_length == 0:
            return 0

        return self.data[len(self.header) + 1 + self.header.payload_length]

    @destination_id.setter
    def destination_id(self, identifier):
        self.header.destination_tx_id = identifier

    def __str__(self):
        return f"{self.header} {self.payload}"

    def to_bytes(self):
        """
        Convert packet to an array of bytes (array.array('B')) for transmission
        """
        return self.data

    def crc_is_good(self) -> bool:
        new_header_crc = calculate_crc(self.header.to_bytes())
        header_crc_is_good = (self.header_crc == new_header_crc)

        if not header_crc_is_good:
            return False

        if self.header.payload_length == 0:
            return True
        else:
            # print(f"Checking crc for {self.payload}")
            new_payload_crc = calculate_crc(self.payload.to_bytes())
            return self.payload_crc == new_payload_crc


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
