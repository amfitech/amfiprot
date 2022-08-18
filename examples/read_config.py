import json
import amfiprot


def main():
    conn = amfiprot.UsbConnection(0xc17, 0xd12)
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

    device_name = dev.name()
    print(f"Device name: {device_name}\n")

    fw_version = dev.firmware_version()
    print(f"Firmware version: {fw_version['major']}.{fw_version['minor']}.{fw_version['patch']}.{fw_version['build']}")

    config = dev.read_config()
    for category in config:
        for parameter in category['parameters']:
            print(parameter)

    # Write to JSON file
    with open('read.json', 'w', encoding='utf8') as out_file:
        json.dump(config, out_file, indent=4)

    # Read from JSON file and write to target
    # with open('new_config.json', 'r', encoding='utf8') as in_file:
    #     new_config = json.load(in_file)
    #     dev.write_config(new_config)

    conn.stop()
    return 0


if __name__ == '__main__':
    main()
