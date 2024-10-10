from .payload import Payload
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
    RESET_PARAMETER = 0x24
    REQUEST_PROCEDURE_SPEC = 0x30
    REPLY_PROCEDURE_SPEC = 0x31
    REQUEST_PROCEDURE_CALL = 0x32
    REPLY_PROCEDURE_CALL = 0x33


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

    def __str__(self):
        return f"<{type(self).__name__}>"

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

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': self.data[0]
        }


class ReplyDeviceIdPayload(CommonPayload):
    SIZE = 14

    def __init__(self, tx_id: int, uuid: int):
        self.tx_id = tx_id
        self.uuid = uuid

    @classmethod
    def from_bytes(cls, data):
        tx_id = data[1]
        uuid = int.from_bytes(data[10:14] + data[6:10] + data[2:6], byteorder='little')     # Reorder uint32 blocks, to match earlier formatting of UUID
        return ReplyDeviceIdPayload(tx_id, uuid)

    def __len__(self):
        return self.SIZE

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"tx_id: {self.tx_id}, uuid: {self.uuid:024x}"

    def to_bytes(self):
        uuid_as_bytes = self.uuid.to_bytes(12, byteorder='little')
        data = array.array('B', [CommonPayloadId.REPLY_DEVICE_ID, self.tx_id])
        data.extend(uuid_as_bytes[8:12])                                                     # Reorder uint32 blocks, to match earlier formatting of UUID
        data.extend(uuid_as_bytes[4:8])
        data.extend(uuid_as_bytes[0:4])
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_DEVICE_ID,
            'tx_id': self.tx_id,
            'uuid': self.uuid
        }


class SetTxIdPayload(CommonPayload):
    SIZE = 14

    def __init__(self, tx_id, uuid):
        self.tx_id = tx_id
        self.uuid = uuid

    @classmethod
    def from_bytes(cls, data):
        tx_id = data[1]
        uuid = int.from_bytes(data[10:14] + data[6:10] + data[2:6], byteorder='little')     # Reorder uint32 blocks, to match earlier formatting of UUID
        return SetTxIdPayload(tx_id, uuid)

    def __len__(self):
        return self.SIZE

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"tx_id: {self.tx_id}, uuid: {self.uuid:024x}"

    def to_bytes(self):
        uuid_as_bytes = self.uuid.to_bytes(12, byteorder='little')
        data = array.array('B', [CommonPayloadId.SET_TX_ID, self.tx_id])
        data.extend(uuid_as_bytes[8:12])                                                     # Reorder uint32 blocks, to match earlier formatting of UUID
        data.extend(uuid_as_bytes[4:8])
        data.extend(uuid_as_bytes[0:4])
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.SET_TX_ID,
            'tx_id': self.tx_id,
            'uuid': self.uuid
        }


class RequestFirmwareVersionPayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.REQUEST_FIRMWARE_VERSION])

    @classmethod
    def from_bytes(cls, data):
        return RequestFirmwareVersionPayload()

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REQUEST_FIRMWARE_VERSION
        }


class ReplyFirmwareVersionPayload(CommonPayload):
    SIZE = 17

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
        class_prefix = super().__str__() + " "
        return class_prefix + f"fw_version: {self.fw_version['major']}.{self.fw_version['minor']}.{self.fw_version['patch']}.{self.fw_version['build']}"

    def __len__(self):
        return self.SIZE

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REPLY_FIRMWARE_VERSION])
        data.extend(self.fw_version['major'].to_bytes(4, byteorder='little'))
        data.extend(self.fw_version['minor'].to_bytes(4, byteorder='little'))
        data.extend(self.fw_version['patch'].to_bytes(4, byteorder='little'))
        data.extend(self.fw_version['build'].to_bytes(4, byteorder='little'))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_FIRMWARE_VERSION,
            'fw_version': self.fw_version
        }

class RequestFirmwareVersionPerIdPayload(CommonPayload):
    def __init__(self, processor_id: int = 0):
        self.data = array.array('B', [CommonPayloadId.REQUEST_FIRMWARE_VERSION_PER_ID, processor_id])

    @classmethod
    def from_bytes(cls, data):
        processor_id = data[1]
        return RequestFirmwareVersionPerIdPayload(processor_id)

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REQUEST_FIRMWARE_VERSION_PER_ID,
            'processor_id': self.data[1]
        }

