mergepurge
==========

mergepurge is a package of convenience functions for working with Pandas DataFrames of contact and account data. 
It provides high level methods for merging partial records and purging duplicates.

Requirements
------------

- **Python 3** (3.4 if you want to actively retrain the parsers in the usaddress and probablepeople packages with your own data)
- setup.py will automatically install the following if not present:
    - pandas
    - numpy
    - usaddress
    - probablepeople
    - fuzzywuzzy

Install
-------

<s>Pip</s> (not on PYPI yet)  
Use [pip](http://pip.readthedocs.org/en/latest/quickstart.html), a python package manager ([beginner's guide here](http://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python/)) and a virtual environment.

Manually with Git

.. code:: bash

    git clone https://github.com/mikecunha/mergepurge.git mergepurge
    cd mergepurge
    python setup.py install


Usage
-----

.. code:: python

    >>> from mergepurge import clean, match

Build a standardized set of columns to use for matching

.. code:: python

    >>> import pandas as pd
    >>> contacts = pd.read_csv('data.csv')
    >>> contacts = clean.build_matching_cols(contacts,
    ...                                      ['address', 'city', 'ST', 'zip'],
    ...                                      ['firstname', 'lastname'],
    ...                                      ['company'])


