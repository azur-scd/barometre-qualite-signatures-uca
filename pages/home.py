import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

jumbotron = html.Div(
    dbc.Container(
        [
            html.H1("Jumbotron", className="display-3"),
            html.P(
                "Use Containers to create a jumbotron to call attention to "
                "featured content or information.",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P(
                "Use utility classes for typography and spacing to suit the "
                "larger container."
            ),
            html.P(
                dbc.Button("Learn more", color="primary"), className="lead"
            ),
        ],
        fluid=True,
        className="py-3",
    ),
    className="p-3 bg-light rounded-3",
)

layout = dbc.Row(
    [jumbotron],
    className="align-items-md-stretch",
)