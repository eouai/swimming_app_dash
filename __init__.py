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
server = app.server

# Define variables
css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdn.rawgit.com/plotly/dash-app-stylesheets/30b641e2e89753b13e6557b9d65649f13ea7c64c/dash-docs-custom.css',
    ]
#    'https://gonts.googleapis.com/css?family=Dosis',
#    'https://dcnjs.cloudflare.com/ajax.libs/font-awesome/4.7.0/css/font-awesome.min.css',
#

# read in data
# Set data types
# df_SV = pd.read_csv('data/swimming_data_processed.csv')

def lookup(s):
    dates = {date: pd.to_datetime(date) for date in s.unique()}
    return s.map(dates)


headers = ['Unnamed: 0', '100 Split', '150 Split', '200 Split', '250 Split',
           '300 Split', '350 Split', '400 Split', '450 Split', '50 Split',
           '500 Split', 'Class', 'Date', 'Event', 'Gender', 'Meet', 'Place',
           'Points', 'Previous record', 'School', 'Swimmer', 'Year',
           'full_results', 'key', 'relay_position', 'swim_time', 'time_cleanup',
           'time_obj', 'date_time', 'date_year']
dtypes = {'Unnamed: 0': 'int', '100 Split': 'str', '150 Split': 'str', '200 Split': 'str',
          '250 Split': 'str', '300 Split': 'str', '350 Split': 'str', '400 Split': 'str',
          '450 Split': 'str', '50 Split': 'str', '500 Split': 'str', 'Class': 'str',
          'Date': 'str', 'Event': 'str', 'Gender': 'str', 'Meet': 'str', 'Place': 'str',
          'Points': 'str', 'Previous record': 'str', 'School': 'str', 'Swimmer': 'str',
          'Year': 'str', 'full_results': 'bool', 'key': 'int', 'relay_position': 'str',
          'swim_time': 'str', 'time_cleanup': 'str', 'time_obj': 'str', 'date_time': 'str',
          'date_year': 'int'}
df_state = pd.read_csv('data/swimming_data_state_processed.csv', dtype=dtypes)
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


#################################################
#     Helper functions for graph variables      #
#################################################

def generate_hover_text(df, place, all_classes_selected, all_meets_selected):
    min_y_count = get_finals_y_count(df)
    if place > min_y_count:
        names = df.sort_values(['date_year', 'time_obj'], ascending=[False, True])\
            .groupby('date_year')['Swimmer'].last()
        times = df.sort_values(['date_year', 'time_obj'], ascending=[False, True])\
            .groupby('date_year')['time_obj'].last()
        times = [time.strftime('%M:%S.%f')[:-4] for time in times]
        hover_text = names.str.cat(times, sep=' ')
    else:
        names = df.sort_values(['date_year', 'time_obj'], ascending=[False, True])\
            .groupby('date_year')['Swimmer'].nth(place)
        times = df.sort_values(['date_year', 'time_obj'], ascending=[False, True])\
            .groupby('date_year')['time_obj'].nth(place)
        times = [time.strftime('%M:%S.%f')[:-4] for time in times]
        hover_text = names.str.cat(times, sep=' ')
    if all_classes_selected:
        hover_text = hover_text + ' - ' + generate_class_hover_text(df, place)
    if all_meets_selected:
        hover_text = hover_text + ': ' + generate_meet_name(df, place)
        hover_text = hover_text + ' ' + generate_event_name(df, place)
        for i, row in hover_text.iteritems():
            if 'Relay' in row:
                hover_text.replace(row, row + ' (lead-off)', inplace=True)
    return hover_text


def generate_class_hover_text(df, place):
    hover_text = df.sort_values(
        ['date_year', 'time_obj'], ascending=[False, True]) \
        .groupby('date_year')[['Class']].nth(place)['Class'].sort_index(ascending=True)
    return hover_text


def generate_meet_name(df, place):
    hover_text = df.sort_values(
        ['date_year', 'time_obj'], ascending=[False, True]) \
        .groupby('date_year')[['Meet']].nth(place)['Meet'].sort_index(ascending=True)
    return hover_text


