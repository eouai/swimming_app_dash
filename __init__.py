#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 17:15:48 2018

@author: burtg-dev
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
# import dash_table_experiments as dte
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
from datetime import timedelta
import plotly.graph_objs as go
# import os

# os.chdir('/var/www/FlaskApp/FlaskApp')

# Create app and designate app settings
app = dash.Dash()
app.config.supress_callback_exceptions = True
app.title = 'Utah High-School State Swimming Records'
server = app.server

# Define variables
css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdn.rawgit.com/plotly/dash-app-stylesheets/30b641e2e89753b13e6557b9d65649f13ea7c64c/dash-docs-custom.css',
    ]
#    'https://gonts.googleapis.com/css?family=Dosis',
#    'https://dcnjs.cloudflare.com/ajax.libs/font-awesome/4.7.0/css/font-awesome.min.css',

# read in data
# Set data types


def lookup(s):
    dates = {date: pd.to_datetime(date) for date in s.unique()}
    return s.map(dates)


headers = ['Unnamed: 0', '100 Split', '150 Split', '200 Split', '250 Split',
           '300 Split', '350 Split', '400 Split', '450 Split', '50 Split',
           '500 Split', 'Class', 'Date', 'Event', 'Gender', 'Meet', 'Place',
           'Points', 'Previous record', 'School', 'Swimmer', 'Year',
           'full_results', 'key', 'relay_position', 'swim_time', 'time_cleanup',
           'time_obj', 'date_time', 'date_year', 'swim_year']
dtypes = {'Unnamed: 0': 'int', '100 Split': 'str', '150 Split': 'str', '200 Split': 'str',
          '250 Split': 'str', '300 Split': 'str', '350 Split': 'str', '400 Split': 'str',
          '450 Split': 'str', '50 Split': 'str', '500 Split': 'str', 'Class': 'str',
          'Date': 'str', 'Event': 'str', 'Gender': 'str', 'Meet': 'str', 'Place': 'str',
          'Points': 'str', 'Previous record': 'str', 'School': 'str', 'Swimmer': 'str',
          'Year': 'str', 'full_results': 'bool', 'key': 'int', 'relay_position': 'str',
          'swim_time': 'str', 'time_cleanup': 'str', 'time_obj': 'str', 'date_time': 'str',
          'date_year': 'int', 'swim_year': 'int'}
df_state = pd.read_csv('data/swimming_data_state_processed.csv', dtype=dtypes)
df_seeds = pd.read_csv('data/swimming_data_seeds_processed.csv')
df_state['time_obj'] = lookup(df_state['time_obj'])
df_state['100 Split'] = lookup(df_state['100 Split'])
df_state['150 Split'] = lookup(df_state['150 Split'])
df_state['200 Split'] = lookup(df_state['200 Split'])
df_state['250 Split'] = lookup(df_state['250 Split'])
df_state['300 Split'] = lookup(df_state['300 Split'])
df_state['350 Split'] = lookup(df_state['350 Split'])
df_state['400 Split'] = lookup(df_state['400 Split'])
df_state['450 Split'] = lookup(df_state['450 Split'])
df_state['500 Split'] = lookup(df_state['500 Split'])
df_state['50 Split'] = lookup(df_state['50 Split'])
df_seeds['time_obj'] = lookup(df_seeds['time_obj'])


#################################################
#     Helper functions for graph variables      #
#################################################

def generate_hover_text(df, place, all_classes_selected, all_meets_selected, year_range):
    y_counts = get_finals_y_counts(df)
    i = year_range[0]
    hover_text = pd.Series()
    for y_count in y_counts:
        if place > y_count:
            swimmer_name, swimmer_time, class_text, meet_name, event_name, \
                school_name, relay_position = get_nth_result(df, y_count, i)
            append_text = swimmer_name + ' ' + swimmer_time + ' ' + \
                str([class_text if all_classes_selected else ''][0]) + \
                str([': ' + meet_name if all_meets_selected else ''][0]) + \
                str([' ' + event_name if all_meets_selected else ''][0]) + \
                str([' (lead-off)' if all_meets_selected & (relay_position == '1.0') &
                    ('Relay' in event_name) else ''][0]) + \
                str([' - ' + school_name if team_relay_lookup(event_name) else ''][0])
            hover_text.at[i] = append_text
        else:
            swimmer_name, swimmer_time, class_text, meet_name, event_name, \
                school_name, relay_position = get_nth_result(df, place, i)
            append_text = swimmer_name + ' ' + swimmer_time + ' ' + \
                str([class_text if all_classes_selected else ''][0]) + \
                str([': ' + meet_name if all_meets_selected else ''][0]) + \
                str([' ' + event_name if all_meets_selected else ''][0]) + \
                str([' (lead-off)' if all_meets_selected & (relay_position == '1.0') &
                    ('Relay' in event_name) else ''][0]) + \
                str([' - ' + school_name if team_relay_lookup(event_name) else ''][0])
            hover_text.at[i] = append_text
        i += 1
    return hover_text


