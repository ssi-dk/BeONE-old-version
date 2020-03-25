import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import components.admin as admin
from dash.dependencies import Input, Output, State
from components import html_components as hc
from components import mongo_interface as mongo_interface
from flask_caching import Cache
from components import import_data as import_data
from components.sample_report import SAMPLE_PAGESIZE, sample_report, children_sample_list_report, samples_next_page
from components.aggregate_report import aggregate_report, update_aggregate_fig, aggregate_species_dropdown
import components.global_vars as global_vars
from dash.exceptions import PreventUpdate

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import datetime
from datetime import datetime as dt
import pathlib
import keys

os.chdir('/Users/stefanocardinale/Documents/SSI/DATABASES/')

df = pd.read_csv('map_testing_data.csv', sep=";")

def samples_list(active, collection_name=None):
    links = [
        {
            "icon": "fa-list",
            "href": ""
        },
        {
            "icon": "fa-money-check",
            "href": "sample-report"
        },
        {
            "icon": "fa-chart-pie",
            "href": "aggregate"
        },
        {
            "icon": "fa-traffic-light",
            "href": "pipeline-report"
        },
        {
            "icon": "fa-link",
            "href": "link-to-files"
        }
    ]
    link_list = []
    for item in links:
        href = "/" + item["href"]
        if collection_name is not None:
            href = "/collection/{}/{}".format(collection_name, item["href"])
        if active == item['href']:
            link_list.append(dcc.Link(
                html.I(className="fas {} fa-fw".format(item['icon'])),
                className="btn btn-outline-secondary active",
                href=href
            ))
        else:
            link_list.append(dcc.Link(
                html.I(className="fas {} fa-fw".format(item['icon'])),
                className="btn btn-outline-secondary",
                href=href
            ))
    return link_list

external_scripts = [
    'https://kit.fontawesome.com/24170a81ff.js',
]

app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=external_scripts
)

app.title = "BeONE"
app.config["suppress_callback_exceptions"] = True
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': keys.cache_location
})
cache_timeout = 60

app.css.append_css(
    {"external_url": "https://fonts.googleapis.com/css?family=Lato"})

