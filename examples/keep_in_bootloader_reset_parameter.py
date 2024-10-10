import hid
import amfiprot
import amfiprot_amfitrack as amfitrack
import array

if __name__ == '__main__':
    # Define your vendor ID and product ID
    vendor_id = 0x0C17
    product_id = 0x0D12 # Sensor
    # product_id = 0x0D01 # Source

    # Loop until a device is found
    device = None
    while device is None:
        # Get the list of all devices matching this vendor ID and product ID
        device_list = hid.enumerate(vendor_id, product_id)

        # Find the first device that matches
        for d in device_list:
            if d['vendor_id'] == vendor_id and d['product_id'] == product_id:
                # Open the device by path
                device = hid.device()
                device.open_path(d['path'])
                print("device found")
                break


    # Send and receive messages as before
    payload = amfiprot.common_payload.RequestFirmwareVersionPayload()
    print(payload.to_bytes())
    packet = amfiprot.Packet.from_payload(payload, 255).to_bytes()
    new_byte = b'\x01'
    new_packet = array.array('B', new_byte) + packet
    print(new_packet)
    # message = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]

    # device.write(new_packet)
    device.close()

    device = None
    while device is None:
        # Get the list of all devices matching this vendor ID and product ID
        device_list = hid.enumerate(vendor_id, product_id)

        # Find the first device that matches
        for d in device_list:
            if d['vendor_id'] == vendor_id and d['product_id'] == product_id:
                # Open the device by path
                device = hid.device()
                device.open_path(d['path'])
                print("device found")
                break


    # Send and receive messages as before
    # ResetParameterPayload(171 == Reset to compiled default / !171 == Factory default)
    payload = amfiprot.common_payload.ResetParameterPayload(5)
    print(payload)
    packet = amfiprot.Packet.from_payload(payload).to_bytes()
    new_byte = b'\x01'
    new_packet = array.array('B', new_byte) + packet
    print(new_packet)
    device.write(new_packet)
    device.close()