class ReplyFirmwareVersionPerIdPayload(CommonPayload):
    SIZE = 18

    def __init__(self, major: int, minor: int, patch: int, build: int, processor_id: int):
        self.fw_version = {'major': major, 'minor': minor, 'patch': patch, 'build': build}
        self.processor_id = processor_id

    @classmethod
    def from_bytes(cls, data):
        major = int.from_bytes(data[1:5], byteorder='little')
        minor = int.from_bytes(data[5:9], byteorder='little')
        patch = int.from_bytes(data[9:13], byteorder='little')
        build = int.from_bytes(data[13:17], byteorder='little')
        processor_id = data[17]
        return ReplyFirmwareVersionPerIdPayload(major, minor, patch, build, processor_id)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"fw_version: {self.fw_version['major']}.{self.fw_version['minor']}.{self.fw_version['patch']}.{self.fw_version['build']}"

    def __len__(self):
        return self.SIZE

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REPLY_FIRMWARE_VERSION])
        data.extend(self.fw_version['major'].to_bytes(4, byteorder='little'))
        data.extend(self.fw_version['minor'].to_bytes(4, byteorder='little'))
        data.extend(self.fw_version['patch'].to_bytes(4, byteorder='little'))
        data.extend(self.fw_version['build'].to_bytes(4, byteorder='little'))
        data.extend(self.processor_id.to_bytes(1, byteorder='little'))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_FIRMWARE_VERSION,
            'fw_version': self.fw_version,
            'processor_id': self.processor_id
        }
    

class DebugOutputPayload(CommonPayload):
    def __init__(self, debug_message: str):
        self.debug_message = debug_message

    @classmethod
    def from_bytes(cls, data):
        debug_message = byte_array_to_string(data[1:])
        return DebugOutputPayload(debug_message)

    def __len__(self):
        return len(self.debug_message) + 2

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"debug_message: {self.debug_message}"

    def to_bytes(self):
        arr = array.array('B', [CommonPayloadId.DEBUG_OUTPUT])
        arr.extend(self.debug_message.encode('ascii'))
        arr.append(0)
        return arr

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.DEBUG_OUTPUT,
            'debug_message': self.debug_message
        }


class RequestDeviceNamePayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.REQUEST_DEVICE_NAME])

    @classmethod
    def from_bytes(cls, data):
        return RequestDeviceNamePayload()

    def __len__(self):
        return len(self.data)

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
        class_prefix = super().__str__() + " "
        return class_prefix + f"name: {self.name}"

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

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': self.data[0]
        }

class ResetParameterPayload(CommonPayload):
    def __init__(self, ResetParameter: int = 0):
        self.data = array.array('B', [CommonPayloadId.RESET_PARAMETER, ResetParameter])

    @classmethod
    def from_bytes(cls, data):
        ResetParameter = data[1]
        return RequestFirmwareVersionPerIdPayload(ResetParameter)

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.RESET_PARAMETER,
            'resetParameter_id': self.data[1]
        }

class RequestCategoryCountPayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.REQUEST_CATEGORY_COUNT])

    @classmethod
    def from_bytes(cls, data):
        return RequestCategoryCountPayload()

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': self.data[0]
        }


class ReplyCategoryCountPayload(CommonPayload):
    SIZE = 2

    def __init__(self, category_count):
        self.category_count = category_count

    @classmethod
    def from_bytes(cls, data):
        category_count = int.from_bytes(data[1:2], byteorder='little', signed=False)
        return ReplyCategoryCountPayload(category_count)

    def __len__(self):
        return self.SIZE

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"category_count: {self.category_count}"

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REPLY_CATEGORY_COUNT])
        data.extend(self.category_count.to_bytes(2, byteorder='little'))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_CATEGORY_COUNT,
            'category_count': self.category_count
        }


class RequestConfigurationCategoryPayload(CommonPayload):
    SIZE = 2

    def __init__(self, category_id):
        self.category_id = category_id

    @classmethod
    def from_bytes(cls, data):
        category_id = data[1]
        return RequestConfigurationCategoryPayload(category_id)

    def __len__(self):
        return self.SIZE

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"category_id: {self.category_id}"

    def to_bytes(self):
        return array.array('B', [CommonPayloadId.REQUEST_CONFIGURATION_CATEGORY, self.category_id])

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
        class_prefix = super().__str__() + " "
        return class_prefix + f"category_id: {self.category_id}, category_name: {self.category_name}"

    def __len__(self):
        return 2 + len(self.category_name) + 1

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REPLY_CONFIGURATION_CATEGORY, self.category_id])
        data.extend(self.category_name.encode('ascii'))
        data.append(0)
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_CONFIGURATION_CATEGORY,
            'category_id': self.category_id,
            'category_name': self.category_name
        }


