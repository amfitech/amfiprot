from typing import List, Union, Tuple, TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from .device import Device

from .common_payload import *


class Configurator:
    def __init__(self, device):
        self.device = device

    def read_all(self) -> List[dict]:
        config = []

        for cat_index in range(self._get_category_count()):
            category_name = self._get_category_name(cat_index)
            category = {'category': category_name, 'parameters': []}

            for param_index in range(self._get_parameter_count(cat_index)):
                name, uid = self._get_parameter_name_uid(cat_index, param_index)
                value = self.read(uid)

                category['parameters'].append({'uid': uid, 'name': name, 'value': value})

            config.append(category)
        return config

    def write_all(self, config):
        # Check config
        # for parameter in config:
        #     keys = parameter.keys()
        #     if 'name' not in keys or 'uid' not in keys or 'value' not in keys:
        #         raise ValueError(
        #             "Invalid configuration format. Expected list of dicts, each containing "
        #             "the keys 'name', 'uid' and 'value'.")

        # Write all parameters
        for category in config:
            for parameter in category['parameters']:
                # Read back the parameter in order to 1. check that it exists and 2. get the value type
                try:
                    value, data_type = self.read(parameter['uid'], return_datatype=True)
                except TimeoutError:
                    warnings.warn(f"Parameter \"{parameter['name']}\" ({parameter['uid']}) does not exist on device")
                    continue

                # print(f"{parameter['name']} read as {value}")

                # Set value
                self.set_config_value(parameter['uid'], parameter['value'], data_type)

                # print(f"{parameter['name']} set to {parameter['value']}")

                # Read it back again, to ensure that it is set
                new_value = self.config_value_from_uid(parameter['uid'])

                # print(f"{parameter['name']} read as {new_value}")

                if new_value != parameter['value']:
                    raise ValueError(
                        f"Could not set parameter {parameter['name']} ({parameter['uid']}). Expected {parameter['value']}, got {new_value}.")

    def read(self, uid, return_datatype: bool = False) -> Union[int, float, bool, str]:
        self.device.node.send_payload(RequestConfigurationValueUidPayload(uid))
        packet = self.device._await_packet(ReplyConfigurationValueUidPayload)

        if packet.payload.uid != uid:
            warnings.warn("Config UIDs did not match. Trying again...")
            packet = self.device._await_packet(ReplyConfigurationValueUidPayload)

        if return_datatype:
            return packet.payload.config_value, packet.payload.data_type
        else:
            return packet.payload.config_value

    def write(self, uid, value, data_type):  # TODO: data_type should be inferred automatically. It's a hassle to have to provide it in an interactive prompt.
        self.device.node.send_payload(SetConfigurationValueUidPayload(uid, value, data_type))

    def reset_to_default(self):
        self.device.node.send_payload(LoadDefaultConfigurationPayload())

    def _get_category_count(self):
        self.device.node.send_payload(RequestCategoryCountPayload())
        packet = self.device._await_packet(ReplyCategoryCountPayload)
        return packet.payload.category_count

    def _get_category_name(self, index) -> str:
        self.device.node.send_payload(RequestConfigurationCategoryPayload(index))
        packet = self.device._await_packet(ReplyConfigurationCategory)
        return packet.payload.category_name

    def _get_parameter_count(self, index):
        self.device.node.send_payload(RequestConfigurationValueCountPayload(index))
        packet = self.device._await_packet(ReplyConfigurationValueCountPayload)
        return packet.payload.config_value_count

    def _get_parameter_name_uid(self, category_index, parameter_index) -> Tuple[str, int]:
        self.device.node.send_payload(RequestConfigurationNameUidPayload(category_index, parameter_index))
        packet = self.device._await_packet(ReplyConfigurationNameUidPayload)
        return packet.payload.configuration_name, packet.payload.configuration_uid

    def __save_current_config_as_default(self):
        pass