app.layout = html.Div(
    id="app-container",
    children=[
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="sample-store", data=[], storage_type='session'),
        dcc.Store(id="project-store", data=[], storage_type='session'),
        dcc.Store(id="param-store", data={}),
        dcc.Store(id="selected-run", data=None),
        dcc.Store(id="selected-species", data=None),
        html.Div([
            html.Div(id='content', children=[

                hc.html_topbar(),
                html.Div([
                    html.Button([
                        html.I(id="topbar-toggle",
                               # n_clicks=0,
                               className="fas fa-angle-double-up"),
                    ], style={"fontSize":'24px'})
                ], style={'padding-left': '750px', 'padding-bottom': '20px'}),
                html.Nav([
                    dcc.Tabs(
                        id="control-tabs",
                        value="isolates-tab",
                        children=[
                            dcc.Tab(className='circos-tab', label="Surveys", value="survey-tab"),
                            dcc.Tab(className='circos-tab', label="Analyses", value="analyses-tab"),
                            dcc.Tab(className='circos-tab', label="Reports", value="reports-tab"),
                            dcc.Tab(className='circos-tab', label="Isolates", value="isolates-tab"),
                        ],
                        className='circos-control-tabs six columns'
                    ),
                ], className='navbar navbar-expand topbar'),

                html.Main([
                        html.Div([
                            html.Div([
                                html.Div(
                                    samples_list('/'),
                                    className="btn-group-lg shadow-sm",
                                    id="selected-view-buttons"
                                ),
                            ], className="col-100", style={'padding-left':'600px', 'padding-top': '30px'}),
                        ], className="row mb-4"),
                    html.Div(id='tab-content', style={"padding-top":"10px"}),
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
        samples = import_data.filter_all(run_names=selected_run,
                                         projection={'name': 1})
        #samples = hc.generate_table(samples)
        if "_id" in samples:
            samples["_id"] = samples["_id"].astype(str)

        samples = samples.to_dict("rows")

        print("The samples are: {}".format(samples))
        return [selected_run, [], samples, species_options]

    elif n_clicks != 0 and n_clicks2 != 0:
        species_options = mongo_interface.get_species_list(selected_run)
        samples = import_data.filter_all(species=[selected_specie], run_names=selected_run)
        #samples = hc.generate_table(samples)

        if "_id" in samples:
            samples["_id"] = samples["_id"].astype(str)

        samples = samples.to_dict("rows")

        selected_specie = ["{}".format(selected_specie)]

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
     Input('project-store', 'data'),
     Input("url", "pathname")]
)
def render_content(tab, n_clicks, selected_run, selected_samples, project_samples, pathname):
    print('render_content')

    if tab == 'survey-tab':
        if project_samples is None:
            raise PreventUpdate
        else:
            samples = project_samples
            print("the number of project samples is {}".format(len(samples)))
            columns_names = global_vars.COLUMNS

            return hc.html_tab_surveys(samples, columns_names)

    elif tab == 'analyses-tab':

            return hc.html_tab_analyses()

    elif tab == 'reports-tab':
        return hc.html_tab_reports()

    elif tab == 'isolates-tab':

        if pathname is None or pathname == "/":
            pathname = "/"
        path = pathname.split("/")

        if path[1] == "collection":
            # collection_view = True
            if len(path) > 2:  # /collection/collectionname
                collection_name = path[2]
                if len(path) > 3:  # /collection/collectionname/section
                    section = path[3]
                else:  # /collection/collectionname
                    section = ""
            else:  # /collection
                section = ""
        else:  # /section
            section = path[1]

        if section == "":
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

            print("the number of samples is: {}".format(len(samples)))
            view = hc.html_tab_bifrost(samples, columns_names)

        elif section == "sample-report":
            print("selected_samples are : {}".format(selected_samples))
            view = sample_report(selected_samples)
        # elif section == "pipeline-report":
        #     view = pipeline_report(sample_store)
        # elif section == "resequence-report":
        #     samples_panel = "d-none"
        #     view = resequence_report(collection_name)
        # elif section == "link-to-files":
        #     view = link_to_files(sample_store)
        elif section == "aggregate":
            view = aggregate_report(selected_samples)
        else:
           # samples_panel = "d-none"
            view = "Not found"

        # if collection_view:
        #     collection_selector_list = "row"
        #     run_list = "d-none"
        #     collections_nav += " active"
        # elif section == "resequence-report":
        #     collection_selector_list = "row"
        #     run_list = "d-none"
        # else:
        #     collection_selector_list = "row d-none"
        #     run_list = ""

        return [view]

@app.callback(
    [Output('run-selector','n_clicks'),
     Output('run-list', 'value'),
     Output('specie-selector', 'n_clicks'),
     Output('species-list', 'value')],
    [Input('reset-button', 'n_clicks')]
)
def update(reset):
    return [0, '', 0, '']

@app.callback(
    [Output("selected-view-buttons", "children")],
    [Input("url", "pathname")],
)
def update_run_name(pathname):

    if pathname is None or pathname == "/":
        pathname = "/"
    path = pathname.split("/")

    samples_nav = "nav-item"
    resequence_nav = "nav-item"

    if path[1] == "collection":
        #collection_view = True
        if len(path) > 2: #/collection/collectionname
            collection_name = path[2]
            if len(path) > 3:  # /collection/collectionname/section
                section = path[3]
            else:  # /collection/collectionname
                section = ""
        else:  # /collection
            section = ""
    else:  # /section
        section = path[1]

    return [samples_list(section)]


@app.callback(
    Output("sample-report", "children"),
    [Input("page-n", "children"),
     Input("sample-store", "data")]
)
def fill_sample_report(page_n, sample_store):
    page_n = int(page_n)
    sample_ids = list(
        map(lambda x: x["_id"], sample_store))
    if len(sample_ids) == 0:
        return None

    data_table = import_data.filter_all(
        sample_ids=sample_ids,
        pagination={"page_size": SAMPLE_PAGESIZE, "current_page": page_n})
    max_page = len(sample_store) // SAMPLE_PAGESIZE
    # We need to have fake radio buttons with the same ids to account for times
    # when not all SAMPLE_PAGESIZE samples are shown and are not taking the ids required by the callback
    html_fake_radio_buttons = html.Div([dcc.RadioItems(
        options=[
            {'label': '', 'value': 'nosample'}
        ],
        value='noaction',
        id="sample-radio-{}".format(n_sample)
    ) for n_sample in range(len(data_table), SAMPLE_PAGESIZE)], style={"display": "none"})
    return [
        html.H4("Page {} of {}".format(page_n + 1, max_page + 1)),
        html.Div(children_sample_list_report(data_table)),
        html_fake_radio_buttons,
        admin.html_qc_expert_form(),
        html.H4("Page {} of {}".format(page_n + 1, max_page + 1)),
        dcc.ConfirmDialog(
            id='qc-confirm',
            message='Are you sure you want to send sample feedback?',
        )
    ]

@app.callback(
    [Output("plot-species", "value"),
     Output("plot-species", "options")],
    [Input("sample-store", "data"),
     Input("plot-species-source", "value")],
    [State("plot-species", "value")]
)
def aggregate_species_dropdown_f(sample_store, plot_species, selected_species):
    return aggregate_species_dropdown(sample_store, plot_species, selected_species)

@app.callback(
    [Output("summary-plot", "figure"),
     Output("mlst-plot", "figure")],
    [Input("plot-species", "value")],
    [State("sample-store", "data"),
    State("plot-species-source", "value")]
)
@cache.memoize(timeout=cache_timeout)  # in seconds
def update_aggregate_fig_f(selected_species, samples, plot_species_source):
    return update_aggregate_fig(selected_species, samples, plot_species_source)


@app.callback(
    Output("page-n",
            "children"),
    [Input("prevpage", "n_clicks_timestamp"),
        Input("prevpage2", "n_clicks_timestamp"),
        Input("nextpage", "n_clicks_timestamp"),
        Input("nextpage2", "n_clicks_timestamp")],
    [State("page-n", "children"),
        State("max-page", "children")]
)
def next_page(prev_ts, prev_ts2, next_ts, next_ts2, page_n, max_page):
    return samples_next_page(prev_ts, prev_ts2, next_ts, next_ts2, page_n, max_page)

@app.callback(
    [Output("topbar-collapse", "is_open")],
    [Input("topbar-toggle", "n_clicks")],
    [State("topbar-collapse", "is_open")]
)
def topbar_toggle(n, is_open):
    print("topbar_toggle")
    if n:
        #print("the number of clicks is {}".format(n))
        if is_open:
            return [False]
        else:
            return [True]
    else:
        raise PreventUpdate


@app.callback(
    Output('datatable-interact-map', 'figure'),
    [Input('datatable-interact-location', 'derived_virtual_selected_rows')]
)
def update_figures(derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df

    mapbox_access_token = "pk.eyJ1Ijoic3RlZmFub2NhcmRpbmFsZSIsImEiOiJjazg3aWUwengwZmg1M2VwcnJzc3pnNmNkIn0.W_t9-PNkeag5yie239nI4Q"

    # Generate a list for hover text display
    # textList = []
    # for area, region in zip(dfs[keyList[0]]['Province/State'], dfs[keyList[0]]['Country/Region']):
    #
    #     if type(area) is str:
    #         if region == "Hong Kong" or region == "Macau" or region == "Taiwan":
    #             textList.append(area)
    #         else:
    #             textList.append(area + ', ' + region)
    #     else:
    #         textList.append(region)

    fig2 = go.Figure(go.Scattermapbox(
        lat=dff['lat'],
        lon=dff['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            color='#ca261d'),
        #     #size=dfs[keyList[0]]['Confirmed'].tolist(),
        #     sizemin=4,
        #     sizemode='area',
        #     sizeref=2. * max(dff[keyList[0]]['Confirmed'].tolist()) / (150. ** 2),
        # ),
        #text=textList,
        hovertemplate="<b>%{text}</b><br><br>" +
                      "%{hovertext}<br>" +
                      "<extra></extra>")
    )
    fig2.update_layout(
        plot_bgcolor='#151920',
        paper_bgcolor='#cbd2d3',
        margin=go.layout.Margin(l=10, r=10, b=10, t=0, pad=40),
        hovermode='closest',
        transition={'duration': 1000},
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            style="light",
            # The direction you're facing, measured clockwise as an angle from true north on a compass
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=55.6659557 if len(derived_virtual_selected_rows) == 0 else dff['lat'][
                    derived_virtual_selected_rows[0]],
                lon=12.5898586 if len(derived_virtual_selected_rows) == 0 else dff['lon'][
                    derived_virtual_selected_rows[0]]
            ),
            pitch=0,
            zoom=5 if len(derived_virtual_selected_rows) == 0 else 4
        )
    )

    return fig2

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8054)
