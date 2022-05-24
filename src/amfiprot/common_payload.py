from .payload import Payload, PayloadType
import array
import enum
import struct
from abc import abstractmethod


class CommonPayloadId(enum.IntEnum):  # When PayloadType is Common, these PayloadID's are available
    REQUEST_DEVICE_ID = 0x00
    REPLY_DEVICE_ID = 0x01
    SET_TX_ID = 0x02
    REQUEST_FIRMWARE_VERSION = 0x03
    REPLY_FIRMWARE_VERSION = 0x04
    FIRMWARE_START = 0x05
    FIRMWARE_DATA = 0x06
    FIRMWARE_END = 0x07
    REQUEST_DEVICE_NAME = 0x08
    REPLY_DEVICE_NAME = 0x09
    REQUEST_CONFIGURATION_VALUE = 0x0A
    REPLY_CONFIGURATION_VALUE = 0x0B
    SET_CONFIGURATION_VALUE = 0x0C
    REQUEST_CONFIGURATION_NAME = 0x0D
    REPLY_CONFIGURATION_NAME = 0x0E
    LOAD_DEFAULT = 0x0F
    SAVE_AS_DEFAULT = 0x10
    REQUEST_CONFIGURATION_NAME_AND_UID = 0x11
    REPLY_CONFIGURATION_NAME_AND_UID = 0x12
    REQUEST_CONFIGURATION_VALUE_UID = 0x13
    REPLY_CONFIGURATION_VALUE_UID = 0x14
    SET_CONFIGURATION_VALUE_UID = 0x15
    REQUEST_CONFIGURATION_CATEGORY = 0x16
    REPLY_CONFIGURATION_CATEGORY = 0x17
    REQUEST_CONFIGURATION_VALUE_COUNT = 0x18
    REPLY_CONFIGURATION_VALUE_COUNT = 0x19
    REQUEST_CATEGORY_COUNT = 0x1A
    REPLY_CATEGORY_COUNT = 0x1B
    REQUEST_FIRMWARE_VERSION_PER_ID = 0x1C
    REPLY_FIRMWARE_VERSION_PER_ID = 0x1D
    DEBUG_OUTPUT = 0x20
    REBOOT = 0x21


class ConfigValueType(enum.IntEnum):
    BOOL = 0
    CHAR = 1
    INT8 = 2
    UINT8 = 3
    INT16 = 4
    UINT16 = 6
    INT32 = 8
    UINT32 = 10
    INT64 = 12
    UINT64 = 14
    FLOAT = 16
    DOUBLE = 18
    PROCEDURE_CALL = 100


class CommonPayload(Payload):
    @classmethod
    @abstractmethod
    def from_bytes(cls, data):
        """ Used as a common interface to instantiate a payload subclass from incoming raw byte data via a factory """
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @property
    def type(self):
        return 0

    @abstractmethod
    def to_bytes(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass


class RequestDeviceIdPayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.REQUEST_DEVICE_ID])

    @classmethod
    def from_bytes(cls, data):
        return RequestDeviceIdPayload()

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "Request device ID"

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': self.data[0]
        }


class ReplyDeviceIdPayload(CommonPayload):
    def __init__(self, tx_id: int, uuid: int):
        self.tx_id = tx_id
        self.uuid = uuid
        self.data = array.array('B', [CommonPayloadId.REPLY_DEVICE_ID, self.tx_id])
        self.data.extend(self.uuid.to_bytes(12, byteorder='little'))

    @classmethod
    def from_bytes(cls, data):
        tx_id = data[1]
        uuid = int.from_bytes(data[2:14], byteorder='little')
        return ReplyDeviceIdPayload(tx_id, uuid)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return f"TxID {self.tx_id}; UUID; {self.uuid:024x}"

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'tx_id': self.tx_id,
            'uuid': self.uuid
        }


class SetTxIdPayload(CommonPayload):
    def __init__(self, tx_id):
        self.tx_id = tx_id
        self.data = array.array('B', [CommonPayloadId.SET_TX_ID, self.tx_id])

    @classmethod
    def from_bytes(cls, data):
        tx_id = data[1]
        return SetTxIdPayload(tx_id)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        pass

    def to_bytes(self):
        pass

    def to_dict(self):
        pass


class RequestFirmwareVersionPayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.REQUEST_FIRMWARE_VERSION])

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


