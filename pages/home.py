import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import config

dash.register_page(__name__, path='/')

url_subpath = config.URL_SUBPATH

jumbotron = html.Div(
    dbc.Container(
        [
            html.H2("Barometre des signatures des publications scientifiques UCA", className="lead display-6 text-center mb-5"),
            html.P(children=[
            html.Span("Le baromètre des signatures des publications UCA est un outil de suivi de la qualité de l'identification (et donc de la visibilité) d'UCA et de ses structures de recherche dans le contexte de l'évaluation de la production scientifique de l'établissement. "),
              html.Strong("Le périmètre du baromètre des signatures recouvre exclusivement les publications référencées dans Scopus. Les données de l'année N sont stabilisées à l'été N+1."),
              ],
              className="lead"
              ),
            dcc.Markdown('''
               Les indicateurs calculés portent sur l'analyse des mentions d'adresse de chaque publication (il peut y en avoir plusieurs par publication en cas de co-auteurs UCA) et sur l'analyse de la qualité des signatures au niveau agrégé des publications.
               Dans le cas où une publication implique plusieurs laboratoires, elle est donc comptabilisée plusieurs fois dans l'analyse des mentions d'afiliation, par contre elle ne sera comptabilisée qu'une seule fois dans l'analyse au niveau publication. 

               Conformément à la [charte de signature scientifique UCA](https://univ-cotedazur.fr/recherche-innovation/services-aux-chercheurs/signature-scientifique-1), quatre cas de figure ont été évalués :
               - **Cas 1. Université Côte d'Azur (forme développée)** : la publication contient au moins une mention d'affiliation qui comprend la forme littérale (sous toutes ses variantes possibles) d'Université Côte d'Azur
               - **Cas 2. UCA (Sigle)** : Université Côte d'Azur n'est pas mentionnée sous sa forme développée mais la publication contient au moins une mention d'affiliation qui comprend seulement le sigle UCA
               - **Cas 3. Université Nice Sophia Antipolis ou UNS** : Université côte d'Azur n'est pas mentionnée (ni sous forme littérale ni avec son sigle) mais la publication comprend au moins une mention d'affiliation qui comprend le sigle UNS ou la forme littérale (sous toutes ses variantes possibles) d'Université Nice Sophia Antipolis
               - **Cas 4. Université Côte d'Azur n'est pas mentionnée** : Université Côte d'Azur (forme littérale ou sigle) n'est présente dans aucune des mentions d'affiliation de la publication (la publication alors est repérée par la structure de recherche ou l'établissement composante)
'''),
            html.P(
                dbc.Button("Accéder au tableau de bord", color="primary",href=f"{url_subpath}/dashboard",), className="lead text-center"
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