def get_nth_result(df, place, i):
    names = get_nth_names(df, place)
    times = get_nth_times(df, place)
    classes_text = get_nth_class(df, place)
    meet_names = get_nth_meet_names(df, place)
    event_names = get_nth_event_names(df, place)
    school_names = get_nth_school_names(df, place)
    nth_relay_positions = get_relay_position(df, place)
    times = times.apply(lambda x: x.strftime('%M:%S.%f')[:-4])
    swimmer_name = names.loc[i]
    swimmer_time = times.loc[i]
    class_text = classes_text.loc[i]
    meet_name = meet_names.loc[i]
    event_name = event_names.loc[i]
    relay_position = nth_relay_positions.loc[i]
    school_name = school_names.loc[i]
    return swimmer_name, swimmer_time, class_text, meet_name, event_name, school_name, relay_position


def get_nth_names(df, place):
    names = df.sort_values(['swim_year', 'time_obj'], ascending=[False, True]) \
        .groupby('swim_year')['Swimmer'].nth(place)
    return names


def get_nth_school_names(df, place):
    school_names = df.sort_values(['swim_year', 'time_obj'], ascending=[False, True]) \
        .groupby('swim_year')['School'].nth(place)
    return school_names


def get_nth_times(df, place):
    times = df.sort_values(['swim_year', 'time_obj'], ascending=[False, True]) \
        .groupby('swim_year')['time_obj'].nth(place)
    return times


def get_nth_class(df, place):
    the_classes = df.sort_values(['swim_year', 'time_obj'], ascending=[False, True]) \
        .groupby('swim_year')['Class'].nth(place)
    return the_classes


def get_nth_meet_names(df, place):
    meet_names = df.sort_values(['swim_year', 'time_obj'], ascending=[False, True]) \
        .groupby('swim_year')['Meet'].nth(place)
    return meet_names


def get_nth_event_names(df, place):
    event_names = df.sort_values(['swim_year', 'time_obj'], ascending=[False, True]) \
        .groupby('swim_year')['Event'].nth(place)
    return event_names


def get_relay_position(df, place):
    nth_relay_positions = df.sort_values(['swim_year', 'time_obj'], ascending=[False, True]) \
        .groupby('swim_year')['relay_position'].nth(place)
    return nth_relay_positions


def get_nth_swim_times(df, place):
    swim_times = df.sort_values('time_obj').groupby('swim_year').time_obj.nth(place)
    return swim_times


def get_last_swim_times(df):
    swim_times = df.sort_values('time_obj').groupby('swim_year').time_obj.last()
    return swim_times


def generate_y_data(df, place, year_range):
    y_counts = get_finals_y_counts(df)
    y_data = df.sort_values('time_obj').groupby('swim_year').time_obj.nth(0)
    i = year_range[0]
    for y_count in y_counts:
        if place > y_count:
            swim_times = get_last_swim_times(df)
            swim_time = swim_times.loc[i]
            y_data.at[i] = swim_time
        else:
            swim_times = get_nth_swim_times(df, place)
            swim_time = swim_times.loc[i]
            y_data.at[i] = swim_time
        i += 1
    return y_data


def get_finals_y_counts(df):
    y_counts = list(df.sort_values('time_obj').groupby(
        'swim_year').time_obj.count())
    for i in range(len(y_counts)):
        y_counts[i] = y_counts[i] - 1
    return y_counts


