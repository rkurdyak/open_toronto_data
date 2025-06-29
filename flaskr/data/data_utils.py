import pandas as pd
import os
import requests
import json

# Define the base URL for the City of Toronto CKAN API
BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

def fetch_package(package_id, base_url=BASE_URL):
    """
    Fetch the package (dataset) metadata using its ID.
    """
    url = f"{base_url}/api/3/action/package_show"
    params = {"id": package_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["result"]

def fetch_resource_data(resource, base_url=BASE_URL):
    """
    Fetch resource data depending on whether it is datastore active or not.
    Returns either raw CSV/text or binary content for download.
    """
    if resource.get("datastore_active"):
        # Option 1: Retrieve full CSV dump
        dump_url = f"{base_url}/datastore/dump/{resource['id']}"
        csv_data = requests.get(dump_url).text
        return csv_data, "csv"
    else:
        # Option 2: Retrieve resource metadata to get download URL
        meta_url = f"{base_url}/api/3/action/resource_show"
        params = {"id": resource["id"]}
        meta_response = requests.get(meta_url, params=params)
        meta_response.raise_for_status()
        resource_metadata = meta_response.json()["result"]
        download_url = resource_metadata.get("url")
        file_response = requests.get(download_url)
        file_response.raise_for_status()
        # Infer format from metadata or URL extension
        file_format = resource_metadata.get("format", "").lower() or os.path.splitext(download_url)[-1].lstrip(".")
        return file_response.content, file_format

# Load data

def save_resource(data, file_format, filepath):
    """
    Save the downloaded resource data to a file.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    mode = "w" if file_format == "csv" else "wb"
    with open(filepath, mode) as f:
        f.write(data)
    print(f"Saved file to {filepath}")

def load_csv(filepath):
    """
    Load a CSV file into a pandas DataFrame.
    """
    return pd.read_csv(filepath)

def load_json(filepath):
    """
    Load a JSON file.
    """
    with open(filepath, "r") as f:
        return json.load(f)

def process_package(package_id, data_dir="data"):
    """
    Process a package and save its resources to the data directory.
    
    Args:
        package_id (str): The ID of the package to process
        data_dir (str): The directory to save the data to (default: "data")
    """
    # Fetch package metadata
    package = fetch_package(package_id)
    
    # Create package directory
    package_dir = os.path.join(data_dir, package_id)
    os.makedirs(package_dir, exist_ok=True)
    
    # Save package metadata
    metadata_path = os.path.join(package_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(package, f, indent=2)
    
    # Iterate over resources
    for resource in package.get("resources", []):
        print(f"Processing resource: {resource.get('name')}")
        try:
            data, file_format = fetch_resource_data(resource)
            # Create a safe filename based on resource name and file format
            safe_name = "".join(
                c if c.isalnum() else "_" for c in resource['name']
            )
            filename = f"{safe_name}.{file_format}"
            filepath = os.path.join(package_dir, filename)
            
            save_resource(data, file_format, filepath)

            # Load data if it's in CSV format
            if file_format == "csv":
                df = load_csv(filepath)
                print(f"Loaded {len(df)} rows from {filename}")
            # Add additional loaders if needed
        except Exception as e:
            print(f"Failed to process resource {resource.get('id')}: {e}")
    
    return package_dir

# Taken from https://dash.plotly.com/layout

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])