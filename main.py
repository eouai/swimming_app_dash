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

df_SV_raw = pd.read_csv('swimming_data.csv')

def cleanup_SV(df_SV_raw):
    df_SV_raw['Year'] = pd.DatetimeIndex(df_SV_raw['Date']).year
    df_SV_raw = df_SV_raw[['Event', 'Time Full', 'Year', 'Swimmer', 'Gender']]
    return df_SV_raw

df_SV = cleanup_SV(df_SV_raw)

df_State_raw = pd.read_csv('swimming_data_state.csv')

def cleanup_state(df_State_raw):
    df_State_raw['Place'] = df_State_raw['Place'].fillna(0)
    df_State_raw['Place'] = df_State_raw['Place'].apply(lambda x: int(x))
    df_State_raw['Year'] = df_State_raw['Year'].fillna('NA')
    df_State_raw['Year'] = df_State_raw['Year'].apply(lambda x: '09' if x=='9' else x)
    years = [' FR ',' SO ',' JR ',' SR ',' 09 ',' 10 ',' 11 ',' 12 ']
    df_State_raw['Year'] = df_State_raw['Year'].apply(lambda x: x if any(x == year for year in map(str.strip, years)) else 'NA')
    for index, row in df_State_raw.iterrows():
        school_name = row['School']
        for year in years:
            if year in school_name:
                if row['Year'] not in map(str.strip, years):
                    df_State_raw.loc[index, 'Year'] = year.strip()
                df_State_raw.loc[index, 'School'] = school_name[school_name.find(year)+4:]
                break
    year_mapping = {'09':'FR', '10':'SO', '11':'JR', '12':'SR'}
    df_State_raw['Year'].replace(year_mapping, inplace=True)
    gender_mapping = {'Boys': 'Men', 'Girls':'Women'}
    df_State_raw['Gender'].replace(gender_mapping, inplace=True)
    return df_State_raw
 

df_State = cleanup_state(df_State_raw)
    

app.config.supress_callback_exceptions=True

unique_events = df_SV['Event'].unique()
events = []
for event in unique_events:
    events.append({'label': event, 'value': event})

gender = [{'label': 'M', 'value': 'M'},
          {'label': 'F', 'value': 'F'}
        ]
performer = [{'label': 'Top Performances', 'value': 'Performances'},
             {'label': 'Top Performers', 'value': 'Performers'}]


df_SV = cleanup_SV(df_SV_raw)
css = [
       'https://cdn.rawgit.com/plotly/dash-app-stylesheets/8485c028c19c393e9ab85e1a4fafd78c489609c2/dash-docs-base.css',
       'https://gonts.googleapis.com/css?family=Dosis',
       'https://dcnjs.cloudflare.com/ajax.libs/font-awesome/4.7.0/css/font-awesome.min.css'
       ]
#        'https://cdn.rawgit.com/plotly/dash-app-stylesheets/30b641e2e89753b13e6557b9d65649f13ea7c64c/dash-docs-custom.css',

app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
        ]) 
 
index_page = html.Div([
        html.A([
                dcc.Link('Sky View Swimmers', href='/page-1')
                ]),
        html.A([
                dcc.Link('State Swimming Reports', href='/page-2')
                ])])

page_1_layout = html.Div([
        html.Label('Event Select'),
        dcc.Dropdown(
                id='event-selection',
                options = events,
                value='' #events[2]
                ),
        html.Label('Gender Select'),
        dcc.Dropdown(
                id='gender-selection',
                options = gender,
                value='' #gender[0]
                ),
        html.Label('Performance Select'),
        dcc.Dropdown(
                id='performer-selection',
                options = performer,
                value='' #performer[0]
                ),
        html.Div([
                html.Div(id='table-content')],
                style={
                        'font-size':'12px'
                        })
        ])
  
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
    filtered_df_SV = pd.DataFrame(df_SV[df_SV['Event']==selected_event])
    filtered_df_SV = pd.DataFrame(filtered_df_SV[filtered_df_SV['Gender']==selected_gender])
    filtered_df_SV = filtered_df_SV.sort_values('Time Full', ascending=True)
    if selected_performance == "Performers":
        filtered_df_SV = filtered_df_SV.groupby(('Event','Gender','Swimmer')).first()
        filtered_df_SV = filtered_df_SV.reset_index()
        filtered_df_SV = filtered_df_SV.sort_values(by='Time Full')
    return generate_table(filtered_df_SV)
    
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname is None:
        return ''
    if pathname.endswith('/') and pathname != '/':
        pathname = pathname[:len(pathname) - 1]
    if pathname == '/page-1':
        return page_1_layout
    if pathname == '/page-2':
        return page_2_layout
    else:
        return index_page

app.css.append_css({'external_url': css})

if __name__ == '__main__':
    app.run_server(debug=True)
    