def generate_y_axis_max(df, seeds, all_classes_selected, selected_event):
    y_counts = list(set(get_finals_y_counts(df)))
    y_axis_max = df.sort_values('time_obj')\
        .groupby('swim_year').time_obj.nth(15).max()
    seed_max = seeds.time_obj.max()
    for y_count in y_counts:
        if 15 > y_count:
            if all_classes_selected:
                temp_y = df.sort_values('time_obj').groupby('swim_year')\
                    .time_obj.nth(y_count).max()
                if temp_y > y_axis_max: y_axis_max = temp_y
            else:
                temp_y = df.sort_values('time_obj').groupby('swim_year')\
                    .time_obj.nth(y_count).max()
                if temp_y > y_axis_max: y_axis_max = temp_y
                y_axis_max = max(y_axis_max, seed_max)
        else:
            if all_classes_selected:
                temp_y = df.sort_values('time_obj').groupby('swim_year') \
                    .time_obj.nth(15).max()
                if temp_y > y_axis_max: y_axis_max = temp_y
            else:
                temp_y = df.sort_values('time_obj').groupby('swim_year') \
                    .time_obj.nth(15).max()
                if temp_y > y_axis_max: y_axis_max = temp_y
                y_axis_max = max(y_axis_max, seed_max)
    if selected_event == '50 Yard Freestyle':
        y_axis_max = y_axis_max + timedelta(seconds=0.25)
    else:
        y_axis_max = y_axis_max + timedelta(seconds=2.00)
    return y_axis_max


def generate_y_axis_min(df, selected_event):
    y_axis_min = df.sort_values('time_obj').groupby('swim_year')\
                     .time_obj.nth(0).min() - timedelta(seconds=1)
    if selected_event == '50 Yard Freestyle':
        y_axis_min = y_axis_min + timedelta(seconds=.75)
    return y_axis_min


def generate_legend_name(place, all_classes_selected, selected_class, all_meets_selected):
    if all_classes_selected or all_meets_selected:
        if place == 0:
            return 'Fastest Overall Time'
        elif place == 7:
            return '8th Fastest Time'
        else:
            return '16th Fastest Time'
    else:
        if place == 0:
            return str(selected_class) + ' State Champion'
        elif place == 7:
            return '8th Place'
        else:
            return '16th Place'


def filter_slider_df(df, selected_class):
    if selected_class == 'All Classes':
        selected_class = ['6A', '5A', '4A', '3A', '2A']
    else:
        selected_class = [selected_class]

    df = df[df['full_results']]
    df = df[df['Class'].isin(selected_class)]
    return df


def get_slider_years_range(df):
    time_cutoff = datetime.strptime('2000-01-01 00:12:00.00', '%Y-%m-%d %H:%M:%S.%f')
    df = df[df['time_obj'] < time_cutoff]
    years = np.sort(df['swim_year'].unique()).astype('int')
    return years


def filter_gender(df, selected_gender):
    df = df[df['Gender'] == selected_gender]
    return df


def filter_class(df, selected_class):
    if selected_class == 'All Classes':
        selected_class = ['6A', '5A', '4A', '3A', '2A']
    else:
        selected_class = [selected_class]
    df = df[df['Class'].isin(selected_class)]
    return df


def set_all_classes_selected(selected_class):
    return selected_class == 'All Classes'


def filter_years(df, year_range):
    df = df[df['date_year'] >= year_range[0]]
    df = df[df['date_year'] <= year_range[1]]
    return df


def filter_missing_times(df):
    time_cutoff = datetime.strptime('2000-01-01 00:12:00.00', '%Y-%m-%d %H:%M:%S.%f')
    df = df[df['time_obj'] < time_cutoff]
    return df


def filter_duplicates(df):
    df = df.sort_values(['swim_year', 'time_obj'], ascending=[False, True])\
        .drop_duplicates(['swim_year', 'Swimmer'])
    return df


def ind_relay_lookup(selected_event):
    return selected_event in relay_events.keys()


def team_relay_lookup(selected_event):
    return selected_event in team_relays.keys()


def filter_meets_and_event(df, seeds, selected_event, selected_meets):
    relay_split = ind_relay_lookup(selected_event)
    team_relay = team_relay_lookup(selected_event)
    if team_relay:
        df = df[~df['relay_position'].isin(relay_positions)]
    seeds = seeds[seeds['Event'] == selected_event]
    if selected_meets == 'State Finals':
        df = df[df['Meet'] == 'State Finals']
        if relay_split:
            df = filter_relay_splits(df, selected_event)
        else:
            df = filter_finals_only_event(df, selected_event)
        all_meets_selected = False
    else:
        if relay_split:
            df = filter_relay_splits(df, selected_event)
        else:
            df1 = filter_finals_only_event(df, selected_event)
            df2 = filter_relays_as_individual_swim_event(df, selected_event)
            df = pd.concat([df1, df2])
        all_meets_selected = True
    return df, seeds, all_meets_selected


