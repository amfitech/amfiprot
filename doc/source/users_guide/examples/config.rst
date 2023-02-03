********************
Device configuration
********************

Read from device
----------------
Entire configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the configuration will be split into categories:

.. code-block::

    cfg = dev.config.read_all()

    # Print all parameters
    for category in cfg:
        for parameter in category['parameters']:
            print(parameter)

It is also possible to get the configuration as a flat list of parameters:

.. code-block::

    cfg = dev.config.read_all(flat_list=True)

    # Print all parameters
    for parameter in cfg:
        print(parameter)

Single parameter
^^^^^^^^^^^^^^^^

.. code-block::

    uid = 31415926

    param = dev.config.read(uid)


Write to device
---------------
Entire configuration
^^^^^^^^^^^^^^^^^^^^
.. code-block::

    # "cfg" can be either a flat_list or sorted by category
    dev.config.write_all(cfg)

Single parameter
^^^^^^^^^^^^^^^^
.. code-block::

    uid = 31415926
    new_value = 2.0

    dev.config.write(uid, value)

Output to a file
----------------

JSON
^^^^
.. code-block::

    import json

    cfg = dev.config.read_all()

    with open("config.json", "w") as outfile:
        json.dump(cfg, outfile, indent=4)

Load from a file
----------------
JSON
^^^^

.. code-block::

    import json

    with open("config.json", "w") as infile:
        cfg = json.load(infile)

