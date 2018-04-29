# import raw CSV, process the file, write to new CSV

import pandas as pd
import re
import os

#os.chdir('/var/www/FlaskApp/FlaskApp')

year_mapping = {'09':'FR', '10':'SO', '11':'JR', '12':'SR'}
gender_mapping = {'Boys': 'M', 'Men': 'M', 'Girls':'W', 'Women': 'W'}

# Read in initial data sets from CSV.
df_SV_raw = pd.read_csv('data/swimming_data.csv')
df_State_raw = pd.read_csv('data/swimming_data_state.csv')

# Define CSV cleanup and processing methods
def cleanup_SV(df_SV_raw):
    df_SV_raw['Year'] = pd.DatetimeIndex(df_SV_raw['Date']).year
    df_SV_raw = df_SV_raw[['Event', 'Time Full', 'Year', 'Swimmer', 'Gender']]
    return df_SV_raw

def cleanup_state(df_State_raw):
    df_State_raw = process_place(df_State_raw)
    df_State_raw = process_school_year(df_State_raw)
    df_State_raw = process_gender(df_State_raw)
    df_State_raw = process_times(df_State_raw)
    return df_State_raw

def process_place(df_State_raw):
    # Fill NA with 0 and convert col to int format
    df_State_raw['Place'] = df_State_raw['Place'].fillna(0)
    df_State_raw['Place'] = df_State_raw['Place'].apply(lambda x: int(x))
    return df_State_raw

def process_school_year(df_State_raw):
    # Standardize school year formatting
    # Remove school year when it appears in school name col 'School'
    df_State_raw['Year'] = df_State_raw['Year'].fillna('NA')
    df_State_raw['Year'] = df_State_raw['Year'].apply(lambda x: '09' if x=='9' else x)
    school_years = [' FR ',' SO ',' JR ',' SR ',' 09 ',' 10 ',' 11 ',' 12 ']
    df_State_raw['Year'] = df_State_raw['Year'].apply(
            lambda x: x if any(x == year for year in map(str.strip, school_years)) else 'NA')
    for index, row in df_State_raw.iterrows():
        school_name = row['School']
        for year in school_years:
            if year in school_name:
                if row['Year'] not in map(str.strip, school_years):
                    df_State_raw.loc[index, 'Year'] = year.strip()
                df_State_raw.loc[index, 'School'] = school_name[school_name.find(year)+4:]
                break
    df_State_raw['Year'].replace(year_mapping, inplace=True)
    return df_State_raw

def process_gender(df_State_raw):
    # Standardize gender formatting
    df_State_raw['Gender'].replace(gender_mapping, inplace=True)
    return df_State_raw

def process_times(df_State_raw):
    # Times come in text format
    # Convert times to time obj
    # also extract seconds and minutes values, write those values to new col
    df_State_raw['time_cleanup'] = df_State_raw['Final Time'].apply(
            lambda x: re.sub("[^0-9\.\:]", "", x))
    df_State_raw['time_split'] = df_State_raw['time_cleanup'].apply(
            lambda x: x.split(":"))
    df_State_raw['time_seconds'] = df_State_raw['time_split'].apply(
            lambda x: 999.9 if len(x[0]) == 0 else (float(x[0])
            if len(x) == 1 else 60 * float(x[0]) + float(x[1])))
    df_State_raw['time_str'] = df_State_raw['time_split'].apply(
            lambda x: '2000-01-01 00:59:59.99' if len(x[0]) == 0 else ('2000-01-01 00:00:' + x[0]
            if len(x) == 1 else '2000-01-01 00:0' +x[0] + ':' + x[1]))
    df_State_raw['time_obj'] = pd.to_datetime(df_State_raw['time_str'])
    df_State_raw['min_obj'] = df_State_raw['time_obj'].apply(
            lambda x: x.time().strftime('%M:%S.%f')[:-4])
    df_State_raw['date_time'] = pd.to_datetime(df_State_raw['Date'])
    df_State_raw['date_year'] = df_State_raw['date_time'].map(lambda x: x.year)
    df_State_raw['seed_time_split'] = df_State_raw['Seed'].apply(
            lambda x: x.split(":"))
    df_State_raw['seed_time_str'] = df_State_raw['seed_time_split'].apply(
            lambda x: '2000-01-01 00:59:59.99' if len(x[0]) == 0 else ('2000-01-01 00:00:' + x[0]
            if len(x) == 1 else '2000-01-01 00:0' +x[0] + ':' + x[1]))
    df_State_raw['seed_time_obj'] = pd.to_datetime(df_State_raw['seed_time_str'])
    df_State_raw['seed_min_obj'] = df_State_raw['seed_time_obj'].apply(
        lambda x: x.time().strftime('%M:%S.%f')[:-4])
    df_State_raw['seed_time_seconds'] = df_State_raw['seed_time_split'].apply(
            lambda x: 999.9 if len(x[0]) == 0 else (float(x[0])
            if len(x) == 1 else 60 * float(x[0]) + float(x[1])))
    return df_State_raw

# Cleanup and process the CSV files
df_SV = cleanup_SV(df_SV_raw)
df_State = cleanup_state(df_State_raw)

df_SV.to_csv('data/swimming_data_processed.csv')
df_State.to_csv('data/swimming_data_state_processed.csv')