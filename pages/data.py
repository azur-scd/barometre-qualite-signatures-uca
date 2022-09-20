#!/usr/local/bin python
# -*- coding: utf-8 -*-
import pathlib
import dash
import pandas as pd
import json
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_dvx as dvx
import config

dash.register_page(__name__, path='/data')

# config variables
observation_date = config.OBSERVATION_DATE

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data", observation_date).resolve()

# helpers functions

# Load data
df_detail = pd.read_csv(DATA_PATH.joinpath(
    "detail_controle_mentionAdresses.csv"), sep=',', encoding="utf-8", dtype={"@afids": str})
df_regroup = pd.read_csv(DATA_PATH.joinpath(
    "regroupbypublis_controle_mentionAdresses.csv"), sep=',', encoding="utf-8", dtype={"annee_pub": str})

# Page layout

layout = html.Div([
    html.Div(html.H4('Dataset des publications'),
             className="row flex-display"),
    html.Div(dvx.Grid(
        id="grid_regroup",
        dataSource=df_regroup.to_dict(orient="records"),
        columns=[{
            "dataField": "dc:identifiers",
            "caption": "Id Scopus", },
            {
            "dataField": "prism:doi",
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
            "dataField": "Is_dc:creator",
            "caption": "Auteur créateur UCA" 
            },
             {
            "dataField": "regroup_mention_adresse_norm",
            "caption": "(all) Mentions aff normalisées" ,
            "visible": False
            },
              {
            "dataField": "regroup_@afids",
            "caption": "(all) Id Scopus de structures",
            "visible": False
            },
             {
            "dataField": "regroup_affiliation_name",
            "caption": "(all) Affiliations" 
            },
             {
            "dataField": "regroup_ce:indexed-name",
            "caption": "(all) Auteurs" 
            },
             {
            "dataField": "synthese_mention_adresse_norm",
            "caption": "(synthese) Mention aff normalisée" 
            }],
        keyExpr="dc:identifiers",
        selectionMode="none",
        columnChooserIsEnabled=True,
        pageSizeSelectorIsEnabled=True,
        allowedPageSizes=[5, 10, 20, 50]
    ),
        className="row flex-display"),
        html.Hr(),
    html.Div(html.H4('Dataset des mentions d\'affiliation'),
             className="row flex-display"),
    html.Div(
        dvx.Grid(
            id="grid_detail",
            dataSource=df_detail.to_dict(orient="records"),
            columns=[{
            "dataField": "dc:identifiers",
            "caption": "Id Scopus", },
            {
            "dataField": "prism:doi",
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
            "dataField": "@afids",
            "caption": "Id Scopus de structure",
            "visible": False
            },
            {
            "dataField": "mentionAffil_reconstruct",
            "caption": "(source) Mention affiliation" 
            },
             {
            "dataField": "@auid",
            "caption": "Is Scopus auteur" ,
            "visible": False
            },
              {
            "dataField": "ce:indexed-name",
            "caption": "Auteur",
            },
             {
            "dataField": "@orcid",
            "caption": "Orcid",
            "visible": False
            },
            {
            "dataField": "corresponding_author",
            "caption": "Auteur de correspondance UCA" 
            },
             {
            "dataField": "Is_dc:creator",
            "caption": "Auteur créateur UCA" ,
            },
              {
            "dataField": "mentionAffil_reconstruct_subsentence_cleaned",
            "caption": "Mention aff nettoyéé",
            "visible": False
            },
              {
            "dataField": "fuzzy_extractone_uca_developpee",
            "caption": "Score forme UCA développée",
            "visible": False
            },
             {
            "dataField": "fuzzy_extractone_uca_sigle",
            "caption": "Score forme UCA sigle",
            "visible": False
            },
              {
            "dataField": "fuzzy_extractone_uns_developpee",
            "caption": "Score forme UNS développée",
            "visible": False
            },
             {
            "dataField": "fuzzy_extractone_uns_sigle",
            "caption": "Score forme UNS sigle",
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
            keyExpr="dc:identifiers",
            selectionMode="none",
            columnChooserIsEnabled=True,
            pageSizeSelectorIsEnabled=True,
            allowedPageSizes=[5, 10, 20, 50]
        ),
        className="row flex-display")
])
