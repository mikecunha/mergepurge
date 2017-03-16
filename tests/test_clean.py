from mergepurge import clean
import pandas as pd
import numpy as np

t_data = pd.Series({'name': 'Timothy Testerosa III'})
t_parsed = (np.nan, 'Timothy', 'Testerosa', 'Timothy Testerosa')

# FIXME - load a csv file with a name column and the 4 correctly parsed name parts as 4 other cols
# Then, iterate over the names


def test_clean_contact_name():
    assert clean.parse_contact_name(t_data, ['name'], False) == t_parsed
