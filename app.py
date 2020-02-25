import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, ClientsideFunction
from components import html_components as hc
from components import mongo_interface as mongo_interface
from flask_caching import Cache
from components import import_data as import_data

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib
import keys

app = dash.Dash(
    __name__,
    meta_tags=[{"content": "width=device-width, initial-scale=1"}],
)

app.title = "beone"
app.config["suppress_callback_exceptions"] = True
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': keys.cache_location
})
cache_timeout = 60

server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Read data
dt = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

KEY = "BIFROST_DB_KEY"

external_scripts = [
    'https://kit.fontawesome.com/24170a81ff.js',
]

def top_bar():
    return html.Nav([
        html.Ul(id='tablist', className="nav nav-tabs", children=[

            html.Li(dcc.Link([
                html.I(className="fas fa-file-medical fa-fw"),
                html.Span("Isolates")
            ], className='nav-link', href="/isolates", style={'fontSize': 24}),
                className='nav-item show active',
                role='presentation'),
            html.Li(dcc.Link(
                [
                    html.I(className='fas fa-chart-pie fa-fw'),
                    html.Span("Analyses")
                ], className='nav-link', href="/analyses",  style={'fontSize': 24}),
                className='nav-item', id="analyses-nav2"),
            html.Li(dcc.Link(
                [
                    html.I(className='fas fa-clipboard fa-fw'),
                    html.Span("Reports")
                ], className='nav-link', href="/reports",  style={'fontSize': 24}),
                className='nav-item', id='reports_test')
        ]),
    ], className='navbar navbar-expand text-black topbar shadow',
        style={'fontSize': 24, 'background-color': "#e3f2fd", 'textAlign': 'center'}
    )

def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Welcome to BeONE")
        ],
    )

app.layout = html.Div(
    id="app-container",
    children=[
        dcc.Store(id="sample-store", data=[], storage_type='session'),
        html.Div([
            html.Div(id='content', children=[
                hc.html_topbar(),
                html.Nav([
                    dcc.Tabs(
                        id="control-tabs",
                        value="bifrost-tab",
                        children=[
                            dcc.Tab(className='circos-tab', label="Projects", value="projects-tab"),
                            dcc.Tab(className='circos-tab', label="Analyses", value="results-tab"),
                            dcc.Tab(className='circos-tab', label="Reports", value="reports-tab"),
                            dcc.Tab(className='circos-tab', label="Bifrost", value="bifrost-tab"),
                        ],
                        className='circos-control-tabs six columns'
                    ),
                ], className='navbar navbar-expand topbar'),
                html.Main([
                    html.Div(id='tab-content'),
                ], className='container-fluid', role='main')
            ])
        ], id='content-wrapper', className="d-flex flex-column",
        )
    ],
)

@app.callback(
    [Output('run-list', 'options'),
     Output('species-list', 'options')],
    [Input('run-list', 'value')])
def update_dropdowns(selected_run):
    return hc.dropdowns_options(selected_run)

# @app.callback(
#     [Output('DBtable_samples', 'data')],
#     [Input('run-list', 'value')]
# )
# def update_samples():
#
#     df = import_data.filter_all(run_names=['stefano_playground'])
#     df = df['name']
#     data = [{'label': j, 'values': j} for j in df]
#     return data

@app.callback(
    [Output('tab-content', 'children')],
    [Input('control-tabs', 'value')]
)
def render_content(tab):
    print('render_content')

    if tab == 'projects-tab':
        return hc.html_tab_projects()

    elif tab == 'results-tab':
        return hc.html_tab_results()

    elif tab == 'reports-tab':
        return hc.html_tab_reports()

    elif tab == 'bifrost-tab':
        return hc.html_tab_bifrost()

@app.callback(
    [
        #        Output("filter-sample-count", "children"),
        Output("datatable-ssi_stamper", "data"),
        #        Output("datatable-ssi_stamper", "virtualization")
    ],
    [
        Input("placeholder0", "children"),
        Input('run-list', 'value')
        #     Input("sample-store", "data")
    ],
)
def update_filter_table(ignore, selected_run):
    print('update_filter_table')
    # if len(sample_store) == 0:
    #     return ["0", [{}], False]
    # sample_ids = list(
    #     map(lambda x: x["_id"], sample_store))

    if selected_run is None:
        selected_run = 'stefano_playground'

    sample_ids = mongo_interface.get_samples_id('not defined', selected_run)
    samples = import_data.filter_all(
        sample_ids=sample_ids)

    samples = hc.generate_table(samples)

    # if len(sample_store) > 500:
    #     virtualization = True
    # else:
    #     virtualization = False
    return [samples.to_dict("rows")]

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8054)
