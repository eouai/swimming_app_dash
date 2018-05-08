# import raw CSV, process the file, write to new CSV

import pandas as pd
import re
import numpy as np
import os

#os.chdir('/var/www/FlaskApp/FlaskApp')

year_mapping = {'09':'FR', '10':'SO', '11':'JR', '12':'SR'}
gender_mapping = {'Boys': 'M', 'Men': 'M', 'Girls':'W', 'Women': 'W'}
high_school_mapping = {"Alta Hawks High School": "Alta High School",
                        "Alta High School-UT": "Alta High School",
                        "American Fork High Schoo": "American Fork High School",
                        "American Fork High School-UT": "American Fork High School",
                        "Bear River High School-VA": "Bear River High School",
                        "Ben Lomond": "Ben Lomond High School",
                        "Ben Lomond High": "Ben Lomond High School",
                        "Ben Lomond-VA": "Ben Lomond High School",
                        "Bingham High School-UT": "Bingham High School",
                        "Bingham Miners": "Bingham High School",
                        "Brighton High School-UT": "Brighton High School",
                        "J Canyon View High": "Canyon View High School",
                        "M Canyon View High": "Canyon View High School",
                        "S Canyon View High": "Canyon View High School",
                        "T Canyon View High": "Canyon View High School",
                        "Canyon View High": "Canyon View High School",
                        "Canyonview High School": "Canyon View High School",
                        "Canyonview High School-VA": "Canyon View High School",
                        "D Canyon View High": "Canyon View High School",
                        "Carbon High School-VA": "Carbon High School",
                        "Cedar City High": "Cedar City High School",
                        "Cedar City High School-VA": "Cedar City High School",
                        "Copper Hills High School-UT": "Copper Hills High School",
                        "Corner Canyon High S": "Corner Canyon High School",
                        "Cottonwood High School-UT": "Cottonwood High School",
                        "Davis High School-UT": "Davis High School",
                        "Delta High School-VA": "Delta High School",
                        "Desert Hills High School-VA": "Desert Hills High School",
                        "East High School Leopards": "East High School",
                        "Emery High School-UT": "Emery High School",
                        "Fremont High School-UT": "Fremont High School",
                        "Ghs Swimming-VA": "Gainesville High School",
                        "Grand County High Schoo": "Grand County High School",
                        "Hillcrest High High School": "Hillcrest High School",
                        "Hunter High School-UT": "Hunter High School",
                        "Hurricane High School-VA": "Hurricane High School",
                        "Intermountain Christian High": "Intermountain Christian School",
                        "Intermountain Christian School-VA": "Intermountain Christian School",
                        "Jordan High School-UT": "Jordan High School",
                        "Juan Diego Catholic High Schoo": "Juan Diego Catholic High School",
                        "Juan Diego Catholic High Schoo-UT": "Juan Diego Catholic High School",
                        "Juan Diego High Schoo": "Juan Diego Catholic High School",
                        "Juan Diego High School": "Juan Diego Catholic High School",
                        "FR Juan Diego High School": "Juan Diego High School",
                        "Judge Memorial Catholic High S": "Judge Memorial High School",
                        "Judge Memorial Catholic High S-UT": "Judge Memorial High School",
                        "Kearns High School-UT": "Kearns High School",
                        "Layton High School-UT": "Layton High School",
                        "Lehi High School-UT": "Lehi High School",
                        "SR Logan High School": "Logan High School",
                        "Lone Peak High School-UT": "Lone Peak High School",
                        "North Summit High School": "North Summit High",
                        "North Summit HS": "North Summit High",
                        "North Summit-VA": "North Summit High",
                        "Northridge High School-UT": "Northridge High School",
                        "Oakley School": "Oakley High School",
                        "Ogden High Swimming": "Ogden High School",
                        "Orem High School Tigers": "Orem High School",
                        "Park City High School-VA": "Park City High School",
                        "Pleasant Grove High School-UT": "Pleasant Grove High School",
                        "Richfield High School Wildcats-VA": "Richfield High School",
                        "Riverton High School-UT": "Riverton High School",
                        "Rowland Hall HS": "Rowland Hall High School",
                        "Rowland Hall St. Marks": "Rowland Hall High School",
                        "Rowland Hall St. Marks-VA": "Rowland Hall High School",
                        "Salt Lake Lutheran High School-VA": "Salt Lake Lutheran High School",
                        "South Summit High School Swim": "South Summit High School",
                        "Spanish Fork High": "Spanish Fork High School",
                        "Stanbury High School": "Stansbury High School",
                        "Syracuse High School Swimiming": "Syracuse High School",
                        "Syracuse High School-UT": "Syracuse High School",
                        "Taylorsville High School-UT": "Taylorsville High School",
                        "Telos Academy": "Telos Academy High School",
                        "Uintah High School Swim Team": "Uintah High School",
                        "Viewmont HighSchool-UT": "Viewmont High School",
                        "Wasatch Academy Swim Team": "Wasatch Academy High School",
                        "Wasatch High School-VA": "Wasatch High School",
                        "Waterford High School-VA": "Waterford High School",
                        "Weber High School-UT": "Weber High School",
                        "West High School-UT": "West High School",
                        "West Jordan High School-UT": "West Jordan High School",}


# Read in initial data sets from CSV.
df_SV_raw = pd.read_csv('data/swimming_data.csv')
df_State_raw = pd.read_csv('data/swimming_data_state.csv')
df_State_raw = df_State_raw[np.isfinite(df_State_raw['key'])]

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
    df_State_raw = process_school_name(df_State_raw)
    return df_State_raw


def process_school_name(df_State_raw):
    df_State_raw['School'] = df_State_raw['School'].apply(lambda x: x.strip())
    df_State_raw['School'] = df_State_raw['School'].apply(
        lambda x: high_school_mapping[x] if x in high_school_mapping else x)
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
        if pd.isnull(row['School']):
            continue
        else:
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
    df_State_raw['seed_time_cleanup'] = df_State_raw['Seed'].apply(
        lambda x: re.sub("[^0-9\.\:]", "", x))
    df_State_raw['seed_time_split'] = df_State_raw['seed_time_cleanup'].apply(
            lambda x: str(x).split(":"))
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