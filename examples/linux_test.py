import amfiprot
import time

if __name__ == '__main__':
    conn = amfiprot.UsbConnection(0xc17, 0xd12)
    nodes = conn.find_nodes()
    dev = amfiprot.Device(nodes[0])
    conn.start()

    # print(dev.name())
    # print(dev.read_config())

    start = time.time()

    while True: #time.time() - start < 60:
        packet = dev.get_packet()

        if packet is not None:
            print(".", end="")
        # # else:
        # #     print("-", end="")

    conn.stop()