class RequestConfigurationNameUidPayload(CommonPayload):
    SIZE = 4

    def __init__(self, category_index: int, config_index: int):
        self.category_index = category_index
        self.config_index = config_index

    @classmethod
    def from_bytes(cls, data):
        category_index = data[1]
        config_index = int.from_bytes(data[2:4], byteorder='little')
        return RequestConfigurationNameUidPayload(category_index, config_index)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"cate"

    def __len__(self):
        return self.SIZE

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REQUEST_CONFIGURATION_NAME_AND_UID, self.category_index])
        data.extend(int.to_bytes(self.config_index, length=2, byteorder='little'))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REQUEST_CONFIGURATION_NAME_AND_UID,
            'category_index': self.category_index,
            'config_index': self.config_index
        }


class ReplyConfigurationNameUidPayload(CommonPayload):
    def __init__(self, configuration_name: str, configuration_uid: int, config_index: int, category_index: int):
        self.configuration_uid = configuration_uid
        self.configuration_name = configuration_name
        self.config_index = config_index
        self.category_index = category_index

    @classmethod
    def from_bytes(cls, data):
        config_index = int.from_bytes(data[1:3], byteorder='little')
        category_index = int.from_bytes(data[3:4], byteorder='little')
        uid = int.from_bytes(data[4:8], byteorder='little')
        name = byte_array_to_string(data[8:])
        return ReplyConfigurationNameUidPayload(name, uid, config_index, category_index)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"category_index: {self.category_index}, config_index: {self.config_index}, config_name: {self.configuration_name}, config_uid: {self.configuration_uid}"

    def __len__(self):
        return 8 + len(self.configuration_name) + 1

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REPLY_CONFIGURATION_NAME_AND_UID])
        data.extend(self.config_index.to_bytes(2, byteorder='little'))
        data.extend(self.category_index.to_bytes(1, byteorder='little'))
        data.extend(self.configuration_uid.to_bytes(2, byteorder='little'))
        data.extend(self.configuration_name.encode('ascii'))
        data.append(0)
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_CONFIGURATION_NAME_AND_UID,
            'config_index': self.config_index,
            'category_index': self.category_index,
            'configuration_uid': self.configuration_uid,
            'configuration_name': self.configuration_name
        }


class RequestConfigurationValueCountPayload(CommonPayload):
    SIZE = 2

    def __init__(self, category_index: int):
        self.category_index = category_index

    @classmethod
    def from_bytes(cls, data):
        category_index = data[1]
        return RequestConfigurationValueCountPayload(category_index)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"category_index: {self.category_index}"

    def __len__(self):
        return self.SIZE

    def to_bytes(self):
        return array.array('B', [CommonPayloadId.REQUEST_CONFIGURATION_VALUE_COUNT, self.category_index])

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_CONFIGURATION_VALUE_UID,
            'category_index': self.category_index
        }


class ReplyConfigurationValueCountPayload(CommonPayload):
    SIZE = 4

    def __init__(self, category_index: int, config_value_count: int):
        self.category_index = category_index
        self.config_value_count = config_value_count

    @classmethod
    def from_bytes(cls, data):
        category_index = int.from_bytes(data[1:2], byteorder='little')
        config_value_count = int.from_bytes(data[2:4], byteorder='little')
        return ReplyConfigurationValueCountPayload(category_index, config_value_count)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"category_index: {self.category_index}, config_value_count: {self.config_value_count}"

    def __len__(self):
        return self.SIZE

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REPLY_CONFIGURATION_VALUE_COUNT])
        data.extend(self.category_index.to_bytes(1, byteorder='little'))
        data.extend(self.config_value_count.to_bytes(2, byteorder='little'))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_CONFIGURATION_VALUE_COUNT,
            'config_value_count': self.config_value_count
        }


