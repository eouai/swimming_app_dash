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
app.config.supress_callback_exceptions=True
server = app.server

# Define variables
css = [
    'https://cdn.rawgit.com/plotly/dash-app-stylesheets/8485c028c19c393e9ab85e1a4fafd78c489609c2/dash-docs-base.css',
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    ]
#    'https://gonts.googleapis.com/css?family=Dosis',
#    'https://dcnjs.cloudflare.com/ajax.libs/font-awesome/4.7.0/css/font-awesome.min.css',
#    'https://cdn.rawgit.com/plotly/dash-app-stylesheets/30b641e2e89753b13e6557b9d65649f13ea7c64c/dash-docs-custom.css',

# read in data
df_SV = pd.read_csv('data/swimming_data_processed.csv')
df_State = pd.read_csv('data/swimming_data_state_processed.csv')
df_State['time_obj'] = df_State.time_obj.apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))
df_State['seed_time_obj'] = df_State.seed_time_obj.apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))

#################################################
#     Helper functions for graph variables      #
#################################################


def generate_hover_text(filtered_df_state, place, selected_class):
    hover_text = filtered_df_state.sort_values(
        ['date_year', 'time_seconds'], ascending=[False, True]) \
        .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']] \
        .nth(place)['Swimmer'].sort_index(ascending=True).str.cat(
        (filtered_df_state.sort_values(['date_year', 'time_seconds'],
                                       ascending=[False, True])
         .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']]
         .nth(place)['min_obj'].apply(lambda x: x[:8])).sort_index(ascending=True), sep=' ')
    if len(selected_class) > 1:
        hover_text = hover_text + ' - ' + generate_class_hover_text(filtered_df_state, place)
    return hover_text


def generate_class_hover_text(filtered_df_state, place):
    hover_text = filtered_df_state.sort_values(
        ['date_year', 'time_seconds'], ascending=[False, True]) \
        .groupby('date_year')[['Class']].nth(place)['Class'].sort_index(ascending=True)
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
          {'label': 'F', 'value': 'W'}]

performer = [{'label': 'Top Performances', 'value': 'Performances'},
             {'label': 'Top Performers', 'value': 'Performers'}]

classes = [{'label': '6A', 'value': ['6A']},
           {'label': '5A', 'value': ['5A']},
           {'label': '4A', 'value': ['4A']},
           {'label': '3A', 'value': ['3A']},
           {'label': '2A', 'value': ['2A']},
           {'label': 'Overall', 'value': ['6A', '5A', '4A', '3A', '2A']}]

#########################################################################
#                   APP STRUCTURE                                       #
#########################################################################

