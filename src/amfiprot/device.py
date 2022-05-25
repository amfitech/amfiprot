from __future__ import annotations
import multiprocessing as mp
from typing import List, TYPE_CHECKING
import warnings
import time
import os
from abc import ABC
from .packet import Packet, PacketType
from .common_payload import *
from .payload import UndefinedPayload

if TYPE_CHECKING:
    from .node import Node


class Device:
    """ High-level interface to a physical device. This is an abstraction layer on top of the `Node` class.
    For low-level access (i.e. sending custom packets or payloads) it is possible to use `Device.node` directly.
    Do note, that `Device.node.get_packet` does not have any knowledge of application-specific payload IDs. Thus,
    to interpret the payloads correctly, always use `Device.get_packet` to read packets. """
    def __init__(self, node: Node):
        self.node = node
        self.tx_id = node.tx_id
        self.uuid = node.uuid

    def id(self) -> int:
        self.node.send_payload(RequestDeviceIdPayload())
        packet = self._await_packet(ReplyDeviceIdPayload)
        return packet.payload.tx_id, packet.payload.uuid

    def firmware_version(self) -> dict:
        self.node.send_payload(RequestFirmwareVersionPayload())
        packet = self._await_packet(ReplyFirmwareVersionPayload)
        return packet.payload.fw_version

    def name(self) -> str:
        self.node.send_payload(RequestDeviceNamePayload())
        packet = self._await_packet(ReplyDeviceNamePayload)
        return packet.payload.name

    def config_category_count(self):
        self.node.send_payload(RequestCategoryCountPayload())
        packet = self._await_packet(ReplyCategoryCountPayload)
        return packet.payload.category_count

    def config_category_name(self, index):
        self.node.send_payload(RequestConfigurationCategoryPayload(index))
        packet = self._await_packet(ReplyConfigurationCategory)
        return packet.payload.category_name

    def config_parameter_count(self, category_id):
        self.node.send_payload(RequestConfigurationValueCountPayload(category_id))
        packet = self._await_packet(ReplyConfigurationValueCountPayload)
        return packet.payload.config_value_count

    def config_name_uid(self, category_id, config_id):
        self.node.send_payload(RequestConfigurationNameUidPayload(category_id, config_id))
        packet = self._await_packet(ReplyConfigurationNameUidPayload)
        return packet.payload.configuration_name, packet.payload.configuration_uid

    def config_value_from_uid(self, uid, return_datatype: bool = False):
        self.node.send_payload(RequestConfigurationValueUidPayload(uid))
        packet = self._await_packet(ReplyConfigurationValueUidPayload)

        if packet.payload.uid != uid:
            warnings.warn("Config UIDs did not match. Trying again...")
            packet = self._await_packet(ReplyConfigurationValueUidPayload)

        if return_datatype:
            return packet.payload.config_value, packet.payload.data_type
        else:
            return packet.payload.config_value

    def config_value_from_index(self, index):
        pass

    def read_config(self) -> List[dict]:
        config = []

        for cat_index in range(self.config_category_count()):
            category_name = self.config_category_name(cat_index)
            category = {'category': category_name, 'parameters': []}

            for param_index in range(self.config_parameter_count(cat_index)):
                name, uid = self.config_name_uid(cat_index, param_index)
                value = self.config_value_from_uid(uid)

                category['parameters'].append({'uid': uid, 'name': name, 'value': value})

            config.append(category)
        return config

    def write_config(self, config: List[dict]):
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
                    value, data_type = self.config_value_from_uid(parameter['uid'], return_datatype=True)
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
                    raise ValueError(f"Could not set parameter {parameter['name']} ({parameter['uid']}). Expected {parameter['value']}, got {new_value}.")

    def update_firmware(self, path_to_bin: str, print_progress: bool = False):
        file_size = os.path.getsize(path_to_bin)
        bin_data = array.array('B')

        with open(path_to_bin, 'rb') as bin_file:
            bin_data.fromfile(bin_file, file_size)

        # Slice array into appropriately sized payloads (depends on the connection)
        max_payload_size = self.node.max_payload_size()
        chunk_size = max_payload_size - 2
        chunks = [bin_data[i:i + chunk_size] for i in range(0, file_size, chunk_size)]

        # Send firmware start command
        self.node.send_payload(FirmwareStartPayload())
        self._await_reply(PayloadType.SUCCESS, timeout_ms=10_000)

        # Send data packets and receive Ack for each packet
        progress_timer = MilliTimer(1000, autostart=True)

        for index, chunk in enumerate(chunks):
            payload = FirmwareDataPayload(chunk)
            self.node.send_payload(payload, packet_type=PacketType.REQUEST_ACK)
            self._await_reply(PayloadType.SUCCESS, timeout_ms=10_000)

            if progress_timer.expired():
                progress = (index / len(chunks)) * 100
                print(f"Firmware sent: {progress:.1f}%")
                progress_timer.start()

        # Send firmware end command
        self.node.send_payload(FirmwareEndPayload())

    def set_config_value(self, uid, value, data_type):
        self.node.send_payload(SetConfigurationValueUidPayload(uid, value, data_type))

    def load_default_config(self):
        self.node.send_payload(LoadDefaultConfigurationPayload())

    def __save_current_config_as_default(self):
        pass

    def set_tx_id(self, tx_id):
        payload = SetTxIdPayload(array.array('B', [tx_id]))
        self.node.send_payload(payload)

    def reboot(self):
        # FIXME: Device cannot be reached after reboot unless both `Connection` and `Device` are deleted and recreated. Maybe only if the rebooted device is physically connected via USB.
        self.node.send_payload(RebootPayload())

    def get_packet(self) -> Packet:
        """ For specialized devices, this is where we reinterpret UndefinedPaylods as
        application-specific payload types """
        return self.node.get_packet()

    def _await_packet(self, payload_class, timeout_ms=1000):
        packet = None
        timer = MilliTimer(timeout_ms, autostart=True)

        while packet is None or type(packet.payload) != payload_class:
            packet = self.get_packet()

            if timer.expired():
                raise TimeoutError("Packet not returned.")

        return packet

    def _await_ack(self, timeout_ms=1000):
        packet = None
        timer = MilliTimer(timeout_ms, autostart=True)

        while packet is None or packet.packet_type != PacketType.ACK:
            packet = self.get_packet()

            if packet is not None:
                if packet.payload_type == PayloadType.NOT_IMPLEMENTED:
                    print("Received NOT_IMPLEMENTED packet!")
                elif packet.payload_type == PayloadType.SUCCESS:
                    print("Received SUCCESS")
                elif packet.payload_type == PayloadType.FAILURE:
                    print("Received FAILURE")
                else:
                    print(f"Received {packet.payload_type}")

            if timer.expired():
                raise TimeoutError("Timed out waiting for Ack.")

        return

    def _await_reply(self, payload_type: PayloadType, timeout_ms: int = 1000):
        packet = None
        timer = MilliTimer(timeout_ms, autostart=True)

        while packet is None or packet.payload_type != payload_type:
            packet = self.get_packet()

            if timer.expired():
                raise TimeoutError("Packet not returned.")

        return


class MilliTimer:
    def __init__(self, duration, autostart=False):
        self.duration = duration
        self.start_time = None

        if autostart:
            self.start()

    def start(self):
        self.start_time = time.time_ns() // 1_000_000

    def expired(self):
        if self.start_time is None:
            return False

        return (time.time_ns() // 1_000_000) - self.start_time >= self.duration
