import amfiprot
import time

VENDOR_ID = 0xC17
PRODUCT_ID_SENSOR = 0xD12
PRODUCT_ID_SOURCE = 0xD01

if __name__ == '__main__':
    conn = amfiprot.USBConnection(VENDOR_ID, PRODUCT_ID_SENSOR)
    nodes = conn.find_nodes()
    dev = amfiprot.Device(nodes[0])
    conn.start()

    # print(dev.name())
    # print(dev.read_config())

    start = time.time()

    while True: #time.time() - start < 60:
        packet = dev.get_packet()

        if packet is not None:
            print(".", end="", flush=True)
        # # else:
        # #     print("-", end="")

    conn.stop()