vertical = True
app.layout = html.Div([
        html.Div(
            dcc.Tabs(
                tabs=[
                    {'label': 'State Meet Reports', 'value': 1},
                #    {'label': 'Sky View Reports', 'value': 2},
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
#                 GRAPH AND TABLE DATA AND SETTINGS                      #
##########################################################################

def generate_figure(filtered_df_state, y_axis_min, y_axis_max, selected_event, selected_gender, selected_class):
    return {
        'data': [
            # Spline Graph for 1st place finisher in the event
            go.Scatter(
                x=np.sort(filtered_df_state['date_year'].unique()),
                y=filtered_df_state.sort_values('time_obj').groupby('date_year').time_obj.nth(0),
                text=generate_hover_text(filtered_df_state, 0, selected_class),
                mode='lines+markers',
                name='State Champion',
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for 8th place finisher in the event
            go.Scatter(
                x=np.sort(filtered_df_state['date_year'].unique()),
                y=filtered_df_state.sort_values('time_obj').groupby('date_year').time_obj.nth(7),
                text=generate_hover_text(filtered_df_state, 7, selected_class),
                mode='lines+markers',
                name='8th Place',
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for 16th place finisher in the event
            go.Scatter(
                x=np.sort(filtered_df_state['date_year'].unique()),
                y=filtered_df_state.sort_values('time_obj').groupby('date_year').time_obj.nth(15),
                text=generate_hover_text(filtered_df_state, 15, selected_class),
                mode='lines+markers',
                name='16th Place',
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for slowest qualifying time for State in the event
            go.Scatter(
                x=(np.sort(filtered_df_state['date_year'].unique()) if len(selected_class) == 1 else []),
                y=(filtered_df_state.groupby('date_year').seed_time_obj.agg('max') if
                   len(selected_class) == 1 else []),
                text=(((filtered_df_state.sort_values(
                    ['date_year', 'seed_time_seconds'], ascending=[False, False])
                        .groupby('date_year')[['Swimmer', 'seed_time_obj', 'seed_min_obj']]
                        .head(1)['seed_min_obj'].apply(lambda x: x[:5]).sort_index(ascending=False)).str.cat(
                    (filtered_df_state.sort_values(['date_year', 'seed_time_seconds'], ascending=[False, False])
                     .groupby('date_year')[['Swimmer', 'seed_time_obj', 'seed_min_obj']]
                     .head(1)['seed_min_obj'].apply(lambda x: x[-2:])).sort_index(ascending=False),
                    sep='.')) if len(selected_class) == 1 else ""),
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
            height=500
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
        dash.dependencies.Output('seed-times', 'figure'),
        [dash.dependencies.Input('event-selection', 'value'),
         dash.dependencies.Input('gender-selection', 'value'),
         dash.dependencies.Input('class-selection', 'value')])
def update_figure(selected_event, selected_gender, selected_class):
    filtered_df_state = pd.DataFrame(df_State[df_State['Event'] == selected_event])
    filtered_df_state = filtered_df_state[filtered_df_state['Gender'] == selected_gender]
    filtered_df_state = filtered_df_state[filtered_df_state['Class'].isin(selected_class)]

    time_cutoff = datetime.strptime('2000-01-01 00:12:00.00', '%Y-%m-%d %H:%M:%S.%f')
    y_axis_min = filtered_df_state.sort_values('time_obj').groupby('date_year')\
        .time_obj.nth(0).min() - timedelta(seconds=1)
    if len(selected_class) > 1:
        y_axis_max = filtered_df_state[filtered_df_state['time_obj'] < time_cutoff]\
            .sort_values('time_obj').groupby('date_year').time_obj.nth(15).max() + timedelta(seconds=2)
        if selected_event == '50 Yard Freestyle':
            y_axis_max = y_axis_max - timedelta(seconds=1.5)
    else:
        y_axis_max = filtered_df_state[filtered_df_state['time_obj'] < time_cutoff]\
            .sort_values('time_obj').groupby('date_year').time_obj.last().max()
    if selected_event == '50 Yard Freestyle':
        y_axis_min = y_axis_min + timedelta(seconds=.5)
    return generate_figure(filtered_df_state, y_axis_min, y_axis_max, selected_event, selected_gender, selected_class)


# Callback for table - Sky View Top Swimmers by event
@app.callback(
        dash.dependencies.Output('table-content', 'children'),
        [dash.dependencies.Input('event-selection', 'value'),
         dash.dependencies.Input('gender-selection', 'value'),
         dash.dependencies.Input('performer-selection', 'value')])
def update_table(selected_event, selected_gender, selected_performance):
    filtered_df_sv = pd.DataFrame(df_SV[df_SV['Event'] == selected_event])
    filtered_df_sv = pd.DataFrame(filtered_df_sv[filtered_df_sv['Gender'] == selected_gender])
    filtered_df_sv = filtered_df_sv.sort_values('Time Full', ascending=True)
    if selected_performance == "Performers":
        filtered_df_sv = filtered_df_sv.groupby(('Event', 'Gender', 'Swimmer')).first()
        filtered_df_sv = filtered_df_sv.reset_index()
        filtered_df_sv = filtered_df_sv.sort_values(by='Time Full')
    return generate_table(filtered_df_sv)


@app.callback(Output('tab-output', 'children'), [Input('tabs', 'value')])
def display_tab_content(value):
    if value == 2:
        return html.Div([
            html.Div([
                html.Label('Event Select'),
                dcc.Dropdown(
                    id='event-selection',
                    options=SV_events,
                    value='')],
                style=dict(width='200px', display='table-cell', padding='5px'),
            ),
            html.Div([
                html.Label('Gender Select'),
                dcc.Dropdown(
                    id='gender-selection',
                    options=gender,
                    value='')],
                style=dict(width='150px', display='table-cell', padding='5px'),
            ),
            html.Div([
                html.Label('Performance Select'),
                dcc.Dropdown(
                    id='performer-selection',
                    options=performer,
                    value='')],
                style=dict(width='200px', display='table-cell', padding='5px')
            ),
           html.Div([
                html.Div(id='table-content')],
                style={'font-size': '12px'},
                )])
    else:
        return html.Div([
            html.Div([
                html.Label('Event Select'),
                dcc.Dropdown(
                    id='event-selection',
                    options=State_events,
                    value='')],
                style=dict(width='200px', display='table-cell', padding='5px'),
            ),
            html.Div([
                html.Label('Gender Select'),
                dcc.Dropdown(
                    id='gender-selection',
                    options=gender,
                    value=''
                    )],
                style=dict(width='150px', display='table-cell', padding='5px'),
            ),
            html.Div([
                html.Label('Class Select'),
                dcc.Dropdown(
                    id='class-selection',
                    options=classes,
                    value=''
                    )],
                style=dict(width='150px', display='table-cell', padding='5px'),
            ),
            html.Div([
                dcc.Graph(
                    id='seed-times',
                    className='ten columns',
                    config={'modeBarButtonsToRemove': ['zoomIn2d', 'zoomOut2d', 'lasso2d',
                                                       'autoScale2d', 'select2d', 'sendDataToCloud',
                                                       'toggleSpikelines', 'zoom2d']})
            ])
        ])


# Launch App
app.css.append_css({'external_url': css})

if __name__ == '__main__':
    app.run_server(debug=True)
