#!/usr/local/bin python
# -*- coding: utf-8 -*-
import pathlib
import dash
import pandas as pd
import plotly.express as px
import json
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
from textwrap3 import wrap
import config

dash.register_page(__name__, path='/')

# config variables
port = config.PORT
host = config.HOST
url_subpath = config.URL_SUBPATH
observation_date = config.OBSERVATION_DATE

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data", observation_date).resolve()

# Params

COLORS = {'ni_uca_ni_uns': 'grey',
          'uca_developpee': '#3288BD',
          'uca_sigle_seul': 'rgb(122,230,212)',
          'uns_seul': 'rgb(241,225,91)',
          'indice_ni_uca_ni_uns': 'grey',
          'indice_uca_developpee': '#3288BD',
          'indice_uca_sigle_seul': 'rgb(122,230,212)',
          'indice_uns_seul': 'rgb(241,225,91)'}

chart_cols = ['ni_uca_ni_uns', 'uca_developpee',
                  'uca_sigle_seul', 'uns_seul']

# helpers functions

# Load data
df_detail = pd.read_csv(DATA_PATH.joinpath(
    "detail_controle_mentionAdresses.csv"), sep=',', encoding="utf-8",dtype={"@afids": str})
df_regroup = pd.read_csv(DATA_PATH.joinpath(
    "regroupbypublis_controle_mentionAdresses.csv"), sep=',', encoding="utf-8", dtype={"annee_pub": str})
regroup_crosstab_valeurs_absolues = pd.read_csv(DATA_PATH.joinpath("consolidation/regroup_crosstab_annee_mention_valeurs_absolues.csv"), sep=',', encoding="utf-8")
regroup_crosstab_pourcentages = pd.read_csv(DATA_PATH.joinpath("consolidation/regroup_crosstab_annee_mention_pourcentages.csv"), sep=',', encoding="utf-8")
regroup_crosstab_indices = pd.read_csv(DATA_PATH.joinpath("consolidation/regroup_crosstab_annee_mention_indices.csv"), sep=',', encoding="utf-8")
structures_value_counts = pd.read_csv(DATA_PATH.joinpath("consolidation/detail_afids_value_counts.csv"),sep=',', encoding="utf-8", dtype={"value": str})

section_synthese_pub = html.Div([
    html.Div(html.H4('Synthèse de la qualité des signatures par publications'),
             className="row flex-display"),
                        dcc.Markdown('''
- **cas 1. UCA DEVELOPPEE** : la publication contient au moins une mention d'affiliation qui comprend la forme littérale (sous toutes ses variantes possibles) d'Université Côte d'Azur
- **cas 2. UCA SIGLE SEUL** : sinon (hors cas 1) la publication contient au moins une mention d'affiliation qui comprend le sigle UCA
- **cas 3. UNS seul** : sinon (hors cas 1 et 2) la publication contient au moins une mention d'affiliation qui comprend le sigle UNS ou la forme littérale (sous toutes ses variantes possibles) d'université de Nice
- **cas 4. NI UCA NI UNS** : aucune des mentions d'affiliation de la publication ne contient la forme littérale ou le signe UCA ou UNS (la publication alors est repérée par l'unité de recherche)
'''),
    html.Div(dcc.RadioItems(
        options={
            'qte': 'Valeurs absolues',
            'percent': 'Pourcentage',
            'indice': 'Indice base 100 en 2016'
        },
        inline=True,
        value='qte',
        id="radio-regroup-datatype"
    ), className="row flex-display"),
    html.Div(
        [
            html.Div(id="table-regroup",
                     className="pretty_container six columns",
                     ),
            html.Div(
                [dcc.Graph(id="fig-regroup")],
                className="pretty_container six columns",
            ),
        ],
        className="row flex-display",
    ),
])

