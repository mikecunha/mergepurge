from mergepurge import clean
import pandas as pd
import numpy as np


complete = pd.read_csv('complete_parsed.tsv',
                       sep='\t', encoding='utf-8',
                       dtype={'aa_streetnum': str, 'aa_zip': str, 'zipcode': str})

COMP_LOC_COLS = ['address', 'city', 'state', 'zipcode']
COMP_CONTACT_COLS = ['first', 'last']
COMP_COMPANY_COLS = ['company']
BUILT_COLS = [col for col in complete.columns if col.startswith('aa_')]

partial = pd.read_csv('./incomplete.tsv',
                      sep='\t', encoding='utf-8',
                      dtype={'aa_streetnum': str, 'aa_zip': str, 'zipcode': str})


def test_clean_contact_name():
    # Re-parse approx 100 records
    for _, test_record in complete.iterrows():
        known = (test_record.get('aa_title', np.nan), test_record.get('aa_firstname', np.nan),
                 test_record.get('aa_lastname', np.nan), test_record.get('aa_fullname', np.nan))
        parsed = clean.parse_contact_name(test_record, COMP_CONTACT_COLS, strict=False)
        assert parsed == known


def test_parse_location_cols():
    for _, test_record in complete.iterrows():
        known = (test_record.get('aa_streetnum', np.nan), test_record.get('aa_street', np.nan),
                 test_record.get('aa_city', np.nan), test_record.get('aa_state', np.nan),
                 test_record.get('aa_zip', np.nan), test_record.get('aa_fulladdy', np.nan))
        parsed = clean.parse_location_cols(test_record, COMP_LOC_COLS, strict=False)
        assert parsed == known


def test_parse_business_name():
    for _, test_record in complete.iterrows():
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
