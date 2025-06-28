from dash import Dash, dcc, html, Input, Output
from pathlib import Path
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

geojson_folder = Path(__file__).parent / 'GeoJSON' / 'neighbourhoods'
geojson_files = list(geojson_folder.glob('*.geojson'))

dropdown_values = {
    'statistics': ['Median Age',
                   'Median Total Income',
                   'Percent Deemed Low-Income',
                   'Average Family Size',
                   'Total # of People with Diabetes, age 20+',
                   'Total population 2022',
                   'Total population 2023',
                   'Age-Standardized Diabetes Rate',
                   'Diabetes Rate (95% CI) LL, Total',
                   'Diabetes Rate (95% CI) UL, Total',
                   'Total Diabetes Prevalence',
                   'Diabetes Prevalence (95% CI) LL, Total',
                   'Diabetes Prevalence (95% CI) UL, Total',
                   '# People with MHV',
                   'Age Standardized MHV Rate',
                   'Number of Hospitalizations',
                   'Age-Standardized Annual Hospitalization Rate (per 100 people)']
}

# Load and prepare the GeoJSON data
geojson_data = {}
# Store min and max values for each statistic
stat_ranges = {}

# First pass: load all data and calculate ranges
for f in geojson_files:
    name = f.stem
    # Read the file and ensure it's in WGS84
    gdf = gpd.read_file(f)
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    elif gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs(epsg=4326)
    # Ensure AREA_SHORT_CODE is string type
    gdf['AREA_SHORT_CODE'] = gdf['AREA_SHORT_CODE'].astype(str)
    geojson_data[name] = gdf

# Calculate min and max for each statistic across all neighborhoods
for stat in dropdown_values['statistics']:
    all_values = []
    for gdf in geojson_data.values():
        all_values.extend(gdf[stat].tolist())
    stat_ranges[stat] = {
        'min': min(all_values),
        'max': max(all_values)
    }

centre_lat, centre_lon = 43.6532, 79.3832

app = Dash(__name__)

app.layout = html.Div([
    dcc.Checklist(
        id = 'nbhd_checklist',
        options = [{'label':nbhd, 'value':nbhd} for nbhd in geojson_data.keys()],
        value = [nbhd for nbhd in geojson_data.keys()]
    ),
    dcc.Dropdown(
        id = 'statistic_dropdown',
        options = [{'label':statistic, 'value':statistic} for statistic in dropdown_values['statistics']],
        value = 'Median Age'
    ),
    html.Div([
    dcc.Graph(id = 'plot1')
    ])
])

# define callbacks

@app.callback(
    Output('plot1', 'figure'),
    [Input('nbhd_checklist', 'value'),
     Input('statistic_dropdown', 'value')]
)

def update_figures(selected_neighbourhoods, selected_dropdown):
    fig = go.Figure()
    
    # Set initial map bounds for Toronto
    toronto_bounds = {
        'north': 43.8555,  # Northern boundary
        'south': 43.5800,  # Southern boundary
        'east': -79.1150,  # Eastern boundary
        'west': -79.6392   # Western boundary
    }
    
    # Get the global min and max for the selected statistic
    min_val = stat_ranges[selected_dropdown]['min']
    max_val = stat_ranges[selected_dropdown]['max']
    
    # Only show colorbar for the first neighborhood to avoid overlapping
    for i, name in enumerate(selected_neighbourhoods):
        gj = geojson_data[name]
        
        # Convert GeoDataFrame to GeoJSON
        geojson_dict = gj.__geo_interface__
        
        # add a choropleth layer per neighbourhood
        fig.add_trace(go.Choroplethmapbox(
            geojson=geojson_dict,
            locations=gj['AREA_NAME'].tolist(),
            z=gj[selected_dropdown].tolist(),
            featureidkey='properties.AREA_NAME',
            showscale=(i == 0),  # Only show colorbar for first neighborhood
            marker_opacity=0.7,
            marker_line_width=1,
            name=name,
            colorscale='Viridis',  # Use a perceptually uniform color scale
            zmin=min_val,  # Use global min value
            zmax=max_val,  # Use global max value
            colorbar=dict(
                title=dict(
                    text=selected_dropdown,
                    font=dict(size=14)
                ),
                thickness=20,
                len=0.5,
                x=1.02,  # Position colorbar to the right of the map
                y=0.5,   # Center it vertically
                xanchor='left',
                yanchor='middle',
                ticks='outside',  # Show ticks outside the colorbar
                nticks=5  # Limit number of ticks for clarity
            ),
            hovertemplate=(
                '<b>%{location}</b><br>' +
                f'{selected_dropdown}: %{{z:.1f}}<br>' +  # Format numbers to 1 decimal place
                '<extra></extra>'
            )
        ))
    
    # Update layout with Toronto-specific settings
    fig.update_layout(
        mapbox_style='carto-positron',
        mapbox=dict(
            center=dict(lat=centre_lat, lon=centre_lon),
            zoom=10,
            bounds=toronto_bounds
        ),
        margin=dict(l=0, r=50, t=0, b=0),  # Add right margin for colorbar
        height=800,
        hovermode='closest'
    )
    
    return fig
        
    
if __name__ == '__main__':
    app.run(debug=True)