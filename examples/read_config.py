import amfiprot

if __name__ == '__main__':
    physical_devices = amfiprot.UsbConnection.discover()
    conn = None

    for dev in physical_devices:
        #print(dev)
        if "amfitrack" in dev['product'].lower():
            conn = amfiprot.UsbConnection(dev['vid'], dev['pid'])

    if conn is None:
        raise ConnectionError("No Amfitrack devices found on USB.")

    nodes = conn.find_nodes()

    if len(nodes) < 1:
        raise ConnectionError("No nodes found.")

    dev = amfiprot.Device(nodes[0])

    conn.start()

    cfg = dev.config.read_all(flat_list=True)

    # for param in cfg:
    #     if param['uid'] == 1651667736:
    #         param['value'] = not param['value']
    #         break

    dev.config.write_all(cfg)

    conn.stop()