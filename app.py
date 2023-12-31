from dash import Dash, dash_table, dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np
from functions import *
from algorytm_genetyczny import Genetic_algorithm_knapsack
import concurrent.futures
import subprocess

app = Dash(__name__)

colors = {
    'background': '#FFFFFF',
    'text': '#e87000'
}

page_size = 10
df_original = read_all_data()
df = df_original.copy()
df['views_per_video'] = df['views'] / df['video_count']
df_pivoted = create_summaries(df)
df_choosed = pd.DataFrame()
df_info = pd.read_csv('data/information/general_information.csv',na_values=['None'],header=0)
min_age = df_info['Age'].min()
max_age = df_info['Age'].max()
min_weight = df_info['Weight'].min()
max_weight = df_info['Weight'].max()
min_height = df_info['Height'].min()
max_height = df_info['Height'].max()
gender_options = list(df_info['Gender'].dropna().unique())
ethnicity_options = list(df_info['Ethnicity'].dropna().unique())
location_option = list(df_info['Birthplace'].dropna().unique())
start_button = 0
vid_button = 0
info_button = 0
star_button = 0
choosed = 0

        

@callback(
    Output('interactive_table', 'data'),
    Input('datatable-page-count', 'value'),
    Input('interactive_table', "page_current"),
    Input('interactive_table', "page_size"),
    Input('interactive_table', 'sort_by'),
    Input('interactive_table', 'filter_query'),
    Input('interactive_table',"derived_virtual_selected_rows"),
    Input('gender_selected', "value"),
    Input('ethnicity_selected', "value"),
    Input('location_selected', 'value'),
    Input('age_selected', 'value'),
    Input('height_selected',"value"),
    Input('weight_selected', "value"),
    Input('max_actors', "value"),
    Input('min_actors', "value"),
    Input('vid_download', 'n_clicks'),
    Input('info_download', 'n_clicks'),
    Input('star_update', 'n_clicks'),
    Input('start', 'n_clicks'),
    Input('max_cost', 'value'))
def update_table(page_num,page_current, page_size, sort_by, filter, selected,gender,ethnicity,location,age,height,weight,max_num,min_num,vid_d,info_d,star_d,button,max_cost):
    global start_button, df_choosed, choosed, vid_button, info_button, start_button

    filtering_expressions = filter.split(' && ')

    if not choosed:
        dff = df_pivoted.copy()
    else:
        dff = df_choosed.copy()
    

    if vid_d > vid_button:
        vid_button = vid_d
        subprocess.run(['python','get_data.py'])

    if info_d > info_button:
        info_button = info_d
        subprocess.run(['python','get_information.py'])

    if star_d > start_button:
        start_button = star_d
        subprocess.run(['python','get_information.py'])

    if button > start_button and max_cost:
        start_button = button
        print('started')
        df_temp = create_summaries(df)

        if gender:
            df_temp = df_temp[df_temp['Gender'].isin(gender)]
        if ethnicity:
            df_temp = df_temp[df_temp['Ethnicity'].isin(ethnicity)]
        if location:
            df_temp = df_temp[df_temp['Birthplace'].isin(location)]
        if age:
            df_temp = df_temp[(age[0] <= df_temp['Age']) &(df_temp['Age'] <= age[1])]
        if height:
            df_temp = df_temp[(height[0] <= df_temp['Height']) & (df_temp['Height'] <= height[1])]
        if weight:
            df_temp = df_temp[(weight[0] <= df_temp['Weight']) & (df_temp['Weight'] <= weight[1])]
        if max_num:
            maxx = int(max_num)
        else:
            maxx = np.Inf
        if min_num:
            minn = int(min_num)
        else:
            minn = 1
            
        with concurrent.futures.ThreadPoolExecutor() as executor:
            print(df_temp.head(5))
            algorithm = Genetic_algorithm_knapsack(weights=list(df_temp['Cost']),values=list(df_temp['Current_Viewership']),max_weight=int(max_cost),max_num_of_items=maxx,min_num_of_items=minn)
            print('steted work')
            future = executor.submit(algorithm.algorithm)
            print('choosed')
            best_bits,best_result = future.result()
            
        
        df_temp['choosed'] = best_bits
        df_temp = df_temp[df_temp['choosed'] == 1]
        dff = df_temp.copy()
        df_choosed = dff.copy()
        choosed = 1 
    else:
        start_button = button
    
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if selected:
        pass
    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )


    page = page_current
    size = page_num
    dff = dff.iloc[page * size: (page + 1) * size].to_dict('records')
    return dff


@callback(
    Output('first_graph', 'children'),
    Input('interactive_table', 'data')
    )
