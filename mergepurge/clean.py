import re
from collections import OrderedDict
import pandas as pd
import numpy as np
import probablepeople
import usaddress


STATES = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"}


# parsed categories of business names to keep
# (keeping sur and given names for doctors, lawyers, etc.)
KEEPERS = ['CorporationName', 'Surname', 'GivenName']


def find_repeated_address_label(addr):
    """Analyzes addresses that raise RepeatedLabelErrors

    Args:
        addr (str): Concatenated address string

    Returns:
        problem_key (str): The first label that was repeated
        problem_vals (list): A list of parsed values with that label
        nameparts_so_far (dict): A dictionary that includes the problem key with one of the
            possible values
    """
    parsed = usaddress.parse(addr)

    nameparts_so_far = {}
    problem_key = None
    problem_vals = set()

    for (v, k) in parsed:
        if k in nameparts_so_far.keys():
            problem_key = k
            problem_vals.add(v)
            problem_vals.add(nameparts_so_far[k])
        nameparts_so_far[k] = v

    return problem_key, problem_vals, nameparts_so_far


def parse_location_cols(row, addr_cols, strict=True):
    """Parses address columns with usaddress library

    Returns a subset of normalized address components that are useful when comparing contacts.
    Eliminates notes and other non-address text from dirty data.

    Args:
        row (pd.Series): A record
        addr_cols (list): A list of column names in the record, in order, that collectively contain
            an address
        strict (boolean, optional): Whether or not to raise a RepeatedLabelError when parsing, if
            False, the first value of the repeated labels will be used for the parse

    Returns:
        A standardized value (str, or np.nan if missing) for the following parts of a parsed
        mailing address:
            addy_num, street, city, state, zip_, full_addy

    Warning:
        This strips out 'Address 2' data like `C/O Recipient and P.O. Box 1234`
        as well as some prefixes and modifiers of street names and should not be used as a valid
        mailing address.

    Example:
        Adding four new columns of parsed address data to a pd.DataFrame:
    >>> from mergepurge import clean
    >>> df['p_street_num'], df['p_street'], df['p_city'], df['p_state'], *_ = \
    ...     zip(*df.apply(clean.parse_location_cols, axis=1, addr_cols=['address','city','state']))
    """

    row = row.fillna('')
    concat = []
    for col in addr_cols:
        if 'street' in col.lower():
            val = str(row.get(col, ''))
            concat.append(val + ',')
        else:
            concat.append(str(row.get(col, '')))

    concat = ' '.join(concat)

    cleaned = re.sub(r'(not\s*available|not\s*provided|n/a)', '', concat, flags=re.IGNORECASE)
    cleaned = re.sub('\n+', ', ', concat)
    cleaned = re.sub('\s+', ' ', concat)

    # help the usaddress tokenizer by spreading out words on either side of a slash ('/')
    # note: in 3 steps to avoid splitting up numerical fractions like '1/2'
    cleaned = re.sub(r'(?P<one>[^0-9]+)[/\\](?P<two>[0-9]+)', '\g<1> / \g<2>', cleaned)
    cleaned = re.sub(r'(?P<one>[^0-9]+)[/\\](?P<two>[^0-9]+)', '\g<1> / \g<2>', cleaned)
    cleaned = re.sub(r'(?P<one>[0-9]+)[/\\](?P<two>[^0-9]+)', '\g<1> / \g<2>', cleaned)

    try:
        parsed = usaddress.tag(cleaned)
    except usaddress.RepeatedLabelError as e:
        if strict:
            raise e

        parsed = [OrderedDict()]
        # take the first occurance of each of the fields we are interested in
        for (val, addr_part) in reversed(e.parsed_string):
            if addr_part == 'AddressNumber':
                parsed[0]['AddressNumber'] = val
            elif addr_part == 'StreetName':
                parsed[0]['StreetName'] = val
            elif addr_part == 'StateName':
                parsed[0]['StateName'] = val

        problem_key, problem_vals, part_parsed = find_repeated_address_label(cleaned)

    addy_num = parsed[0].get('AddressNumber', np.nan)

    # Concat some of the Streetname parts so highways and routes don't appear as bare numbers
    street = []
    for col in ['StreetNamePreModifier', 'StreetNamePreType', 'StreetName', ]:
        street.append(parsed[0].get(col, ''))

    street = ' '.join(street).strip()
    if street == '':
        street = np.nan

    city     = parsed[0].get('PlaceName', np.nan)
    state    = parsed[0].get('StateName', np.nan)
    zip_     = parsed[0].get('ZipCode', np.nan)

    if pd.isnull(state):
        # fallback to the unparsed State column if there is one and the value looks good
        for col in addr_cols:
            if 'state' in col.lower():
                row_state = row.get(col, '').upper().strip()
                if row_state in STATES:
                    state = row_state
                    break

    full_addy = cleaned

    return addy_num, street, city, state, zip_, full_addy


