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
# df_SV = pd.read_csv('data/swimming_data_processed.csv')
df_State = pd.read_csv('data/swimming_data_state_processed.csv')
df_State['time_obj'] = df_State.time_obj.apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))
df_State['seed_time_obj'] = df_State.seed_time_obj.apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))

#################################################
#     Helper functions for graph variables      #
#################################################


def generate_hover_text(filtered_df_state_finals, place, overall_selected):
    min_y_count = get_finals_y_count(filtered_df_state_finals)
    if place > min_y_count:
        hover_text = filtered_df_state_finals.sort_values(
            ['date_year', 'time_seconds'], ascending=[False, True])\
            .groupby('date_year')['Swimmer'].last().str.cat(
            (filtered_df_state_finals.sort_values(
                ['date_year', 'time_seconds'], ascending=[False, True])
             .groupby('date_year')['min_obj'].last()), sep=' ')
    else:
        hover_text = filtered_df_state_finals.sort_values(
            ['date_year', 'time_seconds'], ascending=[False, True]) \
            .groupby('date_year')['Swimmer'].nth(place).str.cat(
            (filtered_df_state_finals.sort_values(
                ['date_year', 'time_seconds'], ascending=[False, True])
             .groupby('date_year')['min_obj'].nth(place)), sep=' ')
    if overall_selected:
        hover_text = hover_text + ' - ' + generate_class_hover_text(filtered_df_state_finals, place)
    return hover_text


def generate_class_hover_text(filtered_df_state_finals, place):
    hover_text = filtered_df_state_finals.sort_values(
        ['date_year', 'time_seconds'], ascending=[False, True]) \
        .groupby('date_year')[['Class']].nth(place)['Class'].sort_index(ascending=True)
    return hover_text


def generate_y_data(filtered_df_state_finals, place):
    min_y_count = get_finals_y_count(filtered_df_state_finals)
    if place > min_y_count:
        y_data = filtered_df_state_finals.sort_values('time_obj').groupby('date_year').time_obj.last()
    else:
        y_data = filtered_df_state_finals.sort_values('time_obj').groupby('date_year').time_obj.nth(place)

    return y_data


def get_finals_y_count(filtered_df_state_finals):
    return int(filtered_df_state_finals.sort_values('time_obj').groupby(
        'date_year').time_obj.count().min()) - 1


def generate_y_axis_max(filtered_df_state_finals, filtered_df_state_seeds, overall_selected, selected_event):
    if overall_selected:
        y_axis_max = filtered_df_state_finals.sort_values('time_obj')\
                         .groupby('date_year').time_obj.nth(15).max() + timedelta(seconds=2)
    else:
        finals_max = filtered_df_state_finals.sort_values('time_obj')\
            .groupby('date_year').time_obj.last().max()
        seed_max = filtered_df_state_seeds.sort_values('seed_time_obj')\
            .groupby('date_year').seed_time_obj.last().max()
        y_axis_max = max(finals_max, seed_max) + timedelta(seconds=2)
    if selected_event == '50 Yard Freestyle':
        y_axis_max = y_axis_max - timedelta(seconds=1.75)
    return y_axis_max


def generate_y_axis_min(filtered_df_state_finals, selected_event):
    y_axis_min = filtered_df_state_finals.sort_values('time_obj').groupby('date_year')\
                     .time_obj.nth(0).min() - timedelta(seconds=1)
    if selected_event == '50 Yard Freestyle':
        y_axis_min = y_axis_min + timedelta(seconds=.25)
    return y_axis_min


def generate_legend_name(place, overall_selected, selected_class):
    if overall_selected:
        if place == 0:
            return 'Fastest Overall State Time'
        elif place == 7:
            return '8th Fastest Overall Time'
        else:
            return '16th Fastest Overall Time'
    else:
        if place == 0:
            return str(selected_class[0]) + ' State Champion'
        elif place == 7:
            return '8th Place'
        else:
            return '16th Place'