def update_lower_graph(data):
    temp = pd.DataFrame(data)['star']
    dff = df[df['star'].isin(temp)]
    # fig = px.bar(df, x="star", y='video_count')

    # fig.update_layout(
    #     plot_bgcolor=colors['background'],
    #     paper_bgcolor=colors['background'],
    # )

    return html.Div([
        dcc.Graph(id='line_graph_views',

                  figure={
                      'data': [
                          {
                          'x': dff[dff['star']==star]['date'],
                          'y': dff[dff['star']==star]['views'],
                          'type': 'line',
                          'name': star,

                        #   'showlegend':False,
                        #   'marker': {'color': colors['text']},
                            }
                            for star in dff['star'].unique()
                      ],
                        'layout': 
                            {
                            'xaxis': {'title':'Date'},
                            'yaxis' : {'title':'AGV Views per video'},
                            'backgroundColor': '#000000',
                            'transition': 
                                {
                                'duration': 500,
                                'easing': 'cubic-in-out'
                                }   
                            }
                        },style={'width': '48%', 'display': 'inline-block'}
                  ),
        dcc.Graph(id='line_graph_video',

                  figure={
                      'data': [
                          {
                          'x': dff[dff['star']==star]['date'],
                          'y': dff[dff['star']==star]['video_count'],
                          'type': 'line',
                          'name': star,

                        #   'marker': {'color': colors['text']},
                            }
                            for star in dff['star'].unique()
                      ],
                        'layout': 
                            {
                            'xaxis':  {'title':'Date'},
                            'yaxis' : {'title':'Video Count'},
                            'backgroundColor': '#000000',
                            'transition': 
                                {
                                'duration': 500,
                                'easing': 'cubic-in-out'
                                }   
                            }
                        },
                        style={'width': '48%', 'display': 'inline-block'}
                  )
    ])


@callback(
    Output('table-side-graph','children'),
    Input('interactive_table', 'data'))
def update_side_plot(data):
    temp = pd.DataFrame(data)['star']
    dff = df[df['star'].isin(temp)]

    return html.Div([
        dcc.Graph(id='bar_graph',

                  figure={
                      'data': [
                          {
                          'x': dff[dff['star']==star]['star'],
                          'y': dff[dff['star']==star]['views_per_video'],
                          'type': 'bar',
                          'name': star,
                            }
                            for star in dff['star'].unique()
                      ],
                       'layout':
                       {
                            'xaxis': {"title":'Actor'},
                            'yaxis' : {"title":'Summarized Views'},
                       }

                         }
                  )])

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
    html.Div(children=[
        html.Div(children=[
            html.Label('Gender'),
            dcc.Dropdown(gender_options,placeholder='Select Genders',id='gender_selected',multi=True),
            html.Label('Enthnicity'),
            dcc.Dropdown(ethnicity_options,placeholder='Select Ethnicity',id='ethnicity_selected',multi=True),
            html.Label('Location'),
            dcc.Dropdown(location_option,placeholder='Select Location',id='location_selected',multi=True)], 
            style={'color': colors['text'],'width': '33%','display': 'inline-block'}
        ),
        html.Div(children=[
            html.Label('Age'),
            dcc.RangeSlider(min_age,max_age,id='age_selected',allowCross=False),
            html.Label('Height'),
            dcc.RangeSlider(min_height,max_height,id='height_selected',allowCross=False),
            html.Label('Weight'),
            dcc.RangeSlider(min_weight,max_weight,id='weight_selected',allowCross=False)], 
            style={'color': colors['text'],'width': '33%','display': 'inline-block'}
        ),
        html.Div(children=[
            dcc.Textarea(placeholder='min num of actors (optional)',id='min_actors'),
            dcc.Textarea(placeholder='max num of actors (optional)',id='max_actors'),
            dcc.Textarea(placeholder='your cost limit (only numbers)',id='max_cost'),
            html.Button('download_views',id='vid_download',n_clicks=0),
            html.Button('update_info',id='info_download',n_clicks=0),
            html.Button('Choose actors',id='start',n_clicks=0)], 
            style={'color': colors['text'],'width': '33%','display': 'inline-block'}
        ),


    ]),
    html.Div(children=[
        html.Label('actors in one page'),
        dcc.Input(
            id='datatable-page-count',
            type='number',
            min=1,
            max=29,
            value=10),
            ]),

    html.Div(children=[html.Div(children=
            dash_table.DataTable(
            id='interactive_table',
            columns=[
                {'id': i, 'name': i, 'selectable': True} for i in df_pivoted.columns
            ],
            data=df_pivoted.to_dict('records'),
            editable=True,
            filter_action="custom",
            filter_query='',
            sort_action="custom",
            sort_mode="multi",
            row_deletable=True,
            sort_by=[],
            page_action="custom",
            page_current= 0,
            page_size= page_size,
            ),style={'width': '48%','height':'330px','display': 'inline-block','overflowY': 'auto'}),
            

        
        html.Div(id='table-side-graph',style={'backgroundColor': colors['background'],'display': 'inline-block','width': '48%'})],
        ),
    
    
    html.Div(id='first_graph',style={'backgroundColor': colors['background']}),
    html.Div(id='selected_graph',style={'backgroundColor': colors['background']}),
    html.Div(id='datatable-interactivity-container',style={'width': '48%', 'display': 'inline-block'}),
    html.Div(id='algorithm-container',style={'width': '48%', 'display': 'inline-block'}),
    html.Div(children=[
            'if you really need to:',
            html.Button('update star.csv',id='star_update',n_clicks=0)], 
            style={'color': colors['text'],'width': '33%','display': 'inline-block'}
        )

])



if __name__ == '__main__':
    app.run()
