import array
import usb.core
import usb.util
import multiprocessing as mp
import time
from abc import ABC, abstractmethod
from typing import List
from .packet import Packet
from .common_payload import RequestDeviceIdPayload, ReplyDeviceIdPayload
from .node import Node

USB_HID_REPORT_LENGTH = 64


class Connection(ABC):
    @abstractmethod
    def find_nodes(self) -> List[Node]:
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def enqueue_packet(self, packet: Packet):
        pass


class UsbConnection(Connection):
    def __init__(self, app_specific_payload_types: dict = None):
        usb_devices = get_amfitrack_devices()
        if len(usb_devices) > 0:
            self.usb_device = usb_devices[0]
            self.usb_device.set_configuration()
        else:
            raise ConnectionError("No devices detected")

        self.receive_process: mp.Process = None
        self.transmit_process: mp.Process = None
        self.nodes: List[Node] = []
        self.transmit_queue: mp.Queue = mp.Queue()

    def find_nodes(self) -> List[Node]:
        # Create 'request device id' packet
        payload = RequestDeviceIdPayload()
        packet = Packet.from_payload(payload, destination_id=255)  # TODO: Make enum for destination BROADCAST and PC

        # Send packet via USB
        bytes_to_transmit: array.array = array.array('B', [1])  # USB header Report ID, packet length only required on IN packets (???)
        bytes_to_transmit.extend(packet.to_bytes())

        while len(bytes_to_transmit) < 64:
            bytes_to_transmit.append(0)


        self.usb_device.write(0x1, bytes_to_transmit, 1000)

        start_time = time.time()

        rx_packets = []
        while time.time() - start_time < 1:
            try:
                data = self.usb_device.read(0x81, 64)
            except usb.core.USBTimeoutError:
                pass
            rx_packet = Packet(data[2:])

            if type(rx_packet.payload) == ReplyDeviceIdPayload:
                rx_packets.append(rx_packet)

        for packet in rx_packets:
            if type(packet.payload) == ReplyDeviceIdPayload:
                uuids = [node.uuid for node in self.nodes]
                if packet.payload.uuid not in uuids:
                    node = Node(tx_id=packet.payload.tx_id, uuid=packet.payload.uuid, connection=self)
                    self.nodes.append(node)

        return self.nodes

    def enqueue_packet(self, packet: Packet):
        self.transmit_queue.put(packet)

    def start(self):
        # Create tx process
        self.transmit_process = mp.Process(target=transmit_usb_packets, args=(self.transmit_queue,))
        self.transmit_process.start()

        # Create rx process
        tx_ids = [node.tx_id for node in self.nodes]
        rx_queues = [node.receive_queue for node in self.nodes]

        self.receive_process = mp.Process(target=receive_usb_packets, args=(tx_ids, rx_queues))
        self.receive_process.start()

    def stop(self):
        if self.receive_process.is_alive():
            self.receive_process.terminate()
            self.receive_process.join()

        if self.transmit_process.is_alive():
            self.transmit_process.terminate()
            self.transmit_process.join()

    def __str__(self):
        # print(device)
        bus = self.usb_device.bus
        address = self.usb_device.address

        vendor_id = self.usb_device.idVendor
        product_id = self.usb_device.idProduct

        manufacturer_string_index = self.usb_device.iManufacturer
        product_string_index = self.usb_device.iProduct
        serial_number_string_index = self.usb_device.iSerialNumber

        manufacturer = usb.util.get_string(self.usb_device, manufacturer_string_index)
        product = usb.util.get_string(self.usb_device, product_string_index)
        serial_number = usb.util.get_string(self.usb_device, serial_number_string_index)

        return f"Found {product} ({manufacturer}) on bus {bus} address {address}. VID={vendor_id},"\
               f" PID={product_id}, SN={serial_number}"


def receive_usb_packets(tx_ids, rx_queues: List[mp.Queue]):
    print(f"Receive process started! {len(tx_ids)} node(s) registered.")

    devices = get_amfitrack_devices()
    if len(devices) < 1:
        raise ConnectionError("No devices found!")

    dev = devices[0]

    while True:
        try:
            rx_data = dev.read(0x81, USB_HID_REPORT_LENGTH, 1000)
        except usb.core.USBTimeoutError:
            continue

        rx_packet = Packet(rx_data[2:])

        for index, tx_id in enumerate(tx_ids):
            if tx_id == rx_packet.source_id:
                rx_queues[index].put(rx_packet)


def transmit_usb_packets(tx_queue: mp.Queue):
    print("Transmit process started!")

    devices = get_amfitrack_devices()
    if len(devices) < 1:
        raise ConnectionError("No devices found!")

    dev = devices[0]

    while True:
        tx_packet = tx_queue.get(block=True)

        byte_data = array.array('B', [1])
        byte_data.extend(tx_packet.to_bytes())
        byte_data.extend([0] * (64 - len(byte_data)))
        dev.write(0x01, byte_data)


def get_amfitrack_devices():
    device_list = []

    devices = usb.core.find(find_all=True, idVendor=0x0C17, idProduct=0x0D12)

    if devices is None:
        raise ValueError('Device is not found')

    for device in devices:
        device_list.append(device)

    return device_list