section_synthese_mention = html.Div([
    html.Div(html.H4('Synthèse de la qualité des signatures par mentions d\'affiliation'),
             className="row flex-display"),
                                     dcc.Markdown('''
- **cas 1. UCA DEVELOPPEE** : la mention d'adresse comprend la forme littérale (sous toutes ses variantes possibles) d'Université Côte d'Azur
- **cas 2. UCA SIGLE SEUL** : sinon (hors cas 1) la mention d'adresse comprend le sigle UCA
- **cas 3. UNS seul** : sinon (hors cas 1 et 2) la mention d'adresse comprend le sigle UNS ou la forme littérale (sous toutes ses variantes possibles) d'université de Nice
- **cas 4. NI UCA NI UNS** : la mention d'adresse ne comprend ni la forme littérale ni le signe UCA ou UNS
'''),
                                     dcc.Markdown('''
*Les catégories UCA affiliation) et UNS divers sont des structures factices créées afin de regrouper les mentions d\'affiliation qui ne contiennent pas d'élément permettant d\'associer une publication à une structure de recherche précise mais dont les informations ont tout de même permis d'affilier la publication à UCA (ex : signature du type "Observatoire de la Côte d'Azur")*
'''),
    html.Div(
        html.Div(dcc.RangeSlider(
            id="rangeslider-year",
            min=2016,
            max=2022,
            step=1,
            marks={i: "{}".format(i) for i in [
                2016, 2017, 2018, 2019, 2020, 2021, 2022]},
            value=[2016, 2022],
            className="dcc_control",
            updatemode="drag",
            tooltip={"placement": "bottom", "always_visible": True}
        ),
            style={"width": "100%"}
        ),
        className="row flex-display"),
    html.Div(
        [
            html.Div(id="table-detail",
                     className="pretty_container six columns",
                     ),
            html.Div(
                [dcc.Graph(id="fig-detail", style={"height": "100%"})],
                className="pretty_container six columns",
            ),
        ],
        className="row flex-display",
    ),
])

section_structure_view = html.Div([
    html.Div(html.H4('Qualité des signatures par structure de recherche'),
             className="row flex-display"),
    html.Div(
        html.Div( dcc.Dropdown(
                            id="selected-structure",
                            options=structures_value_counts.to_dict(orient='records'),
                            # for multiselect : value=[num["value"] for num in dict_structures],
                            value=structures_value_counts.to_dict(orient='records')[0]["value"],
                            className="dcc_control",
                        ),
            style={"width": "40%"}
        ),
        className="row flex-display"),
    html.Div(
        [    
            html.Div([dcc.Graph(id="fig-structure-pie")],
                     className="pretty_container six columns",
                     ),
            html.Div(
                [   dcc.RadioItems(
        options={
            'qte': 'Valeurs absolues',
            'percent': 'Pourcentage'
        },
        inline=True,
        value='qte',
        id="radio-structure-view-datatype"
    ),
                    dcc.Graph(id="fig-structure-area")],
                className="pretty_container six columns",
            ),
        ],
        className="row flex-display",
    ),
])

# Page layout
layout = html.Div([
    section_synthese_pub,
    html.Hr(),
    section_synthese_mention,
    html.Hr(),
    section_structure_view
])


@callback(
    [Output("fig-regroup", "figure"),
    Output("table-regroup", "children")],
    Input("radio-regroup-datatype", "value"),
)
def update_regroup_section(radio_regroup_datatype):
    chart_title = 'Evolution du type de mentions d\'affiliation par année de publication'
    # callbacks interactions
    if radio_regroup_datatype == "qte":
        fig = px.bar(regroup_crosstab_valeurs_absolues.iloc[:-1, :].iloc[:, :-1], x='annee_pub',
                     y=chart_cols, color_discrete_map=COLORS, title=chart_title)
        fig.update_yaxes(title_text='Nombre de publications')
        table = dash_table.DataTable(regroup_crosstab_valeurs_absolues.to_dict('records'), [
            {"name": i.replace("_", " ").upper(), "id": i} for i in regroup_crosstab_valeurs_absolues.columns])
    if radio_regroup_datatype == "percent":
        fig = px.area(regroup_crosstab_valeurs_absolues.iloc[:-1, :].iloc[:, :-1], x='annee_pub', y=chart_cols,
                      groupnorm='percent', color_discrete_map=COLORS, title=chart_title)
        fig.update_yaxes(title_text='Pourcentage du nombre de publications')
        table = dash_table.DataTable(regroup_crosstab_pourcentages.to_dict('records'), [
            {"name": i.replace("_", " ").upper(), "id": i} for i in regroup_crosstab_pourcentages.columns])
    if radio_regroup_datatype == "indice":
        fig = px.line(regroup_crosstab_indices.sort_values(by=['annee_pub'], ascending=[True]), x='annee_pub', y=[
                      'indice_ni_uca_ni_uns', 'indice_uca_developpee', 'indice_uca_sigle_seul', 'indice_uns_seul'], color_discrete_map=COLORS, title=chart_title)
        fig.update_yaxes(
            title_text='Pourcentage du nombre de publications en indice de base 100 en 2016')
        table = dash_table.DataTable(regroup_crosstab_indices.to_dict('records'), [
            {"name": i.replace("_", " ").upper(), "id": i} for i in regroup_crosstab_indices.columns if "indice_" in i])
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
    return fig,table

