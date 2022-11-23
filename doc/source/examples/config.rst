********************
Device configuration
********************

Read from device
================

.. code-block::

    # Read configuration from device
    cfg = dev.config.read_all()

    # Print all parameters
    for category in cfg:
        for parameter in category['parameters']:
            print(parameter)

Write to device
===============


Output to a file
================

JSON
----
.. code-block::

    import json

    cfg = dev.config.read_all()

    with open("config.json", "w") as outfile:
        json.dump(cfg, outfile, indent=4)


Load from a file
================
.. code-block::

    import json

    with open("config.json", "w") as infile:
        cfg = json.load(infile)
