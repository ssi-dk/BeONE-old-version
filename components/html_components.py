import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

def html_div_main():

    return html.Div([
        html.Div([
                html.Div([
                    html.Div(
                        [
                            html.H3("Here we are going to show some content",
                                    className="m-0 font-weight-bold text-primary"),
                        ],
                        className="card-header py-3"
                    ),

                    # html.Div([
                    #     html.Div([
                    #         html.Div([
                    #             html.Div(id="tsv-download")
                    #         ], className="col-auto"),
                    #     ], className="row mb-3"),
                    #     html.Div([], id="placeholder0"),
                    # ], className="card-body bigtable")

                ], id="card-content", className="card-body", style={"border":"1px DarkGrey solid", 'padding-top':'10px', 'height':'500px'}),
            ], className='eleven columns')
    ], className='row', style={'padding-top': '10px'})