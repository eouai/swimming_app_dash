import pandas as pd

# import numpy as np
# from datetime import datetime

dtypes = {'Unnamed: 0': 'int', '100 Split': 'str', '150 Split': 'str', '200 Split': 'str',
          '250 Split': 'str', '300 Split': 'str', '350 Split': 'str', '400 Split': 'str',
          '450 Split': 'str', '50 Split': 'str', '500 Split': 'str', 'Class': 'str',
          'Date': 'str', 'Event': 'str', 'Gender': 'str', 'Meet': 'str', 'Place': 'str',
          'Points': 'str', 'Previous record': 'str', 'School': 'str', 'Swimmer': 'str',
          'Year': 'str', 'full_results': 'bool', 'key': 'int', 'relay_position': 'str',
          'swim_time': 'str', 'time_cleanup': 'str', 'time_obj': 'str', 'date_time': 'str',
          'date_year': 'int', 'swim_year': 'int'}
df_state = pd.read_csv('data/swimming_data_state_processed.csv', dtype=dtypes)
df_state['Swimmer'] = df_state.Swimmer.str.strip()
df_state['relay_names'] = df_state.Swimmer.apply(lambda x: x.count(',') > 1)


def structure_swimmer_comparison(df, col, sort_order):
    df = df[[col, 'School', 'Gender', 'swim_year']] \
        .drop_duplicates([col, 'School'])
    df[col+'_lower'] = df[col].str.strip().str.lower()
    df = df.sort_values(sort_order)
    # Remove entries with grouped relay names
    df['char_count'] = df[col].apply(lambda x: x.count(','))
    df = df[df['char_count'] < 2]
    df = df.drop('char_count', axis=1)
    df['n2'] = df[col].shift(-1)
    df['s2'] = df.School.shift(-1)
    df['g2'] = df.Gender.shift(-1)
    df['d2'] = df.swim_year.shift(-1)
    return df


def compile_name_dict(n1, n2, g1, g2, y1, y2, s1, s2, trunc):
    if pd.isnull(n2):
        n2, g2, y2, s2 = n1, g1, y1, s1
    if (abs(y1 - y2) < 5) & (g1 == g2) & (s1 == s2) & ((n1.lower() == n2[:-trunc].lower())
                                                       or (n2.lower() == n1[:-trunc].lower())):
        # Found a truncated version of a name
        if n1 == n2[:-trunc]:
            # No case mismatch, trunc version is exact match, update to longer name version
            name_lookup[n1 + s1] = n2
        elif n2.lower() == n1[:-trunc].lower():
            # Trunc version has case mismatch, n1 is the longer string
            # update to longer name (sorted descending, so higher case will be n1)
            name_lookup[n1 + s1] = n1
            name_lookup[n2 + s1] = n1
        else:
            # Trunc version has case mismatch, n2 is the longer string
            name_lookup[n1 + s1] = n2
            name_lookup[n2 + s1] = n2
    elif (abs(y1 - y2) < 5) & (g1 == g2) & (s1 == s2) & (n1.lower() == n2.lower()):
        # Found a case mismatch, no trunc occurring on an otherwise matched name
        if [n1 + s1][0] in name_lookup.keys():
            pass
        else:
            name_lookup[n1 + s1] = n1
        if [n2 + s1][0] in name_lookup.keys():
            pass
        else:
            name_lookup[n2 + s1] = n1
    else:
        if [n1 + s1][0] in name_lookup.keys():
            pass
        else:
            name_lookup[n1 + s1] = n1


def update_name(name, relay, lookup_value):
    the_name = name if relay else name_lookup[lookup_value]
    return the_name


def write_clean_name(df, col):
    df['lookup_value'] = df[col] + df.School
    df['clean_name'] = df.apply(lambda row: update_name(row[col], row['relay_names'],
                                                        row['lookup_value']), axis=1)
    return df


col = 'Swimmer'
trunc_len = 1

for i in range(5):
    sort_order = [col + '_lower', 'School']
    for j in range(2):
        name_lookup = {}
        swimmer_names = structure_swimmer_comparison(df_state, col, sort_order)
        swimmer_names.apply(lambda row: compile_name_dict(row[col], row['n2'], row['Gender'], row['g2'],
                                                          row['swim_year'], row['d2'], row['School'],
                                                          row['s2'], trunc_len), axis=1)
        df_state = write_clean_name(df_state, col)
        sort_order = list(reversed(sort_order))
    col = 'clean_name'  # first time through check Swimmer name col, after that use the updated clean_name col

trunc_len = 2
sort_order = [col + '_lower', 'School']

for i in range(3):
    for j in range(2):
        name_lookup = {}
        swimmer_names = structure_swimmer_comparison(df_state, col, sort_order)
        swimmer_names.apply(lambda row: compile_name_dict(row[col], row['n2'], row['Gender'], row['g2'],
                                                          row['swim_year'], row['d2'], row['School'],
                                                          row['s2'], trunc_len), axis=1)
        df_state = write_clean_name(df_state, col)
        sort_order = list(reversed(sort_order))

trunc_len = 3

for i in range(2):
    for j in range(2):
        name_lookup = {}
        swimmer_names = structure_swimmer_comparison(df_state, col, sort_order)
        swimmer_names.apply(lambda row: compile_name_dict(row[col], row['n2'], row['Gender'], row['g2'],
                                                          row['swim_year'], row['d2'], row['School'],
                                                          row['s2'], trunc_len), axis=1)
        df_state = write_clean_name(df_state, col)
        sort_order = list(reversed(sort_order))

trunc_len = 4

for i in range(1):
    for j in range(2):
        name_lookup = {}
        swimmer_names = structure_swimmer_comparison(df_state, col, sort_order)
        swimmer_names.apply(lambda row: compile_name_dict(row[col], row['n2'], row['Gender'], row['g2'],
                                                          row['swim_year'], row['d2'], row['School'],
                                                          row['s2'], trunc_len), axis=1)
        df_state = write_clean_name(df_state, col)
        sort_order = list(reversed(sort_order))

df_state.to_csv('data/name_cleanup3.csv')
