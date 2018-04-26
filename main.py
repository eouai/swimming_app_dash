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
#from dash.dependencies import Input, Output
import pandas as pd
import re
import numpy as np
import datetime
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
    df_State_raw['Year'] = df_State_raw['Year'].apply(
            lambda x: x if any(x == year for year in map(str.strip, years)) else 'NA')
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
    gender_mapping = {'Boys': 'M', 'Men': 'M', 'Girls':'W', 'Women': 'W'}
    df_State_raw['Gender'].replace(gender_mapping, inplace=True)
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
            lambda x: x.time().strftime('%M:%S%f')[:-4])
    df_State_raw['date_time'] = pd.to_datetime(df_State_raw['Date'])
    df_State_raw['date_year'] = df_State_raw['date_time'].map(lambda x: x.year)
    df_State_raw['seed_time_split'] = df_State_raw['Seed'].apply(
            lambda x: x.split(":"))
    df_State_raw['seed_time_str'] = df_State_raw['seed_time_split'].apply(
            lambda x: '2000-01-01 00:59:59.99' if len(x[0]) == 0 else ('2000-01-01 00:00:' + x[0]
            if len(x) == 1 else '2000-01-01 00:0' +x[0] + ':' + x[1]))
    df_State_raw['seed_time_obj'] = pd.to_datetime(df_State_raw['seed_time_str'])
    df_State_raw['seed_min_obj'] = df_State_raw['seed_time_obj'].apply(
        lambda x: x.time().strftime('%M:%S%f')[:-4])
    df_State_raw['seed_time_seconds'] = df_State_raw['seed_time_split'].apply(
            lambda x: 999.9 if len(x[0]) == 0 else (float(x[0]) 
            if len(x) == 1 else 60 * float(x[0]) + float(x[1])))
    return df_State_raw

df_State = cleanup_state(df_State_raw)

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
    hour_val = 0
    min_val_min = int(df.sort_values('time_seconds')['time_seconds'].head(1))//60
    sec_val_min = int(df.sort_values('time_seconds')
        ['time_seconds'].head(1)%60)-1
    if len(selected_class) == 1:
        min_val_max = int(df.sort_values('seed_time_seconds',ascending=False)
            ['seed_time_seconds'].head(1))//60
        sec_val_max = int(df.sort_values('seed_time_seconds',ascending=False)
            ['seed_time_seconds'].head(1)%60)+2
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

app.config.supress_callback_exceptions=True

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
        html.Button([
                dcc.Link('Sky View Swimmers', href='/page-1')
                ]),
        html.Button([
                dcc.Link('State Swimming Reports', href='/page-2')
                ])])

