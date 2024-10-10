import amfiprot


def main():
    conn = amfiprot.USBConnection()
    nodes = conn.find_nodes()

    if len(nodes) == 0:
        raise ConnectionError("No nodes found!")

    dev = amfiprot.Device(nodes[0])
    conn.start()

    print(f"Updating firmware for {dev.name()}...")

    dev.update_firmware("Amfitrack2_Sensor_H7_103.bin", print_progress=True)
    print("Done")

    conn.stop()


if __name__ == '__main__':
    main()