def generate_event_name(df, place):
    hover_text = df.sort_values(
        ['date_year', 'time_obj'], ascending=[False, True]) \
        .groupby('date_year')[['Event']].nth(place)['Event'].sort_index(ascending=True)
    return hover_text


def generate_y_data(df, place):
    min_y_count = get_finals_y_count(df)
    if place > min_y_count:
        y_data = df.sort_values('time_obj').groupby('date_year').time_obj.last()
    else:
        y_data = df.sort_values('time_obj').groupby('date_year').time_obj.nth(place)

    return y_data


def get_finals_y_count(df):
    return int(df.sort_values('time_obj').groupby(
        'date_year').time_obj.count().min()) - 1


def generate_y_axis_max(df, df_seeds, all_classes_selected, selected_event):
    min_y_count = get_finals_y_count(df)
    min_y_count2 = get_finals_y_count(df_seeds)
    if all_classes_selected:
        if min_y_count > 15:
            min_y_count = 15
        y_axis_max = df.sort_values('time_obj').groupby('date_year')\
                         .time_obj.nth(min_y_count).max() + timedelta(seconds=2)
    else:
        min_y_count = min(min_y_count, min_y_count2)
        finals_max = df.sort_values('time_obj').groupby('date_year')\
            .time_obj.nth(min_y_count).max()
        seed_max = df_seeds.sort_values('time_obj').groupby('date_year')\
            .time_obj.nth(min_y_count).max()
        y_axis_max = max(finals_max, seed_max) + timedelta(seconds=2)
    if selected_event == '50 Yard Freestyle':
        y_axis_max = y_axis_max - timedelta(seconds=1.75)
    return y_axis_max


def generate_y_axis_min(df, selected_event):
    y_axis_min = df.sort_values('time_obj').groupby('date_year')\
                     .time_obj.nth(0).min() - timedelta(seconds=1)
    if selected_event == '50 Yard Freestyle':
        y_axis_min = y_axis_min + timedelta(seconds=.25)
    return y_axis_min


def generate_legend_name(place, all_classes_selected, selected_class):
    if all_classes_selected:
        if place == 0:
            return 'Fastest Overall State Time'
        elif place == 7:
            return '8th Fastest Overall Time'
        else:
            return '16th Fastest Overall Time'
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
    years = np.sort(df['date_year'].unique()).astype('int')
    return years


def filter_gender(df, selected_gender):
    df = df[df['Gender'] == selected_gender]
    return df


def filter_class(df, selected_class):
    if selected_class == 'All Classes':
        selected_class = ['6A', '5A', '4A', '3A', '2A']
        all_classes_selected = True
    else:
        selected_class = [selected_class]
        all_classes_selected = False
    df = df[df['Class'].isin(selected_class)]
    return df, all_classes_selected


def filter_years(df, year_range):
    df = df[df['date_year'] >= year_range[0]]
    df = df[df['date_year'] <= year_range[1]]
    return df


def filter_missing_times(df):
    time_cutoff = datetime.strptime('2000-01-01 00:12:00.00', '%Y-%m-%d %H:%M:%S.%f')
    df = df[df['time_obj'] < time_cutoff]
    return df


def filter_duplicates(df):
    df = df.sort_values(['date_year', 'time_obj'], ascending=[False, True])\
        .drop_duplicates(['date_year', 'Swimmer'])
    return df


def filter_meets_and_event(df, selected_event, selected_meets):
    df_seeds = df[df['Meet'] == 'State Seed']
    df_seeds = df_seeds[df_seeds['Event'] == selected_event]

    if selected_meets == 'State Finals':
        df = df[df['Meet'] == 'State Finals']
        df = df[df['Event'] == selected_event]
        all_meets_selected = False
    else:
        all_meets_selected = True
        if selected_event == '50 Yard Freestyle':
            df1 = df[df['Event'] == selected_event]
            df2 = df[(df['Event'] == '200 Yard Freestyle Relay') & (df['relay_position'] == '1.0')]
            df = pd.concat([df1, df2])
        elif selected_event == '100 Yard Freestyle':
            df1 = df[df['Event'] == selected_event]
            df2 = df[(df['Event'] == '400 Yard Freestyle Relay') & (df['relay_position'] == '1.0')]
            df = pd.concat([df1, df2])
        else:
            df = df[df['Event'] == selected_event]
    return df, df_seeds, all_meets_selected


