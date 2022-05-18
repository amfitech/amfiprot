# Amfiprot Python library

This is a Python library used to interact with products implementing the Amfiprot protocol.



## Code guidelines

Use [PEP8 Style Guide](https://peps.python.org/pep-0008/). PyCharm has built-in PEP8 syntax check.





## Developer installation

After cloning the repo, create a virtual environment and activate it:

```shell
python -m venv .\venv
.\venv\Scripts\activate.bat
```

In the virtual environment install packages from `requirements.txt` and then install the `amfitrack` package itself with the 'editable' option:

```shell
pip install -r requirements.txt
pip install -e .
```


## User installation

`pip install -U amfiprot`