class ReplyFirmwareVersionPayload(CommonPayload):
    def __init__(self, major: int, minor: int, patch: int, build: int):
        self.fw_version = {'major': major, 'minor': minor, 'patch': patch, 'build': build}

    @classmethod
    def from_bytes(cls, data):
        major = int.from_bytes(data[1:5], byteorder='little')
        minor = int.from_bytes(data[5:9], byteorder='little')
        patch = int.from_bytes(data[9:13], byteorder='little')
        build = int.from_bytes(data[13:17], byteorder='little')
        return ReplyFirmwareVersionPayload(major, minor, patch, build)

    def __str__(self):
        return f"Firmware version: {self.fw_version['major']}.{self.fw_version['minor']}.{self.fw_version['patch']}.{self.fw_version['build']}"

    def __len__(self):
        pass

    def to_bytes(self):
        pass

    def to_dict(self):
        pass



class RequestDeviceNamePayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.REQUEST_DEVICE_NAME])

    @classmethod
    def from_bytes(cls, data):
        return RequestDeviceNamePayload()

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return f"Request device ID"

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': self.data[0]
        }


class ReplyDeviceNamePayload(CommonPayload):
    def __init__(self, name: str):
        self.name = name

    @classmethod
    def from_bytes(cls, data):
        name = byte_array_to_string(data[1:])
        return ReplyDeviceNamePayload(name)

    def __len__(self):
        return len(self.name) + 2

    def __str__(self):
        return f"Reply device name: {self.name}"

    def to_bytes(self):
        arr = array.array('B', [CommonPayloadId.REPLY_DEVICE_NAME])
        arr.extend(self.name.encode('ascii'))
        arr.append(0)
        return arr

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_DEVICE_NAME,
            'name': self.name
        }


class RebootPayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.REBOOT])

    @classmethod
    def from_bytes(cls, data):
        return RebootPayload()

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "Reboot"

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': self.data[0]
        }


class RequestCategoryCountPayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.REQUEST_CATEGORY_COUNT])

    @classmethod
    def from_bytes(cls, data):
        return RequestCategoryCountPayload()

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "Request category count"

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': self.data[0]
        }


class ReplyCategoryCountPayload(CommonPayload):
    def __init__(self, category_count):
        self.category_count = category_count
        self.data = array.array('B', [CommonPayloadId.REPLY_CATEGORY_COUNT])
        self.data.extend(self.category_count.to_bytes(2, byteorder='little'))

    @classmethod
    def from_bytes(cls, data):
        category_count = int.from_bytes(data[1:2], byteorder='little', signed=False)
        return ReplyCategoryCountPayload(category_count)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return f"Reply category count: {self.category_count}"

    def to_bytes(self):
        arr = array.array('B', [CommonPayloadId.REPLY_CATEGORY_COUNT])
        arr.extend(int.to_bytes(self.category_count, length=1, byteorder='little')) # TODO: Just use directly?
        return arr

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_CATEGORY_COUNT,
            'category_count': self.category_count
        }


class RequestConfigurationCategoryPayload(CommonPayload):
    def __init__(self, category_id):
        self.category_id = category_id
        self.data = array.array('B', [CommonPayloadId.REQUEST_CONFIGURATION_CATEGORY, category_id])

    @classmethod
    def from_bytes(cls, data):
        category_id = data[1]
        return RequestConfigurationCategoryPayload(category_id)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return f"Request category id: {self.category_id}"

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REQUEST_CONFIGURATION_CATEGORY,
            'category_id': self.category_id
        }


class ReplyConfigurationCategory(CommonPayload):
    def __init__(self, category_id: int, category_name: str):
        self.category_id = category_id
        self.category_name = category_name

    @classmethod
    def from_bytes(cls, data):
        category_id = data[1]
        category_name = byte_array_to_string(data[2:])
        return ReplyConfigurationCategory(category_id, category_name)

    def __str__(self):
        return f"<Reply configuration category> id: {self.category_id}, name: {self.category_name}"

    def __len__(self):
        pass

    def to_bytes(self):
        pass

    def to_dict(self):
        pass


class RequestConfigurationNameUidPayload(CommonPayload):
    def __init__(self, config_category: int, config_index: int):
        self.data = array.array('B', [CommonPayloadId.REQUEST_CONFIGURATION_NAME_AND_UID])
        self.data.extend(int.to_bytes(config_category, length=1, byteorder='little'))
        self.data.extend(int.to_bytes(config_index, length=2, byteorder='little'))

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


