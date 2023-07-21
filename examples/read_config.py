import amfiprot

if __name__ == '__main__':
    physical_devices = amfiprot.USBConnection.discover()
    conn = None

    for dev in physical_devices:
        #print(dev)
        if "amfitrack" in dev['product'].lower():
            conn = amfiprot.USBConnection(dev['vid'], dev['pid'])
            if (conn):
                nodes = conn.find_nodes()

                print("USB device: {} ({})".format(conn.usb_device.product, conn.usb_device.serial_number))
                if len(nodes) < 1:
                    print("  No nodes found.")
                
                for node in nodes:
                    dev = amfiprot.Device(node)
                    conn.start()

                    cfg = dev.config.read_all()
                    for category in cfg:
                        print("  {}".format(category['name']))
                        for item in category['parameters']:
                            print("    {} = {}".format(item['name'], item['value']))
                print()

    if conn is None:
        raise ConnectionError("No Amfitrack devices found on USB.")


    # Changing a parameter can be done by:

    # for param in cfg:
    #     if param['uid'] == 1651667736:    # RF hub
    #         param['value'] = not param['value']
    #         break

    #dev.config.write_all(cfg)