import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from dash import Dash, dcc, html, Input, Output
import plotly.express as px


import json

def read_geojson_with_json(filepath):
    """Reads a GeoJSON file using the json library.

    Args:
        filepath (str): The path to the GeoJSON file.

    Returns:
        dict: A dictionary representing the GeoJSON data.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
def convert_data_type_to_int(column):
    return column.astype(int)

# Example usage:
geojson_data = read_geojson_with_json('/Users/robertkurdyak/laundry_flask/flaskr/data/neighbourhoods/Neighbourhoods___4326_geojson.geojson')

neighbourhood_profiles_2021 = pd.read_excel(r'/Users/robertkurdyak/laundry_flask/flaskr/data/neighbourhood-profiles/neighbourhood_profiles_2021_158_model.xlsx')

neighbourhood_profiles_2021_t = neighbourhood_profiles_2021.transpose()

new_headers = neighbourhood_profiles_2021_t.iloc[0]
neighbourhood_profiles_2021_t = neighbourhood_profiles_2021_t[1:]
neighbourhood_profiles_2021_t.columns = new_headers
neighbourhood_profiles_2021_t.columns = neighbourhood_profiles_2021_t.columns.str.strip()

neighbourhood_profiles_2021_t['AREA_SHORT_CODE'] = neighbourhood_profiles_2021_t['Neighbourhood Number'].apply(convert_data_type_to_int)
geo_df['AREA_SHORT_CODE'] = geo_df['AREA_SHORT_CODE'].apply(convert_data_type_to_int)

geo_df = gpd.GeoDataFrame.from_features(geojson_data["features"]).merge(neighbourhood_profiles_2021, on = 'AREA_SHORT_CODE')

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Summary Statistics by Toronto Neighbourhood'),
    html.P('Select a Summary Statistic:'),
    dcc.Dropdown(
        id = 'dropdown_selection',
        options = geo_df.columns
        value = 'Median total income in 2020  among recipients ($)',
        inline = 'True'),
    dcc.Graph(id='graph')
])

@app.callback(
    Output('graph', 'figure'),
    Input('dropdown_selection', 'value')
    )
def display_choropleth(dropdown_selection):
    
    df = geo_df 