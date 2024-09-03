import dash
from dash import html

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Hello World'),

    html.Div(children='''
        Welcome to YAICT - Yet Another Image Captioning Tool.
    '''),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)