class RequestConfigurationValueUidPayload(CommonPayload):
    SIZE = 5

    def __init__(self, config_uid: int):
        self.config_uid = config_uid

    @classmethod
    def from_bytes(cls, data):
        config_uid = int.from_bytes(data[1:5], byteorder='little')
        return RequestConfigurationValueUidPayload(config_uid)

    def __str__(self):
        class_prefix = super().__str__() + ""
        return class_prefix + f"config_uid: {self.config_uid}"

    def __len__(self):
        return self.SIZE

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REQUEST_CONFIGURATION_VALUE_UID])
        data.extend(int.to_bytes(self.config_uid, length=4, byteorder='little'))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REQUEST_CONFIGURATION_VALUE_UID,
            'config_uid': self.config_uid
        }


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
        class_prefix = super().__str__() + " "
        return class_prefix + f"config_value: {self.config_value}"

    def __len__(self):
        return len(self.to_bytes())  # FIXME: hack

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REPLY_CONFIGURATION_VALUE_UID])
        data.extend(int.to_bytes(self.uid, 4, byteorder='little'))
        data.append(self.data_type)
        data.extend(encode_config_value(self.data_type, self.config_value))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_CONFIGURATION_VALUE_UID,
            'config_uid': self.uid,
            'config_value': self.config_value
        }


class LoadDefaultConfigurationPayload(CommonPayload):
    def __init__(self):
        self.data = array.array('B', [CommonPayloadId.LOAD_DEFAULT])

    @classmethod
    def from_bytes(cls, data):
        return LoadDefaultConfigurationPayload()

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.LOAD_DEFAULT
        }

class SaveAsDefaultConfigurationPayload(CommonPayload):
    SIZE = 13

    def __init__(self, uuid):
        self.uuid = uuid

    @classmethod
    def from_bytes(cls, data):
        #uuid = int.from_bytes(data[1:13], byteorder='little')
        uuid = int.from_bytes(data[9:13] + data[5:9] + data[1:5], byteorder='little')       # Reorder uint32 blocks, to match earlier formatting of UUID
        return SaveAsDefaultConfigurationPayload(uuid)

    def __len__(self):
        return self.SIZE

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"uuid: {self.uuid:024x}"

    def to_bytes(self):
        uuid_as_bytes = self.uuid.to_bytes(12, byteorder='little')
        data = array.array('B', [CommonPayloadId.SAVE_AS_DEFAULT])
        data.extend(uuid_as_bytes[8:12])                                                    # Reorder uint32 blocks, to match earlier formatting of UUID
        data.extend(uuid_as_bytes[4:8])
        data.extend(uuid_as_bytes[0:4])
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.SAVE_AS_DEFAULT,
            'uuid': self.uuid
        }

class FirmwareStartPayload(CommonPayload):
    SIZE = 2

    def  __init__(self, processor_id: int = 0):
        self.processor_id = processor_id

    @classmethod
    def from_bytes(cls, data):
        processor_id = data[1]
        return FirmwareStartPayload(processor_id)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"processor_id: {self.processor_id}"

    def __len__(self):
        return self.SIZE

    def to_bytes(self):
        return array.array('B', [CommonPayloadId.FIRMWARE_START, self.processor_id])

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.FIRMWARE_START,
            'processor_id': self.processor_id
        }


class FirmwareDataPayload(CommonPayload):
    def __init__(self, firmware_data, processor_id: int = 0):
        self.data = array.array('B', [CommonPayloadId.FIRMWARE_DATA, processor_id])
        firmware_bytes = array.array('B', firmware_data)
        self.data.extend(firmware_bytes)

    @classmethod
    def from_bytes(cls, data):
        processor_id = data[1]
        firmware_data = data[2:]
        return FirmwareDataPayload(firmware_data, processor_id)

    def __str__(self):
        return "Firmware data payload: " + str(self.data)

    def __len__(self):
        return len(self.data)

    def to_bytes(self):
        return self.data

    def to_dict(self):
        pass


class FirmwareEndPayload(CommonPayload):
    SIZE = 2

    def  __init__(self, processor_id: int = 0):
        self.processor_id = processor_id

    @classmethod
    def from_bytes(cls, data):
        processor_id = data[1]
        return FirmwareEndPayload(processor_id)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"processor_id: {self.processor_id}"

    def __len__(self):
        return self.SIZE

    def to_bytes(self):
        return array.array('B', [CommonPayloadId.FIRMWARE_END, self.processor_id])

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.FIRMWARE_END,
            'processor_id': self.processor_id
        }


