from dash import Dash, dcc, html, Input, Output
from pathlib import Path
import geopandas as gpd
import plotly.express as px
from plotly.figure_factory import create_distplot
import dash_bootstrap_components as dbc
from scipy.stats import percentileofscore

# Path to your single GeoJSON file containing all neighbourhoods and statistics
geojson_path = Path(__file__).parent / 'toronto_map_data.geojson'

# Load the master GeoDataFrame
gdf = gpd.read_file(geojson_path)
# Ensure CRS is WGS84 (EPSG:4326)
if gdf.crs is None or gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

colors = ['green']
# List of statistics available in the GeoJSON properties
statistics = [
    'Median Age',
    'Median Total Income',
    'Percent Deemed Low-Income',
    'Average Family Size',
    'Total # of People with Diabetes, age 20+',
    'Total population 2022',
    'Total population 2023',
    'Age-Standardized Diabetes Rate',
    'Total Diabetes Prevalence',
    'Number of People with Mental-Health-Related Visits',
    'Age-Standardized Mental Health Visitation Rate',
    'Number of Hospitalizations',
    'Age-Standardized Annual Hospitalization Rate (per 100 people)'
]

# Compute global min/max for each statistic
stat_ranges = {
    stat: {
        'min': gdf[stat].min(),
        'max': gdf[stat].max()
    }
    for stat in statistics
}

# Centre of Toronto for map
centre_lat, centre_lon = 43.6532, -79.3832

# Initialise Dash app
app = Dash(__name__, 
        #    requests_pathname_prefix='/simple_website/', 
        #    routes_pathname_prefix='/simple_website/', 
           external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
# Layout with DBC components
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1(
                'Mapping Health Outcomes Across Toronto Neighbourhoods',
                className='app-title text-center'
            ),
            html.H2(
                'By Rob Kurdyak',
                className='app-subtitle text-center'
            )
        ])
    ], className='app-header mb-4'),

    # Statistic Dropdown above graphs
    dbc.Row([
        dbc.Col([
            html.H6("Select Statistic:", className='mt-4 mb-3 text-center'),
            dcc.Dropdown(
                id='statistic_dropdown',
                options=[
                    {'label': stat, 'value': stat}
                    for stat in statistics
                ],
                value=statistics[0],
                className='statistic-dropdown'
            )
        ], width=6)
    ], className='mb-4 justify-content-center'),

    # Map and Graph Side by Side
    dbc.Row([
        # Map Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Toronto Neighbourhood Map",
                               className='map-title text-center'),
                dbc.CardBody([
                    dcc.Graph(
                        id='map_graph',
                        config={'scrollZoom': True},
                        className='map-container full-height-graph',
                        style={'height': '100%'}
                    )
                ])
            ], className='full-height-card')
        ], width=6),
        # Graph Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Distribution Analysis",
                               className='graph-title text-center'),
                dbc.CardBody([
                    html.Div(
                        id='percentile_text',
                        className='percentile-text',
                        style={'margin-bottom': '1rem'}
                    ),
                    dcc.Graph(id='dist_graph', className='graph-container full-height-graph', style={'height': '100%'})
                ])
            ], className='full-height-card')
        ], width=6)
    ]),
], fluid=True)

# Callback to update map based on selected statistic
@app.callback(
    Output('map_graph', 'figure'),
    [Input('statistic_dropdown', 'value')]
)
def update_map(selected_stat):
    zmin = stat_ranges[selected_stat]['min']
    zmax = stat_ranges[selected_stat]['max']
    # Custom colorblind-friendly sequential scale
    custom_scale = ['#f8f9fa', '#c7d59f', '#9bad4e']
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.__geo_interface__,
        locations='AREA_NAME',
        featureidkey='properties.AREA_NAME',
        color=selected_stat,
        color_continuous_scale='viridis',
        opacity=0.85,
        range_color=(zmin, zmax),
        mapbox_style='carto-positron',
        center={'lat': centre_lat, 'lon': centre_lon},
        zoom=10,
        hover_name='AREA_NAME',
        hover_data={selected_stat: ':.1f'}
    )
    fig.update_layout(
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        hovermode='closest',
        coloraxis_colorbar=dict(
            title=selected_stat,
            tickfont=dict(color='#9bad4e'),
            # titlefont=dict(color='#9bad4e'),
            bgcolor='#f8f9fa',
            outlinecolor='#ebb39b',
            thickness=18
        )
    )
    return fig

# Callback to update histogram and percentile text based on click and statistic
@app.callback(
    [Output('dist_graph', 'figure'),
     Output('percentile_text', 'children')],
    [Input('map_graph', 'clickData'),
     Input('statistic_dropdown', 'value')]
)
def update_dist_and_text(clickData, selected_stat):
    data = gdf[selected_stat].dropna().values
    group_labels = [selected_stat]
    fig = create_distplot(
        [data],
        group_labels,
        show_hist=True,
        show_rug=False,
        histnorm='probability density',
        colors=['#21968a']
    )
    
    # Update the histogram bars to be more discernible
    for trace in fig.data:
        if trace.type == 'histogram':
            trace.marker.line.width = 1  # Add border to bars
            trace.marker.line.color = '#2d5016'  # Darker border color
            trace.opacity = 0.8  # Slightly more opaque
            trace.nbinsx = 15  # Fewer bins for wider bars
    
    text = ''
    # If a neighbourhood is clicked, show its value and percentile
    if clickData and clickData.get('points'):
        val = clickData['points'][0]['z']
        name = clickData['points'][0]['location']
        min_val = data.min()
        max_val = data.max()
        # Determine annotation position based on proximity to min/max
        if abs(val - min_val) < abs(val - max_val):
            annotation_pos = 'top right'
        else:
            annotation_pos = 'top left'
        fig.add_vline(
            x=val,
            line_dash='dash',
            annotation_text=name,
            annotation_position=annotation_pos,
            line_color='black',
            line_width=3  # Make the vertical line more visible
        )
        pct = percentileofscore(gdf[selected_stat], val, kind='rank')
        if pct >= 50:
            text = (f"{name}'s {selected_stat} is higher than "
                    f"{pct:.1f}% of Toronto neighbourhoods.")
        else:
            lower_pct = 100 - pct
            text = (f"{name}'s {selected_stat} is lower than "
                    f"{lower_pct:.1f}% of Toronto neighbourhoods.")
    else:
        # Fallback: show summary stats
        mean_val = gdf[selected_stat].mean()
        median_val = gdf[selected_stat].median()
        min_val = gdf[selected_stat].min()
        max_val = gdf[selected_stat].max()
        text = (
            f"Toronto Neighbourhoods\n"
            f"Mean: {mean_val:.2f}    "
            f"Median: {median_val:.2f}    "
            f"Min: {min_val:.2f}    "
            f"Max: {max_val:.2f}"
        )
    
    fig.update_layout(
        margin={'l': 40, 'r': 40, 't': 40, 'b': 40},
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='#f8f9fa',
        font=dict(color='#9bad4e'),
        xaxis=dict(title=selected_stat, color='#9bad4e'),
        yaxis=dict(title='Percentage of Neighbourhoods', color='#9bad4e')
    )
    return fig, text

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
