#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 17:15:48 2018

@author: burtg-dev
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
#import dash_table_experiments as dte
from dash.dependencies import Input, Output
import pandas as pd
#import regex as re
import re
import numpy as np
import datetime
import plotly.graph_objs as go
import flask
import os

#os.chdir('/var/www/FlaskApp/FlaskApp')

# Create app and designate app settings
app = dash.Dash()
app.config.supress_callback_exceptions=True
server = app.server

# Read in initial data sets from CSV.
df_SV_raw = pd.read_csv('swimming_data.csv')
df_State_raw = pd.read_csv('swimming_data_state.csv')

# Define variables
year_mapping = {'09':'FR', '10':'SO', '11':'JR', '12':'SR'}
gender_mapping = {'Boys': 'M', 'Men': 'M', 'Girls':'W', 'Women': 'W'}
css = [
       'https://cdn.rawgit.com/plotly/dash-app-stylesheets/8485c028c19c393e9ab85e1a4fafd78c489609c2/dash-docs-base.css',
#       'https://gonts.googleapis.com/css?family=Dosis',
#       'https://dcnjs.cloudflare.com/ajax.libs/font-awesome/4.7.0/css/font-awesome.min.css',
#        'https://cdn.rawgit.com/plotly/dash-app-stylesheets/30b641e2e89753b13e6557b9d65649f13ea7c64c/dash-docs-custom.css',
       'https://codepen.io/chriddyp/pen/bWLwgP.css'
       ]


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

# Helper functions for graph variables
def to_unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000 

def get_date_vars(df, selected_class):
    #year, month, day values of time objects are not needed
    #swimming results only require min:sec.sec data
    #defaulting all time objects to 2000-01-01
    #timestamp = datetime.date.today()
    year_val = 2000 #timestamp.year
    mon_val = 1 #timestamp.month
    day_val = 1 #timestamp.day
    hour_val = 5
    min_val_min = int(df.sort_values('time_seconds')['time_seconds'].head(1))//60
    sec_val_min = int(df.sort_values('time_seconds')
        ['time_seconds'].head(1)%60)-1
    if len(selected_class) == 1:
        min_val_max = int(df.sort_values('seed_time_seconds',ascending=False)
            ['seed_time_seconds'].head(1))//60
        sec_val_max = int(df.sort_values('seed_time_seconds',ascending=False)
            ['seed_time_seconds'].head(1)%60)+4
    else:
        min_val_max = int(df.sort_values('time_seconds').groupby('date_year') \
            .time_seconds.nth(15).max()//60)
        sec_val_max = int(df.sort_values('time_seconds').groupby('date_year') \
            .time_seconds.nth(15).max()%60+4)
    if sec_val_min < 0:
        min_val_min = min_val_min - 1
        sec_val_min = sec_val_min + 60
    if sec_val_max > 59:
        min_val_max = min_val_max + 1
        sec_val_max = sec_val_max - 60
    return year_val,mon_val,day_val,hour_val,min_val_min,sec_val_min,min_val_max,sec_val_max

def generate_hover_text(filtered_df_State, place, selected_class):
    hover_text = filtered_df_State.sort_values(
        ['date_year', 'time_seconds'], ascending=[False, True]) \
        .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']] \
        .nth(place)['Swimmer'].sort_index(ascending=True).str.cat((filtered_df_State.sort_values(
        ['date_year', 'time_seconds'], ascending=[False, True])
     .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']]
     .nth(place)['min_obj'].apply(lambda x: x[:8])).sort_index(ascending=True), sep = ' ')
    if len(selected_class) > 1:
        hover_text = hover_text + ' - ' + generate_class_hover_text(filtered_df_State, place)
    return hover_text

def generate_class_hover_text(filtered_df_State, place):
    hover_text = filtered_df_State.sort_values(
        ['date_year', 'time_seconds'], ascending=[False, True]) \
        .groupby('date_year')[['Class']].nth(place)['Class'].sort_index(ascending=True)

#        (filtered_df_State[filtered_df_State['Place'] == place].sort_values(
#        ['date_year', 'time_seconds'], ascending=[False, True])
#              .groupby('date_year')['Class'].head(1).sort_index(ascending=False))
#             if len(selected_class) > 1 else "")
#    )
    return hover_text

# Create dictionaries for dropdown menus
unique_SV_events = df_SV['Event'].unique()
SV_events = []
for event in unique_SV_events:
    SV_events.append({'label': event, 'value': event})
    
unique_State_events = df_State['Event'].unique()
State_events = []
for event in unique_State_events:
    State_events.append({'label': event, 'value': event})

gender = [{'label': 'M', 'value': 'M'},
          {'label': 'F', 'value': 'W'}
        ]