class SetConfigurationValueUidPayload(CommonPayload):
    def __init__(self, uid, value, data_type):
        self.config_uid = uid
        self.config_value = value
        self.data_type = data_type

    @classmethod
    def from_bytes(cls, data):
        config_uid = int.from_bytes(data[1:5], byteorder='little')
        data_type = data[5]
        value = decode_config_value(data_type, data[6:])
        return SetConfigurationValueUidPayload(config_uid, value, data_type)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"config_uid: {self.config_uid}, config_value: {self.config_value}"

    def __len__(self):
        return len(self.to_bytes())  # FIXME: hack

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.SET_CONFIGURATION_VALUE_UID])
        data.extend(int.to_bytes(self.config_uid, length=4, byteorder='little'))
        data.extend(int.to_bytes(self.data_type, length=1, byteorder='little'))
        data.extend(encode_config_value(self.config_value, self.data_type))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.SET_CONFIGURATION_VALUE_UID,
            'config_uid': self.config_uid,
            'config_value': self.config_value
        }
    
class RequestProcedureSpec(CommonPayload):
    def __init__(self, index, uid=None):
        self.RPC_Index = index
        self.RPC_UID = uid

    @classmethod
    def from_bytes(cls, data):
        RPC_Index = int.from_bytes(data[1:3], byteorder='little')
        RPC_UID = int.from_bytes(data[3:7], byteorder='little')
        return RequestProcedureSpec(RPC_Index, RPC_UID)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"RPC_Index: {self.RPC_Index}, RPC_UID: {self.RPC_UID}"

    def __len__(self):
        return len(self.to_bytes())  # FIXME: hack

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REQUEST_PROCEDURE_SPEC])
        data.extend(int.to_bytes(self.RPC_Index, length=2, byteorder='little'))
        data.extend(int.to_bytes(self.RPC_UID, length=4, byteorder='little'))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REQUEST_PROCEDURE_SPEC,
            'RPC_Index': self.RPC_Index,
            'RPC_UID': self.RPC_UID
        }
    
class ReplyProcedureSpec(CommonPayload):
    def __init__(self, index=None, uid=None, returnValueType=None, Param1Type=None, Param2Type=None, Param3Type=None, Param4Type=None, Param5Type=None, Name=None):
        self.RPC_Index = index
        self.RPC_UID = uid
        self.RPC_ReturnValueType = returnValueType
        self.RPC_Param1Type = Param1Type
        self.RPC_Param2Type = Param2Type
        self.RPC_Param3Type = Param3Type
        self.RPC_Param4Type = Param4Type
        self.RPC_Param5Type = Param5Type
        self.RPC_Name = Name

    @classmethod
    def from_bytes(cls, data):
        RPC_Index = int.from_bytes(data[1:3], byteorder='little')
        RPC_UID = int.from_bytes(data[3:7], byteorder='little')
        RPC_ReturnValueType = data[7]
        RPC_Param1Type = data[8]
        RPC_Param2Type = data[9]
        RPC_Param3Type = data[10]
        RPC_Param4Type = data[11]
        RPC_Param5Type = data[12]
        string_bytes = data[13:].tobytes()
        RPC_Name = string_bytes.decode('utf-8')
        return ReplyProcedureSpec(RPC_Index, RPC_UID, RPC_ReturnValueType, RPC_Param1Type, RPC_Param2Type, RPC_Param3Type, RPC_Param4Type, RPC_Param5Type, RPC_Name)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"RPC_Index: {self.RPC_Index}, RPC_UID: {self.RPC_UID}, RPC_ReturnValueType: {self.RPC_ReturnValueType}, RPC_Param1Type: {self.RPC_Param1Type}, RPC_Param2Type: {self.RPC_Param2Type}, RPC_Param3Type: {self.RPC_Param3Type}, RPC_Param4Type: {self.RPC_Param4Type}, RPC_Param5Type: {self.RPC_Param5Type}, RPC_Name: {self.RPC_Name}"

    def __len__(self):
        return len(self.to_bytes())  # FIXME: hack

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REPLY_PROCEDURE_SPEC])
        data.extend(int.to_bytes(self.RPC_Index, length=2, byteorder='little'))
        data.extend(int.to_bytes(self.RPC_UID, length=4, byteorder='little'))
        data.append(self.RPC_ReturnValueType)
        data.append(self.RPC_Param1Type)
        data.append(self.RPC_Param2Type)
        data.append(self.RPC_Param3Type)
        data.append(self.RPC_Param4Type)
        data.append(self.RPC_Param5Type)
        data.extend(self.RPC_Name)
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_PROCEDURE_SPEC,
            'RPC_Index': self.RPC_Index,
            'RPC_UID': self.RPC_UID,
            'RPC_ReturnValueType': self.RPC_ReturnValueType,
            'RPC_Param1Type': self.RPC_Param1Type,
            'RPC_Param2Type': self.RPC_Param2Type,
            'RPC_Param3Type': self.RPC_Param3Type,
            'RPC_Param4Type': self.RPC_Param4Type,
            'RPC_Param5Type': self.RPC_Param5Type,
            'RPC_Name': self.RPC_Name,
        }
    
