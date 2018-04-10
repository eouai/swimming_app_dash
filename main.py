#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 17:15:48 2018

@author: burtg-dev
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
#from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go


app = dash.Dash()
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
        dash.dependencies.Output('text-content', 'children'),
        [dash.dependencies.Input('event-selection','value'),
         dash.dependencies.Input('gender-selection','value')])
def select_index(selected_event, selected_gender):
    print(selected_event)
    print(selected_gender)
    text = pd.DataFrame(df[df['Event']==selected_event])
    text = pd.DataFrame(df[df['Gender']==selected_gender])
    text = text.sort_values('Time Full', ascending=True)
    return generate_table(text)
    
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
        html.Div([
                html.Div(id='text-content')],
                style={
                        'font-size':'12px'
                        })
        ])


    




#@app.callback(dash.dependencies.Output('page-content', 'children'),
#              [dash.dependencies.Input('url', 'pathname')])

#app.layout = html.Div([
#        #html.H4('Swimming App'),
#        dcc.Graph(id='Swimming Data'),
#        dcc.Slider(
#                id='year-slider',
#                min=df['Year'].min(),
#                max=df['Year'].max(),
#                value=df['Year'].min(),
#                step=None,
#                marks={str(year): str(year) for year in df['Year'].unique()}
#                )
#        #generate_table(df)
#        ])

#@app.callback(
#        dash.dependencies.Output('Swimming Data', 'figure'),
#        [dash.dependencies.Input('year-slider', 'value')])
#
#def update_figure(selected_year):
#    filtered_df = df[df.year == selected_year]
#    traces = []
#    for i in filtered_df.cont 

if __name__ == '__main__':
    app.run_server(debug=True)
    
