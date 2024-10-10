import array
import sys
import serial
import serial.tools.list_ports
import multiprocessing as mp
import time
import hashlib
import enum
import atexit
from typing import List, Optional
from cobs import cobs
from .packet import Packet, PacketDestination
from .common_payload import RequestDeviceIdPayload, ReplyDeviceIdPayload, RequestDeviceNamePayload, ReplyDeviceNamePayload
from .node import Node
from .connection import Connection

class UARTConnection(Connection):
    """An implementation of :class:`amfiprot.Connection` used to connect to UART devices."""
    MAX_PAYLOAD_SIZE = 54  # 1 byte needed for CRC

    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_device = get_matching_device(port, baudrate)

        if self.serial_device is None:
            raise ConnectionError("Could not connect to device!")

        self.receive_process: mp.Process = None
        self.transmit_process: mp.Process = None
        self.uart_task: mp.Process = None
        self.nodes: List[Node] = []
        self.transmit_queue: mp.Queue = mp.Queue()
        self.global_receive_queue: mp.Queue = mp.Queue()
        self.uart_connection_lost: mp.Event = mp.Event()
        self.node_update_queue: mp.Queue = mp.Queue()
        

    def __del__(self):
        try:
            self.stop()
        except AttributeError:
            pass  # Processes not started

    @classmethod
    def discover(cls):
        ports = serial.tools.list_ports.comports()
        device_list = []

        for port in ports:
            device_info = {
                'port': port.device,
                'description': port.description,
                'hwid': port.hwid
            }
            device_list.append(device_info)

        return device_list

    def find_nodes(self) -> List[Node]:
        payload = RequestDeviceIdPayload()
        packet = Packet.from_payload(payload, destination_id=PacketDestination.BROADCAST)

        bytes_to_transmit: array.array = array.array('B')
        bytes_to_transmit.extend(packet.to_bytes())
        cobs_encoded = cobs.encode(bytes(bytes_to_transmit)) + b'\x00'

        self.serial_device.write(cobs_encoded)

        start_time = time.time()

        rx_packets = []
        while time.time() - start_time < 1:
            if self.serial_device.in_waiting > 0:
                data = self.serial_device.read_until(b'\x00')
                try:
                    cobs_decoded = cobs.decode(data[:-1])
                    arr = array.array('B') 
                    arr.frombytes(cobs_decoded)
                    rx_packet = Packet(arr)
                    if type(rx_packet.payload) == ReplyDeviceIdPayload:
                        rx_packets.append(rx_packet)
                except:
                    pass
                    #print("UART package error")

        nodes = []

        for packet in rx_packets:
            if type(packet.payload) == ReplyDeviceIdPayload:
                uuids = [node.uuid for node in nodes]
                if packet.payload.uuid not in uuids:
                    node = Node(tx_id=packet.payload.tx_id, uuid=packet.payload.uuid, connection=self)
                    nodes.append(node)

        for node in nodes:
            payload = RequestDeviceNamePayload()
            packet = Packet.from_payload(payload, destination_id=node.tx_id)

            bytes_to_transmit: array.array = array.array('B')
            bytes_to_transmit.extend(packet.to_bytes())
            cobs_encoded = cobs.encode(bytes(bytes_to_transmit)) + b'\x00'

            self.serial_device.write(cobs_encoded)

            start_time = time.time()

            while time.time() - start_time < 1:
                if self.serial_device.in_waiting > 0:
                    data = self.serial_device.read_until(b'\x00')
                    try:
                        cobs_decoded = cobs.decode(data[:-1])
                        arr = array.array('B') 
                        arr.frombytes(cobs_decoded)
                        rx_packet = Packet(arr)
                        if type(rx_packet.payload) == ReplyDeviceNamePayload:
                            node.name = rx_packet.payload.name
                            break
                    except:
                        pass
                        #print("UART package error")

        if nodes_changed(nodes, self.nodes):
            self.nodes = nodes
            if self.receive_process is not None and self.transmit_process is not None:
                self.stop()
                self.start()

        self.serial_device.close()

        return self.nodes

    def enqueue_packet(self, packet: Packet):
        self.transmit_queue.put(packet)

    def max_payload_size(self) -> int:
        return self.MAX_PAYLOAD_SIZE

    def start(self):
        atexit.register(connection_exit_handler, self)

        tx_ids = [node.tx_id for node in self.nodes]
        rx_queues = [node.receive_queue for node in self.nodes]

        self.uart_task = mp.Process(target=uart_task, args=(self.port, self.baudrate, tx_ids, rx_queues, self.transmit_queue, self.global_receive_queue, self.node_update_queue))
        self.uart_task.start()
        time.sleep(1)  # To allow processes to start up

    def stop(self):
        if self.uart_task is not None:
            if self.uart_task.is_alive():
                time.sleep(1)
                self.uart_task.terminate()
                self.uart_task.join()
                self.serial_device.close()

    def refresh(self):
        tx_ids = [node.tx_id for node in self.nodes]
        self.node_update_queue.put({'tx_ids': tx_ids})

    def __str__(self):
        return f"UART Connection on port {self.port} at baudrate {self.baudrate}"


