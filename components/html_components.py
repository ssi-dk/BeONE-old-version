import dash_html_components as html
import components.import_data as import_data
import components.mongo_interface as mongo_interface
import dash_core_components as dcc
from datetime import datetime as dt

import pandas as pd
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
            ], className='pretty_container four columns', style={"border":"1px DarkGrey solid", 'padding-bottom':'5px', 'padding-left':'5px'}),

            html.Div([
                html.H5("Select specie",
                        className="m-0 font-weight-bold text-primary"),
                dcc.Dropdown(
                    id="species-list",
                    #options=dropdowns_options()[1],
                    value=None
                ),
            ], className='pretty_container three columns',
                style={"border": "1px DarkGrey solid", 'padding-bottom': '5px', 'padding-left': '5px'}),
            generate_DBtable("samples", "stefano_playground"),
        ], className='pretty_container eleven columns', style={"border":"1px DarkGrey solid", 'padding-bottom':'5px', 'padding-left':'5px'})
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
    print(db_list)
    return db_list

def dropdowns_options(selected_run):
    print("dropdown_run_options")
    run_list = import_data.get_run_list()
    run_options = [
        {
            "label": "{} ({})".format(run["name"],
                                      len(run["samples"])),
            "value": run["name"]
        } for run in run_list]

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

    print(species_options)
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

def generate_DBtable(type, coll):
    print("generate_DBtable")

    connection = import_data.get_connection()
    db = connection.get_database()

    if type == "runs":
        runs = list(db.runs.find({},  # {"type": "routine"}, #Leave in routine
                                 {"name": 1,
                                  "_id": 0,
                                  "samples": 1}).sort([['metadata.created_at', pymongo.DESCENDING]]))
        run_options = [
            {
                "label": "{}".format(run["name"]),
                "value": len(run["samples"])
            } for run in runs]

        df = pd.DataFrame(run_options)

    elif type == "samples":
        runs = list(db.runs.find({'name':'stefano_playground'},  # {"type": "routine"}, #Leave in routine
                                 {"name": 1,
                                  "_id": 0,
                                  "samples": 1}).sort([['metadata.created_at', pymongo.DESCENDING]]))
        sample_options = [
            {
                "label": "{}".format(run["sample"]),
                "value": len(run["samples"])
            } for run in runs]

        df = pd.DataFrame(run_options)


    table = html.Div([
        html.Div([
            dash_table.DataTable(
                id='DBtable',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                row_selectable='multi',
                style_cell={'textAlign': 'left'},
                style_as_list_view=False,
                filter_action='native',

                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'fontSize': '7',
                    'textAlign': 'center',
                },
                # style_table={'overflowX': 'scroll','overflowY': 'scroll'}
            )

        ], className="card-body")
    ], className="row",
        style={"max-height": '700px',
               'overflowX': 'scroll',
               'overflowY': 'scroll',
               'border': 'thin lightgrey solid',
               'width':'98%',
               'display':'block'}
    )
    return table