def filter_finals_only_event(df, selected_event):
    df = df[df['Event'] == selected_event]
    return df


def filter_relay_splits(df, selected_event):
    df_temp = df.drop(df.index)
    for i in range(len(relay_events[selected_event])):
        this_event = relay_events[selected_event][i]['Event']
        this_position = relay_events[selected_event][i]['relay_position']
        df1 = df[df['Event'].isin(this_event)]
        df1 = df1[df1['relay_position'].isin(this_position)]
        df_temp = pd.concat([df_temp, df1])
    df = df_temp
    return df


def filter_relays_as_individual_swim_event(df, selected_event):
    if selected_event == '50 Yard Freestyle':
        df = df[(df['Event'] == '200 Yard Freestyle Relay') & (df['relay_position'] == '1.0')]
    elif selected_event == '100 Yard Freestyle':
        df = df[(df['Event'] == '400 Yard Freestyle Relay') & (df['relay_position'] == '1.0')]
    else:
        df = df[df['Event'] == 'No Relays']  # Ugly way of creating an empty dataframe
    return df


# Create dictionaries for drop-down menus


all_events = [{'label': '200 Free', 'value': '200 Yard Freestyle'},
              {'label': '200 IM', 'value': '200 Yard IM'},
              {'label': '50 Free', 'value': '50 Yard Freestyle'},
              {'label': '100 Fly', 'value': '100 Yard Butterfly'},
              {'label': '100 Free', 'value': '100 Yard Freestyle'},
              {'label': '500 Free', 'value': '500 Yard Freestyle'},
              {'label': '100 Back', 'value': '100 Yard Backstroke'},
              {'label': '100 Breast', 'value': '100 Yard Breaststroke'},
              {'label': 'Medley Relay - 50 Back split',
               'value': '200 Yard Medley Relay - Backstroke Split'},
              {'label': 'Medley Relay - 50 Breast split',
               'value': '200 Yard Medley Relay - Breaststroke Split'},
              {'label': 'Medley Relay - 50 Fly split',
               'value': '200 Yard Medley Relay - Butterfly Split'},
              {'label': 'Relay - 50 Free split',
               'value': '200 Relay - Freestyle Split'},
              {'label': 'Relay - 100 Free split',
               'value': '400 Relay - Freestyle Split'},
              {'label': '200 Medley Relay - Team', 'value': '200 Yard Medley Relay'},
              {'label': '200 Free Relay - Team', 'value': '200 Yard Freestyle Relay'},
              {'label': '400 Free Relay - Team', 'value': '400 Yard Freestyle Relay'}]

individual_state_events = [{'label': '200 Free', 'value': '200 Yard Freestyle'},
                           {'label': '200 IM', 'value': '200 Yard IM'},
                           {'label': '50 Free', 'value': '50 Yard Freestyle'},
                           {'label': '100 Fly', 'value': '100 Yard Butterfly'},
                           {'label': '100 Free', 'value': '100 Yard Freestyle'},
                           {'label': '500 Free', 'value': '500 Yard Freestyle'},
                           {'label': '100 Back', 'value': '100 Yard Backstroke'},
                           {'label': '100 Breast', 'value': '100 Yard Breaststroke'}, ]

team_relays = {'200 Yard Medley Relay': '200 Yard Medley Relay',
              '200 Yard Freestyle Relay': '200 Yard Freestyle Relay',
              '400 Yard Freestyle Relay': '400 Yard Freestyle Relay'}

relay_events = {'200 Yard Medley Relay - Backstroke Split':
                    [{'Event': ['200 Yard Medley Relay'], 'relay_position': ['1.0']}],
                '200 Yard Medley Relay - Breaststroke Split':
                    [{'Event': ['200 Yard Medley Relay'], 'relay_position': ['2.0']}],
                '200 Yard Medley Relay - Butterfly Split':
                    [{'Event': ['200 Yard Medley Relay'], 'relay_position': ['3.0']}],
                '200 Relay - Freestyle Split':
                    [{'Event': ['200 Yard Freestyle Relay'],
                      'relay_position': ['2.0', '3.0', '4.0']},
                     {'Event': ['200 Yard Medley Relay'],
                      'relay_position': ['4.0']}, ],
                '400 Relay - Freestyle Split':
                    [{'Event': ['400 Yard Freestyle Relay'],
                      'relay_position': ['2.0', '3.0', '4.0']}, ]}

