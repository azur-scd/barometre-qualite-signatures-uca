import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from templates.templates import get_slider_range
import helpers.functions as fn
import plotly.express as px
import sqlalchemy as sqla
import json
from textwrap3 import wrap
import config

dash.register_page(__name__, path='/dashboard')

# config params
publis_last_obs_date = config.PUBLIS_LAST_OBS_DATE
colors = config.COLORS
chart_cols = config.COLS
chart_cols_charte = config.COLS_CHARTE

# get relative db folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "publications.db").resolve()

dbEngine = sqla.create_engine(f'sqlite:///{DB_PATH}')
# regroup data
df_bsi_publis_uniques = pd.read_sql(
    f'select annee_pub,synthese_mention_adresse_norm, synthese_mention_adresse_norm_charte from bsi_publis_uniques_{publis_last_obs_date}', dbEngine)
df_bsi_publis_uniques["annee_pub"] = df_bsi_publis_uniques["annee_pub"].astype(
    str)
crosstab_bsi_publis_uniques = fn.get_crosstab_simple(
    df_bsi_publis_uniques, "annee_pub", "synthese_mention_adresse_norm")
crosstab_percent_bsi_publis_uniques = fn.get_crosstab_percent(
    df_bsi_publis_uniques, "annee_pub", "synthese_mention_adresse_norm")
crosstab_indice_bsi_publis_uniques = fn.get_crosstab_indice(
    crosstab_bsi_publis_uniques, chart_cols).drop(chart_cols, axis=1)
# detail data
df_bsi_all_by_mention = pd.read_sql(
    f'select annee_pub,affiliation_name,mention_adresse_norm, mention_adresse_norm_charte from bsi_all_by_mention_adresse_{publis_last_obs_date}', dbEngine)
df_bsi_all_by_mention["annee_pub"] = df_bsi_all_by_mention["annee_pub"].astype(
    str)

collapse_regroup_data = html.Div(
    [
        dbc.Button(
            "Voir les données des graphiques",
            id="collapse-button-regroup",
            className="mb-3",
            color="success",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(id="table-regroup"),
            id="collapse-regroup",
            is_open=False,
        ),
        html.Br(),
    ]
)

collapse_detail_data = html.Div(
    [
        dbc.Button(
            "Voir les données du graphique",
            id="collapse-button-detail",
            className="mb-3",
            color="success",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(id="table-detail"),
            id="collapse-detail",
            is_open=False,
        ),
        html.Br(),
    ]
)

row_legend = html.Div([
    dbc.Row([
        dbc.Col(dbc.RadioItems(
            options=[
                {"label": "4 cas de figure", "value": "quatre_cas"},
                {"label": "Cas 3 et 4 regroupés", "value": "trois_cas"}
            ],
            inline=True,
            value="quatre_cas",
            id="cas"),
            width=4)
    ])
])

row_widgets_regroup = html.Div(
    [
        dbc.Row(
            [
                dbc.Col([get_slider_range("slider-pie-regroup"),
                        fn.load_with_spinner(dcc.Graph(id="pie-regroup"))], style={"borderRight": "1px solid #7191b3"}, width=5),
                dbc.Col([dbc.RadioItems(
                    options=[
                        {"label": "Valeur absolue", "value": "qte"},
                        {"label": "Pourcentage", "value": "percent"},
                        {"label": "Indice base 100 en 2016", "value": "indice"},
                    ],
                    inline=True,
                    value="qte",
                    id="radio-regroup-datatype"
                ),
                    fn.load_with_spinner(dcc.Graph(id="barchart-regroup"))], width=7),
            ]
        ),
    ],
    className="p-3 bg-light rounded-3"
)