page_1_layout = html.Div([
    html.Div([
        html.Label('Event Select'),
        dcc.Dropdown(
                id='event-selection',
                options = SV_events,
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
    ])

page_2_layout = html.Div([
    html.Div([
        html.Label('Event Select'),
        dcc.Dropdown(
                id='event-selection',
                options = State_events,
                value='' #events[2]
                )],
        style = dict(width = '50%',
                display = 'table-cell',
                     ),
        ),
    html.Div([
        html.Label('Gender Select'),
        dcc.Dropdown(
            id='gender-selection',
            options = gender,
            value='' #gender[0]
            )],
        style = dict(width = '35%',
                display = 'table-cell',
                     ),
        ),
    html.Div([
        html.Label('Class Select'),
        dcc.Dropdown(
            id='class-selection',
            options = classes,
            value='' #gender[0]
            )],
        style = dict(width = '45%',
                display = 'table-cell',
                     ),
        ),
    html.Div([
        dcc.Graph(id='seed-times')

        ])
    ])

@app.callback(
        dash.dependencies.Output('seed-times', 'figure'),
        [dash.dependencies.Input('event-selection', 'value'),
         dash.dependencies.Input('gender-selection', 'value'),
         dash.dependencies.Input('class-selection', 'value')])
def update_figure(selected_event, selected_gender, selected_class):
    
    filtered_df_State = pd.DataFrame(df_State[df_State['Event'] == selected_event])
    filtered_df_State = filtered_df_State[filtered_df_State['Gender'] == selected_gender]
    filtered_df_State = filtered_df_State[filtered_df_State['Class'].isin(selected_class)]
    print("test")
    year_val, mon_val, day_val, hour_val, min_val_min, sec_val_min \
        ,min_val_max, sec_val_max = get_date_vars(filtered_df_State, selected_class)
    y_axis_min = to_unix_time(datetime.datetime(year_val,mon_val,day_val,hour_val,
                                                min_val_min,sec_val_min))
    y_axis_max = to_unix_time(datetime.datetime(year_val,mon_val,day_val,hour_val,
                                                min_val_max,sec_val_max))
    print(y_axis_min, y_axis_max)
    print(filtered_df_State.sort_values('time_seconds').groupby('date_year').time_obj.nth(15))
    return generate_figure(filtered_df_State, y_axis_min, y_axis_max, selected_event, selected_gender, selected_class)

def generate_figure(filtered_df_State, y_axis_min, y_axis_max, selected_event, selected_gender, selected_class):
    return {
      'data': [
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
              hoverinfo='text'
          ),
          go.Scatter(
              x=np.sort(filtered_df_State['date_year'].unique()),
              y=filtered_df_State.sort_values('time_seconds').groupby('date_year').time_obj.nth(15),
              text=((filtered_df_State.sort_values(
                  ['date_year', 'time_seconds'], ascending=[False, True])
                  .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']]
                  .nth(15)['Swimmer']).sort_index(ascending=True).str.cat(
                  (filtered_df_State.sort_values(
                      ['date_year', 'time_seconds'], ascending=[False, True])
                   .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']]
                   .nth(15)['min_obj'].apply(lambda x: x[:5])).sort_index(ascending=True),
                  sep=' '
              ).str.cat(
                  (filtered_df_State.sort_values(
                      ['date_year', 'time_seconds'], ascending=[False, True])
                   .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']]
                   .nth(15)['min_obj'].apply(lambda x: x[-2:])).sort_index(ascending=True),
                  sep='.'
              )),
              mode='lines+markers',
              name='16th Place',
              hoverinfo='text'
          ),
          go.Scatter(
              x=np.sort(filtered_df_State['date_year'].unique()),
              y=filtered_df_State.sort_values('time_seconds').groupby('date_year').time_obj.nth(7),
              text=((filtered_df_State.sort_values(
                  ['date_year', 'time_seconds'], ascending=[False, True])
                  .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']]
                  .nth(7)['Swimmer']).sort_index(ascending=True).str.cat(
                  (filtered_df_State.sort_values(
                      ['date_year', 'time_seconds'], ascending=[False, True])
                   .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']]
                   .nth(7)['min_obj'].apply(lambda x: x[:5])).sort_index(ascending=True),
                  sep=' '
                  ).str.cat(
                  (filtered_df_State.sort_values(
                      ['date_year', 'time_seconds'], ascending=[False, True])
                   .groupby('date_year')[['Swimmer', 'time_obj', 'min_obj']]
                   .nth(7)['min_obj'].apply(lambda x: x[-2:])).sort_index(ascending=True),
                  sep='.'
              )),
              mode='lines+markers',
              name='8th Place',
              hoverinfo='text'
          ),
          go.Scatter(
              x=np.sort(filtered_df_State['date_year'].unique()),
              y=filtered_df_State.sort_values('time_seconds').groupby('date_year').time_obj.nth(0),
              text=((filtered_df_State[filtered_df_State['Place'] == 1].sort_values(
                    ['date_year','time_seconds'],ascending=[False,True])
                  .groupby('date_year')[['Swimmer','time_obj','min_obj']]
                  .head(1)['Swimmer']).sort_index(ascending=False).str.cat(
                  (filtered_df_State[filtered_df_State['Place'] == 1].sort_values(
                    ['date_year','time_seconds'],ascending=[False,True])
                  .groupby('date_year')[['Swimmer','time_obj','min_obj']]
                  .head(1)['min_obj'].apply(lambda x: x[:5])).sort_index(ascending=False),
                  sep=' '
                  ).str.cat(
                  (filtered_df_State[filtered_df_State['Place'] == 1].sort_values(
                    ['date_year','time_seconds'],ascending=[False,True])
                  .groupby('date_year')[['Swimmer','time_obj','min_obj']]
                  .head(1)['min_obj'].apply(lambda x: x[-2:])).sort_index(ascending=False),
                  sep='.'
          )),
          mode='lines+markers',
          name='State Champion',
          hoverinfo='text'
          )],
      'layout': go.Layout(
          title='State Times by Year',
          yaxis={'title': 'Times',
                 'range': [y_axis_min,y_axis_max],
                 'tickformat': '%M:%S.%2f'},
          xaxis={'title': 'Year',
                 'dtick': 1},
          hovermode='closest'
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
    
