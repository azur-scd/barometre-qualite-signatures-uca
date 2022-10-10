#!/usr/local/bin python
# -*- coding: utf-8 -*-
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
import dash_dvx as dvx
import config

dash.register_page(__name__, path='/data')

# config params
publis_last_obs_date = config.PUBLIS_LAST_OBS_DATE

# get relative db folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "publications.db").resolve()

dbEngine = sqla.create_engine(f'sqlite:///{DB_PATH}')

#regroup data
df_bsi_publis_uniques = pd.read_sql(
    f'select * from bsi_publis_uniques_{publis_last_obs_date}', dbEngine)
#detail data
df_bsi_all_by_mention = pd.read_sql(
    f'select * from bsi_all_by_mention_adresse_{publis_last_obs_date}', dbEngine)

grid_bsi_publis_uniques = dvx.Grid(
        id="grid_regroup",
        dataSource=df_bsi_publis_uniques.to_dict(orient="records"),
        columns=[{
            "dataField": "dc_identifiers",
            "caption": "Id Scopus", },
            {
            "dataField": "prism_doi",
            "caption": "DOI" 
            },
            {
            "dataField": "reference",
            "caption": "Rérérence" 
            },
            {
            "dataField": "annee_pub",
            "caption": "Année de publication" 
            },
            {
            "dataField": "corresponding_author",
            "caption": "Auteur de correspondance UCA" 
            },
            {
            "dataField": "Is_dc_creator",
            "caption": "Auteur créateur UCA" 
            },
             {
            "dataField": "regroup_mention_adresse_norm",
            "caption": "(all) Mentions aff normalisées" ,
            "visible": False
            },
              {
            "dataField": "regroup__afids",
            "caption": "(all) Id Scopus de structures",
            "visible": False
            },
             {
            "dataField": "regroup_affiliation_name",
            "caption": "(all) Affiliations" 
            },
             {
            "dataField": "regroup_ce_indexed_name",
            "caption": "(all) Auteurs" 
            },
             {
            "dataField": "synthese_mention_adresse_norm",
            "caption": "(synthese) Mention aff normalisée",
            }],
        keyExpr="dc_identifiers",
        selectionMode="none",
        columnChooserIsEnabled=True,
        pageSizeSelectorIsEnabled=True,
        allowedPageSizes=[5, 10, 20, 50]
    )

grid_bsi_all_by_mention = dvx.Grid(
            id="grid_detail",
            dataSource=df_bsi_all_by_mention.to_dict(orient="records"),
            columns=[{
            "dataField": "dc_identifiers",
            "caption": "Id Scopus", },
            {
            "dataField": "prism_doi",
            "caption": "DOI" 
            },
            {
            "dataField": "reference",
            "caption": "Rérérence" 
            },
            {
            "dataField": "annee_pub",
            "caption": "Année de publication" 
            },
            {
            "dataField": "_afids",
            "caption": "Id Scopus de structure",
            "visible": False
            },
            {
            "dataField": "mentionAffil_reconstruct",
            "caption": "(source) Mention affiliation" 
            },
             {
            "dataField": "_auid",
            "caption": "Is Scopus auteur" ,
            "visible": False
            },
              {
            "dataField": "ce_indexed_name",
            "caption": "Auteur",
            },
             {
            "dataField": "_orcid",
            "caption": "Orcid",
            "visible": False
            },
            {
            "dataField": "corresponding_author",
            "caption": "Auteur de correspondance UCA" 
            },
             {
            "dataField": "Is_dc_creator",
            "caption": "Auteur créateur UCA" ,
            },
              {
            "dataField": "mentionAffil_reconstruct_subsentence_cleaned",
            "caption": "Mention aff nettoyée",
            "visible": False
            },
              {
            "dataField": "fuzzy_uca_developpee",
            "caption": "Score forme UCA développée",
            "visible": False
            },
             {
            "dataField": "fuzzy_uca_sigle",
            "caption": "Score forme UCA sigle",
            "visible": False
            },
              {
            "dataField": "fuzzy_uns",
            "caption": "Score forme UNS",
            "visible": False
            },
              {
            "dataField": "mention_adresse_norm",
            "caption": "Mention aff normalisée",
            },
              {
            "dataField": "affiliation_name",
            "caption": "Affiliation",
            }],
            keyExpr="dc_identifiers",
            selectionMode="none",
            columnChooserIsEnabled=True,
            pageSizeSelectorIsEnabled=True,
            allowedPageSizes=[5, 10, 20, 50]
        )

layout = html.Div(
    dbc.Row([
        html.H3("Dataset des publications", className="text-center"),
        grid_bsi_publis_uniques,
        html.H3("Dataset des mentions d'affiliation", className="text-center"),
        grid_bsi_all_by_mention,
    ])
)