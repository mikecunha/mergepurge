mergepurge
==========

``import mergepurge as mp``

This is a package of convenience functions for working with Pandas DataFrames of contact and account data. 
It provides high level functions for preprocessing contact information, finding related records, and merging partial records. In the future it will also facilitate purging duplicates.

Pandas makes it very easy to load a new DataFrame with a list of contacts from most file/data formats. 
This package aims to make it easy to quickly preprocess that DataFrame and compare it to other lists of contacts or accounts with only vague requirements on input data-structure and formatting.  

The code here stems from code I have written repeatedly in Jupyter notebooks as preprocessing steps to clean up client data.

Functions and Roadmap
---------------------

The currently implemented high-level methods include:

**preprocessing contact info**  
``mp.clean.build_matching_cols()`` will standardize address, human names, and business names with a series of preprocessing steps and output a standard set of columns (prefixed with '``aa_``') that can be used as input to ``find_related()``.


**finding matches**  
``mp.match.find_related()`` uses a fixed algorithm of fuzzy and exact comparisons on a combo of fields (hand-coded decision tree) to find related contact or account records. I plan on adding an array of additional matching algorithms to choose from that will allow you to select the best one for your specific data.

**merging records**  
``mp.match.merge_lists()`` adds the chosen columns of one DataFrame to the matching records of another DataFrame. In the future I plan on adding "upsert" <en\.wikipedia\.org/wiki/Merge\_\(SQL\)\#Synonymous> and more complicated joins to let you specify how to handle one-to-many and many-many relationships between DataFrames.

In the mean-time, ``build_matching_cols()`` and some other lower-level functions in this package can help you quickly get to a point where you are ready to experiment with your own matching and merging code:

Requirements
------------

**Python 3** (3.4 if you want to use the probableparser command-line tool to actively retrain the parsers in the usaddress and probablepeople packages with your own data)

setup.py will automatically install the following if not present

- pandas
- numpy
- usaddress
- probablepeople
- fuzzywuzzy

Install
-------

Manually with Git

.. code:: bash

    git clone https://github.com/mikecunha/mergepurge.git mergepurge
    cd mergepurge
    python setup.py install


Usage
-----

.. code:: python

    >>> import mergepurge as mp

Build a standardized set of columns to use for matching

.. code:: python

    >>> import pandas as pd
    >>> contacts = pd.read_csv('data.csv')
    >>> contacts = mp.clean.build_matching_cols(contacts,
    ...                                         ['address', 'city', 'ST', 'zip'],
    ...                                         ['firstname', 'lastname'],
    ...                                         ['company'])



