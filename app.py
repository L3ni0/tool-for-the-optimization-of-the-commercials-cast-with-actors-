from dash import Dash, dash_table, dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd
from functions import read_all_data, split_filter_part

app = Dash(__name__)

colors = {
    'background': '#FFFFFF',
    'text': '#e87000'
}

page_size = 10



df = read_all_data()
df_pivoted = df.pivot_table(index='star',columns='date',values='views').reset_index()


@callback(
    Output('interactive_table', 'data'),
    Input('interactive_table', "page_current"),
    Input('interactive_table', "page_size"),
    Input('interactive_table', 'sort_by'),
    Input('interactive_table', 'filter_query'),
    Input('interactive_table',"derived_virtual_selected_rows"))
def update_table(page_current, page_size, sort_by, filter, selected):
    filtering_expressions = filter.split(' && ')
    dff = df_pivoted
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
    size = page_size
    print(dff.head())
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
    Output('selected_graph','children'),
    Input('interactive_table',"derived_virtual_selected_rows"),
    Input('interactive_table', 'data')
)
def show_selected_rows(selected_rows,data):
    dff = pd.DataFrame(data)
    print(dff.iloc[selected_rows])

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
                          'y': dff[dff['star']==star]['views'],
                          'type': 'bar',
                          'name': star,
                            }
                            for star in dff['star'].unique()
                      ]

                         }
                  )])

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

    html.H1(
        children='InfluStatsHub',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='A fast stats for your Influencers and more', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
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
            column_selectable="single",
            row_selectable="multi",
            selected_rows=[],
            row_deletable=True,
            sort_by=[],
            page_action="custom",
            page_current= 0,
            page_size= page_size,
            ),style={'width': '48%', 'display': 'inline-block'}),

        
        html.Div(id='table-side-graph',style={'backgroundColor': colors['background'],'display': 'inline-block'})],
        ),
    
    html.Div(id='first_graph',style={'backgroundColor': colors['background']}),
    html.Div(id='selected_graph',style={'backgroundColor': colors['background']}),
    html.Div(id='datatable-interactivity-container',style={'width': '48%', 'display': 'inline-block'})
])



if __name__ == '__main__':
    app.run(debug=True)