# Create dictionaries for dropdown menus
# unique_SV_events = df_SV['Event'].unique()
# SV_events = []
# for event in unique_SV_events:
#    SV_events.append({'label': event, 'value': event})
    
unique_state_events = df_state['Event'].unique()
state_events = []
for event in unique_state_events:
    state_events.append({'label': event, 'value': event})

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

# default_year_min = 2012

unique_high_schools = df_state.School.unique()
unique_high_schools.sort()
high_schools = []
for high_school in unique_high_schools:
    high_schools.append({'label': high_school, 'value': high_school})


#########################################################################
#                       APP STRUCTURE                                   #
#########################################################################

vertical = False
app.layout = html.Div([
        html.Div(
            dcc.Tabs(
                tabs=[
                    {'label': 'Individual Events', 'value': 1},
                    {'label': 'Reports by High School', 'value': 2},
                    {'label': 'Relay Splits', 'value': 3},
                ],
                value=1,
                id='tabs',
                vertical=vertical,
                style={
                    'width': '50%',
                    'height': '50%',
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

def generate_figure(df, df_seeds, y_axis_min, y_axis_max, selected_event,
                    selected_class, all_classes_selected, year_range, all_meets_selected):
    return {
        'data': [
            # Spline Graph for 1st place finisher in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1]+1, 1),
                y=generate_y_data(df, 0),
                text=generate_hover_text(df, 0, all_classes_selected, all_meets_selected),
                mode='lines+markers',
                name=generate_legend_name(0, all_classes_selected, selected_class),
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for 8th place finisher in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1] + 1, 1),
                y=generate_y_data(df, 7),
                text=generate_hover_text(df, 7, all_classes_selected, all_meets_selected),
                mode='lines+markers',
                name=generate_legend_name(7, all_classes_selected, selected_class),
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for 16th place finisher in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1] + 1, 1),
                y=generate_y_data(df, 15),
                text=generate_hover_text(df, 15, all_classes_selected, all_meets_selected),
                mode='lines+markers',
                name=generate_legend_name(15, all_classes_selected, selected_class),
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for slowest qualifying time for State in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1] + 1, 1) if not all_classes_selected else [],
                y=(df_seeds.groupby('date_year').time_obj.agg('max')
                   if not all_classes_selected else []),
                text=((df_seeds.sort_values(['date_year', 'time_obj'], ascending=[False, False])
                       .groupby('date_year')[['Swimmer', 'time_obj']].head(1)['time_obj']
                       .apply(lambda x: x.strftime('%M:%S.%f')[:-4]).sort_index(ascending=False))
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
            yaxis={'title': 'Times', 'range': [y_axis_max,y_axis_min],
                   'tickformat': '%M:%S.%2f'},
            xaxis={'title': 'Year', 'dtick': 1},
            hovermode='closest',
            hoverlabel=dict(bgcolor='white', font=dict(size=18)),
            height=500,
            dragmode='pan'
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
    filtered_df_state, all_classes_selected = filter_class(filtered_df_state, selected_class)
    filtered_df_state = filter_years(filtered_df_state, year_range)
    filtered_df_state = filter_missing_times(filtered_df_state)
    filtered_df_state, filtered_df_state_seeds, all_meets_selected = \
        filter_meets_and_event(filtered_df_state, selected_event, selected_meets)
    filtered_df_state = filter_duplicates(filtered_df_state)

    y_axis_min = generate_y_axis_min(filtered_df_state, selected_event)
    y_axis_max = generate_y_axis_max(filtered_df_state, filtered_df_state_seeds,
                                     all_classes_selected, selected_event)

    return generate_figure(filtered_df_state, filtered_df_state_seeds, y_axis_min,
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


# Callback for table - Top Swimmers by event by highschool
@app.callback(
        dash.dependencies.Output('table-content', 'children'),
        [dash.dependencies.Input('event-selection', 'value'),
         dash.dependencies.Input('gender-selection', 'value'),
         dash.dependencies.Input('high-school-selection', 'value')])
def update_table(selected_event, selected_gender, selected_highschool):
    filtered_df_state = pd.DataFrame(df_state[df_state['Event'] == selected_event])
    filtered_df_state = filtered_df_state[filtered_df_state['Gender'] == selected_gender]
    filtered_df_state = filtered_df_state[filtered_df_state['School'] == selected_highschool]
    best_seed_time = filtered_df_state.sort_values('seed_time_obj').groupby('Swimmer')[
        ['seed_time_obj', 'date_year']].nth(0)
    best_finals_time = filtered_df_state.sort_values('time_obj').groupby('Swimmer')[
        ['time_obj', 'date_year']].nth(0)

    combined = best_seed_time.append(best_finals_time)
    combined = combined.reset_index()
    combined['best_time'] = combined[['seed_time_obj', 'time_obj']].min(axis=1)
    combined = combined.sort_values('best_time').groupby('Swimmer')[['Swimmer', 'date_year', 'best_time']].nth(0)
    combined['best_time'] = combined['best_time'].apply(lambda x: x.strftime('%M:%S.%f')[:-4])
    combined = combined.sort_values('best_time')
    return generate_table(combined)


@app.callback(Output('tab-output', 'children'), [Input('tabs', 'value')])
def display_tab_content(value):
    if value == 2:
        return html.Div([
            html.Div([
                html.Label('Event Select'),
                dcc.Dropdown(
                    id='event-selection',
                    options=state_events,
                    value='200 Yard Freestyle')],
                style=dict(width='200px', display='table-cell', padding='5px', zIndex=1002),
            ),
            html.Div([
                html.Label('Gender Select'),
                dcc.Dropdown(
                    id='gender-selection',
                    options=gender,
                    value='W')],
                style=dict(width='150px', display='table-cell', padding='5px', zIndex=1002),
            ),
            html.Div([
                html.Label('High School Select'),
                dcc.Dropdown(
                    id='high-school-selection',
                    placeholder='Type a high-school name...',
                    options=high_schools,
                    value='Alta High School')],
                style=dict(width='250px', display='table-cell', padding='5px', zIndex=1002)
            ),
            html.Div([
                html.Div(id='table-content')],
                style={'font-size': '12px'},
            ),
            ])
    else:
        return html.Div([
            html.Div([
                html.Label('Event'),
                dcc.Dropdown(
                    id='event-selection',
                    options=state_events,
                    value='200 Yard Freestyle')],
                style=dict(width='200px', display='table-cell', padding='5px', zIndex=1002),
            ),
            html.Div([
                html.Label('Gender'),
                dcc.Dropdown(
                    id='gender-selection',
                    options=gender,
                    value='W'
                    )],
                style=dict(width='150px', display='table-cell', padding='5px', zIndex=1002),
            ),
            html.Div([
                html.Label('Class'),
                dcc.Dropdown(
                    id='class-selection',
                    options=classes,
                    value='All Classes'
                    )],
                style=dict(width='150px', display='table-cell', padding='5px', zIndex=1002),
            ),
            html.Div([
                dcc.RadioItems(
                    id='meet-selection',
                    options=finals_or_overall,
                    value='State Finals'
                    )],
                style=dict(fontWeight='bold')
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
                html.Label('Year Range',
                           style=dict(width='50%', verticalAlign='bottom',
                                      padding='20px', display='inline-block'))]),
            html.Div([
                dcc.RangeSlider(
                    id='year-slider-selection',
                    step=None,
                    allowCross=False,
                )],
                style=dict(width='50%', verticalAlign='bottom',
                           padding='20px', display='inline-block'))
        ])


# Launch App
app.css.append_css({'external_url': css})
# app.css.append_css({.Select {z-index: 1002;}})

if __name__ == '__main__':
    app.run_server(debug=True)