def filter_slider_df(selected_event, selected_gender, selected_class, df):
    if selected_class == 'Overall':
        selected_class = ['6A', '5A', '4A', '3A', '2A']
    else:
        selected_class = [selected_class]

    filtered_df_state = pd.DataFrame(df_State[df_State['Event'] == selected_event])
    filtered_df_state = filtered_df_state[filtered_df_state['Gender'] == selected_gender]
    filtered_df_state = filtered_df_state[filtered_df_state['Class'].isin(selected_class)]
    filtered_df_state = filtered_df_state[filtered_df_state['full_results']]
    return filtered_df_state


def get_slider_years_range(filtered_df_state):
    time_cutoff = datetime.strptime('2000-01-01 00:12:00.00', '%Y-%m-%d %H:%M:%S.%f')
    filtered_df_state_finals = filtered_df_state[filtered_df_state['time_obj'] < time_cutoff]
    years = np.sort(filtered_df_state_finals['date_year'].unique())
    return years

# Create dictionaries for dropdown menus
# unique_SV_events = df_SV['Event'].unique()
# SV_events = []
# for event in unique_SV_events:
#    SV_events.append({'label': event, 'value': event})
    
unique_state_events = df_State['Event'].unique()
state_events = []
for event in unique_state_events:
    state_events.append({'label': event, 'value': event})

gender = [{'label': 'M', 'value': 'M'},
          {'label': 'F', 'value': 'W'}]

performer = [{'label': 'Top Performances', 'value': 'Performances'},
             {'label': 'Top Performers', 'value': 'Performers'}]

classes = [{'label': 'Overall', 'value': 'Overall'},
           {'label': '6A', 'value': '6A'},
           {'label': '5A', 'value': '5A'},
           {'label': '4A', 'value': '4A'},
           {'label': '3A', 'value': '3A'},
           {'label': '2A', 'value': '2A'},
           ]

# default_year_min = 2012

unique_high_schools = df_State.School.unique()
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

def generate_figure(filtered_df_state_finals, filtered_df_state_seeds, y_axis_min,
                    y_axis_max, selected_event, selected_class, overall_selected,
                    year_range):
    return {
        'data': [
            # Spline Graph for 1st place finisher in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1]+1, 1),
                y=generate_y_data(filtered_df_state_finals, 0),
                text=generate_hover_text(filtered_df_state_finals, 0, overall_selected),
                mode='lines+markers',
                name=generate_legend_name(0, overall_selected, selected_class),
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for 8th place finisher in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1] + 1, 1),
                y=generate_y_data(filtered_df_state_finals, 7),
                text=generate_hover_text(filtered_df_state_finals, 7, overall_selected),
                mode='lines+markers',
                name=generate_legend_name(7, overall_selected, selected_class),
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for 16th place finisher in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1] + 1, 1),
                y=generate_y_data(filtered_df_state_finals, 15),
                text=generate_hover_text(filtered_df_state_finals, 15, overall_selected),
                mode='lines+markers',
                name=generate_legend_name(15, overall_selected, selected_class),
                hoverinfo='text',
                marker=dict(size=10),
                line=dict(shape='spline')
                ),
            # Spline Graph for slowest qualifying time for State in the event
            go.Scatter(
                x=np.arange(year_range[0], year_range[1] + 1, 1) if not overall_selected else [],
                y=(filtered_df_state_seeds.groupby('date_year').seed_time_obj.agg('max')
                   if not overall_selected else []),
                text=(((filtered_df_state_seeds.sort_values(
                    ['date_year', 'seed_time_seconds'], ascending=[False, False])
                        .groupby('date_year')[['Swimmer', 'seed_time_obj', 'seed_min_obj']]
                        .head(1)['seed_min_obj'].apply(lambda x: x[:5]).sort_index(ascending=False)).str.cat(
                    (filtered_df_state_seeds.sort_values(['date_year', 'seed_time_seconds'], ascending=[False, False])
                     .groupby('date_year')[['Swimmer', 'seed_time_obj', 'seed_min_obj']]
                     .head(1)['seed_min_obj'].apply(lambda x: x[-2:])).sort_index(ascending=False),
                    sep='.')) if not overall_selected else ""),
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
         dash.dependencies.Input('year-slider-selection', 'value')])
