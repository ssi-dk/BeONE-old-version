import os
import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask_caching import Cache
import bifrost.admin as admin
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
import re
import io

from components.import_data import *
from components import html_components as hc

from bifrost.sample_report import SAMPLE_PAGESIZE, sample_report, children_sample_list_report, samples_next_page
from bifrost.aggregate_report import aggregate_report, update_aggregate_fig, aggregate_species_dropdown
import components.global_vars as global_vars
from dash.exceptions import PreventUpdate

import react_phylo
import pandas as pd
import plotly.graph_objects as go
import keys

os.chdir('/Users/stefanocardinale/Documents/SSI/DATABASES/')

data = pd.read_csv('map_testing_data.csv', sep=";")

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

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    data = df.to_dict('records')
    columns = [{'name': i, 'id': i} for i in df.columns]

    return [data, columns]

external_scripts = [
    'https://kit.fontawesome.com/24170a81ff.js',
    '/Users/stefanocardinale/Documents/SSI/git.repositories3/phylocanvas/phylocanvas/dev/index.js'
]

app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=external_scripts,
 #   assets_external_path=['/Users/stefanocardinale/Documents/SSI/git.repositories3/phylocanvas/phylocanvas/dev/data']
)
#app.scripts.config.serve_locally = False

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
    id="wrapper",
    children=[
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="sample-store", data=[], storage_type='session'),
        dcc.Store(id="analysis-store", data=[], storage_type='session'),
        dcc.Store(id="survey-store", data=[], storage_type='session'),
        dcc.Store(id="selected-run", data=None),
        dcc.Store(id="selected-species", data=None),
            html.Div([
                hc.sidebar2(),
            ], className="navbar-nav", id='sidebar-nav', style={'width': '24%', "display": "inline-block"}),

            html.Div(children=[
                html.Div([
                    html.Main([

                        html.Nav([
                            dcc.Tabs(
                                id='control-tabs',
                                value='isolates-tab',
                                className='circos-control-tabs',
                                children=[
                                    dcc.Tab(className='circos-tab', label='Surveys', value='survey-tab'),
                                    dcc.Tab(className='circos-tab', label='Analyses', value='analyses-tab'),
                                    dcc.Tab(className='circos-tab', label='Reports', value='reports-tab'),
                                    dcc.Tab(className='circos-tab', label='Isolates', value='isolates-tab'),
                                ]
                            ),
                        ], className='navbar topbar', style={"fontSize": "2rem"}),
                        html.Div(
                            samples_list('/'),
                            className="btn-group-lg shadow-sm",
                            id="selected-view-buttons"
                        ),
                        html.Div(id='tab-content', style={"padding-top": "10px"}),
                    ], className='container-fluid', role='main')
                ], id="content"),
            ], id="content-wrapper", style={'width': '74%', "display": "inline-block"}
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

    run_options = hc.dropdown_run_options()[0]
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
        species_options = get_species_list()

        print("The selected run is: {}".format(selected_run))
        print("Species options are: {}".format(species_options))
        return ['', [], [], species_options]

    elif n_clicks == 0 and n_clicks2 != 0:
        species_options = get_species_list()
        samples = filter_all(species=[selected_specie], projection={'_id': 1, 'name': 1})
        # samples = hc.generate_table(samples)
        if "_id" in samples:
            samples["_id"] = samples["_id"].astype(str)

        print("The samples are: {}".format(samples))
        samples = samples.to_dict("rows")

        selected_specie = ["{}".format(selected_specie)]
        print("The selected run is: {}".format(selected_run))
        print("The selected specie is: {}".format(selected_specie))
        print("Species options are: {}".format(species_options))
        return ['', selected_specie, samples, species_options]

    elif n_clicks != 0 and n_clicks2 == 0:
        species_options = get_species_list(selected_run)
        samples = filter_all(run_names=selected_run, projection={'_id': 1, 'name': 1})
        #samples = hc.generate_table(samples)
        if "_id" in samples:
            samples["_id"] = samples["_id"].astype(str)

        samples = samples.to_dict("rows")

        print("The samples are: {}".format(samples))
        print("The species list is: {}".format(species_options))
        print("The run name is: {}".format(selected_run))
        return [selected_run, [], samples, species_options]

    elif n_clicks != 0 and n_clicks2 != 0:
        species_options = get_species_list(selected_run)
        samples = filter_all(species=[selected_specie], run_names=selected_run, projection={'_id': 1, 'name': 1})
        #samples = hc.generate_table(samples)

        if "_id" in samples:
            samples["_id"] = samples["_id"].astype(str)

        samples = samples.to_dict("rows")

        selected_specie = ["{}".format(selected_specie)]

        return [selected_run, selected_specie, samples, species_options]


@app.callback(
    [Output('analysis-store', 'data')],
    [Input('upload-samples', 'n_clicks'),
     Input('datatable-ssi_stamper', 'derived_virtual_data'),
     Input('datatable-ssi_stamper', 'derived_virtual_selected_rows')]
)
def update_selected_samples(n_clicks, rows, selected_rows):
    print("update_selected_samples")

    if n_clicks == 0:
        raise PreventUpdate

    else:
        data = pd.DataFrame(rows)
        data = data.take(selected_rows)
        samples = data.to_dict('rows')

    print("the number of selected samples is: {}".format(len(samples)))

    return [samples]

@app.callback(
    [Output('survey-store', 'data'),
     Output('save-survey', 'n_clicks'),
     Output('load-button', 'n_clicks')],
    [Input('metadata-table', 'derived_virtual_data'),
     Input('metadata-table', 'derived_virtual_selected_rows')]
)
def store_survey(rows, selected_rows):
    print("store_survey")

    data = pd.DataFrame(rows)
    data = data.take(selected_rows)
    survey = data.to_dict('rows')

    return [survey, 0, 0]

@app.callback(
    [Output('metadata-table', 'data'),
     Output('metadata-table', 'columns')],
    [Input('upload-survey-button', 'n_clicks'),
     Input('load-button', 'n_clicks'),
     Input('surveys-list', 'value')],
    [State('upload-survey', 'contents'),
     State('upload-survey', 'filename')]
)
def load_survey(n_clicks, n_clicks2, selected_survey, content, filename):
    print("load_survey")

    if n_clicks2 == 0:

        raise PreventUpdate

    elif n_clicks == 1 and n_clicks2 == 0:
        raise PreventUpdate

    elif n_clicks2 == 1:
        if selected_survey is None and content is None:
            raise PreventUpdate

        elif selected_survey is None and content is not None:
            df, columns = parse_contents(content, filename)
            print(df)

            return df, columns

        elif selected_survey is not None:
            print(str(selected_survey))
            df = get_survey(selected_survey)
            df = df[0]['cases']
            columns = [{"name": k, "id": k} for k, v in df[0].items()]
            print(df)
            print(columns)

            return df, columns

@app.callback(
    [Output('tab-content', 'children')],
    [Input('date-picker-select', 'start_date'),
     Input('date-picker-select', 'end_date'),
     Input('control-tabs', 'value'),
     Input('run-selector', 'n_clicks'),
     Input('run-list', 'value'),
     Input('sample-store', 'data'),
     Input('analysis-store', 'data')],
     [State("url", "pathname")]
)
def render_content(start_date, end_date, tab, n_clicks, selected_run, selected_samples, project_samples, pathname):
    print('render_content')
    if start_date is not None:
        start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        #start_date_string = start_date.strftime('%Y-%m-%d')
        print(start_date)
    if end_date is not None:
        end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')
        #print(start_date)

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

    if tab == 'survey-tab':
        return hc.html_tab_surveys(section)


    elif tab == 'analyses-tab':
        if section == "":
            if project_samples is None:
                raise PreventUpdate
            else:
                samples = project_samples
                print("the number of project samples is {}".format(len(samples)))
                print(project_samples)
                columns_names = global_vars.COLUMNS

                return hc.html_tab_analyses(samples, columns_names)
        elif section == "sample-report":
            view = html.Div([
                    html.Div([
                        dcc.Upload(id='upload-data', children=[
                            dbc.Button('Upload Newick File', n_clicks=0, size='sm')])
                    ], style={'padding-bottom': '5px'}),
                    html.Div(id='output-data-upload'),
                    react_phylo.Phylo(
                    id='output',
                    data=''),
            ])
            return [view]
        else:
            raise PreventUpdate

    elif tab == 'reports-tab':
        raise PreventUpdate

    elif tab == 'isolates-tab':

        if section == "":
            if n_clicks == 0 or selected_run == []:
                if selected_samples is not None:
                    columns_names = global_vars.QC_COLUMNS
                    samples = selected_samples
                else:
                    samples = []
                    columns_names = global_vars.QC_COLUMNS
            else:
                columns_names = global_vars.QC_COLUMNS
                samples = selected_samples

            print("the number of samples is: {}".format(len(samples)))
            view = hc.html_tab_bifrost(samples, start_date, end_date, columns_names)

        elif section == "sample-report":

            ids = [sample['_id'] for sample in selected_samples]

            query = filter_all(sample_ids=ids, projection={'properties': 1})

            if "_id" in query:
                query["_id"] = query["_id"].astype(str)

            data = query.to_dict("rows")

            view = sample_report(data)


        elif section == "aggregate":
            view = aggregate_report(selected_samples)
        else:
           # samples_panel = "d-none"
            view = "Not found"

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
    [Output("selected-view-buttons", "children"),
     Output('control-tabs', 'value')],
    [Input("url", "pathname")],
    [State('control-tabs', 'value')],
)
def update_url(pathname, tab):

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

    tab == '{}'.format(tab)
    return [samples_list(section), tab]


