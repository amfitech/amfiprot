import amfiprot

VENDOR_ID = 0xC17
PRODUCT_ID_SENSOR = 0xD12
PRODUCT_ID_SOURCE = 0xD01

def main():
    conn = amfiprot.USBConnection(VENDOR_ID, PRODUCT_ID_SOURCE)
    conn.start()

    while True:
        if conn.global_receive_queue.qsize() > 0:
            packet = conn.global_receive_queue.get()
            print(packet)

    conn.stop()


if __name__ == '__main__':
    main()
    