class ReplyConfigurationNameUidPayload(CommonPayload):
    def __init__(self, configuration_name: str, configuration_uid: int, config_index: int, category_index: int):
        self.configuration_uid = configuration_uid
        self.configuration_name = configuration_name
        self.config_index = config_index
        self.category_index = category_index

    @classmethod
    def from_bytes(cls, data):
        # TODO: What is at data[1:2]???
        config_index = int.from_bytes(data[1:3], byteorder='little')
        category_index = int.from_bytes(data[3:4], byteorder='little')
        uid = int.from_bytes(data[4:8], byteorder='little')
        name = byte_array_to_string(data[8:])
        return ReplyConfigurationNameUidPayload(name, uid, config_index, category_index)

    def __str__(self):
        return f"<Configuration> {self.category_index}.{self.config_index}: {self.configuration_name} ({self.configuration_uid})"

    def __len__(self):
        pass

    def to_bytes(self):
        pass

    def to_dict(self):
        pass


class RequestConfigurationValueCountPayload(CommonPayload):
    def __init__(self, config_category: int):
        self.data = array.array('B', [CommonPayloadId.REQUEST_CONFIGURATION_VALUE_COUNT])
        self.data.extend(int.to_bytes(config_category, length=1, byteorder='little'))

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


class ReplyConfigurationValueCountPayload(CommonPayload):
    def __init__(self, category_index: int, config_value_count: int):
        self.category_index = category_index
        self.config_value_count = config_value_count

    @classmethod
    def from_bytes(cls, data):
        category_index = int.from_bytes(data[1:2], byteorder='little')
        config_value_count = int.from_bytes(data[2:4], byteorder='little')
        return ReplyConfigurationValueCountPayload(category_index, config_value_count)

    def __str__(self):
        return f"<Config value count> Category index: {self.category_index}, config value count: {self.config_value_count}"

    def __len__(self):
        pass

    def to_bytes(self):
        pass

    def to_dict(self):
        pass


class RequestConfigurationValueUidPayload(CommonPayload):
    def __init__(self, config_uid: int):
        self.data = array.array('B', [CommonPayloadId.REQUEST_CONFIGURATION_VALUE_UID])
        self.data.extend(int.to_bytes(config_uid, length=4, byteorder='little'))

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


class ReplyConfigurationValueUidPayload(CommonPayload):
    def __init__(self, uid, config_value: int, data_type: ConfigValueType):
        self.config_value = config_value
        self.data_type = data_type
        self.uid = uid

    @classmethod
    def from_bytes(cls, data):
        uid = int.from_bytes(data[1:5], byteorder='little')
        value_type = int.from_bytes(data[5:6], byteorder='little')
        value = decode_config_value(value_type, data[6:])
        return ReplyConfigurationValueUidPayload(uid, value, value_type)

    def __str__(self):
        return f"<Config value> {self.config_value}"

    def __len__(self):
        pass

    def to_bytes(self):
        pass

    def to_dict(self):
        pass


class LoadDefaultConfigurationPayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.LOAD_DEFAULT])

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass

class SaveAsDefaultConfigurationPayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', CommonPayloadId.SAVE_AS_DEFAULT)

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


class FirmwareStartPayload(CommonPayload):
    def  __init__(self, processor_id: int = 0):
        self.data = array.array('B', [CommonPayloadId.FIRMWARE_START, processor_id])

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


class FirmwareDataPayload(CommonPayload):
    def __init__(self, firmware_data: tuple, processor_id: int = 0):
        self.data = array.array('B', [CommonPayloadId.FIRMWARE_DATA, processor_id])
        firmware_bytes = array.array('B', firmware_data)
        self.data.extend(firmware_bytes)

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


class FirmwareEndPayload(CommonPayload):
    def __init__(self, processor_id: int = 0):
        self.data = array.array('B', [CommonPayloadId.FIRMWARE_END, processor_id])

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


class SetConfigurationValueUidPayload(CommonPayload):
    def __init__(self, uid, value, data_type):
        self.data = array.array('B', [CommonPayloadId.SET_CONFIGURATION_VALUE_UID])
        self.data.extend(int.to_bytes(uid, length=4, byteorder='little'))
        self.data.extend(int.to_bytes(data_type, length=1, byteorder='little'))
        self.data.extend(encode_config_value(value, data_type))

    @classmethod
    def from_bytes(cls, data):
        pass

    def __str__(self):
        pass

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


def byte_array_to_string(byte_array: array.array):
    return bytes(byte_array).decode('ascii').rstrip('\x00')


