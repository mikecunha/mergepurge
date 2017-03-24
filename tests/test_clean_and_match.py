import os
import pytest
from mergepurge import clean, match
import pandas as pd
import numpy as np


COMP_PATH = os.path.join('tests', 'complete_parsed.tsv')
COMP_DTYPES = {'aa_streetnum': str, 'aa_zip': str, 'zipcode': str}
complete = pd.read_csv(COMP_PATH, sep='\t', encoding='utf-8', dtype=COMP_DTYPES)

COMP_LOC_COLS     = ['address', 'city', 'state', 'zipcode']
COMP_CONTACT_COLS = ['first', 'last']
COMP_COMPANY_COLS = ['company']
BUILT_COLS        = [col for col in complete.columns if col.startswith('aa_')]

PARTIAL_PATH = os.path.join('tests', 'incomplete.tsv')
PARTIAL_DTYPES = {'aa_streetnum': str, 'aa_zip': str, 'zipcode': str}
partial = pd.read_csv(PARTIAL_PATH, sep='\t', encoding='utf-8', dtype=PARTIAL_DTYPES)

PART_LOC_COLS     = ['address', 'city', 'state', 'zipcode']
PART_CONTACT_COLS = ['first', 'last']
PART_COMPANY_COLS = ['company']

# #################  Test clean.py  ################ #

trecords = [row for (index, row) in complete.iterrows()]


@pytest.mark.parametrize('test_record', trecords)
def test_clean_contact_name(test_record):
    known = (test_record.get('aa_title', np.nan), test_record.get('aa_firstname', np.nan),
             test_record.get('aa_lastname', np.nan), test_record.get('aa_fullname', np.nan))
    parsed = clean.parse_contact_name(test_record, COMP_CONTACT_COLS, strict=False)
    assert parsed == known


@pytest.mark.parametrize('test_record', trecords)
def test_parse_location_cols(test_record):
    known = (test_record.get('aa_streetnum', np.nan), test_record.get('aa_street', np.nan),
             test_record.get('aa_city', np.nan), test_record.get('aa_state', np.nan),
             test_record.get('aa_zip', np.nan), test_record.get('aa_fulladdy', np.nan))
    parsed = clean.parse_location_cols(test_record, COMP_LOC_COLS, strict=False)
    assert parsed == known


@pytest.mark.parametrize('test_record', trecords)
def test_parse_business_name(test_record):
    known = test_record.get('aa_company', np.nan)
    parsed = clean.parse_business_name(test_record, COMP_COMPANY_COLS, strict=False)
    assert parsed == known


def test_build_matching_cols():
    known = complete[BUILT_COLS].head(10).copy()
    built = clean.build_matching_cols(complete.head(10).copy(),
                                      COMP_LOC_COLS,
                                      COMP_CONTACT_COLS,
                                      COMP_COMPANY_COLS)
    assert all(built[BUILT_COLS] == known)


# ################  Test match.py  ################# #

partial_parsed  = clean.build_matching_cols(partial.copy(),
                                            PART_LOC_COLS,
                                            PART_CONTACT_COLS,
                                            PART_COMPANY_COLS)
related_records = match.find_related(partial_parsed, complete)
partial_parsed['matching_record'] = [sin_ind for (mtype, sfor_ind, sin_ind) in related_records]

part_records = [row for (index, row) in partial_parsed.iterrows()]


@pytest.mark.parametrize('row', part_records)
def test_find_related(row):

    # Accept int or comma-delimted string as input
    known = set(str(row.get('ID', '')).split(','))
    known = {int(ind) for ind in known}

    found = set(row.get('matching_record', ''))
    print('Searching for partial record:')
    print(row)
    print('\nKnown to match index {}, found {}'.format(str(known), str(found)))

    assert known == found
