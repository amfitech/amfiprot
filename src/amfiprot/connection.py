import array
import usb.core
import usb.util
import multiprocessing as mp
import time
import crcmod
from abc import ABC, abstractmethod
from typing import List
from .packet import Packet, PacketDestination
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

    @abstractmethod
    def max_payload_size(self) -> int:
        pass


class UsbConnection(Connection):
    MAX_PAYLOAD_SIZE = 54  # 1 byte needed for CRC

    def __init__(self, vendor_id: int = 0x0C17, product_id: int = 0x0D12):
        self.vendor_id = vendor_id
        self.product_id = product_id

        usb_devices = get_usb_devices(vendor_id, product_id)
        if len(usb_devices) > 0:
            self.usb_device = usb_devices[0]
            self.usb_device.set_configuration()
        else:
            raise ConnectionError("No devices detected")

        self.receive_process: mp.Process = None
        self.transmit_process: mp.Process = None
        self.nodes: List[Node] = []
        self.transmit_queue: mp.Queue = mp.Queue()
        self.global_receive_queue: mp.Queue = mp.Queue()

    def __del__(self):
        self.stop()

    def find_nodes(self) -> List[Node]:
        # Create 'request device id' packet
        payload = RequestDeviceIdPayload()
        packet = Packet.from_payload(payload, destination_id=PacketDestination.BROADCAST)

        # Send packet via USB
        bytes_to_transmit: array.array = array.array('B', [1])  # USB header Report ID, packet length only required on IN packets (???)
        bytes_to_transmit.extend(packet.to_bytes())

        while len(bytes_to_transmit) < 64:
            bytes_to_transmit.append(0)

        self.usb_device.write(0x1, bytes_to_transmit, 1000)

        start_time = time.time()

        rx_packets = []
        while time.time() - start_time < 1:
            data = None

            try:
                data = self.usb_device.read(0x81, 64)
            except usb.core.USBTimeoutError:
                pass

            if data is None:
                continue

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

    def max_payload_size(self) -> int:
        return self.MAX_PAYLOAD_SIZE

    def start(self):
        # Create tx process
        self.transmit_process = mp.Process(target=transmit_usb_packets, args=(self.vendor_id, self.product_id, self.transmit_queue))
        self.transmit_process.start()

        # Create rx process
        tx_ids = [node.tx_id for node in self.nodes]
        rx_queues = [node.receive_queue for node in self.nodes]

        self.receive_process = mp.Process(target=receive_usb_packets, args=(self.vendor_id, self.product_id, tx_ids, rx_queues, self.global_receive_queue))
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


def receive_usb_packets(vendor_id, product_id, tx_ids, rx_queues: List[mp.Queue], global_receive_queue: mp.Queue):
    print(f"Receive process started! {len(tx_ids)} node(s) registered.")

    devices = get_usb_devices(vendor_id, product_id)
    if len(devices) < 1:
        raise ConnectionError("No devices found!")

    dev = devices[0]

    while True:
        try:
            rx_data = dev.read(0x81, USB_HID_REPORT_LENGTH, 1000)
        except usb.core.USBTimeoutError:
            continue

        rx_packet = Packet(rx_data[2:])
        # print(rx_packet)

        # TODO: Check CRC of header and payload
        if not rx_packet.header_crc_good():
            print("Header CRC check failed!")

        if not rx_packet.payload_crc_good():
            print("Payload CRC check failed!")

        global_receive_queue.put(rx_packet)

        for index, tx_id in enumerate(tx_ids):
            if tx_id == rx_packet.source_id:
                rx_queues[index].put(rx_packet)


def transmit_usb_packets(vendor_id, product_id, tx_queue: mp.Queue):
    print("Transmit process started!")

    devices = get_usb_devices(vendor_id, product_id)
    if len(devices) < 1:
        raise ConnectionError("No devices found!")

    dev = devices[0]

    while True:
        tx_packet = tx_queue.get(block=True)

        # print("Sending: " + str(tx_packet))

        byte_data = array.array('B', [1])
        byte_data.extend(tx_packet.to_bytes())
        byte_data.extend([0] * (64 - len(byte_data)))
        # bytes_written = dev.write(0x01, byte_data)
        # print(f"{bytes_written} bytes sent.")


def get_usb_devices(vendor_id, product_id):
    device_list = []

    devices = usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id)

    if devices is None:
        raise ValueError('Device is not found')

    for device in devices:
        device_list.append(device)

    return device_list
