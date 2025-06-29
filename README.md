# Toronto Health Outcomes Mapping Dashboard

An interactive web application that visualizes health outcomes and demographic data across Toronto neighbourhoods using Dash and Plotly.

## Features

- **Interactive Choropleth Map**: Visualize health statistics across Toronto neighbourhoods
- **Distribution Analysis**: Histogram showing the distribution of selected statistics
- **Neighbourhood Comparison**: Click on neighbourhoods to see percentile rankings
- **Multiple Health Metrics**: Diabetes rates, mental health visits, hospitalizations, and demographic data

## Technologies Used

- **Dash**: Web framework for building analytical web applications
- **Plotly**: Interactive plotting library
- **GeoPandas**: Geospatial data manipulation
- **Bootstrap**: Responsive UI components

## Local Development

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd laundry_flask
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
cd simple_website
python one_geojson_test.py
```

5. Open your browser and navigate to `http://localhost:8050`

## Data Sources

The application uses health and demographic data from:
- Toronto Public Health
- Canadian Institute for Health Information
- Statistics Canada

## Deployment

This application is configured for deployment on Vercel. The repository includes:
- `vercel.json`: Vercel configuration
- `runtime.txt`: Python version specification
- `requirements.txt`: Python dependencies

## Project Structure

```
laundry_flask/
├── simple_website/
│   ├── one_geojson_test.py    # Main Dash application
│   ├── app.py                 # WSGI entry point
│   ├── assets/
│   │   └── custom.css         # Custom styling
│   └── toronto_map_data.geojson  # Geospatial data
├── requirements.txt           # Python dependencies
├── vercel.json               # Vercel configuration
├── runtime.txt               # Python runtime version
└── README.md                 # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Author

Rob Kurdyak 