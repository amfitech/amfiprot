Updating firmware
=================

Sending a firmware binary to an Amfiprot device is as simple as giving the path to the binary:

.. code-block::

    firmware_path = 'my_firmware.bin'
    dev.update_firmware(firmware_path, print_progress=True)


.. admonition:: Note

    AmfiTrack devices will only accept :emphasis:`signed` binaries.

If firmware update was successful, the device will automatically reboot.