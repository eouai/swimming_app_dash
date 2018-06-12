import pandas as pd

seeds = pd.read_csv('data/state_meet_seeds_and_finals_only.csv')

seeds = seeds[seeds['Meet'] == 'State Seed']
seeds = seeds.sort_values(['date_year', 'time_obj'], ascending=[False, True])\
    .groupby(['Gender', 'Event', 'date_year', 'Class'])['Gender', 'Event', 'date_year',
                                                        'Class', 'time_obj'].last()
seeds = seeds.reset_index()


def time_format(time_split):
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
    return time_obj


seeds['time_obj'] = seeds['time_obj'].apply(lambda x: time_format(x.split(":")))

seeds.to_csv('data/swimming_data_seeds_processed.csv')
