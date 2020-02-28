import dash_html_components as html
import components.import_data as import_data
import components.mongo_interface as mongo_interface
import dash_core_components as dcc
from datetime import datetime as dt
import components.global_vars as global_vars

import pandas as pd
import numpy as np
import pymongo
import dash_table
import dash_bootstrap_components as dbc
KEY = "BIFROST_DB_KEY"

def html_div_main():

    return html.Div([
        html.Div([
            html.Div([
                html.H5("Select run",
                        className="m-0 font-weight-bold text-primary"),
                dcc.Dropdown(
                    id="run-list",
                    #options=dropdowns_options()[0],
                    value=None
                ),
            ], className='pretty_container four columns', style={'border':'1px DarkGrey solid',
                                                                 'padding-bottom':'5px',
                                                                 'padding-left':'5px',
                                                                 'position':'relative',
                                                                 'zIndex':999}),
            table_main(),
            # html.Div([
            #     html.H5("Select specie",
            #             className="m-0 font-weight-bold text-primary"),
            #     dcc.Dropdown(
            #         id="species-list",
            #         #options=dropdowns_options()[1],
            #         value=None
            #     ),
            # ], className='pretty_container three columns',
            #     style={"border": "1px DarkGrey solid", 'padding-bottom': '5px', 'padding-left': '5px'}),
        ], className='pretty_container eleven columns', style={'border':'1px DarkGrey solid',
                                                               'padding-bottom':'5px',
                                                               'padding-left':'5px'})
    ], className='row', style={'padding-top': '10px'})

def dropdown_db_options():
    print(dropdown_db_options)
    db_list = import_data.get_db_list()
    # db_options = [
    #     {
    #         "label": "{}".format(i),
    #         "value": i
    #     } for i in db_list
    # ]
    return db_list

def dropdowns_options(selected_run):
    print("dropdown_species_options")
    run_list = import_data.get_run_list()
    run_options = [
        {
            "label": "{}".format(run["name"]),
            "value": run["name"]
        } for run in run_list]

    if selected_run is None:
        selected_run = 'stefano_playground'

    species_list = import_data.get_species_list("not provided", selected_run)

    species_options = []
    for item in species_list:
        if pd.isna(item["_id"]):
            species_options.append({
                "label": "Not classified",
                "value": "Not classified"
            })
        else:
            species_options.append({
                "label": item["_id"],
                "value": item["_id"]
            })
   # print(species_options)
    return [run_options, species_options]

def html_topbar():
    return html.Div([
        html.Div([
            html.Ul([
                html.H5("Select Database"),
                dcc.RadioItems(id="radiobuttons1",
                               options=[
                                   {"label": "All ", "value": "all"},
                                   {"label": "Local ", "value": "active"},
                                   {"label": "Remote ", "value": "custom"},
                               ],
                               value="active",
                               labelStyle={"display": "inline-block"},
                               className="dcc_control",
                               ),
                dcc.Dropdown(
                    id="db-list",
                    options=dropdown_db_options(),
                    value=None
                )
            ], className='four columns', style={'display': 'inline-block'}),
            html.Div([
                html.H5("Select Time Range", style={'padding-bottom':'22px'}),
                dcc.DatePickerRange(
                    id="date-picker-select",
                    start_date=dt(2014, 1, 1),
                    end_date=dt(2014, 1, 15),
                    min_date_allowed=dt(2014, 1, 1),
                    max_date_allowed=dt(2014, 12, 31),
                    initial_visible_month=dt(2014, 1, 1),
                )
            ], className='six columns', style={'display':'inline-block', 'padding-left':'5px'}),
        ], className='pretty_container five columns', style={"border":"1px DarkGrey solid", 'padding-bottom':'5px', 'padding-left':'5px'}),
        html.Div([
            html.H5("News")
        ], className='pretty_container five columns', style={"border":"1px DarkGrey solid", 'padding-bottom':'5px', 'padding-left':'5px', 'height':'120px', 'text-align':'center'})
    ], className='row', style={'padding-top':'5px', 'padding-bottom':'10px'})