def update_figure(selected_event, selected_gender, selected_class, year_range):
    if selected_class == 'Overall':
        selected_class = ['6A', '5A', '4A', '3A', '2A']
        overall_selected = True
    else:
        selected_class = [selected_class]
        overall_selected = False
    filtered_df_state = pd.DataFrame(df_State[df_State['Event'] == selected_event])
    filtered_df_state = filtered_df_state[filtered_df_state['Gender'] == selected_gender]
    filtered_df_state = filtered_df_state[filtered_df_state['Class'].isin(selected_class)]
    filtered_df_state = filtered_df_state[filtered_df_state['full_results']]

    time_cutoff = datetime.strptime('2000-01-01 00:12:00.00', '%Y-%m-%d %H:%M:%S.%f')
    filtered_df_state_seeds = filtered_df_state
    filtered_df_state_finals = filtered_df_state[filtered_df_state['time_obj'] < time_cutoff]

    y_axis_min = generate_y_axis_min(filtered_df_state_finals, selected_event)
    y_axis_max = generate_y_axis_max(filtered_df_state_finals, filtered_df_state_seeds,
                                     overall_selected, selected_event)
    print(type(year_range))
    print(year_range[0])
    print(type(year_range[0]))
    return generate_figure(filtered_df_state_finals, filtered_df_state_seeds, y_axis_min,
                           y_axis_max, selected_event, selected_class, overall_selected,
                           year_range)


# Callback to update slider value
@app.callback(dash.dependencies.Output('year-slider-selection', 'value'),
              [dash.dependencies.Input('event-selection', 'value'),
               dash.dependencies.Input('gender-selection', 'value'),
               dash.dependencies.Input('class-selection', 'value')])
def update_slider_value(selected_event, selected_gender, selected_class):
    filtered_df_state = filter_slider_df(selected_event, selected_gender, selected_class, df_State)
    years = get_slider_years_range(filtered_df_state)

    if years.max() - years.min() > 10:
        default_year_min = years.max() - 10
    else:
        default_year_min = years.min()
    value = [default_year_min, years.max()]
    return value


# Callback to update slider marks
@app.callback(dash.dependencies.Output('year-slider-selection', 'marks'),
              [dash.dependencies.Input('event-selection', 'value'),
               dash.dependencies.Input('gender-selection', 'value'),
               dash.dependencies.Input('class-selection', 'value')])
def update_slider_marks(selected_event, selected_gender, selected_class):
    filtered_df_state = filter_slider_df(selected_event, selected_gender, selected_class, df_State)
    years = get_slider_years_range(filtered_df_state)

    marks_list = np.arange(years.min(), years.max() + 1, 1).tolist()
    marks = {}
    for mark in marks_list:
        marks[mark] = str(mark)
    return marks


# Callback to update slider min
@app.callback(dash.dependencies.Output('year-slider-selection', 'min'),
              [dash.dependencies.Input('event-selection', 'value'),
               dash.dependencies.Input('gender-selection', 'value'),
               dash.dependencies.Input('class-selection', 'value')])
def update_slider_min(selected_event, selected_gender, selected_class):
    filtered_df_state = filter_slider_df(selected_event, selected_gender, selected_class, df_State)
    years = get_slider_years_range(filtered_df_state)

    slider_min = years.min()
    return slider_min


# Callback to update slider max
@app.callback(dash.dependencies.Output('year-slider-selection', 'max'),
              [dash.dependencies.Input('event-selection', 'value'),
               dash.dependencies.Input('gender-selection', 'value'),
               dash.dependencies.Input('class-selection', 'value')])
def update_slider_max(selected_event, selected_gender, selected_class):
    filtered_df_state = filter_slider_df(selected_event, selected_gender, selected_class, df_State)
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
    filtered_df_state = pd.DataFrame(df_State[df_State['Event'] == selected_event])
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
                    value='Overall'
                    )],
                style=dict(width='150px', display='table-cell', padding='5px', zIndex=1002),
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
