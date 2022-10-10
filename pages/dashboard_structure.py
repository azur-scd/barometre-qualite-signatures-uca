import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from templates.templates import get_slider_range
import helpers.functions as fn
import plotly.express as px
import sqlalchemy as sqla
import dash_dvx as dvx
import json
import config

dash.register_page(__name__, path='/dashboard-par-structure')

# config params
publis_last_obs_date = config.PUBLIS_LAST_OBS_DATE
colors = config.COLORS
chart_cols_charte = config.COLS_CHARTE
mapping_variable = config.MAPPING_VARIABLE


# get relative db folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "publications.db").resolve()

dbEngine = sqla.create_engine(f'sqlite:///{DB_PATH}')

json_referentiel_structures = pd.read_sql(
    f'select affiliation_name, affiliation_id, id, parent_id from referentiel_structures_{publis_last_obs_date}', dbEngine).to_json(orient="records")

# DVX COMPONENTS
listgrid_structures = html.Div(dvx.List(
    id="list_structures",
    dataSource=json.loads(json_referentiel_structures),
    keyExpr="id",
    parentIdExpr="parent_id",
    filterRowIsEnabled=True,  # if you don't want the row filter undre the header
    # if you want to have the ability to show/hide columns in the UI
    columnChooserIsEnabled=False,
    selectionMode="leavesOnly",
    pagingIsEnabled=False,
    columns=[{
        "dataField": 'affiliation_name',
        "caption": 'Structures'
    }
    ],
    # defaultSelectedRowKeys=[7]
)
)

layout = html.Div([dcc.Store(id="selected_structures_afids"),
                   dcc.Store(id="selected_structures_data"),
                   dbc.Row(dcc.Markdown('''
    *Les catégories UCA affiliation) et UNS divers sont des structures factices créées afin de regrouper les mentions d'affiliation qui ne contiennent pas d'élément permettant d'associer une publication 
    à une structure de recherche précise mais dont les informations ont tout de même permis d'affilier la publication à UCA (ex : signature du type "Observatoire de la Côte d'Azur")*''')
                           ),
                   dbc.Row([dbc.Col(listgrid_structures, width=4),
                            dbc.Col([dbc.Alert(id="selected_structures_names_output", color="primary"),
                                     dbc.Alert(
                                         id="selected_structures_total_output", color="success"),
                                     get_slider_range("slider-pie"),
                                     fn.load_with_spinner(
                                         dcc.Graph(id="pie-structure")),
                                     dbc.RadioItems(
                                options=[
                                    {"label": "Valeur absolue", "value": "qte"},
                                    {"label": "Pourcentage", "value": "percent"},
                                ],
                                inline=True,
                                value="qte",
                                id="radio-bar-datatype"
                            ),
                                fn.load_with_spinner(dcc.Graph(id="bar-structure"))],
                       width=8),
                   ],
    className="p-3 bg-light rounded-3")
],
)


@callback(
    Output('selected_structures_names_output', 'children'),
    Output('selected_structures_afids', 'data'),
    Input('list_structures', 'selected_rows'),
    suppress_callback_exceptions=True
)
def get_selected_structures(selected_rows):
    if selected_rows is None or len(selected_rows) == 0:
        display_text = "Sélectionner une ou plusieurs structures dans la liste"
        afids = None
    else:
        display_text = f'Structures sélectionnées : {", ".join(([str(p["affiliation_name"]) for p in list(selected_rows)]))}'
        afids = ",".join(([str(p["affiliation_id"])
                         for p in list(selected_rows)]))
    print(afids)
    return display_text, afids


@callback(
    Output('selected_structures_data', 'data'),
    Input('selected_structures_afids', 'data'),
)
def update_dataframe(selected_structures_afids):
    if selected_structures_afids is not None:
        list_selected_structures_afids = list(
            selected_structures_afids.split(","))
        if len(list_selected_structures_afids) == 1:
            where_request = f"_afids  = '{list_selected_structures_afids[0]}'"
        else:
            tuple_selected_structures_afids = tuple(
                list_selected_structures_afids)
            where_request = f"_afids in {tuple_selected_structures_afids}"
        df = pd.read_sql(
            f"select dc_identifiers, annee_pub, mention_adresse_norm from bsi_all_by_mention_adresse_{publis_last_obs_date} where {where_request}", dbEngine)
    else:
        df = pd.DataFrame(data={})
    return df.to_json(orient="records")


@callback(
    Output('selected_structures_total_output', 'children'),
    Output('pie-structure', 'figure'),
    [Input('selected_structures_afids', 'data'),
     Input('selected_structures_data', 'data'),
     Input('slider-pie', 'value')]
)
def update_pie_chart(selected_structures_afids,selected_structures_data, slider_pie):
    if selected_structures_afids is not None:
        df = pd.read_json(selected_structures_data)
        filtered_data = df[(df["annee_pub"].astype(int) >= int(slider_pie[0])) & (
            df["annee_pub"].astype(int) <= int(slider_pie[1]))]
        fig = px.pie(filtered_data, names='mention_adresse_norm', color='mention_adresse_norm',
                     color_discrete_map=colors, hole=0.7, title="Ventilation des mentions d'affiliation")
        display_total = f"La sélection comprend {df.shape[0]} mentions d'affiliations correspondant à {df.drop_duplicates(subset=['dc_identifiers']).shape[0]} publications"
        fig.for_each_trace(lambda t: t.update(
            labels=[mapping_variable[label] for label in t.labels])
        )
    else:
        fig = {}
        display_total = None
    return display_total, fig


@callback(
    Output('bar-structure', 'figure'),
    [Input('selected_structures_afids', 'data'),
     Input('selected_structures_data', 'data'),
     Input("radio-bar-datatype", "value")]
)
def update_bar_chart(selected_structures_afids,selected_structures_data, radio_bar_datatype):
    chart_title = "Evolution du type de mention d'affiliation par année de publication"
    if selected_structures_afids is not None:
        df = pd.read_json(selected_structures_data).reset_index()
        df["annee_pub"] = df["annee_pub"].astype(str)
        crosstab_df = fn.get_crosstab_simple(
            df, "annee_pub", "mention_adresse_norm")
        # on gère ici les modalités de la variable à afficher
        cols = crosstab_df.iloc[:-1, :].iloc[:, :-1].columns.values.tolist()
        del cols[0]
        print(cols)
        crosstab_percent_df = fn.get_crosstab_percent(
            df, "annee_pub", "mention_adresse_norm")
        if radio_bar_datatype == "qte":
            fig = px.bar(crosstab_df.iloc[:-1, :].iloc[:, :-1], x='annee_pub',
                         y=cols, color_discrete_map=colors, title=chart_title)
            fig.update_yaxes(title_text='Nombre de mentions d\'adresse')
            fig.update_traces(textposition='inside', texttemplate="%{value}")
        if radio_bar_datatype == "percent":
            fig = px.bar(crosstab_percent_df.iloc[:-1, :], x='annee_pub',
                         y=cols, color_discrete_map=colors, title=chart_title)
            fig.update_yaxes(title_text="Pourcentage de publications")
            fig.update_traces(textposition='inside',
                              texttemplate="%{value}"+"%")
            fig.update_xaxes(title_text='Année de publication')
        fig.update_layout(legend=dict(
              orientation="h",
              y=-0.3,
            ))
        fig.for_each_trace(lambda t: t.update(name=mapping_variable[t.name],
                                          legendgroup=mapping_variable[t.name],
                                          hovertemplate=t.hovertemplate.replace(
                                              t.name, mapping_variable[t.name])
                                          ))
    else:
        fig = {}
    return fig
