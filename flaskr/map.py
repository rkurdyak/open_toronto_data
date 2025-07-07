from dash import Dash, html, dcc, callback, Output, Input

import plotly.express as px
import pandas as pd
import geopandas as gpd
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


neighbourhood_geojson = read_geojson_with_json('/Users/robertkurdyak/laundry_flask/flaskr/data/neighbourhoods/Neighbourhoods___4326_geojson.geojson')

neighbourhood_profiles_2021 = pd.read_excel(r'/Users/robertkurdyak/laundry_flask/flaskr/data/neighbourhood-profiles/neighbourhood_profiles_2021_158_model.xlsx')

neighbourhood_profiles_2021_t = neighbourhood_profiles_2021.transpose()

new_headers = neighbourhood_profiles_2021_t.iloc[0]
neighbourhood_profiles_2021_t = neighbourhood_profiles_2021_t[1:]
neighbourhood_profiles_2021_t.columns = new_headers
neighbourhood_profiles_2021_t.columns = neighbourhood_profiles_2021_t.columns.str.strip()

app = Dash(
    __name__,
    meta_tags = [
        {
            "name":"viewport", "content":"width=device_width, initial_scale = 1.0"
            }
        ]
    
    
)

tester = neighbourhood_profiles_2021_t[["AREA_SHORT_CODE", "AREA_NAME",
                 r'Total - Age groups of the population - 25% sample data',
                 'Average age of the population',
                 'Median age of the population',
                 'Median total income in 2020  among recipients ($)',
                 'Average total income in 2020 among recipients ($)',
                 "geometry"]]

selectable_columns = [col for col in tester.columns if col not in ["AREA_SHORT_CODE", "AREA_NAME"]] 

# Requires Dash 2.17.0 or later
app.layout = [
    html.H1(children='Toronto Neighbourhoods', style={'textAlign':'center'}),
    dcc.Dropdown(selectable_columns, 'Average age of the poluation', id='dropdown_selection'),
    dcc.Graph(id = 'choropleth_graph')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown_selection', 'value')
)
def display_choropleth(dropdown_selection):
    df = tester
    geojson = neighbourhood
    dff = df[df.dropdown_selection==value]
    
    fig = px.choropleth(
        tester, geojson = geojson, color = dropdown_selection,
        locations='AREA_NAME', featureidkey = 'properties.AREA_SHORT_CODE',
        range_color= [0,6500])
    
    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)