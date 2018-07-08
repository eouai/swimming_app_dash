import pandas as pd
import numpy as np
from datetime import datetime

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

swimmer_names = df_state[['Swimmer', 'School', 'Gender', 'swim_year']]\
    .drop_duplicates(['Swimmer', 'School'])
swimmer_names = swimmer_names.sort_values('Swimmer')
swimmer_names['Swimmer'] = swimmer_names['Swimmer'].str.strip()
# Remove entries with grouped relay names
swimmer_names['char_count'] = swimmer_names['Swimmer'].apply(lambda x: x.count(','))
swimmer_names = swimmer_names[swimmer_names['char_count'] < 2]
swimmer_names = swimmer_names.drop('char_count', axis=1)
# swimmer_names['Date'] = swimmer_names['Date'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y').year)
swimmer_names['n2'] = swimmer_names.Swimmer.shift(-1)
swimmer_names['s2'] = swimmer_names.School.shift(-1)
swimmer_names['g2'] = swimmer_names.Gender.shift(-1)
swimmer_names['d2'] = swimmer_names.swim_year.shift(-1)
swimmer_names = swimmer_names.drop(swimmer_names.index[len(swimmer_names)-1])

name_lookup = {}


def check_name(n1, n2, g1, g2, y1, y2, s1, s2):
    if (abs(y1 - y2) < 5) & (g1 == g2) & (s1 == s2) & (n1 == n2[:-2]):
        name_lookup[n1 + s1] = n2
    else:
        name_lookup[n1 + s1] = n1
    if 'deVita' in n1:
        print(n1)
        print(n2)
    for key in name_lookup.keys():
        if 'deVita' in key:
            print(key)


def update_name(name, relay, lookup_value):
    the_name = name if relay else name_lookup[lookup_value]
    return the_name


swimmer_names.apply(lambda row: check_name(row['Swimmer'], row['n2'],
                                           row['Gender'], row['g2'],
                                           row['swim_year'], row['d2'],
                                           row['School'], row['s2']), axis=1)

df_state['lookup_value'] = df_state.Swimmer + df_state.School
df_state['relay_names'] = df_state.Swimmer.apply(lambda x: x.count(',') > 1)
df_state['clean_name'] = df_state.apply(lambda row: update_name(row['Swimmer'], row['relay_names'],
                                        row['lookup_value']), axis=1)
