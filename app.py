import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from components import html_components as hc
from components import mongo_interface as mongo_interface
from flask_caching import Cache
from components import import_data as import_data
import components.global_vars as global_vars
from dash.exceptions import PreventUpdate

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
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

KEY = "BIFROST_DB_KEY"

external_scripts = [
    'https://kit.fontawesome.com/24170a81ff.js',
]

app.layout = html.Div(
    id="app-container",
    children=[
        dcc.Store(id="sample-store", data=[], storage_type='session'),
        dcc.Store(id="project-store", data=[], storage_type='session'),
        dcc.Store(id="param-store", data={}),
        dcc.Store(id="selected-run", data=None),
        dcc.Store(id="selected-species", data=None),
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
    [Output('datatable-ssi_stamper', "selected_rows")],
    [Input('select-all-button', 'n_clicks')],
    [State('datatable-ssi_stamper', "data")]
)
def select_all(n_clicks, data):

    if n_clicks == 0:
        return [[]]
    else:
        return [[i for i in range(len(data))]]


@app.callback(
    [Output('run-list', 'options')],
    [Input('db-list', 'value')]
)
def update_runs_dropdown(datab):
    print("update_runs_dropdown")
    if datab is None:
        datab = 'bifrost_prod'

    run_options = hc.dropdown_run_options(datab)[0]
    print(run_options)

    return [run_options]


@app.callback(
    [Output('selected-run', 'data'),
     Output('selected-species', 'data'),
     Output('sample-store', 'data'),
     Output('species-list', 'options')],
    [Input('run-selector', 'n_clicks'),
     Input('specie-selector', 'n_clicks'),
     Input('run-list', 'value'),
     Input('species-list', 'value')]
)
def upload_runs(n_clicks, n_clicks2, selected_run, selected_specie):
    if n_clicks == 0 and n_clicks2 == 0:
        species_options = mongo_interface.get_species_list()

        print(selected_run)
        print(species_options)
        return ['', [], [], species_options]

    elif n_clicks == 0 and n_clicks2 != 0:
        species_options = mongo_interface.get_species_list()
        samples = import_data.filter_all(species=[selected_specie])
        samples = hc.generate_table(samples)
        print(samples)
        samples = samples.to_dict("rows")

        selected_specie = ["{}".format(selected_specie)]
        print(selected_run)
        print(selected_specie)
        print(species_options)
        return ['', selected_specie, samples, species_options]

    elif n_clicks != 0 and n_clicks2 == 0:
        species_options = mongo_interface.get_species_list(selected_run)
        samples = import_data.filter_all(run_names=selected_run)
        samples = hc.generate_table(samples)

        samples = samples.to_dict("rows")
        print(selected_run)
        print(selected_specie)
        print(samples)
        print(species_options)
        return [selected_run, [], samples, species_options]

    elif n_clicks != 0 and n_clicks2 != 0:
        species_options = mongo_interface.get_species_list(selected_run)
        samples = import_data.filter_all(species=[selected_specie], run_names=selected_run)
        samples = hc.generate_table(samples)

        samples = samples.to_dict("rows")

        selected_specie = ["{}".format(selected_specie)]
        print(selected_run)
        print("selected specie is: {}".format(selected_specie))
        print(samples)
        print(species_options)
        return [selected_run, selected_specie, samples, species_options]


@app.callback(
    [Output('project-store', 'data')],
    [Input('upload-samples', 'n_clicks'),
     Input('datatable-ssi_stamper', 'derived_virtual_data'),
     Input('datatable-ssi_stamper', 'derived_virtual_selected_rows')]
)
def update_selected_samples(n_clicks, rows, selected_rows):
    print("update_selected_samples")
    #print(prev_sample_store)
    # if selected_run is None:
    #     selected_run = 'stefano_playground'

    if n_clicks == 0:
        raise PreventUpdate

    else:
        data = pd.DataFrame(rows)
        data = data.take(selected_rows)
        samples = data.to_dict('rows')

    print("the number of selected samples is: {}".format(len(samples)))
    #print("selected rows are {}").format(selected_rows)
    return [samples]


@app.callback(
    [Output('tab-content', 'children')],
    [Input('control-tabs', 'value'),
     Input('run-selector', 'n_clicks'),
     Input('run-list', 'value'),
     Input('sample-store', 'data'),
     Input('project-store', 'data')]
)
def render_content(tab, n_clicks, selected_run, selected_samples, project_samples):
    print('render_content')

    if tab == 'projects-tab':

        samples = project_samples
        print("the number of project samples is {}".format(len(samples)))
        columns_names = global_vars.COLUMNS

        return hc.html_tab_projects(samples, columns_names)

    elif tab == 'results-tab':
        return hc.html_tab_results()

    elif tab == 'reports-tab':
        return hc.html_tab_reports()

    elif tab == 'bifrost-tab':
        if n_clicks == 0 or selected_run == []:
            if selected_samples is not None:
                columns_names = global_vars.COLUMNS
                samples = selected_samples
            else:
                samples = []
                columns_names = global_vars.COLUMNS
        else:
            columns_names = global_vars.COLUMNS
            samples = selected_samples

        print(samples)
        return hc.html_tab_bifrost(samples, columns_names)

@app.callback(
    [Output('run-selector','n_clicks'),
     Output('run-list', 'value'),
     Output('specie-selector', 'n_clicks'),
     Output('species-list', 'value')],
    [Input('reset-button', 'n_clicks')]
)
def update(reset):
    return [0, '', 0, '']

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8054)