def fall_back_empty_state(row, orig_col='state'):
    """Attempts to populate missing State Abbrv.

    Useful to ensure the cleaned state column of each record has a value even if the
    call to usaddress.tag() failed

    Example:
    >>> from mergepurge import clean
    >>> df['STATENAME'] = df.apply(clean.fall_back_empty_state, axis=1, args=('State',))
    """

    if pd.isnull(row['STATENAME']):

        # fallback to the unparsed State column as long as it's valid
        row_state = row.fillna('')[orig_col]
        row_state = row_state.upper().strip()
        if row_state in STATES:
            return row_state

    return row['STATENAME']


def find_repeated_label(name_, type=None):
    """Analyzes People names that raise RepeatedLabelErrors

    Args:
        name_ (str): Name of a person e.g. 'Cpt. James T. Kirk'
        type (str, optional): type of parser probablepeople should use, one of 'person', 'company',
        or None (None=defualt which implies 'generic')

    Returns:
        problem_key: str    the first label that was repeated
        problem_vals: list  a list of parsed values with that label
        nameparts_so_far: dict   a dictionary that includes the problem key with one of the
            possible values
    """
    parsed = probablepeople.parse(name_, type)

    nameparts_so_far = {}
    problem_key = None
    problem_vals = set()

    for (v, k) in parsed:
        if k in nameparts_so_far.keys():
            problem_key = k
            problem_vals.add(v)
            problem_vals.add(nameparts_so_far[k])
        nameparts_so_far[k] = v

    return problem_key, problem_vals, nameparts_so_far


def parse_contact_name(row, name_cols, strict=True, type='person'):
    """Parses a person's name with probablepeople library

    Concatenates all the contact name columns into a single string and then attempts to parse it
    into standardized name components and return a subset of the name parts that are useful for
    comparing contacts. This process eliminates notes and other non-name text from dirty data.

    Args:
        row (pd.Series): A record
        name_cols (list): A list of column names in the record, in order, that when concatenated
            comprise a person's name
        strict (boolean, optional): Whether or not to raise a RepeatedLabelError when parsing, if
            False, the last value of the repeated labels will be used for the parse
        type (str): Which probableparser to use: 'generic', 'person' or 'company'

    Returns:
        A subset (tuple of str, or np.nan) of the standardized name components, namely:
            (title, first, last, full_name)
    """

    row = row.fillna('')
    concat = []
    for col in name_cols:
        concat.append(row.get(col, ''))
    concat = ' '.join(concat)

    cleaned = re.sub(r'(not\s*available|not\s*provided|n/a)', '', concat, flags=re.IGNORECASE)

    try:
        parsed = probablepeople.tag(cleaned, type)
    except probablepeople.RepeatedLabelError as e:
        if strict:
            raise e

        problem_key, problem_vals, parsed = find_repeated_label(cleaned)
        parsed = (parsed, '')

    title  = parsed[0].get('PrefixOther', np.nan)
    first  = parsed[0].get('GivenName', np.nan)
    last   = parsed[0].get('Surname', np.nan)
    try:
        full_name = first + ' ' + last
    except TypeError as e:
        full_name = np.nan

    return title, first, last, full_name


def parse_business_name(row, name_cols, strict=True, type='generic'):
    """Parses a Company name with probablepeople library

    Concatenates all the company name columns into a single string and then attempts to parse it
    into standardized name components and return a subset of the name parts that are useful when
    comparing Contacts and Accounts. This process eliminates notes and other non-name text from
    dirty data.

    Args:
        row (pd.Series): A record
        name_cols (list): A list of column names in the record, in order, that when concatenated
            comprise a company/business name
        strict (boolean, optional): Whether or not to raise a RepeatedLabelError when parsing, if
            False, the last value of the repeated labels will be used for the parse
        type (str): Which probableparser to use: 'generic', 'person' or 'company'

    Returns:
        biz_name (str or np.nan): Filtered and standardized company name

    Example:
        Add a new column to a pd.DataFrame with a clean company name
    >>> from mergepurge import clean
    >>> df['clean_company'] = \
    ...     df.apply(clean.parse_business_name, axis=1, name_cols=['Account Name'], strict=False)
    """

    row = row.fillna('')
    concat = []
    for col in name_cols:
        concat.append(str(row.get(col, '')))
    concat = ' '.join(concat)

    # pre-processing (no category for non-names to train parserator with)
    cleaned = re.sub(r'(not\s*available|not\s*provided|n/a)', '', concat, flags=re.IGNORECASE)

    try:
        parsed = probablepeople.tag(cleaned, type)  # type='company'? general parser works better
    except probablepeople.RepeatedLabelError as e:
        if strict:
            raise e

        problem_key, problem_vals, parsed = find_repeated_label(cleaned)
        parsed = (parsed, '')

    # filter out other name components that are bad for matching (e.g. too generic: llc)
    rebuilt_name = []
    for (k, v) in parsed[0].items():
        if k in KEEPERS:
            rebuilt_name.append(v)

    biz_name = ' '.join(rebuilt_name)

    if pd.isnull(biz_name):
        return np.nan

    return biz_name


