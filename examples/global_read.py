import amfiprot


def main():
    conn = amfiprot.UsbConnection()
    conn.start()

    while True:
        if conn.global_receive_queue.qsize() > 0:
            packet = conn.global_receive_queue.get()
            print(packet)

    conn.stop()


if __name__ == '__main__':
    main()
    