class RequestProcedureCall(CommonPayload):
    def __init__(self, uid, Param1Type: ConfigValueType, Param1Value: int, Param2Type: int=None, Param2Value: int=None, Param3Type: int=None, Param3Value: int=None, Param4Type: int=None, Param4Value: int=None, Param5Type: int=None, Param5Value: int=None):
        self.RPC_UID = uid
        self.RPC_Param1Type = Param1Type
        self.RPC_Param1Value = Param1Value
        if Param2Type is None: 
            self.RPC_Param2Type = 0
        else:
            self.RPC_Param2Type = Param2Type
        if Param2Value is None:
            self.RPC_Param2Value = 0
        else:
            self.RPC_Param2Value = Param2Value

        if Param3Type is None: 
            self.RPC_Param3Type = 0
        else:
            self.RPC_Param3Type = Param3Type
        if Param3Value is None:
            self.RPC_Param3Value = 0
        else:
            self.RPC_Param3Value = Param3Value

        if Param4Type is None: 
            self.RPC_Param4Type = 0
        else:
            self.RPC_Param4Type = Param4Type
        if Param4Value is None:
            self.RPC_Param4Value = 0
        else:
            self.RPC_Param4Value = Param4Value

        if Param5Type is None: 
            self.RPC_Param5Type = 0
        else:
            self.RPC_Param5Type = Param5Type
        if Param5Value is None:
            self.RPC_Param5Value = 0
        else:
            self.RPC_Param5Value = Param5Value

    @classmethod
    def from_bytes(cls, data):
        RPC_UID = int.from_bytes(data[1:5], byteorder='little')
        RPC_Param1Type = data[5]
        RPC_Param1Value = decode_config_value(RPC_Param1Type, data[6:14])
        RPC_Param2Type = data[14]
        RPC_Param2Value = decode_config_value(RPC_Param2Type, data[15:23])
        RPC_Param3Type = data[23]
        RPC_Param3Value = decode_config_value(RPC_Param3Type, data[24:32])
        RPC_Param4Type = data[32]
        RPC_Param4Value = decode_config_value(RPC_Param4Type, data[33:41])
        RPC_Param5Type = data[41]
        RPC_Param5Value = decode_config_value(RPC_Param5Type, data[42:50])
        return RequestProcedureCall(RPC_UID, RPC_Param1Type, RPC_Param1Value, RPC_Param2Type, RPC_Param2Value, RPC_Param3Type, RPC_Param3Value, RPC_Param4Type, RPC_Param4Value, RPC_Param5Type, RPC_Param5Value)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"RPC_UID: {self.RPC_UID}, RPC_Param1Type: {self.RPC_Param1Type}, RPC_Param1Value: {self.RPC_Param1Value}, RPC_Param2Type: {self.RPC_Param2Type}, RPC_Param2Value: {self.RPC_Param2Value}, RPC_Param3Type: {self.RPC_Param3Type}, RPC_Param3Value: {self.RPC_Param3Value}, RPC_Param4Type: {self.RPC_Param4Type}, RPC_Param4Value: {self.RPC_Param4Value}, RPC_Param5Type: {self.RPC_Param5Type}, RPC_Param5Value: {self.RPC_Param5Value}"

    def __len__(self):
        return len(self.to_bytes())  # FIXME: hack

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REQUEST_PROCEDURE_CALL])
        data.extend(int.to_bytes(self.RPC_UID, length=4, byteorder='little'))
        data.append(self.RPC_Param1Type)
        data.extend(int.to_bytes(self.RPC_Param1Value, length=8, byteorder='little'))
        data.append(self.RPC_Param2Type)
        data.extend(int.to_bytes(self.RPC_Param2Value, length=8, byteorder='little'))
        data.append(self.RPC_Param3Type)
        data.extend(int.to_bytes(self.RPC_Param3Value, length=8, byteorder='little'))
        data.append(self.RPC_Param4Type)
        data.extend(int.to_bytes(self.RPC_Param4Value, length=8, byteorder='little'))
        data.append(self.RPC_Param5Type)
        data.extend(int.to_bytes(self.RPC_Param5Value, length=8, byteorder='little'))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REQUEST_PROCEDURE_CALL,
            'RPC_UID': self.RPC_UID,
            'RPC_Param1Type': self.RPC_Param1Type,
            'RPC_Param1Value': self.RPC_Param1Value,
            'RPC_Param2Type': self.RPC_Param2Type,
            'RPC_Param2Value': self.RPC_Param2Value,
            'RPC_Param3Type': self.RPC_Param3Type,
            'RPC_Param3Value': self.RPC_Param3Value,
            'RPC_Param4Type': self.RPC_Param4Type,
            'RPC_Param4Value': self.RPC_Param4Value,
            'RPC_Param5Type': self.RPC_Param5Type,
            'RPC_Param5Value': self.RPC_Param5Value,
        }

