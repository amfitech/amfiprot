import warnings
from typing import List, Union, Tuple
from .common_payload import *


class Configurator:
    def __init__(self, device):
        self.device = device

    def read_all(self, flat_list: bool = False) -> List[dict]:
        config = []

        for cat_index in range(self._get_category_count()):
            category_name = self._get_category_name(cat_index)
            category = {'name': category_name, 'parameters': []}

            for param_index in range(self._get_parameter_count(cat_index)):
                name, uid = self._get_parameter_name_uid(cat_index, param_index)
                value = self.read(uid)

                category['parameters'].append({'uid': uid, 'name': name, 'value': value})

            if flat_list:
                for param in category['parameters']:
                    param['category'] = category_name
                    config.append(param)
            else:
                config.append(category)
        return config

    def write_all(self, config):
        # Detect if config is a flat list or categories with nested parameters
        flat_list = False

        if 'uid' in config[0].keys():
            print("Flat list detected!")
            flat_list = True

        # Write all parameters
        if flat_list:
            for parameter in config:
                try:
                    self.write(parameter['uid'], parameter['value'])
                except ValueError:
                    warnings.warn(f"Parameter \"{parameter['name']}\" ({parameter['uid']}) does not exist on device")
        else:
            for category in config:
                for parameter in category['parameters']:
                    try:
                        self.write(parameter['uid'], parameter['value'])
                    except ValueError:
                        warnings.warn(f"Parameter \"{parameter['name']}\" ({parameter['uid']}) does not exist on device")

    def read(self, uid, return_datatype: bool = False) -> Union[int, float, bool, str]:
        self.device.node.send_payload(RequestConfigurationValueUidPayload(uid))
        packet = self.device._await_packet(ReplyConfigurationValueUidPayload)

        if packet.payload.uid != uid:  # Does this ever happen?
            warnings.warn("Config UIDs did not match. Trying again...")
            packet = self.device._await_packet(ReplyConfigurationValueUidPayload)

        if return_datatype:
            return packet.payload.config_value, packet.payload.data_type
        else:
            return packet.payload.config_value

    def write(self, uid, value) -> Union[int, float, bool, str]:
        try:
            old_value, data_type = self.read(uid, return_datatype=True)
        except TimeoutError:
            raise ValueError(f"Parameter does not exist on target (UID: {uid}).")

        if type(value) != type(old_value):
            raise ValueError(f"Data type mismatch (given {type(value)}, expected {type(old_value)}).")

        self.device.node.send_payload(SetConfigurationValueUidPayload(uid, value, data_type))
        response = self.device._await_packet(ReplyConfigurationValueUidPayload)

        return response.payload.config_value

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
        raise NotImplementedError
