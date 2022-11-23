************************************
Setting up a development environment
************************************

For developers
--------------
After cloning the repository, create a virtual environment and activate it:

.. code-block::

    python -m venv .\venv
    .\venv\Scripts\activate.bat

In the virtual environment, install packages from `requirements.txt` and then install the `amfiprot` package itself
with the 'editable' option:

.. code-block::

    pip install -r requirements.txt
    pip install -e .

Now you can edit the source code and try out the changes immediately in your virtual environment without needing to
reinstall the package.