def build_matching_cols(df, addy_cols=None, contact_cols=None, company_cols=None):
    """Adds normalized contact columns to a DataFrame

    First step in the merge/purge process. Generates a set of standardized columns for each record
    in the input DataFrame that can be used to compare to other contact and account records.

    Args:
        addy_cols (list): Address column names in order e.g. ['street','address 2','city',...]
        contact_cols (list): Contact name column names in order e.g. ['first', 'last']
        company_cols (list): Company name column names in order e.g. ['Account Name']

    Returns:
        df (pd.DataFrame): A DataFrame with added columns good for matching against other dataframes
        with similar contact or account data
    """

    if addy_cols is None:
        addy_cols = []
    if contact_cols is None:
        contact_cols = []
    if company_cols is None:
        company_cols = []

    if len(addy_cols) > 0:
        df['aa_streetnum'], df['aa_street'], df['aa_city'],\
            df['aa_state'], df['aa_zip'], df['aa_fulladdy'] = \
            zip(*df[addy_cols].apply(parse_location_cols,
                                     axis=1,
                                     addr_cols=addy_cols,
                                     strict=False))

    if len(contact_cols) > 0:
        df['aa_title'], df['aa_firstname'],\
            df['aa_lastname'], df['aa_fullname'] = \
            zip(*df[contact_cols].apply(parse_contact_name,
                                        axis=1,
                                        name_cols=contact_cols,
                                        strict=False))

    if len(company_cols) == 0:
        return df

    df['aa_company'] = df.apply(parse_business_name, axis=1, name_cols=company_cols, strict=False)

    return df


def clean_US_phone(row, phone_cols, extension=False):
    """Returns cleaned 10 digit str of US phone number

    Concatenates all the phone columns into a single string and then attempts to parse it into a
    standardized 10 digit string, omitting any notes and extensions that were in the input.
    Output is useful for comparing Contacts and Accounts.

    Args:
        row (pd.Series): A record
        phone_cols (list): A list of column names in the record, in order, that when concatenated
            comprise a phone number, e.g. ['country_code','area_code','local_number']
        strict (boolean, optional): Whether or not to raise an Exception when parsing, if
            False (default), unparsable numbers will return np.nan

    Returns:
        If extension=False (default):
            number (str or np.nan): Cleaned, 10 digit phone number
        If extension=True:
            A tuple containing (number, ext):
                number (str or np.nan): Cleaned, 10 digit phone number
                ext (str or np.nan): Cleaned, digits of extension

    Example:
    >>> from mergepurge import clean
    >>> df['phone'] = df.apply(clean.clean_US_phone, axis=1, phone_cols=['dirty_phone'])
    or
    >>> df['phone'], df['ext'] = zip(*df.apply(clean.clean_US_phone,
    ...                                        axis=1,
    ...                                        phone_cols=['dirty_phone'],
    ...                                        extension=True)
    """

    row = row.fillna('')
    concat = []
    for col in phone_cols:
        concat.append(str(row.get(col, '')))
    concat = ' '.join(concat)

    # Drop any weird unicode chars that eval to numeric
    dirty_number = str(concat.encode('ascii', 'ignore'))

    num_and_ext = dirty_number.lower().split("ext", 2)
    number = ''.join(char_ for char_ in num_and_ext[0] if char_.isdigit())
    try:
        ext = ''.join(char_ for char_ in num_and_ext[1] if char_.isdigit())
    except IndexError as e:
        ext = np.nan

    num_len = len(number)
    if num_len == 10:
        pass
    elif num_len == 11 and number.startswith('1'):
        number = number[1:]
    else:
        if extension:
            return np.nan, np.nan
        return np.nan

    if extension:
        return number, ext
    else:
        return number
