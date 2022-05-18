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
    def __len__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @property
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def to_bytes(self):
        pass
    
    @abstractmethod
    def to_dict(self):
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

    def type(self):
        return self.payload_type

    def to_bytes(self):
        return array.array('B', self.data)

    def to_dict(self):
        data_dict = {
            'data': self.data
        }
        return data_dict
