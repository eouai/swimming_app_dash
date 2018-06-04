# import raw CSV, process the file, write to new CSV

import pandas as pd
import re
import numpy as np
from fuzzywuzzy import fuzz
import os

#os.chdir('/var/www/FlaskApp/FlaskApp')

year_mapping = {'09':'FR', '10':'SO', '11':'JR', '12':'SR'}
gender_mapping = {'Boys': 'M', 'Men': 'M', 'Men ': 'M', 'Male': 'M', 'Male ': 'M',
                  'Women': 'W', 'Women ': 'W', 'Female': 'W', 'Female ': 'W',
                  'F': 'W', 'Girls': 'W',
                  'M': 'M', 'W': 'W'}
# Swimmers that have no school year recorded - assuming on average they're juniors
# Most of these swim results are from state meet - less likely for FR to qualify for State
grad_mapping = {'FR': 3, 'SO': 2, 'JR': 1, 'SR': 0, 'NA': 1}


# Define CSV cleanup and processing methods
def get_high_schools(f):
    mapping = {}
    for line in f:
        temp = line.replace('"', '')
        temp = temp.replace('{', '')
        temp = temp.replace(',', '')
        k, v = temp.strip().split(':')
        mapping[k.strip()] = v.strip()
    return mapping


def cleanup_SV(df):
    df['Year'] = pd.DatetimeIndex(df['Date']).year
    df = df[['Event', 'Time Full', 'Year', 'Swimmer', 'Gender']]
    return df


def cleanup_state(df):
    df = process_place(df)
    df = process_school_year(df)
    df = process_gender(df)
    df = reshape_seed(df)
    df = process_times(df)
    df = process_school_name(df)
    # df = fuzzy_matching(df)
    return df


def process_school_name(df):
    df['School'] = df['School'].apply(lambda x: x.strip())
    df['School'] = df['School'].apply(lambda x: x.strip(','))
    df['School'] = df['School'].apply(
        lambda x: high_school_mapping[x])
    return df


def process_place(df):
    # Fill NA with 0 and convert col to int format
    df['Place'] = df['Place'].fillna(0)
    df['Place'] = df['Place'].apply(lambda x: int(x))
    return df


def process_school_year(df):
    # Standardize school year formatting
    # Remove school year when it appears in school name col 'School'
    df['Year'] = df['Year'].fillna('NA')
    df['Year'] = df['Year'].apply(lambda x: '09' if x == '9' else x)
    school_years = [' FR ', ' SO ', ' JR ', ' SR ', ' 09 ', ' 10 ', ' 11 ', ' 12 ']
    df['Year'] = df['Year'].apply(
            lambda x: x if any(x == year for year in map(str.strip, school_years)) else 'NA')
    for index, row in df.iterrows():
        if pd.isnull(row['School']):
            continue
        else:
            school_name = row['School']
            for year in school_years:
                if year in school_name:
                    if row['Year'] not in map(str.strip, school_years):
                        df.loc[index, 'Year'] = year.strip()
                    df.loc[index, 'School'] = school_name[school_name.find(year) + 4:]
                    break
    df['Year'].replace(year_mapping, inplace=True)
    return df


def process_gender(df):
    # Standardize gender formatting
    df['Gender'] = df['Gender'].apply(lambda x: gender_mapping[x])
    return df


def sub_chars(x):
    if x is not None:
        if len(re.findall('\d', x)) > 0:
            x = re.sub("[^0-9.:]", "", x)
        else:
            x = ''
    else:
        x = ''
    return x


def get_swim_year(x):
    swim_year = x.year
    swim_month = x.month
    if swim_month > 5:
        swim_year += 1
    return swim_year


def get_grad_year(row):
    swim_year = row[29]
    grad_year = swim_year + grad_mapping[row[20]]
    grad_year = str(grad_year)
    return grad_year


def reshape_seed(df):
    df['Final Time'] = df['Final Time'].fillna(value='')
    df['Seed'] = df['Seed'].fillna(value='')
    df_temp = df[['key', 'Place', 'Swimmer', 'Year', 'School', 'Gender',
                  'Event', 'Seed', 'Final Time', 'Date', 'Class', 'full_results']]
    df_temp['seed_check'] = df_temp['Seed'].apply(lambda x: len(x))
    df_temp = df_temp[df_temp['seed_check'] > 1]
    df_temp = df_temp.drop(columns='seed_check')
    df['Seed'] = ''
    df_temp['Final Time'] = ''
    df_temp['Meet'] = 'State Seed'
    df_combined = pd.concat([df_temp, df])
    final_times = list(df_combined['Final Time'])
    seed_times = list(df_combined['Seed'])
    count = 0
    swim_times = []
    for item in final_times:
        if len(item) > 0:
            swim_times.append(item)
        else:
            swim_times.append(seed_times[count])
        count += 1
    df_combined['swim_time'] = swim_times
    df_combined = df_combined.drop(columns=['Seed', 'Final Time'])
    return df_combined


def time_format(time_split):
    try:
        if len(time_split) == 0:
            time_str_format = '2000-01-01 00:59:59.99'
        elif (len(time_split) == 1) & (len(time_split[0]) == 0):
            time_str_format = '2000-01-01 00:59:59.99'
        elif (len(time_split) == 1) & (time_split[0] == ' '):
            time_str_format = '2000-01-01 00:59:59.99'
        elif (len(time_split) == 1) & (len(time_split[0]) > 0):
            time_str_format = '2000-01-01 00:00:' + time_split[0]
        else:
            time_str_format = '2000-01-01 00:' + time_split[0] + ':' + time_split[1]
        time_obj = pd.datetime.strptime(time_str_format, '%Y-%m-%d %H:%M:%S.%f')
    except:
        print(time_split)
    return time_obj


def process_times(df):
    df[['50 Split', '100 Split', '150 Split', '200 Split', '250 Split',
        '300 Split', '350 Split', '400 Split', '450 Split', '500 Split']] = \
        df[['50 Split', '100 Split', '150 Split', '200 Split', '250 Split',
            '300 Split', '350 Split', '400 Split', '450 Split', '500 Split']].fillna(value='')
    df['time_cleanup'] = df['swim_time'].apply(lambda x: sub_chars(x))
    df['time_obj'] = df['time_cleanup'].apply(lambda x: time_format(x.split(":")))
    df['50 Split'] = df['50 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['100 Split'] = df['100 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['150 Split'] = df['150 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['200 Split'] = df['200 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['250 Split'] = df['250 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['300 Split'] = df['300 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['350 Split'] = df['350 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['400 Split'] = df['400 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['450 Split'] = df['450 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['500 Split'] = df['500 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['date_time'] = pd.to_datetime(df['Date'])
    df['date_year'] = df['date_time'].map(lambda x: x.year)
    df['swim_year'] = df['date_time'].apply(lambda x: get_swim_year(x))
    df['grad_year'] = df.apply(get_grad_year, axis=1)
    return df


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


# Read in initial data sets from CSV.
# df_SV_raw = pd.read_csv('data/swimming_data.csv')
df_state_raw = pd.read_csv('data/swimming_data_state.csv')
df_state_raw = df_state_raw[np.isfinite(df_state_raw['key'])]

# Cleanup and process the CSV files
# df_SV = cleanup_SV(df_SV_raw)
f = open("high_school_mapping.txt", "r")
high_school_mapping = get_high_schools(f)
df_state = cleanup_state(df_state_raw)

# df_SV.to_csv('data/swimming_data_processed.csv')
df_state.to_csv('data/swimming_data_state_processed.csv')