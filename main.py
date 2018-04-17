#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 17:15:48 2018

@author: burtg-dev
"""

import dash
import flask
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
#from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go


server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

df_raw = pd.read_csv('swimming_data.csv')
df_raw['Year'] = pd.DatetimeIndex(df_raw['Date']).year
df = df_raw[['Event', 'Time Full', 'Year', 'Swimmer', 'Gender']]

app.config.supress_callback_exceptions=True
unique_events = df['Event'].unique()
events = []
for event in unique_events:
    events.append({'label': event, 'value': event})

gender = [{'label': 'M', 'value': 'M'},
          {'label': 'F', 'value': 'F'}
        ]
performer = [{'label': 'Top Performances', 'value': 'Performances'},
             {'label': 'Top Performers', 'value': 'Performers'}]

def generate_table(df, max_rows=10):
    return html.Table(
            #header
            [html.Tr([html.Th(col) for col in df.columns])] +
            
            #body
            [html.Tr([
                    html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), max_rows))]            
            )

@app.callback(
        dash.dependencies.Output('table-content', 'children'),
        [dash.dependencies.Input('event-selection','value'),
         dash.dependencies.Input('gender-selection','value'),
         dash.dependencies.Input('performer-selection', 'value')])
def update_table(selected_event, selected_gender, selected_performance):
    filtered_df = pd.DataFrame(df[df['Event']==selected_event])
    filtered_df = pd.DataFrame(filtered_df[filtered_df['Gender']==selected_gender])
    filtered_df = filtered_df.sort_values('Time Full', ascending=True)
    if selected_performance == "Performers":
        filtered_df = filtered_df.groupby(('Event','Gender','Swimmer')).first()
        filtered_df = filtered_df.reset_index()
        filtered_df = filtered_df.sort_values(by='Time Full')
    return generate_table(filtered_df)
    
app.layout = html.Div([
        html.Label('Event Select'),
        dcc.Dropdown(
                id='event-selection',
                options = events,
                value=events[2]
                ),
        html.Label('Gender Select'),
        dcc.Dropdown(
                id='gender-selection',
                options = gender,
                value=gender[0]
                ),
        html.Label('Performance Select'),
        dcc.Dropdown(
                id='performer-selection',
                options = performer,
                value=performer[0]
                ),
        html.Div([
                html.Div(id='table-content')],
                style={
                        'font-size':'12px'
                        })
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
    