performer = [{'label': 'Top Performances', 'value': 'Performances'},
             {'label': 'Top Performers', 'value': 'Performers'}]

classes = [{'label': '6A', 'value': ['6A']},
           {'label': '5A', 'value': ['5A']},
           {'label': '4A', 'value': ['4A']},
           {'label': '3A', 'value': ['3A']},
           {'label': '2A', 'value': ['2A']},
           {'label': 'Overall', 'value': ['6A','5A','4A','3A','2A']}]

#########################################################################
##################  APP STRUCTURE #######################################
#########################################################################

vertical = True
app.layout = html.Div([
        html.Div(
            dcc.Tabs(
                tabs=[
                    {'label': 'State Meet Reports', 'value': 1},
                    {'label': 'Sky View Reports', 'value': 2},
                ],
                value=1,
                id='tabs',
                vertical=vertical,
                style={
                    'height': '100vh',
                    'borderRight': 'thin lightgrey solid',
                    'textAlign': 'left'
                }
            ),
            style={'width': '20%', 'float': 'left'}
        ),
        html.Div(
            html.Div(id='tab-output'),
            style={'width': '80%', 'float': 'right'}
        )
    ], style={
        'fontFamily': 'Sans-Serif',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'padding': '10px',
    })


##########################################################################
################# GRAPH AND TABLE DATA AND SETTINGS ######################
##########################################################################

def generate_figure(filtered_df_State, y_axis_min, y_axis_max, selected_event, selected_gender, selected_class):
    return {
      'data': [
              #Spline Graph for 1st place finisher in the event
          go.Scatter(
              x=np.sort(filtered_df_State['date_year'].unique()),
              y=filtered_df_State.sort_values('time_seconds').groupby('date_year').time_obj.nth(0),
              text=generate_hover_text(filtered_df_State, 0, selected_class),
              mode='lines+markers',
              name='State Champion',
              hoverinfo='text',
              marker=dict(size=10),
              line=dict(shape='spline')
              ),
            #Spline Graph for 8th place finisher in the event
          go.Scatter(
              x=np.sort(filtered_df_State['date_year'].unique()),
              y=filtered_df_State.sort_values('time_seconds').groupby('date_year').time_obj.nth(7),
              text=generate_hover_text(filtered_df_State, 7, selected_class),
              mode='lines+markers',
              name='8th Place',
              hoverinfo='text',
              marker=dict(size=10),
              line=dict(shape='spline')
              ),
            #Spline Graph for 16th place finisher in the event
          go.Scatter(
              x=np.sort(filtered_df_State['date_year'].unique()),
              y=filtered_df_State.sort_values('time_seconds').groupby('date_year').time_obj.nth(15),
              text=generate_hover_text(filtered_df_State, 15, selected_class),
              mode='lines+markers',
              name='16th Place',
              hoverinfo='text',
              marker=dict(size=10),
              line=dict(shape='spline')
              ),
            #Spline Graph for slowest qualifying time for State in the event
            go.Scatter(
              x=(np.sort(filtered_df_State['date_year'].unique()) if len(selected_class) == 1 else []),
              y=(filtered_df_State.groupby('date_year').seed_time_obj.agg('max') if 
                 len(selected_class) == 1 else []),
              text=(((filtered_df_State.sort_values(
                  ['date_year', 'seed_time_seconds'], ascending=[False, False])
                     .groupby('date_year')[['Swimmer', 'seed_time_obj', 'seed_min_obj']]
                     .head(1)['seed_min_obj'].apply(lambda x: x[:5]).sort_index(ascending=False)).str.cat(
                  (filtered_df_State.sort_values(
                      ['date_year', 'seed_time_seconds'], ascending=[False, False])
                   .groupby('date_year')[['Swimmer', 'seed_time_obj', 'seed_min_obj']]
                   .head(1)['seed_min_obj'].apply(lambda x: x[-2:])).sort_index(ascending=False),
                  sep='.'
              )) if len(selected_class) == 1 else ""),
              mode='lines+markers',
              name='State Qualifying Time',
              hoverinfo='text',
              marker=dict(size=10),
              line=dict(shape='spline')
          )
          ],
      'layout': go.Layout(
          title='%s State Finals Times by Year - %s' % (selected_event, selected_class),
          yaxis={'title': 'Times',
                 'range': [y_axis_max,y_axis_min],
                 'tickformat': '%M:%S.%2f'},
          xaxis={'title': 'Year',
                 'dtick': 1},
          hovermode='closest',
          hoverlabel=dict(bgcolor='white', font=dict(size=18)),
          height=500
          )
      }
    
def generate_table(df, max_rows=10):
    return html.Table(
            #header
            [html.Tr([html.Th(col) for col in df.columns])] +
            
            #body
            [html.Tr([
                    html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), max_rows))]
            )
        
