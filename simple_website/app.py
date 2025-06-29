# WSGI entry point for Vercel deployment
from one_geojson_test import app

# For local development
if __name__ == '__main__':
    app.run(debug=True) 