from enum import IntEnum
from abc import ABCMeta, abstractmethod
import array


class PayloadType(IntEnum):
    COMMON = 0x00
    SUCCESS = 0xF0
    NOT_IMPLEMENTED = 0xFD
    FAILURE = 0xFE
    INVALID_REQUEST = 0xFF


class Payload(metaclass=ABCMeta):
    @abstractmethod
    def __len__(self) -> int:
        """ Length of the payload in bytes (without the CRC byte) """
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    @abstractmethod
    def type(self) -> PayloadType:
        """ Returns the payload type """
        pass

    @abstractmethod
    def to_bytes(self) -> array.array:
        """ Returns the payload as an array of raw bytes (without CRC) """
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """ Returns the payload as a dict """
        pass


class UndefinedPayload(Payload):
    """ This class is used if the PayloadFactory is given data with a payload_type that is not mapped to a
    Payload subclass. """
    def __init__(self, data: array.array, payload_type):
        if not type(data) == array.array:
            # Wrong data type
            raise ValueError("Argument 'data' must be of type array.array('B')")
        else:
            self.data = data
            self.payload_type = payload_type

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

    @property
    def type(self):
        return self.payload_type

    def to_bytes(self):
        return array.array('B', self.data)

    def to_dict(self):
        data_dict = {
            'data': self.data
        }
        return data_dict