gender = [{'label': 'M', 'value': 'M'},
          {'label': 'F', 'value': 'W'}]

performer = [{'label': 'Top Performances', 'value': 'Performances'},
             {'label': 'Top Performers', 'value': 'Performers'}]

classes = [{'label': 'All Classes', 'value': 'All Classes'},
           {'label': '6A', 'value': '6A'},
           {'label': '5A', 'value': '5A'},
           {'label': '4A', 'value': '4A'},
           {'label': '3A', 'value': '3A'},
           {'label': '2A', 'value': '2A'},
           ]

finals_or_overall = [{'label': 'Display Results from State Finals ONLY', 'value': 'State Finals'},
                     {'label': 'Display Results from all meets - State, Regions, etc.', 'value': 'all_results'},
                     ]

table_max_rows = [{'label': 'Display top 10', 'value': 10},
                  {'label': 'Display top 25', 'value': 25}]

unique_high_schools = df_state.School.unique()
unique_high_schools.sort()
high_schools = []
for high_school in unique_high_schools:
    high_schools.append({'label': high_school, 'value': high_school})

individual_events = []
for event in individual_state_events:
    individual_events.append(list(event.values())[1])

df_names = df_state[df_state['Event'].isin(individual_events)]
unique_swimmer_names_1 = df_names.Swimmer.unique()
relay_positions = ['1.0', '2.0', '3.0', '4.0']
df_names = df_state[((df_state['Event'] == '200 Yard Medley Relay')
                     | (df_state['Event'] == '200 Yard Freestyle Relay')
                     | (df_state['Event'] == '400 Yard Freestyle Relay'))
                    & (df_state['relay_position'].isin(relay_positions))]
unique_swimmer_names_2 = df_names.Swimmer.unique()
unique_swimmer_names = np.concatenate((unique_swimmer_names_1, unique_swimmer_names_2), axis=0)
unique_swimmer_names.sort()
unique_swimmer_names = np.unique(unique_swimmer_names)
swimmer_names = []
for name in unique_swimmer_names:
    swimmer_names.append({'label': name, 'value': name})


#########################################################################
#                       APP STRUCTURE                                   #
#########################################################################

vertical = False
app.layout = html.Div([
        html.Div(
            dcc.Tabs(
                tabs=[
                    {'label': 'State Results', 'value': 1},
                    {'label': 'High School Results', 'value': 2},
                    {'label': 'Reports by Swimmer', 'value': 3},
                    {'label': 'State Champions', 'value': 4}
                ],
                value=1,
                id='tabs',
                vertical=vertical,
                style={
                    'width': '75%',
                    'height': '75%',
                    'fontWeight': 'bold',
                    'padding': '10px',
                    'borderBottom': 'solid lightgrey',
                }
            ),
        ),
        html.Div(
            html.Div(id='tab-output'),
            style={'width': '90%', 'float': 'left'}
        )
    ], style={
        'fontFamily': 'Sans-Serif',
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'padding': '10px',
    })


##########################################################################
#                 GRAPH AND TABLE DATA AND SETTINGS                      #
##########################################################################