#####################################################################
############### APP CALLBACKS #######################################
#####################################################################

# Callback for graph - State Swimming Results by year and event
@app.callback(
        dash.dependencies.Output('seed-times', 'figure'),
        [dash.dependencies.Input('event-selection', 'value'),
         dash.dependencies.Input('gender-selection', 'value'),
         dash.dependencies.Input('class-selection', 'value')])
def update_figure(selected_event, selected_gender, selected_class):
    filtered_df_State = pd.DataFrame(df_State[df_State['Event'] == selected_event])
    filtered_df_State = filtered_df_State[filtered_df_State['Gender'] == selected_gender]
    filtered_df_State = filtered_df_State[filtered_df_State['Class'].isin(selected_class)]
    year_val, mon_val, day_val, hour_val, min_val_min, sec_val_min \
        ,min_val_max, sec_val_max = get_date_vars(filtered_df_State, selected_class)
    if selected_event == '50 Yard Freestyle':
        sec_val_max = sec_val_max - 2
        sec_val_min = sec_val_min + 1
    y_axis_min = to_unix_time(datetime.datetime(year_val,mon_val,day_val,hour_val,
                                                min_val_min,sec_val_min))
    y_axis_max = to_unix_time(datetime.datetime(year_val,mon_val,day_val,hour_val,
                                                min_val_max,sec_val_max))
    # need to reduce y_axis_min slightly so that display times that are nearly equal
    # to the range min don't get cut off.
    y_axis_min = y_axis_min - 100
    return generate_figure(filtered_df_State, y_axis_min, y_axis_max, selected_event, selected_gender, selected_class)

# Callback for table - Sky View Top Swimmers by event
@app.callback(
        dash.dependencies.Output('table-content', 'children'),
        [dash.dependencies.Input('event-selection','value'),
         dash.dependencies.Input('gender-selection','value'),
         dash.dependencies.Input('performer-selection', 'value')])
def update_table(selected_event, selected_gender, selected_performance):
    filtered_df_SV = pd.DataFrame(df_SV[df_SV['Event']==selected_event])
    filtered_df_SV = pd.DataFrame(filtered_df_SV[filtered_df_SV['Gender']==selected_gender])
    filtered_df_SV = filtered_df_SV.sort_values('Time Full', ascending=True)
    if selected_performance == "Performers":
        filtered_df_SV = filtered_df_SV.groupby(('Event','Gender','Swimmer')).first()
        filtered_df_SV = filtered_df_SV.reset_index()
        filtered_df_SV = filtered_df_SV.sort_values(by='Time Full')
    return generate_table(filtered_df_SV)
  
@app.callback(Output('tab-output', 'children'), [Input('tabs', 'value')])
def display_tab_content(value):
    if value == 2:
        return html.Div([
            html.Div([
                html.Label('Event Select'),
                dcc.Dropdown(
                        id='event-selection',
                        options = SV_events,
                        value='' #events[2]
                        )],
                style = dict(width = '200px',
                             display = 'table-cell',
                             padding = '5px',
                             ),
                ),
           html.Div([
                html.Label('Gender Select'),
                dcc.Dropdown(
                        id='gender-selection',
                        options = gender,
                        value='' #gender[0]
                        )],
                style = dict(width = '150px',
                             display = 'table-cell',
                             padding='5px',
                             ),
                ),
           html.Div([
                html.Label('Performance Select'),
                dcc.Dropdown(
                        id='performer-selection',
                        options = performer,
                        value='' #performer[0]
                        )],
                style = dict(width = '200px',
                             display = 'table-cell',
                             padding='5px',
                             ),
                ),
           html.Div([
                html.Div(id='table-content')],
                style={
                    'font-size':'12px'
                    },
                )])
    else:
        return  html.Div([
            html.Div([
                html.Label('Event Select'),
                dcc.Dropdown(
                        id='event-selection',
                        options = State_events,
                        value='' #events[2]
                        )],
                style = dict(width = '200px',
                        display = 'table-cell',
                        padding='5px',
                        ),
                ),
            html.Div([
                html.Label('Gender Select'),
                dcc.Dropdown(
                    id='gender-selection',
                    options = gender,
                    value='' #gender[0]
                    )],
                style = dict(width = '150px',
                        display = 'table-cell',
                        padding='5px',
                        ),
                ),
            html.Div([
                html.Label('Class Select'),
                dcc.Dropdown(
                    id='class-selection',
                    options = classes,
                    value='' #gender[0]
                    )],
                style = dict(width = '100px',
                        display = 'table-cell',
                        padding='5px',
                        ),
                ),
            html.Div([
                dcc.Graph(id='seed-times')
                ])
            ])


# Lauch App
app.css.append_css({'external_url': css})

if __name__ == '__main__':
    app.run_server(debug=True)