def html_div_filter():

    return html.Div([
        html.Div(
            [
                html.Div([
                    html.Div(
                        [
                            html.H6("List view",
                                className="m-0 font-weight-bold text-primary"),
                        ],
                        className="card-header py-3"
                    ),

                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div([
                                    # dbc.Button("Remove selected",
                                    #            id="remove-selected",
                                    #            n_clicks=0,
                                    #            size="sm")
                                ]),
                            ], className="col-auto mr-auto"),
                            html.Div([

                                html.Span(
                                    "0", id="filter-sample-count"),
                                ' samples loaded.',

                                dbc.ButtonGroup([
                                    dbc.Button(html.I(className="fas fa-download fa-sm fa-fw"),
                                               id="generate-download-button",
                                               color="secondary",
                                               size="sm",
                                               className="ml-2",
                                               n_clicks=0)
                                ]),
                                html.Div(id="tsv-download")
                            ], className="col-auto"),
                        ], className="row mb-3"),
                        html.Div([], id="placeholder0"),
                        dash_table.DataTable(
                            data=[{}],
                            style_table={
                                'overflowX': 'scroll',
                            },
                            columns=global_vars.COLUMNS,
                            style_cell={
                                'minWidth': '200px',
                                'textAlign': 'center',
                                "fontFamily": "Arial",
                                "padding": "0px 10px",
                                "fontSize": "0.7rem",
                                "height": "auto"
                            },
                            style_cell_conditional=[
                                {
                                    "if": {"column_id": "ssi_stamper_failed_tests"},
                                    "textAlign": "left"
                                }
                            ],
                            fixed_rows={'headers': True},
                            # row_selectable='multi',
                            # filtering=True,  # Front end filtering
                            # sorting=True,
                            selected_rows=[],
                            # style_data_conditional=style_data_conditional,
                            # pagination_settings={
                            #     'current_page': 0,
                            #     'page_size': TABLE_PAGESIZE
                            # },
                            virtualization=False,
                            page_action='none',
                            id="datatable-ssi_stamper")
                    ], className="card-body bigtable")

                ], id="ssi_stamper-report", className="card shadow mb-4"),
            ]
        )
    ])

def html_tab_bifrost():
    view = html.Div([
            html.Div([
                html.H5("Select run",
                        className="m-0 font-weight-bold text-primary"),
                dcc.Dropdown(
                    id="run-list",
                    #options=dropdowns_options()[0],
                    value=None
                ),
            ], className='pretty_container four columns', style={'border':'1px DarkGrey solid',
                                                                 'padding-bottom':'5px',
                                                                 'padding-left':'5px',
                                                                 'position':'relative',
                                                                 'zIndex':999}),
            table_main(),
        ], className='pretty_container eleven columns', style={'border':'1px DarkGrey solid',
                                                               'padding-bottom':'5px',
                                                               'padding-left':'5px'})
    return [view]

def html_tab_projects():
    view = html.Div([
            html.Div([
                html.H5("Species in current run",
                        className="m-0 font-weight-bold text-primary"),
                dcc.Dropdown(
                    id="species-list",
                    #options=[],
                    value=None
                ),
            ], className='pretty_container four columns', style={'border':'1px DarkGrey solid',
                                                                 'padding-bottom':'5px',
                                                                 'padding-left':'5px',
                                                                 'position':'relative',
                                                                 'zIndex':999}),
        ], className='pretty_container eleven columns', style={'border':'1px DarkGrey solid',
                                                               'padding-bottom':'5px',
                                                               'padding-left':'5px'})
    return [view]

def html_tab_results():
    view = html.Div([
        html.Div([
        ], className='pretty_container four columns', style={'border': '1px DarkGrey solid',
                                                             'padding-bottom': '5px',
                                                             'padding-left': '5px',
                                                             'position': 'relative',
                                                             'zIndex': 999}),
    ], className='pretty_container eleven columns', style={'border': '1px DarkGrey solid',
                                                           'padding-bottom': '5px',
                                                           'padding-left': '5px'})
    return [view]

def html_tab_reports():
    view = html.Div([
        html.Div([
        ], className='pretty_container four columns', style={'border': '1px DarkGrey solid',
                                                             'padding-bottom': '5px',
                                                             'padding-left': '5px',
                                                             'position': 'relative',
                                                             'zIndex': 999}),
    ], className='pretty_container eleven columns', style={'border': '1px DarkGrey solid',
                                                           'padding-bottom': '5px',
                                                           'padding-left': '5px'})
    return [view]

