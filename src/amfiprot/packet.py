"""
Packet module docstring
"""
import array
import enum
import crcmod
from .payload import Payload, PayloadType, UndefinedPayload
from .common_payload import create_common_payload


class PacketType(enum.IntEnum):
    NO_ACK = 0
    REQUEST_ACK = 1
    ACK = 2
    REPLY = 3


class Packet:
    """ This class can be instantiated from:
        - raw byte data (received from USB, for example) and an optional PayloadFactory. If no factory is given, only
            built-in amfiprot types are used. If the payload_type is not a built-in type, the Packet will contain an
            UndefinedPayload.
        - a payload and additional header data
    """

    MAX_PACKET_LENGTH = 64  # TODO: Not really a limit to a generic packet, is there?

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
        # if byte_data is not None and len(byte_data) < len(self.HeaderIndex) + 2:
        #     raise ValueError("Data does not contain full header")
        #
        # if len(byte_data) > self.MAX_PACKET_LENGTH:
        #     raise ValueError("Data exceeds max packet length of 64 bytes")
        #
        # if len(byte_data) - self.HEADER_LENGTH < byte_data[self.HeaderIndex.PAYLOAD_LENGTH]:
        #     raise ValueError("Data exceeds max packet length of 64 bytes")
        #
        self.data: array.array = byte_data
        #
        # if len(self.data) <= self.HEADER_LENGTH:
        #     return
        self.header = self.data[:len(self.HeaderIndex)]

        self.payload_data = self.data[len(self.HeaderIndex):len(self.HeaderIndex)+self.payload_length]

        # Create payload object that corresponds to payload_type
        self.payload = create_payload_from_type(self.payload_data, self.payload_type)

    @classmethod
    def from_payload(cls, payload, destination_id, source_id=0, packet_type=PacketType.NO_ACK):
        data = array.array('B', [len(payload),
                                 packet_type,
                                 0,
                                 payload.type,
                                 source_id,
                                 destination_id])

        # cls.packet_number = (cls.packet_number + 1) % 255

        # Append header CRC (not including report_id and packet_length)
        crc8 = crcmod.Crc(0x12F, initCrc=0, rev=False)
        crc8.update(data[:])
        data.append(crc8.crcValue)

        # Append payload and CRC
        crc8.crcValue = 0  # Remember to reset crcValue
        data.extend(payload.to_bytes())
        crc8.update(payload.to_bytes())
        data.append(crc8.crcValue)
        # print(f"crc: 0x{crc8.crcValue:02x}")

        packet = Packet(data)
        return packet

    def __len__(self):
        return len(self.data)

    @property
    def packet_type(self):
        return self.data[self.HeaderIndex.PACKET_TYPE]

    @property
    def payload_length(self):
        return self.data[self.HeaderIndex.PAYLOAD_LENGTH]

    @property
    def payload_type(self) -> int:
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

    @packet_type.setter
    def packet_type(self, message_type):
        self.data[self.HeaderIndex.PACKET_TYPE] = message_type

    def __str__(self):
        return f"Dest: {self.destination_id}, Src: {self.source_id}, Payload_type: {self.payload_type}: {self.payload}"

    def to_bytes(self):
        """
        Convert packet to array.array('B') for transmission
        """
        return self.data


amfiprot_payload_mappings = {
        PayloadType.COMMON: create_common_payload
    }


def create_payload_from_type(payload_data: array.array, payload_type: PayloadType):
    if payload_type in amfiprot_payload_mappings:
        return amfiprot_payload_mappings[payload_type](payload_data)
    else:
        return UndefinedPayload(payload_data, payload_type)
