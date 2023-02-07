Building and publishing the package
===================================

Building a new distribution
---------------------------
Before building a new distribution, make sure to update the version number in :code:`src/amfiprot/__init__.py`. Both the
build script and the documentation will fetch the version number from here.

After updating the version number, run the build script :code:`build.bat` and you should then see a new :code:`.whl`
and :code:`.tar.gz` file in the :code:`dist/` folder. These are the files you will publish to PyPI.

Publishing to PyPI
------------------
Publishing the distribution to PyPI is done using `Twine <https://pypi.org/project/twine/>`_ which must be installed
first:

.. code-block::

    pip install twine

If the two newly created distribution files are the only files present in :code:`dist/`, you can publish them with:

.. code-block::

    python -m twine upload dist/*

Otherwise, you have to specify the filenames individually.