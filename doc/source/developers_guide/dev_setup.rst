*****************************
Development environment setup
*****************************

.. admonition:: Tip

    It is highly recommended to use PyCharm as your IDE, because it is specifically made for Python and thus has
    excellent code completion, real-time syntax checking and makes it easier to work with a virtual environment.

After cloning the repository, create a virtual environment and activate it:

.. code-block::

    python -m venv .\venv
    .\venv\Scripts\activate.bat

With virtual environment activated, install all packages from :code:`requirements.txt` and then install the :code:`amfiprot`
package itself with the 'editable' option:

.. code-block::

    pip install -r requirements.txt
    pip install -e .

Now you can edit the source code and try out the changes immediately in your virtual environment without needing to
reinstall the package every time.