@callback(
    Output("fig-detail", "figure"),
    Output("table-detail", "children"),
    Input("rangeslider-year", "value"),
)
def update_detail_section(rangeslider_year):
    filtered_data = df_detail[(df_detail["annee_pub"] >= int(rangeslider_year[0])) & (
        df_detail["annee_pub"] <= int(rangeslider_year[1]))]
    data = pd.crosstab(filtered_data["affiliation_name"], filtered_data["mention_adresse_norm"],
                                normalize=False, margins=True, margins_name="Total").sort_values('Total', ascending=False).reset_index()
    table = dash_table.DataTable(data.to_dict('records'), [
                                 {"name": i.replace("_", " ").upper(), "id": i} for i in data.columns],
                                 style_data={'whiteSpace': 'normal', 'height': 'auto'},
                                 style_cell={'maxWidth': '200px'},
                                 sort_action='native',
                                 filter_action='native'
                                )
    data_no_margins = data.iloc[1:, :].iloc[:, :-1]
    data_no_margins['affiliation_name_wrapped'] = data_no_margins['affiliation_name'].apply(lambda x: f'{wrap(x, 30)[0]}...')
    fig = px.bar(data_no_margins, orientation='h', y='affiliation_name_wrapped', x=chart_cols, color_discrete_map=COLORS, title="Typologie des mentions d'adresse par structure de recherche")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
                      legend=dict(
        orientation="h",
    y=1.03,
    ))
    fig.for_each_trace(lambda t: t.update(name=t.name.replace("_", " ").upper(),
                                          legendgroup=t.name.replace(
                                              "_", " ").upper(),
                                          hovertemplate=t.hovertemplate.replace(
                                              t.name, t.name.replace("_", " ").upper())
                                          ))
    return fig, table

@callback(
    Output("fig-structure-pie", "figure"),
    Output("fig-structure-area", "figure"),
    [Input("selected-structure", "value"),
    Input("radio-structure-view-datatype", "value"),]
)
def update_structure_view(selected_structure,radio_structure_view_datatype):
    df = df_detail.loc[df_detail['@afids'].isin([str(selected_structure)])]
    df["annee_pub"] = df["annee_pub"].astype(str)
    df_crosstab = pd.crosstab(df["annee_pub"], df["mention_adresse_norm"]).reset_index()
    fig_pie = px.pie(df, names='mention_adresse_norm', color='mention_adresse_norm',color_discrete_map=COLORS, title="Répartition des types de mention d'adresse")
    if radio_structure_view_datatype == "qte":
        fig_area = px.area(df_crosstab, x='annee_pub', y=chart_cols, color_discrete_map=COLORS, title="Evolution de la répartition des types de mention d'adresse")
    if radio_structure_view_datatype == "percent":
        fig_area = px.area(df_crosstab, x='annee_pub', y=chart_cols, groupnorm='percent',color_discrete_map=COLORS, title="Evolution de la répartition des types de mention d'adresse")
    fig_pie.for_each_trace(lambda t: t.update(name=t.name.replace("_", " ").upper(),
                                          legendgroup=t.name.replace(
                                              "_", " ").upper(),
                                          hovertemplate=t.hovertemplate.replace(
                                              t.name, t.name.replace("_", " ").upper())
                                         ))
    fig_area.for_each_trace(lambda t: t.update(name=t.name.replace("_", " ").upper(),
                                          legendgroup=t.name.replace(
                                              "_", " ").upper(),
                                          hovertemplate=t.hovertemplate.replace(
                                              t.name, t.name.replace("_", " ").upper())
                                         ))
    return fig_pie, fig_area