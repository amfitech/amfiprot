import amfiprot


def main():
    conn = amfiprot.UsbConnection()
    nodes = conn.find_nodes()

    if len(nodes) == 0:
        raise ConnectionError("No devices found!")

    print("Found nodes:")
    for node in nodes:
        print(node)
    print("")

    dev = amfiprot.Device(nodes[0])

    print(f"Connected to device with ID: {dev.tx_id}")

    conn.start()
    device_name = dev.read_device_name()
    print(f"Device name: {device_name}\n")

    num_categories = dev.read_category_count()
    print(f"Reading {num_categories} configuration categories...\n")

    for category in range(num_categories):
        category_name = dev.read_config_category(category)
        config_value_count = dev.read_config_value_count(category)

        print(f"#{category}: {category_name} ({config_value_count} parameters)")
        print("------------------------")

        for param in range(config_value_count):
            name, uid = dev.read_config_name_and_uid(category, param)
            value = dev.read_config_value(uid)
            print(f"[{uid}] {name} = {value}")

        print("")

    conn.stop()


if __name__ == '__main__':
    main()
