import array
import usb.core
import usb.util
import multiprocessing as mp
import time
import crcmod
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
from .packet import Packet, PacketDestination
from .common_payload import RequestDeviceIdPayload, ReplyDeviceIdPayload
from .node import Node
from .device import MilliTimer

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

class DeviceNotFoundError(ConnectionError):
    pass


class UsbConnection(Connection):
    MAX_PAYLOAD_SIZE = 54  # 1 byte needed for CRC

    def __init__(self, vendor_id: int, product_id: int, serial_number: int = None):  # Cannot just pass the usb.core.Device, because we need to be able to re-establish connection if the device is temporarily lost
        """ If no serial number is given, the first device that matches vendor_id and product_id is used.
        If no product_id is given, the first device that matches vendor_id is used. """
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.usb_serial_number = serial_number

        self.usb_device = get_matching_device(vendor_id, product_id, serial_number)

        if self.usb_device is None:
            raise ConnectionError("Could not connect to device!")

        self.receive_process: mp.Process
        self.transmit_process: mp.Process
        self.nodes: List[Node] = []
        self.transmit_queue: mp.Queue = mp.Queue()
        self.global_receive_queue: mp.Queue = mp.Queue()

    def __del__(self):
        try:
            self.stop()
        except AttributeError:
            pass  # Processes not started

    @classmethod
    def scan_physical_devices(cls):
        devices = usb.core.find(find_all=True)
        device_list = []

        for device in devices:
            try:
                if device.manufacturer is None or device.product is None:
                    raise ValueError("Unknown device")

                try:
                    serial_number = device.serial_number
                except Exception:
                    serial_number = None

                device_info = {'vid': device.idVendor, 'pid': device.idProduct, 'manufacturer': device.manufacturer, 'product': device.product, 'serial_number': serial_number}
                device_list.append(device_info)
            except Exception:
                continue

        return device_list

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
        usb_device_hash = generate_device_hash(self.usb_device)

        # Create tx process
        self.transmit_process = mp.Process(target=transmit_usb_packets, args=(usb_device_hash, self.transmit_queue))
        self.transmit_process.start()

        # Create rx process
        tx_ids = [node.tx_id for node in self.nodes]
        rx_queues = [node.receive_queue for node in self.nodes]

        self.receive_process = mp.Process(target=receive_usb_packets, args=(usb_device_hash, tx_ids, rx_queues, self.global_receive_queue))
        self.receive_process.start()
        time.sleep(1)  # To allow processes to start up

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


def receive_usb_packets(usb_device_hash, tx_ids, rx_queues: List[mp.Queue], global_receive_queue: mp.Queue):
    IN_ENDPOINT = 0x81

    print(f"Receive process started! {len(tx_ids)} node(s) registered.")

    dev = get_usb_device_by_hash(usb_device_hash)

    while True:
        if dev is None:
            dev = get_usb_device_by_hash(usb_device_hash)
            time.sleep(1)
            continue

        try:
            rx_data = dev.read(IN_ENDPOINT, USB_HID_REPORT_LENGTH, 1000)
        except usb.core.USBTimeoutError:
            continue
        except usb.core.USBError:
            dev = None
            continue

        rx_packet = Packet(rx_data[2:])
        #print(rx_packet)

        # if not rx_packet.crc_is_good():
        #     print("Packet CRC check failed!")

        global_receive_queue.put_nowait(rx_packet)

        for index, tx_id in enumerate(tx_ids):
            if tx_id == rx_packet.source_id:
                rx_queues[index].put_nowait(rx_packet)


def transmit_usb_packets(usb_device_hash, tx_queue: mp.Queue):
    OUT_ENDPOINT = 0x01

    print("Transmit process started!")

    # Connect to device
    dev = get_usb_device_by_hash(usb_device_hash)

    # Process outgoing packets
    while True:
        if dev is None:
            # Try reconnect
            dev = get_usb_device_by_hash(usb_device_hash)
            time.sleep(1)
            continue

        tx_packet = tx_queue.get(block=True)

        # print("Sending: " + str(tx_packet))

        byte_data = array.array('B', [1])
        byte_data.extend(tx_packet.to_bytes())
        byte_data.extend([0] * (64 - len(byte_data)))
        try:
            bytes_written = dev.write(OUT_ENDPOINT, byte_data)
        except usb.core.USBError:  # TODO: Check disconnect in some other way before getting from tx_queue, because this drops packets!
            dev = None

def connect_usb(vendor_id, product_id, serial_number = None):
    for i in range(3):
        try:
            devices = get_usb_devices(vendor_id, product_id)

            if len(devices) > 0:
                break
            else:
                time.sleep(1)
                continue

        except ValueError:
            print("Device not found. Retrying in 1 sec...")
            time.sleep(1)

    if len(devices) < 1:
        raise ConnectionError("Could not reconnect")

    dev = devices[0]
    dev.set_configuration()
    return dev



def get_usb_devices(vendor_id, product_id):
    return list(usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id))

def get_serial_number(device: usb.core.Device) -> int:
    return usb.util.get_string(device, device.iSerialNumber)

def get_matching_device(vendor_id, product_id, serial_number) -> usb.core.Device:
    device = usb.core.find(idVendor=vendor_id, idProduct=product_id)

    if device is None:
        raise ConnectionError("No match!")

    if serial_number is not None:
        current_serial = device.serial_number
        if current_serial == serial_number:
            return device
    else:
        return device

    return None

def generate_device_hash(device: usb.core.Device) -> str:
    string_to_hash = str(device.idVendor) + str(device.idProduct) + str(device.manufacturer) + str(device.product) + str(device.serial_number)
    encoded_string = string_to_hash.encode('utf-8')

    hash = hashlib.md5()
    hash.update(encoded_string)
    return hash.hexdigest()

def get_usb_device_by_hash(hash: str) -> Optional[usb.core.Device]:
    devices = list(usb.core.find(find_all=True))

    if len(devices) > 0:
        for device in devices:
            try:
                current_hash = generate_device_hash(device)
            except ValueError:
                continue
            except NotImplementedError:
                continue

            if hash == current_hash:
                return device

    return None