def generate_figure(df, seeds, y_axis_min, y_axis_max, selected_event,
                    selected_class, all_classes_selected, year_range, all_meets_selected):
    return {
        'data': [
            # Spline Graph for 1st place finisher in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1]+1, 1),
                y=generate_y_data(df, 0, year_range),
                text=generate_hover_text(df, 0, all_classes_selected, all_meets_selected, year_range),
                mode='lines+markers',
                name=generate_legend_name(0, all_classes_selected, selected_class, all_meets_selected),
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for 8th place finisher in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1] + 1, 1),
                y=generate_y_data(df, 7, year_range),
                text=generate_hover_text(df, 7, all_classes_selected, all_meets_selected, year_range),
                mode='lines+markers',
                name=generate_legend_name(7, all_classes_selected, selected_class, all_meets_selected),
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for 16th place finisher in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1] + 1, 1),
                y=generate_y_data(df, 15, year_range),
                text=generate_hover_text(df, 15, all_classes_selected, all_meets_selected, year_range),
                mode='lines+markers',
                name=generate_legend_name(15, all_classes_selected, selected_class, all_meets_selected),
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for slowest qualifying time for State in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1] + 1, 1) if not all_classes_selected else [],
                y=(seeds.groupby('date_year').time_obj.agg('max')
                   if not all_classes_selected else []),
                text=((seeds.sort_values('date_year', ascending=True).time_obj
                       .apply(lambda x: x.strftime('%M:%S.%f')[:-4]))
                      if not all_classes_selected else ""),
                mode='lines+markers',
                name='State Qualifying Time',
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                )
            ],
        'layout': go.Layout(
            title='%s State Finals Times by Year - %s' % (selected_event, selected_class),
            yaxis={'title': 'Times', 'range': [y_axis_max, y_axis_min],
                   'tickformat': '%M:%S.%2f'},
            xaxis={'dtick': 1},
            hovermode='closest',
            hoverlabel=dict(bgcolor='white', font=dict(size=18)),
            height=500,
            dragmode='pan',
            margin=dict(b=30)
            )
      }


def generate_table(df, max_rows=10):
    return html.Table(
            # header
            [html.Tr([html.Th(col) for col in df.columns])] +
            
            # body
            [html.Tr([
                    html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), max_rows))]
            )
        
#####################################################################
#               APP CALLBACKS                                       #
#####################################################################


# Callback for graph - State Swimming Results by year and event
@app.callback(
        dash.dependencies.Output('individual-events', 'figure'),
        [dash.dependencies.Input('event-selection', 'value'),
         dash.dependencies.Input('gender-selection', 'value'),
         dash.dependencies.Input('class-selection', 'value'),
         dash.dependencies.Input('year-slider-selection', 'value'),
         dash.dependencies.Input('meet-selection', 'value')])
def update_figure(selected_event, selected_gender, selected_class, year_range, selected_meets):
    filtered_df_state = df_state[df_state['full_results']]
    filtered_df_state = filter_gender(filtered_df_state, selected_gender)
    filtered_df_state = filter_class(filtered_df_state, selected_class)
    filtered_df_state = filter_years(filtered_df_state, year_range)
    filtered_df_state = filter_missing_times(filtered_df_state)

    filtered_df_seeds = df_seeds
    filtered_df_seeds = filter_gender(filtered_df_seeds, selected_gender)
    filtered_df_seeds = filter_class(filtered_df_seeds, selected_class)
    filtered_df_seeds = filter_years(filtered_df_seeds, year_range)

    all_classes_selected = set_all_classes_selected(selected_class)

    filtered_df_state, filtered_df_seeds, all_meets_selected = \
        filter_meets_and_event(filtered_df_state, filtered_df_seeds, selected_event, selected_meets)
    filtered_df_state = filter_duplicates(filtered_df_state)

    y_axis_min = generate_y_axis_min(filtered_df_state, selected_event)
    y_axis_max = generate_y_axis_max(filtered_df_state, filtered_df_seeds,
                                     all_classes_selected, selected_event)

    return generate_figure(filtered_df_state, filtered_df_seeds, y_axis_min,
                           y_axis_max, selected_event, selected_class, all_classes_selected,
                           year_range, all_meets_selected)


# Callback to update slider value
@app.callback(dash.dependencies.Output('year-slider-selection', 'value'),
              [dash.dependencies.Input('class-selection', 'value')])
def update_slider_value(selected_class):
    filtered_df_state = filter_slider_df(df_state, selected_class)
    years = get_slider_years_range(filtered_df_state)

    if years.max() - years.min() > 10:
        default_year_min = years.max() - 10
    else:
        default_year_min = years.min()
    value = [default_year_min, years.max()]
    return value


# Callback to update slider marks
@app.callback(dash.dependencies.Output('year-slider-selection', 'marks'),
              [dash.dependencies.Input('class-selection', 'value')])
def update_slider_marks(selected_class):
    filtered_df_state = filter_slider_df(df_state, selected_class)
    years = get_slider_years_range(filtered_df_state)

    marks_list = np.arange(years.min(), years.max() + 1, 1).tolist()
    marks = {}
    for mark in marks_list:
        marks[mark] = str(mark)
    return marks