def generate_table(tests_df):
    qc_action = "properties.stamper.summary.stamp.value"
    user_stamp_col = "properties.stamper.summary.stamp.name"
    r1_col = "properties.datafiles.summary.paired_reads"

    # Add needed columns
    for col in [qc_action, user_stamp_col, r1_col]:
        if col not in tests_df:
            tests_df[col] = np.nan

    # Convert to string for comparison later on
    tests_df = tests_df.astype({user_stamp_col: str})

    values = {r1_col: ""}
    tests_df = tests_df.fillna(value=values)
    no_reads_mask = tests_df[r1_col] == ""
    tests_df.loc[no_reads_mask, qc_action] = "core facility (no reads)"
    mask = pd.isnull(tests_df[qc_action])
    tests_df.loc[mask, qc_action] = "not tested"
    slmask = tests_df[qc_action] == "supplying lab"
    tests_df.loc[slmask, qc_action] = "warning: supplying lab"

    user_mask = tests_df[user_stamp_col] == "user_feedback"
    tests_df.loc[user_mask, qc_action] = "👤 " + tests_df.loc[user_mask, qc_action]

    # user_stamp_col = "stamp.supplying_lab_check.value"
    # # Overload user stamp to ssi_stamper
    # if user_stamp_col in tests_df.columns:
    #     user_OK_mask = tests_df[user_stamp_col] == "pass:OK"
    #     tests_df.loc[user_OK_mask, qc_action] = "*OK"
    #     user_sl_mask = tests_df[user_stamp_col] == "fail:supplying lab"
    #     tests_df.loc[user_sl_mask, qc_action] = "*warning: supplying lab"
    #     user_cf_mask = tests_df[user_stamp_col] == "fail:core facility"
    #     tests_df.loc[user_cf_mask, qc_action] = "*core facility"

    test_cols = [col.split(".")[-2] for col in tests_df.columns
                 if (col.startswith("properties.stamper.summary.") and
                     col != "properties.stamper.summary.stamp.status" and
                     col.endswith(".status"))]

    # Round columns:
    for col in global_vars.ROUND_COLUMNS:
        if col in tests_df.columns:
            tests_df[col] = round(tests_df[col], 3)

    def concatenate_failed(row):
        res = []
        tests = {}
        for test_name in test_cols:
            reason_c = "properties.stamper.summary.{}.reason".format(test_name)
            value_c = "properties.stamper.summary.{}.value".format(test_name)
            status_c = "properties.stamper.summary.{}.status".format(test_name)
            if pd.isna(row[value_c]):
                tests[test_name] = {
                    "status": "fail",
                    "reason": "Not tested",
                    "value": ""
                }
            else:
                status = row[status_c]
                reason = row[reason_c]
                value = row[value_c]

                tests[test_name] = {
                    "status": status,
                    "reason": reason,
                    "value": value
                }

        for test_name in tests:
            test = tests[test_name]
            if test["status"] == "fail":
                res.append("Test {}: {}, {}".format(
                    test_name, test["status"], test["reason"]))
        row["ssi_stamper_failed_tests"] = ". ".join(res)
        return row

    tests_df = tests_df.apply(concatenate_failed, axis="columns")

    COLUMNS = global_vars.COLUMNS

    # Generate conditional formatting:
    style_data_conditional = []
    conditional_columns = ["properties.stamper.summary.stamp.value"]

    for status, color in ("fail", "#ea6153"), ("undefined", "#f1c40f"):
        style_data_conditional += list(map(lambda x: {"if": {
            "column_id": x, "filter": '{} eq "{}"'.format(x, status)}, "backgroundColor": color}, conditional_columns))

    for status, color in ("core facility", "#ea6153"), ("warning: supplying lab", "#f1c40f"):
        style_data_conditional += [{"if": {
            "column_id": qc_action, "filter": 'QC_action eq "{}"'.format(status)}, "backgroundColor": color}]

    tests_df["_id"] = tests_df["_id"].astype(str)

    tests_df = tests_df.filter([c["id"] for c in COLUMNS])

    return tests_df

def table_main():
    print("table_main")

    table = html.Div([
        # html.Div([
        #     dash_table.DataTable(
        #         id='DBtable_runs',
        #         columns=[{"name": i, "id": i} for i in df.columns],
        #         data=df.to_dict('records'),
        #         row_selectable='multi',
        #         style_cell={'textAlign': 'left'},
        #         style_as_list_view=False,
        #         filter_action='native',
        #
        #         style_header={
        #             'backgroundColor': 'rgb(230, 230, 230)',
        #             'fontWeight': 'bold',
        #             'fontSize': '7',
        #             'textAlign': 'center',
        #         },
        #         # style_table={'overflowX': 'scroll','overflowY': 'scroll'}
        #     )
        #
        # ], className="card-body", style={'width': '49%', 'display':'inline-block'}),
        html.Div([
            html.Div([], id="placeholder0"),
            dash_table.DataTable(
                data=[{}],
                row_selectable='multi',
                filter_action='native',
                style_table={
                    'overflowX': 'scroll',
                },
                columns=global_vars.COLUMNS,
                style_cell={
                    'minWidth': '180px',
                    'textAlign': 'center',
                    "fontFamily": "Arial",
                    'fontSize': '8',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'fontSize': '7',
                    'textAlign': 'center',
                    'whiteSpace': 'normal'
                },
                style_cell_conditional=[
                    {
                        "if": {"column_id": "ssi_stamper_failed_tests"},
                        "textAlign": "left"
                    }
                ],
                fixed_rows={'headers': True},
                # row_selectable='multi',
                # filtering=True,  # Front end filtering
                # sorting=True,
                selected_rows=[],
                # style_data_conditional=style_data_conditional,
                # pagination_settings={
                #     'current_page': 0,
                #     'page_size': TABLE_PAGESIZE
                # },
                virtualization=False,
                page_action='none',
                id="datatable-ssi_stamper")
        ], className="pretty-container", style={'width': '98%',
                                                'display':'inline-block',
                                                'padding-left':'10px'}),

    ], className="row",
        style={"max-height": '700px',
               'overflowX': 'scroll',
               'overflowY': 'scroll',
               'width':'99%'}
    )
    return table
