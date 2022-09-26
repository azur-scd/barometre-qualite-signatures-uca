import pandas as pd
import dash_loading_spinners as dls

def get_crosstab_simple(df, col1, col2):
    c = pd.crosstab(df[col1], df[col2], normalize=False,
                    margins=True, margins_name="Total").reset_index()
    return c


def get_crosstab_percent(df, col1, col2):
    c = (pd.crosstab(df[col1], df[col2], normalize='index',
         margins=True, margins_name="Total")*100).round(1).reset_index()
    return c


def get_crosstab_indice(df, cols_to_keep):
    # Prend en entrée un crosstab avec margins=True
    indice_data = df.iloc[:-1, :].iloc[:, :-1]
    for c in cols_to_keep:
        indice_data[f'indice_{c}'] = (indice_data[c].div(
            indice_data[c].iloc[0])*100).round(2)
    return indice_data

def load_with_spinner(composant):
    return dls.Hash(composant,
                        color="#435278",
                        speed_multiplier=2,
                        size=80,)