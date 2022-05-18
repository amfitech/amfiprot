from __future__ import annotations
import multiprocessing as mp
import typing
import time
from abc import ABC
from .packet import Packet
from .common_payload import *
from .payload import UndefinedPayload

if typing.TYPE_CHECKING:
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

    def read_device_name(self) -> str:
        self.node.send_payload(RequestDeviceNamePayload())
        packet = self._wait_for_packet(ReplyDeviceNamePayload)
        return packet.payload.name

    def read_category_count(self):
        self.node.send_payload(RequestCategoryCountPayload())
        packet = self._wait_for_packet(ReplyCategoryCountPayload)
        return packet.payload.category_count

    def read_config_category(self, id):
        self.node.send_payload(RequestConfigurationCategoryPayload(id))
        packet = self._wait_for_packet(ReplyConfigurationCategory)
        return packet.payload.category_name

    def read_config_value_count(self, category_id):
        self.node.send_payload(RequestConfigurationValueCountPayload(category_id))
        packet = self._wait_for_packet(ReplyConfigurationValueCountPayload)
        return packet.payload.config_value_count

    def read_config_name_and_uid(self, category_id, config_id):
        self.node.send_payload(RequestConfigurationNameUidPayload(category_id, config_id))
        packet = self._wait_for_packet(ReplyConfigurationNameUidPayload)
        return packet.payload.configuration_name, packet.payload.configuration_uid

    def read_config_value(self, uid):
        self.node.send_payload(RequestConfigurationValueUidPayload(uid))
        packet = self._wait_for_packet(ReplyConfigurationValueUidPayload)
        return packet.payload.config_value

    def set_tx_id(self, tx_id):
        payload = SetTxIdPayload(array.array('B', [tx_id]))
        self.node.send_payload(payload)

    def reboot(self):
        self.node.send_payload(RebootPayload())
        self.node.connection.process()

    def get_packet(self) -> Packet:
        """ For specialized devices, this is where we reinterpret UndefinedPaylods as
        application-specific payload types """
        return self.node.get_packet()

    def _wait_for_packet(self, payload_class):
        packet = None
        while packet is None or type(packet.payload) != payload_class:
            packet = self.get_packet()

        return packet