def decode_config_value(data_type: ConfigValueType, byte_data: array.array):
    if data_type == ConfigValueType.BOOL:
        return bool(int.from_bytes(byte_data, byteorder='little'))
    elif data_type == ConfigValueType.CHAR:
        return byte_data.decode('ascii')
    elif data_type in [ConfigValueType.INT8, ConfigValueType.INT16, ConfigValueType.INT32, ConfigValueType.INT64]:
        return int.from_bytes(byte_data, byteorder='little', signed=True)
    elif data_type in [ConfigValueType.UINT8, ConfigValueType.UINT16, ConfigValueType.UINT32, ConfigValueType.UINT64]:
        return int.from_bytes(byte_data, byteorder='little', signed=False)
    elif data_type == ConfigValueType.FLOAT:
        return struct.unpack('f', byte_data)[0]
    elif data_type == ConfigValueType.DOUBLE:
        return struct.unpack('d', byte_data)[0]
    elif data_type == ConfigValueType.PROCEDURE_CALL:
        return bool(int.from_bytes(byte_data, byteorder='little'))
    else:
        return None

def encode_config_value(value, data_type: ConfigValueType):
    if data_type == ConfigValueType.BOOL:
        return struct.pack("?", value)
    elif data_type == ConfigValueType.CHAR:
        return struct.pack("c", value)
    elif data_type == ConfigValueType.INT8:
        return struct.pack("b", value)
    elif data_type == ConfigValueType.UINT8:
        return struct.pack("B", value)
    elif data_type == ConfigValueType.INT16:
        return struct.pack("<h", value)
    elif data_type == ConfigValueType.UINT16:
        return struct.pack("<H", value)
    elif data_type == ConfigValueType.INT32:
        return struct.pack("<i", value)
    elif data_type == ConfigValueType.UINT32:
        return struct.pack("<I", value)
    elif data_type == ConfigValueType.INT64:
        return struct.pack("<q", value)
    elif data_type == ConfigValueType.UINT64:
        return struct.pack("<Q", value)
    elif data_type == ConfigValueType.FLOAT:
        return struct.pack("f", value)
    elif data_type == ConfigValueType.DOUBLE:
        return struct.pack("d", value)
    elif data_type == ConfigValueType.PROCEDURE_CALL:
        return struct.pack("?", value)
    else:
        return None


payload_ids = {
            CommonPayloadId.REQUEST_DEVICE_ID: RequestDeviceIdPayload,
            CommonPayloadId.REPLY_DEVICE_ID: ReplyDeviceIdPayload,
            CommonPayloadId.REQUEST_DEVICE_NAME: RequestDeviceNamePayload,
            CommonPayloadId.REPLY_DEVICE_NAME: ReplyDeviceNamePayload,
            CommonPayloadId.REQUEST_CATEGORY_COUNT: RequestCategoryCountPayload,
            CommonPayloadId.REPLY_CATEGORY_COUNT: ReplyCategoryCountPayload,
            CommonPayloadId.REQUEST_CONFIGURATION_CATEGORY: RequestConfigurationCategoryPayload,
            CommonPayloadId.REPLY_CONFIGURATION_CATEGORY: ReplyConfigurationCategory,
            CommonPayloadId.REQUEST_CONFIGURATION_NAME_AND_UID: RequestConfigurationNameUidPayload,
            CommonPayloadId.REPLY_CONFIGURATION_NAME_AND_UID: ReplyConfigurationNameUidPayload,
            CommonPayloadId.REQUEST_CONFIGURATION_VALUE_COUNT: RequestConfigurationValueCountPayload,
            CommonPayloadId.REPLY_CONFIGURATION_VALUE_COUNT: ReplyConfigurationValueCountPayload,
            CommonPayloadId.REQUEST_CONFIGURATION_VALUE_UID: RequestConfigurationValueUidPayload,
            CommonPayloadId.REPLY_CONFIGURATION_VALUE_UID: ReplyConfigurationValueUidPayload,
            CommonPayloadId.REQUEST_FIRMWARE_VERSION: RequestFirmwareVersionPayload,
            CommonPayloadId.REPLY_FIRMWARE_VERSION: ReplyFirmwareVersionPayload,
            CommonPayloadId.REBOOT: RebootPayload,
            CommonPayloadId.LOAD_DEFAULT: LoadDefaultConfigurationPayload,
            CommonPayloadId.SET_CONFIGURATION_VALUE_UID: SetConfigurationValueUidPayload,
            CommonPayloadId.SAVE_AS_DEFAULT: SaveAsDefaultConfigurationPayload,
            CommonPayloadId.FIRMWARE_START: FirmwareStartPayload,
            CommonPayloadId.FIRMWARE_DATA:FirmwareDataPayload,
            CommonPayloadId.FIRMWARE_END: FirmwareEndPayload
        }


def create_common_payload(data):
    payload_id = data[0]
    if payload_id in payload_ids:
        return payload_ids[payload_id].from_bytes(data)
    else:
        raise ValueError(f"Payload ID {payload_id} not implemented!")
