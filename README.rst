mergepurge
==========

``import mergepurge as mp``

This is a package of convenience functions for working with Pandas DataFrames of contact and account data. 
It provides high level functions for preprocessing contact information, finding related records, and merging partial records. In the future it will also facilitate purging duplicates.

Pandas makes it very easy to load a new DataFrame with a list of contacts from most file/data formats. 
This package aims to make it easy to quickly preprocess that DataFrame and compare it to other lists of contacts or accounts with only vague requirements on input data-structure and formatting.  

The code here stems from code I have written repeatedly in Jupyter notebooks as preprocessing steps to clean up client data.

Examples of Vague Input Formats
-------------------------------

All of the following example tables of data should work fine as input.

| Name             | Address 1            | Address 2          | City         | State | Zip    |
| ---------------- | -------------------- | ------------------ | ------------ | ----- | ------ |
| Dr. Leo Spaceman | 30 Rockefeller Plaza | GE Bldg            | New York     | NY    | 10112  |
| Dr. Spaceman     | Attn: Leo            | 30 Rockefeller Plz | New York     | NY    | 10112  |

| name             | address                        | city         | state |
| ---------------- | ------------------------------ | ------------ | ----- |
| Dr. Leo Spaceman | 30 Rockefeller Plaza, GE Bldg  | New York     | NY    |
| Dr Spaceman      | Attn: Leo - 30 Rockefeller Plz | New York     | NY    |

| title  | first_name   | last name | Address                        | City         | State |
| ------ | ------------ | --------- | ------------------------------ | ------------ | ----- |
|        | Leo          | Spaceman  | 30 Rockefeller Plaza, GE Bldg  | New York     | NY    |
|        | Doctor       | spaceman  | Attn: Leo - 30 Rockefeller Plz | New York     | NY    |
| Dr     | notavailable | spaceman  | 30 Rockefeller Plaza           | New York     | NY    |

Notice, not only are there different column names and columns, but there are missing values and pieces of information occuring in the wrong column as well. All of those scenarios should be handled ok as long as mixed up data occurs in the same type of column (location, name, or business name) and you pass the correct order of columns to ``build_matching_cols()``.

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

Check out the Jupyter Notebook ``Usage.ipynb`` in the github repo for a detailed example workflow of
how to use mergepurge.
<https://github.com/mikecunha/mergepurge/blob/master/Usage.ipynb>

An overview of things you can do is as follows:

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

Find matching contacts in another dataframe that already has the matching columns in it

.. code:: python

    >>> related = mp.match.find_related(contacts, other_contacts)

Using those matches, add columns from the other dataframe

.. code:: python

    >>> merged_contacts = mp.match.merge_lists(contacts, other_contacts,
    ...                                        matching_indices=related,
    ...                                        wanted_cols=['email','customer_ID'])

Remove columns built for matching

.. code:: python

    >>> built_cols = [col for col in merged_contacts.columns if col.startswith('aa_')]
    >>> merged_contacts.drop(built_cols, axis=1, inplace=True)
