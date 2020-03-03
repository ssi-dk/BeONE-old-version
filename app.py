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
        dcc.Store(id="param-store", data={}),
        dcc.Store(id="selected-collection", data=None),
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
    [State('datatable-ssi_stamper', "derived_virtual_data")]
)
def select_all(n_clicks, selected_rows):
    if selected_rows is None:
        return [[]]
    else:
        return [[i for i in range(len(selected_rows))]]

@app.callback(
    [Output('run-list', 'options')],
    [Input('db-list', 'value')]
)
def update_runs_dropdown(datab):
    print("update_runs_dropdown")
    if datab is None:
        datab = 'bifrost_upgrade_test'
    return hc.dropdown_run_options(datab)


@app.callback(
    [Output('sample-store', 'data'),
     Output('selected-collection', 'data')],
    [Input('upload-samples', 'n_clicks'),
     Input('run-list', 'value'),
     Input('datatable-ssi_stamper', 'derived_virtual_data'),
     Input('datatable-ssi_stamper', 'derived_virtual_selected_rows'),
     Input('datatable-ssi_stamper', 'active_cell')]
)
def update_selected_samples(n_clicks, selected_run, rows, selected_rows, active_cell):
    print("update_selected_samples")
    #print(prev_sample_store)
    if selected_run is None:
        selected_run = 'stefano_playground'

    if n_clicks == 0:
        raise PreventUpdate

    else:
        #sample_ids = mongo_interface.get_samples_id(run_name, datab)
        #samples = import_data.filter_all(run_names=[selected_run], projection={"_id": 1})
        #if "_id" in samples:
        #    samples["_id"] = samples["_id"].astype(str)
        #samples = samples.to_dict('records')

        data = pd.DataFrame(rows)
        data = data.take(selected_rows)
        samples = data.to_dict('rows')

    #print(len(samples))
    print(data.take(selected_rows))
    #print("selected rows are {}").format(selected_rows)
    return [samples, selected_run]

# @app.callback(
#     Output("sample-store", "data"),
#     [Input("upload-samples", "n_clicks"),
#      Input("param-store", "data"),
#      Input("selected-collection", "data")],
#     [State("run-list", "value"),
#      State("species-list", "value"),
#      State("form-species-source", "value"),
#      State("samples-form", "value"),
#      State("sample-store", "data"),
#      ]
# )
# def update_selected_samples(n_clicks, param_store, collection_name,
#                             run_names, species_list,
#                             species_source,
#                             sample_names, prev_sample_store):
#     print('update_selected_samples')
#     if sample_names is not None and sample_names != "":
#         sample_names = sample_names.split("\n")
#     else:
#         sample_names = param_store.get("sample_names", [])
#     if not run_names:
#         run_names = param_store.get("run", [])
#     if not species_list:
#         species_list = param_store.get("species", [])
#
#     # override if selected collection
#     if collection_name is not None:
#         run_names = [collection_name]
#
#     if (n_clicks == 0 and
#             sample_names == [] and
#             run_names == [] and
#             species_list == []):
#         samples = prev_sample_store
#     else:
#
#         samples = import_data.filter_all(
#             species=species_list, species_source=species_source,
#             run_names=run_names,
#             sample_names=sample_names,
#             projection={"name": 1})
#
#         if "_id" in samples:
#             samples["_id"] = samples["_id"].astype(str)
#         samples = samples.to_dict('records')
#     # if deleted_samples:
#     #     samples = [s for s in samples if s["_id"] not in deleted_samples]
#     print(samples)
#     return samples

@app.callback(
    [Output('tab-content', 'children')],
    [Input('control-tabs', 'value'),
     Input('sample-store', 'data'),
     Input('run-list', 'value')]
)
def render_content(tab, data, selected_run):
    print('render_content')
    print(data)

    if tab == 'projects-tab':
        # sample_name = ["CPO20180130", "DK_SSI_5080"]
        # run_name = ['stefano_playground']
        datab = 'bifrost_upgrade_test'
        print(selected_run)

        sample_ids = mongo_interface.get_samples_id(selected_run, datab)
        samples = import_data.filter_all(sample_ids=sample_ids, projection={"name": 1})
        samples = hc.generate_table(samples)
        samples = samples.to_dict("rows")
        columns_names = global_vars.COLUMNS

        # samples = import_data.filter_all(run_names=run_name, sample_names=sample_name)
        # samples = hc.generate_table(samples)
        # samples = samples[['name']]
        # samples = samples.to_dict("rows")

        return hc.html_tab_projects(samples, columns_names)

    elif tab == 'results-tab':
        return hc.html_tab_results()

    elif tab == 'reports-tab':
        return hc.html_tab_reports()

    elif tab == 'bifrost-tab':

        if selected_run is None:
            selected_run = ['stefano_playground']

        #selected_run = [selected_run]
        datab = 'bifrost_upgrade_test'
        print(selected_run)

        sample_ids = mongo_interface.get_samples_id(selected_run, datab)
        samples = import_data.filter_all(sample_ids=sample_ids)
        samples = hc.generate_table(samples)
        samples = samples.to_dict("rows")
        #columns = ['name','properties.species_detection.summary.detected_species']
        columns_names = global_vars.COLUMNS
        print(samples)

    return hc.html_tab_bifrost(samples, columns_names)

# @app.callback(
#     [
#         #        Output("filter-sample-count", "children"),
#         Output("datatable-ssi_stamper", "data"),
#         #        Output("datatable-ssi_stamper", "virtualization")
#     ],
#     [
#         Input("placeholder0", "children"),
#         Input('run-list', 'value'),
#         Input('db-list', 'value'),
#         Input('control-tabs', 'value')
#         #Input("sample-store", "data")
#     ],
# )
# def update_filter_table(ignore, selected_run, DB, tab):
#     print('update_filter_table')
#     if tab == 'bifrost-tab':
#         if selected_run is None:
#             selected_run = 'stefano_playground'
#         if DB is None:
#             DB = 'bifrost_upgrade_test'
#
#         sample_ids = mongo_interface.get_samples_id('not defined', selected_run, DB)
#         samples = import_data.filter_all(sample_ids=sample_ids)
#
#         samples = hc.generate_table(samples)
#         #print(samples)
#
#     elif tab == 'projects-tab':
#         sample_name = ["CPO20180130", "DK_SSI_5080"]
#         run_name = ['stefano_playground']
#
#         samples = import_data.filter_all(run_names=run_name, sample_names=sample_name)
#         samples = hc.generate_table(samples)
#
#         #test = pd.DataFrame(samples)
#         #print(samples)
#
#     print(samples)
#     return [samples.to_dict("rows")]

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8054)
