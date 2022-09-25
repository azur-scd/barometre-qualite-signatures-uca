import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

def widget_card_header(text,title):
    card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.P(f"{title}", className="card-title"),
                html.Hr(className="my-2"),
                html.H5(
                    html.Div(f"{text}"),
                    className="card-text text-center ",
                ),
            ]
        ),
    ],
    color="rgb(113, 145, 179",
    outline=True,
    inverse=True,
    #style={"width": "12rem"},
    )
    return card

def get_slider_range(id):
    return dcc.RangeSlider(id=f"{id}",
                           min=2016,
                           max=2022,
                           step=1,
                           marks={i: "{}".format(i) for i in [
                               2016, 2017, 2018, 2019, 2020, 2021, 2022]},
                           value=[2016, 2022],
                           className="dcc_control",
                           updatemode="drag",
                           tooltip={"placement": "bottom", "always_visible": True})