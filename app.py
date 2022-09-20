#!/usr/local/bin python
# -*- coding: utf-8 -*-
import pathlib
import dash
import pandas as pd
import plotly.express as px
import json
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import config


# config variables
port = config.PORT
host = config.HOST
url_subpath = config.URL_SUBPATH
observation_date = config.OBSERVATION_DATE

external_stylesheets=["https://cdn3.devexpress.com/jslib/21.2.5/css/dx.common.css","https://cdn3.devexpress.com/jslib/21.2.5/css/dx.material.blue.light.compact.css"]

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data", observation_date).resolve()

# Load data
df_detail_nb_rows = pd.read_csv(DATA_PATH.joinpath(
    "detail_controle_mentionAdresses.csv")).shape[0]
df_regroup_nb_rows = pd.read_csv(DATA_PATH.joinpath(
    "regroupbypublis_controle_mentionAdresses.csv")).shape[0]

app = dash.Dash(
    __name__, suppress_callback_exceptions=True, use_pages=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=external_stylesheets,
    url_base_pathname=url_subpath
)
app.title = "Contrôle qualité signatures UCA"
server = app.server

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
)

header = html.Div(
    [
        html.Div(
            [
                html.Img(
                    src=app.get_asset_url(
                        "logo_UCA_bibliotheque_ligne_couleurs.png"),
                    id="plotly-image",
                    style={
                        "height": "60px",
                        "width": "auto",
                        "margin-bottom": "25px",
                    },
                )
            ],
            className="one-third column",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            "Baromètre des signatures des publications scientifiques UCA",
                            style={"margin-bottom": "0px"},
                        ),
                        html.Div(
                            [ dcc.Link(html.A('Synthèse'), href=url_subpath, style={'color': 'blue', 'text-decoration': 'none'}),
                              html.Span(' | ', style={'color': 'blue'}),
                              dcc.Link(html.A('Données'), href=f'{url_subpath}data', style={'color': 'blue', 'text-decoration': 'none'}),
                            ], style={"margin-top": "0px"}
                        ),
                    ]
                )
            ],
            className="one-half column",
            id="title",
        ),
    ],
    id="header",
    className="row flex-display",
    style={"margin-bottom": "25px"},
)
footer = html.Div(
    [
        html.Footer(
            [
                html.Div(
                    [
                        html.Span("2022 - SCD Université Côte d'Azur. | Contact : "),
                        dcc.Link(html.A('geraldine.geoffroy@univ-cotedazur.fr'), href="mailto:geraldine.geoffroy@univ-cotedazur.fr")
                    ])
            ]
        )
    ],
    id="footer",
    className="row flex-display",
    style={"margin-bottom": "25px"}
)


chapeau = html.Div(
    [
        html.Div(
            [html.H6("2016-2022"),
             html.P("Période analysée")],
            className="mini_container",
        ),
        html.Div(
            [html.H6(f'{df_regroup_nb_rows}'), html.P(
                "Nombre de publications")],
            className="mini_container",
        ),
        html.Div(
            [html.H6(f'{df_detail_nb_rows}'), html.P(
                "Nombre de mentions d'adresses")],
            className="mini_container",
        ),
         html.Div(
            [html.H6("22 août 2022"),
             html.P("Date de dernière mise à jour")],
            className="mini_container",
        ),
    ],
    className="row flex-display",
    style={"justify-content": "center"}
)

# Main layout
app.layout = html.Div(
    [
        header,
        chapeau,
        dash.page_container,
        footer
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
    )

# Main
if __name__ == "__main__":
    app.run_server(port=port, host=host)
