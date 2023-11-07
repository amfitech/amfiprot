from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import time
import os
from .packet import Packet, PacketType
from .common_payload import *
from .configurator import Configurator

if TYPE_CHECKING:
    from .node import Node


class Device:
    """ High-level interface to a physical device. This is an abstraction layer on top of the `Node` class.
    For low-level access (i.e. sending custom packets or payloads) it is possible to use `Device.node` directly.
    """

    def __init__(self, node: Node):
        self.node = node
        self.config = Configurator(self)

    def get_tx_id_uuid(self) -> tuple[int, int]:
        self.node.send_payload(RequestDeviceIdPayload())
        packet = self._await_packet(ReplyDeviceIdPayload)

        self.node.tx_id = packet.payload.tx_id
        self.node.uuid = packet.payload.uuid

        return packet.payload.tx_id, packet.payload.uuid

    def firmware_version(self, processor_id: int = 0) -> dict:
        self.node.send_payload(RequestFirmwareVersionPerIdPayload(processor_id))
        packet = self._await_packet(ReplyFirmwareVersionPerIdPayload)
        return packet.payload.fw_version

    def name(self) -> str:
        if self.node.name is None:
            self.node.send_payload(RequestDeviceNamePayload())
            packet = self._await_packet(ReplyDeviceNamePayload)
            self.node.name = packet.payload.name

        return self.node.name

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

            if progress_timer.expired() and print_progress:
                progress = (index / len(chunks)) * 100
                print(f"Firmware sent: {progress:.1f}%")
                progress_timer.start()

        # Send firmware end command
        self.node.send_payload(FirmwareEndPayload())

    def set_tx_id(self, tx_id) -> bool:
        payload = SetTxIdPayload(tx_id, self.node.uuid)
        self.node.send_payload(payload)

        # Connection must be informed of new tx_id
        self.node.tx_id = tx_id
        self.node.connection.refresh()

        # Read back tx_id to ensure that it is set
        new_tx_id, uuid = self.get_tx_id_uuid()
        return new_tx_id == tx_id

    def reboot(self):
        self.node.send_payload(RebootPayload())

    def getProcedureSpec(self, index, uid=None) -> ReplyProcedureCall:
        payload = RequestProcedureSpec(index, uid)
        self.node.send_payload(payload)
        packet = self._await_packet(ReplyProcedureSpec, timeout_ms=1000)
        return packet

    def callProcedure(self, uid, Param1Type: ConfigValueType, Param1Value: int, Param2Type=None, Param2Value=None, Param3Type=None, Param3Value=None, Param4Type=None, Param4Value=None, Param5Type=None, Param5Value=None):
        payload = RequestProcedureCall(uid, Param1Type, Param1Value, Param2Type, Param2Value, Param3Type, Param3Value, Param4Type, Param4Value, Param5Type, Param5Value)
        self.node.send_payload(payload)
        packet = self._await_packet(ReplyProcedureCall, timeout_ms=1000)
        return packet

    def packet_available(self) -> bool:
        return self.node.packet_available()

    def get_packet(self) -> Optional[Packet]:
        """ For specialized devices, this is where we reinterpret UndefinedPayloads as
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

    def stop(self):
        self.start_time = None

    def expired(self):
        if self.start_time is None:
            return False

        return (time.time_ns() // 1_000_000) - self.start_time >= self.duration
