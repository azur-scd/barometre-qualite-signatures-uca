import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from templates.templates import widget_card_header
import sqlalchemy as sqla
import config

# config variables
port = config.PORT
host = config.HOST
publis_last_obs_date = config.PUBLIS_LAST_OBS_DATE

# external JavaScript f& CSS iles
external_scripts = [
    {
        'src': 'https://code.jquery.com/jquery-3.6.0.min.js',
        'integrity': 'sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=',
        'crossorigin': 'anonymous'
    },
    'https://cdnjs.cloudflare.com/ajax/libs/devextreme/22.1.3/js/dx.all.js',
]

# external CSS stylesheets
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    'https://cdnjs.cloudflare.com/ajax/libs/devextreme/22.1.3/css/dx.material.blue.light.compact.css',
]

app = dash.Dash(
    __name__, use_pages=True, suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width"}],
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
)
app.config.suppress_callback_exceptions = True

app.title = "BSO UCA"
server = app.server

# get relative db folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("db", "publications.db").resolve()

dbEngine=sqla.create_engine(f'sqlite:///{DB_PATH}')

df_bsi_publis_uniques = pd.read_sql(f'select dc_identifiers from bsi_publis_uniques_{publis_last_obs_date}',dbEngine)
df_bsi_all_by_mention_adresse = pd.read_sql(f'select dc_identifiers from bsi_all_by_mention_adresse_{publis_last_obs_date}',dbEngine)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=app.get_asset_url('logo_UCA_bibliotheque_ligne_couleurs.png'), height="40px")),
                        dbc.Col(dbc.NavbarBrand("Barometre qualité signatures", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler2", n_clicks=0),
            dbc.Collapse(
                dbc.Nav(
                    [dbc.NavItem(dbc.NavLink("Home", href="/")), 
                    dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Dashboard", href="/dashboard"),
        dbc.DropdownMenuItem("Dashboard par structure", href="/dashboard-par-structure"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Données", href="/data"),
    ],
    nav=True,
    in_navbar=True,
    label="Menu",
)],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse2",
                navbar=True,
            ),
        ],
    style={"max-width":"1800px"}
    ),
    color="#7191b3",
    dark=True,
    className="mb-5",
)

row_widgets_header = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(widget_card_header("2016-2022", "Période observée"),width={"offset": 1, "size":2}),
                dbc.Col(widget_card_header(f'{df_bsi_publis_uniques.shape[0]:,}'.replace(',', ' '),"Nombre de publications"),width=2),
                dbc.Col(widget_card_header(f'{df_bsi_all_by_mention_adresse.shape[0]:,}'.replace(',', ' '),"Nombre de mentions d'adresse"), width=2),
                dbc.Col(widget_card_header("29 août 2022","Date de dernière mise à jour"), width=2),
            ],
            align="center"
        ),
    ]
)

app.layout = dbc.Container(
    fluid=True,
    children=
    [
        navbar,
        row_widgets_header,
        html.Hr(),
        dash.page_container
    ],
    )

# Main
if __name__ == "__main__":
    app.run_server(debug=True,port=port, host=host)
