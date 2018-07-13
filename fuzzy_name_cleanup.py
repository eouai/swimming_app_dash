from fuzzywuzzy import fuzz
import pandas as pd

dtypes = {'Unnamed: 0': 'int', '100 Split': 'str', '150 Split': 'str', '200 Split': 'str',
          '250 Split': 'str', '300 Split': 'str', '350 Split': 'str', '400 Split': 'str',
          '450 Split': 'str', '50 Split': 'str', '500 Split': 'str', 'Class': 'str',
          'Date': 'str', 'Event': 'str', 'Gender': 'str', 'Meet': 'str', 'Place': 'str',
          'Points': 'str', 'Previous record': 'str', 'School': 'str', 'Swimmer': 'str',
          'Year': 'str', 'full_results': 'bool', 'key': 'int', 'relay_position': 'str',
          'swim_time': 'str', 'time_cleanup': 'str', 'time_obj': 'str', 'date_time': 'str',
          'date_year': 'int', 'swim_year': 'int'}
df_state = pd.read_csv('data/swimming_data_state_processed.csv', dtype=dtypes)


def fuzzy_matching(df):
    df = fuzzy_column(df)
    fuzzy_names = list(df['fuzzy'].unique())
    for name in fuzzy_names:
        for compare_name in fuzzy_names:
            the_ratio = fuzz.ratio(compare_name, name)
            if (the_ratio > .95) & (the_ratio < 1):
                print('compare_name: {}'.format(compare_name))
                print('name: {}'.format(name))
                print('ratio: {}'.format(the_ratio))
    return df


def fuzzy_column(df):
    df['fuzzy'] = df['Swimmer'] + ' ' + df['School']\
        .apply(lambda x: x.replace(' High School', '')) + ' ' + df['grad_year']
    return df