class ReplyProcedureCall(CommonPayload):
    def __init__(self, uid=None, ReturnType: ConfigValueType=None, ReturnValue: int=None):
        self.RPC_UID = uid
        self.RPC_ReturnType = ReturnType
        self.RPC_ReturnValue = ReturnValue

    @classmethod
    def from_bytes(cls, data):
        RPC_UID = int.from_bytes(data[1:5], byteorder='little')
        RPC_ReturnType = data[5]
        RPC_ReturnValue = decode_config_value(RPC_ReturnType, data[6:14])
        return ReplyProcedureCall(RPC_UID, RPC_ReturnType, RPC_ReturnValue)

    def __str__(self):
        class_prefix = super().__str__() + " "
        return class_prefix + f"RPC_UID: {self.RPC_UID}, RPC_ReturnType: {self.RPC_ReturnType}, RPC_ReturnValue: {self.RPC_ReturnValue}"

    def __len__(self):
        return len(self.to_bytes())  # FIXME: hack

    def to_bytes(self):
        data = array.array('B', [CommonPayloadId.REPLY_PROCEDURE_CALL])
        data.extend(int.to_bytes(self.RPC_UID, length=4, byteorder='little'))
        data.append(self.RPC_ReturnType)
        data.extend(int.to_bytes(self.RPC_ReturnValue, length=8, byteorder='little'))
        return data

    def to_dict(self):
        return {
            'payload_id': CommonPayloadId.REPLY_PROCEDURE_CALL,
            'RPC_UID': self.RPC_UID,
            'RPC_ReturnType': self.RPC_ReturnType,
            'RPC_ReturnValue': self.RPC_ReturnValue,
        }

def byte_array_to_string(byte_array: array.array):
    return bytes(byte_array).decode('ascii').rstrip('\x00')


def decode_config_value(data_type: ConfigValueType, byte_data: array.array):
    if data_type == ConfigValueType.BOOL:
        return bool(int.from_bytes(byte_data, byteorder='little'))
    elif data_type == ConfigValueType.CHAR:
        return byte_data.tobytes().decode('ascii')
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
            CommonPayloadId.SET_TX_ID: SetTxIdPayload,
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
            CommonPayloadId.FIRMWARE_END: FirmwareEndPayload,
            CommonPayloadId.REQUEST_FIRMWARE_VERSION_PER_ID: RequestFirmwareVersionPerIdPayload,
            CommonPayloadId.REPLY_FIRMWARE_VERSION_PER_ID: ReplyFirmwareVersionPerIdPayload,
            CommonPayloadId.DEBUG_OUTPUT: DebugOutputPayload,
            CommonPayloadId.RESET_PARAMETER: ResetParameterPayload,
            CommonPayloadId.REQUEST_PROCEDURE_SPEC: RequestProcedureSpec,
            CommonPayloadId.REPLY_PROCEDURE_SPEC: ReplyProcedureSpec,
            CommonPayloadId.REQUEST_PROCEDURE_CALL: RequestProcedureCall,
            CommonPayloadId.REPLY_PROCEDURE_CALL: ReplyProcedureCall,
        }


def create_common_payload(data) -> Payload:
    payload_id = data[0]
    if payload_id in payload_ids:
        return payload_ids[payload_id].from_bytes(data)  # type: ignore
    else:
        raise ValueError(f"Payload ID {payload_id} not implemented!")