row_widgets_detail = html.Div([
    dbc.Row([
        dbc.Col(get_slider_range("slider-barchart-detail"), width=6),
        dbc.Col(dbc.RadioItems(
            options=[
                {"label": "Valeur absolue", "value": "qte"},
                {"label": "Valeur absolue en échelle logarithmique",
                 "value": "log"},
                {"label": "Pourcentage", "value": "percent"},
            ],
            inline=True,
            value="qte",
            id="radio-detail-datatype"
        ), width=6)
    ]),
    dbc.Row(dcc.Markdown('''
    *Les catégories UCA affiliation) et UNS divers sont des structures factices créées afin de regrouper les mentions d'affiliation qui ne contiennent pas d'élément permettant d'associer une publication 
    à une structure de recherche précise mais dont les informations ont tout de même permis d'affilier la publication à UCA (ex : signature du type "Observatoire de la Côte d'Azur")*
    '''),
    className="mt-5"
            ),
    dbc.Row(
        dbc.Col(fn.load_with_spinner(dcc.Graph(id="barchart-detail")), width=12))
],
    className="p-3 bg-light rounded-3")

layout = [html.H3("Analyse de la qualité des signatures au niveau des publications", className="text-center"),
          collapse_regroup_data,
          row_widgets_regroup,
          html.Hr(),
          html.H3("Analyse de la qualité des signatures au niveau des mentions d'affiliation",
                  className="text-center"),
          collapse_detail_data,
          row_widgets_detail, ]


@callback(
    Output("collapse-regroup", "is_open"),
    [Input("collapse-button-regroup", "n_clicks")],
    [State("collapse-regroup", "is_open")],
)
def toggle_collapse_regroup(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("collapse-detail", "is_open"),
    [Input("collapse-button-detail", "n_clicks")],
    [State("collapse-detail", "is_open")],
)
def toggle_collapse_detail(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("pie-regroup", "figure"),
    Input("slider-pie-regroup", "value"),
)
def update_pie_regroup(slider_pie_regroup):
    filtered_data = df_bsi_publis_uniques[(df_bsi_publis_uniques["annee_pub"].astype(int) >= int(slider_pie_regroup[0])) & (
        df_bsi_publis_uniques["annee_pub"].astype(int) <= int(slider_pie_regroup[1]))]
    fig = px.pie(filtered_data, names='synthese_mention_adresse_norm', color='synthese_mention_adresse_norm',
                 color_discrete_map=colors, hole=0.7, title="Ventilation globale des mentions d'affiliation (consolidées au niveau publication)")
    fig.for_each_trace(lambda t: t.update(
             labels=[label.replace("_", " ").upper() for label in t.labels])
    )
    return fig


@callback(
    [Output("barchart-regroup", "figure"),
     Output("table-regroup", "children")],
    Input("radio-regroup-datatype", "value"),
)
def update_regroup_section(radio_regroup_datatype):
    chart_title = "Evolution du type de mention d'affiliation (consolidée au niveau publication) par année de publication"
    if radio_regroup_datatype == "qte":
        df = crosstab_bsi_publis_uniques
        fig = px.bar(df.iloc[:-1, :].iloc[:, :-1], x='annee_pub',
                     y=chart_cols, color_discrete_map=colors, title=chart_title)
        fig.update_yaxes(title_text='Nombre de publications')
        fig.update_traces(textposition='inside', texttemplate="%{value}")
        table = dash_table.DataTable(df.to_dict('records'), [
            {"name": i.replace("_", " ").upper(), "id": i} for i in df.columns])
    if radio_regroup_datatype == "percent":
        df = crosstab_percent_bsi_publis_uniques
        fig = px.bar(df.iloc[:-1, :], x='annee_pub',
                     y=chart_cols, color_discrete_map=colors, title=chart_title)
        fig.update_yaxes(title_text="Pourcentage de publications")
        fig.update_traces(textposition='inside', texttemplate="%{value}"+"%")
        table = dash_table.DataTable(df.to_dict('records'), [
            {"name": i.replace("_", " ").upper(), "id": i} for i in df.columns])
    if radio_regroup_datatype == "indice":
        df = crosstab_indice_bsi_publis_uniques
        fig = px.line(df.sort_values(by=['annee_pub'], ascending=[True]), x='annee_pub', y=[
                      'indice_universite_non_mentionnee', 'indice_uca_forme_developpee', 'indice_uca_sigle', 'indice_uns'], color_discrete_map=colors, title=chart_title)
        fig.update_yaxes(
            title_text='Pourcentage du nombre de publications en indice de base 100 en 2016')
        table = dash_table.DataTable(df.to_dict('records'), [
            {"name": i.replace("_", " ").upper(), "id": i} for i in df.columns if "indice_" in i])
    fig.update_xaxes(title_text='Année de publication')
    fig.update_layout(legend=dict(
        orientation="h",
        y=-0.3,
    ))
    fig.for_each_trace(lambda t: t.update(name=t.name.replace("_", " ").upper(),
                                          legendgroup=t.name.replace(
                                              "_", " ").upper(),
                                          hovertemplate=t.hovertemplate.replace(
                                              t.name, t.name.replace("_", " ").upper())
                                          ))
    return fig, table