class ConnectionState(enum.IntEnum):
    INIT = 0
    CONNECTED = 1
    DISCONNECTED = 2


def uart_task(port, baudrate, tx_ids, rx_queues: List[mp.Queue], tx_queue: mp.Queue, global_receive_queue: mp.Queue, node_update_queue: mp.Queue):
    RETRY_LIMIT = 10
    retry_count = 0
    dev = None

    while dev is None:
        try:
            dev = serial.Serial(port, baudrate, timeout=1)
            state = ConnectionState.CONNECTED
        except serial.SerialException:
            retry_count += 1
            if retry_count > RETRY_LIMIT:
                raise ConnectionError("Subprocess could not find device.")
            time.sleep(1)

    tx_ids_local = tx_ids
    rx_queues_local = rx_queues

    while True:
        if state == ConnectionState.CONNECTED:
            while not tx_queue.empty():
                tx_packet = tx_queue.get_nowait()
                byte_data = array.array('B')
                byte_data.extend(tx_packet.to_bytes())
                cobs_encoded = cobs.encode(bytes(byte_data)) + b'\x00'
                try:
                    dev.write(cobs_encoded)
                except serial.SerialException as e:
                    print(f"Could not send packet ({e})")
                    continue

            if not node_update_queue.empty():
                update = node_update_queue.get()
                tx_ids_local = update['tx_ids']

            try:
                if dev.in_waiting > 0:
                    data = dev.read_until(b'\x00')
                    try:
                        cobs_decoded = cobs.decode(data[:-1])
                        arr = array.array('B') 
                        arr.frombytes(cobs_decoded)
                        rx_packet = Packet(arr)
                    
                        if global_receive_queue.full():
                            print("Global receive queue full! Packet discarded.")
                        else:
                            global_receive_queue.put_nowait(rx_packet)

                        index = tx_ids_local.index(rx_packet.source_id)
                        if rx_queues_local[index].full():
                            print(f"RX queue [TxID {tx_ids_local[index]}] full! Packet discarded.")
                        else:
                            rx_queues_local[index].put_nowait(rx_packet)

                    except:
                        pass
                        #print("UART package error")

            except serial.SerialException as e:
                print("UART connection lost.")
                dev.close()
                state = ConnectionState.DISCONNECTED
                continue

        elif state == ConnectionState.DISCONNECTED:
            print("Reconnecting...")
            try:
                dev = serial.Serial(port, baudrate, timeout=1)
                state = ConnectionState.CONNECTED
            except serial.SerialException:
                time.sleep(1)
        else:
            raise ValueError("Invalid state in UART task.")


def get_matching_device(port, baudrate):
    try:
        dev = serial.Serial(port, baudrate, timeout=1)
        return dev
    except serial.SerialException:
        return None


def nodes_changed(list1: List[Node], list2):
    if len(list1) != len(list2):
        return True

    list1.sort(key=lambda x: x.uuid)
    list2.sort(key=lambda x: x.uuid)

    for item1, item2 in zip(list1, list2):
        if item1.uuid != item2.uuid:
            return True

    return False


def connection_exit_handler(connection):
    connection.stop()