# Callback to update slider min
@app.callback(dash.dependencies.Output('year-slider-selection', 'min'),
              [dash.dependencies.Input('class-selection', 'value')])
def update_slider_min(selected_class):
    filtered_df_state = filter_slider_df(df_state, selected_class)
    years = get_slider_years_range(filtered_df_state)

    slider_min = years.min()
    return slider_min


# Callback to update slider max
@app.callback(dash.dependencies.Output('year-slider-selection', 'max'),
              [dash.dependencies.Input('class-selection', 'value')])
def update_slider_max(selected_class):
    filtered_df_state = filter_slider_df(df_state, selected_class)
    years = get_slider_years_range(filtered_df_state)

    slider_max = years.max()
    return slider_max


# Callback for table - Top Swimmers by event by high-school
@app.callback(
        dash.dependencies.Output('high-school-table', 'children'),
        [dash.dependencies.Input('event-selection', 'value'),
         dash.dependencies.Input('gender-selection', 'value'),
         dash.dependencies.Input('high-school-selection', 'value'),
         dash.dependencies.Input('table-rows', 'value')])
def update_highschool_table(selected_event, selected_gender, selected_highschool, table_rows):
    filtered_df_state = df_state[df_state['School'] == selected_highschool]
    filtered_df_state = filter_gender(filtered_df_state, selected_gender)
    filtered_df_state = filter_missing_times(filtered_df_state)
    df_temp = filtered_df_state.drop(filtered_df_state.index)
    filtered_df_state, filtered_df_seeds, all_meets_selected = \
        filter_meets_and_event(filtered_df_state, df_temp, selected_event, finals_or_overall[1]['value'])
    if ind_relay_lookup(selected_event):
        for index, row in filtered_df_state.iterrows():
            if row['relay_position'] == '1.0':
                if 'Relay' in row['Event']:
                    filtered_df_state.loc[index, 'Event'] = row['Event'] + ' (lead-off)'
    elif (selected_event == '100 Yard Freestyle') | (selected_event == '50 Yard Freestyle'):
        for index, row in filtered_df_state.iterrows():
            if row['relay_position'] == '1.0':
                if 'Relay' in row['Event']:
                    filtered_df_state.loc[index, 'Event'] = row['Event'] + ' (lead-off)'

    filtered_df_state = filtered_df_state.sort_values(['time_obj', 'Swimmer'])\
        .drop_duplicates('Swimmer')
    filtered_df_state['time_obj'] = filtered_df_state['time_obj']\
        .apply(lambda x: x.strftime('%M:%S.%f')[:-4])
    filtered_df_state = filtered_df_state[['Swimmer', 'Event', 'Meet', 'time_obj', 'swim_year']]
    filtered_df_state = filtered_df_state.rename(columns={'swim_year': 'Date',
                                                          'time_obj': 'Best Time'})
    filtered_df_state.insert(0, 'Rank', range(1, len(filtered_df_state)+1))

    return generate_table(filtered_df_state, table_rows)


# Callback for table - Top Swimmers by event by high-school
@app.callback(
        dash.dependencies.Output('swimmer-table', 'children'),
        [dash.dependencies.Input('swimmer-selection', 'value')])
def update_swimmer_table(selected_swimmer):
    filtered_df_state = df_state[df_state['Swimmer'] == selected_swimmer]
    filtered_df_state = filtered_df_state[['Event', 'Meet', 'Date', 'School', 'swim_time', '50 Split',
                                           '100 Split', '150 Split', '200 Split']]
    time_cutoff = datetime.strptime('2000-01-01 00:12:00.00', '%Y-%m-%d %H:%M:%S.%f')
    filtered_df_state['50 Split'] = filtered_df_state['50 Split']\
        .apply(lambda x: "" if x > time_cutoff else x.strftime('%M:%S.%f')[:-4])
    filtered_df_state['100 Split'] = filtered_df_state['100 Split']\
        .apply(lambda x: "" if x > time_cutoff else x.strftime('%M:%S.%f')[:-4])
    filtered_df_state['150 Split'] = filtered_df_state['150 Split'] \
        .apply(lambda x: "" if x > time_cutoff else x.strftime('%M:%S.%f')[:-4])
    filtered_df_state['200 Split'] = filtered_df_state['200 Split'] \
        .apply(lambda x: "" if x > time_cutoff else x.strftime('%M:%S.%f')[:-4])
    filtered_df_state['Date'] = filtered_df_state['Date']\
        .apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
    filtered_df_state = filtered_df_state.sort_values('Date', ascending=False)
    filtered_df_state = filtered_df_state.rename(columns={'swim_time': 'Time'})
    return generate_table(filtered_df_state, max_rows=50)