@app.callback(
    Output("sample-report", "children"),
    [Input("page-n", "children"),
     Input("sample-store", "data")]
)
def fill_sample_report(page_n, sample_store):
    page_n = int(page_n)
    sample_names = list(
        map(lambda x: x["name"], sample_store))
    if len(sample_names) == 0:
        return None

    data_table = filter_all(
        sample_names=sample_names,
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
    Output("page-n", "children"),
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
    Output('output', 'NewickString'),
    [Input('upload-data', 'contents')]
)
def display_output(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        out = decoded.decode('utf-8', 'strict')

        return out

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
    tmp = data
    tmp = tmp.set_index(['Hospital'])

    hospitals = tmp.groupby('Hospital')
    # cases = []
    # for k in hospitals.groups:
    #     cases.append(len(hospitals.groups[k]))
    print(hospitals)

    dff = [
        {
            "Hospital": "{}".format(k),
            "cases": len(hospitals.groups[k]),
            'lat': tmp.loc[k]['lat'].values[0],
            'lon': tmp.loc[k]['lon'].values[0]
        } for k in hospitals.groups
    ]

    print(dff)
    dfs = pd.DataFrame(dff)

    mapbox_access_token = "pk.eyJ1Ijoic3RlZmFub2NhcmRpbmFsZSIsImEiOiJjazg3aWUwengwZmg1M2VwcnJzc3pnNmNkIn0.W_t9-PNkeag5yie239nI4Q"

    # Generate a list for hover text display
    #textList = dff['Hospital']
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
        lat=dfs['lat'],
        lon=dfs['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            color='#ca261d',
            size=dfs['cases'],
            sizemin=4,
            sizemode='area',
            sizeref=2. * max(dfs['cases']) / (50. ** 2),
        ),
        #text="Hospital:",
        visible=None,
        hovertext=dfs['Hospital'],
        hovertemplate="<b>Hospital:</b><br>" +
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
                lat=56.1910303,
                lon=10.3666312,
            ),
            pitch=0,
            zoom=6.5 if len(derived_virtual_selected_rows) == 0 else 6.5
        )
    )

    return fig2

@app.callback(
    [Output('alert', 'displayed'),
     Output('confirm', 'displayed'),
     Output('upload-survey-button', 'n_clicks')],
    [Input('save-survey', 'n_clicks'),
     Input('survey-store', 'data')],
     [State('survey-name', 'value')]
)
def output_survey_toDB(n_clicks, cases, name):
    print("Output_survey_toDB")
    if n_clicks == 0:
        return False, False, 0
    else:
        if cases is not None:
            if name is None or name == '':
                print("the name is {}".format(name))
                return True, False, 0
            else:
                df = {'cases': cases, 'name': name}
                hc.save_survey(df)
                return False, True, 0
        else:
            raise PreventUpdate

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8054)