@callback(
    [Output("barchart-detail", "figure"),
     Output("table-detail", "children")],
    [Input("radio-detail-datatype", "value"),
     Input("slider-barchart-detail", "value")]
)
def update_detail_section(radio_detail_datatype, slider_barchart_detail):
    filtered_data = df_bsi_all_by_mention[(df_bsi_all_by_mention["annee_pub"].astype(int) >= int(slider_barchart_detail[0])) & (
        df_bsi_all_by_mention["annee_pub"].astype(int) <= int(slider_barchart_detail[1]))]
    crosstab_simple = fn.get_crosstab_simple(
        filtered_data, "affiliation_name", "mention_adresse_norm").sort_values('Total', ascending=False).reset_index()
    crosstab_percent = fn.get_crosstab_percent(
        filtered_data, "affiliation_name", "mention_adresse_norm")
    if (radio_detail_datatype == 'qte') | (radio_detail_datatype == 'log'):
        data_no_margins = crosstab_simple.iloc[1:, :].iloc[:, :-1]
        data_no_margins['affiliation_name_wrapped'] = data_no_margins['affiliation_name'].apply(
            lambda x: f'{wrap(x, 30)[0]}...')
        if radio_detail_datatype == 'qte':
            fig = px.bar(data_no_margins, x='affiliation_name_wrapped',
                         y=chart_cols, color_discrete_map=colors, height=700)
        if radio_detail_datatype == 'log':
            fig = px.bar(data_no_margins, x='affiliation_name_wrapped',
                         y=chart_cols, color_discrete_map=colors, log_y=True, height=700)
        fig.update_traces(textposition='inside', texttemplate="%{value}")
        fig.update_yaxes(title_text="Nombre de mentions d'adresse")
        table = dash_table.DataTable(crosstab_simple.to_dict('records'), [
            {"name": i.replace("_", " ").upper(), "id": i} for i in crosstab_simple.columns],
            style_data={'whiteSpace': 'normal', 'height': 'auto'},
            style_cell={'maxWidth': '200px'},
            sort_action='native',
            filter_action='native'
        )
    if radio_detail_datatype == 'percent':
        data_no_margins = crosstab_percent.iloc[:-1, :]
        data_no_margins['affiliation_name_wrapped'] = data_no_margins['affiliation_name'].apply(
            lambda x: f'{wrap(x, 30)[0]}...')
        fig = px.bar(data_no_margins, x='affiliation_name_wrapped',
                     y=chart_cols, color_discrete_map=colors, height=700)
        fig.update_traces(textposition='inside', texttemplate="%{value}"+"%")
        fig.update_yaxes(title_text="Pourcentage des mentions d'adresse")
        table = dash_table.DataTable(crosstab_percent.to_dict('records'), [
            {"name": i.replace("_", " ").upper(), "id": i} for i in crosstab_percent.columns],
            style_data={'whiteSpace': 'normal', 'height': 'auto'},
            style_cell={'maxWidth': '200px'},
            sort_action='native',
            filter_action='native'
        )
    fig.update_xaxes(title_text='Structures de recherche')
    fig.for_each_trace(lambda t: t.update(name=t.name.replace("_", " ").upper(),
                                          legendgroup=t.name.replace(
                                              "_", " ").upper(),
                                          hovertemplate=t.hovertemplate.replace(
                                              t.name, t.name.replace("_", " ").upper())
                                          ))
    return fig, table