@app.callback(Output('tab-output', 'children'), [Input('tabs', 'value')])
def display_tab_content(value):
    if value == 1:  # Overview reports
        return html.Div([
            html.Div([
                html.Label('Event'),
                dcc.Dropdown(
                    id='event-selection',
                    options=all_events,
                    value='200 Yard Freestyle'
                    )],
                style=dict(width='250px', display='inline-block', padding='5px', zIndex=1002),
            ),
            html.Div([
                html.Label('Gender'),
                dcc.Dropdown(
                    id='gender-selection',
                    options=gender,
                    value='W'
                    )],
                style=dict(width='100px', display='inline-block', padding='5px', zIndex=1002),
            ),
            html.Div([
                html.Label('Class'),
                dcc.Dropdown(
                    id='class-selection',
                    options=classes,
                    value='All Classes'
                    )],
                style=dict(width='150px', display='inline-block', padding='5px', zIndex=1002),
            ),
            html.Div([
                html.Label(''),
                dcc.RadioItems(
                    id='meet-selection',
                    options=finals_or_overall,
                    value='State Finals'
                    )],
                style=dict(display='inline-block', padding='5px', verticalAlign='bottom')
            ),
            html.Div([
                dcc.Graph(
                    id='individual-events',
                    className='ten columns',
                    config={'modeBarButtonsToRemove': ['zoomIn2d', 'zoomOut2d', 'lasso2d',
                                                       'autoScale2d', 'select2d', 'sendDataToCloud',
                                                       'toggleSpikelines', 'zoom2d']})
            ]),
            html.Div([
                html.Label('Year Range'),
                dcc.RangeSlider(
                    id='year-slider-selection',
                    step=None,
                    allowCross=False,
                )],
                style=dict(width='60%', verticalAlign='bottom', fontWeight='bold',
                           padding='20px', ))  # , display='inline-block'
        ])
    elif value == 2:  # highschool reports
        return html.Div(
            className='ten columns',
            children=[
                html.Div([
                    html.Label('Event'),
                    dcc.Dropdown(
                        id='event-selection',
                        options=all_events,
                        value='200 Yard Freestyle')],
                    style=dict(width='250px', display='inline-block', padding='5px', zIndex=1002),
                ),
                html.Div([
                    html.Label('Gender'),
                    dcc.Dropdown(
                        id='gender-selection',
                        options=gender,
                        value='W')],
                    style=dict(width='100px', display='inline-block', padding='5px', zIndex=1002),
                ),
                html.Div([
                    html.Label('High School'),
                    dcc.Dropdown(
                        id='high-school-selection',
                        placeholder='Type a high-school name...',
                        options=high_schools,
                        value='Alta High School')],
                    style=dict(width='250px', display='inline-block', padding='5px', zIndex=1002)
                ),
                html.Div([
                    dcc.RadioItems(
                        id='table-rows',
                        options=table_max_rows,
                        value=10
                    )],
                    style=dict(display='inline-block', padding='5px', verticalAlign='bottom')
                ),
                html.Div([
                    html.Div(id='high-school-table')],
                    style={'font-size': '12px'},
                ),
            ])
    elif value == 3:  # Individual Swimmer reports
        return html.Div([
            html.Div([
                html.Label('Swimmer Name'),
                dcc.Dropdown(
                    id='swimmer-selection',
                    placeholder='Type a name: Last, First...',
                    options=swimmer_names,
                    value='')],
                style=dict(width='250px', display='table-cell', padding='5px', zIndex=1002)
            ),
            html.Div([
                html.Div(id='swimmer-table')],
                style={'font-size': '12px'},
            ),
        ])
    else:
        return html.Div([])


# Launch App
app.css.append_css({'external_url': css})
# app.css.append_css({.Select {z-index: 1002;}})

if __name__ == '__main__':
    app.run_server(debug=True)
