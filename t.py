import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

# Inicjalizacja aplikacji Dash
app = dash.Dash(__name__)

# Przykładowe dane i wykresy
data = px.data.iris()
scatter_fig = px.scatter(data, x='sepal_width', y='sepal_length', color='species', title='Wykres 1')
bar_fig = px.bar(data, x='species', y='petal_width', title='Wykres 2')

# Układ aplikacji
app.layout = html.Div([
    dcc.Graph(figure=scatter_fig, style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(figure=bar_fig, style={'width': '48%', 'display': 'inline-block'}),
])

if __name__ == '__main__':
    app.run_server(debug=True)