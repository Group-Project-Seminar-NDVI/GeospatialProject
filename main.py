import os
import webbrowser
import requests
import rasterio
from rasterio.transform import from_bounds
import rasterio.io
from affine import Affine
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
from rasterio.features import shapes
import fiona
from shapely.geometry import shape
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from ExtractGeojson import extract_green_spaces  # Assuming this function exists and correctly extracts GeoJSON

# Define the SQLAlchemy base
Base = declarative_base()

# Define the SQLAlchemy model for the polygon features
class PolygonFeature(Base):
    __tablename__ = 'polygon_features'
    id = Column(Integer, primary_key=True)
    geometry = Column(Geometry(geometry_type='POLYGON', srid=4326))
    year = Column(String)  # Add a new column for year

def main():
    access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ3dE9hV1o2aFJJeUowbGlsYXctcWd4NzlUdm1hX3ZKZlNuMW1WNm5HX0tVIn0.eyJleHAiOjE3MDgzODU1MjAsImlhdCI6MTcwODM4MTkyMCwianRpIjoiYzUwYmRjMjYtM2I1Ny00YjJmLWIwOWItMzIxYWRmNDJkMGIxIiwiaXNzIjoiaHR0cHM6Ly9zZXJ2aWNlcy5zZW50aW5lbC1odWIuY29tL2F1dGgvcmVhbG1zL21haW4iLCJzdWIiOiJmOWJiNDk4Yi0wMDZlLTRjNjAtOGY4Zi02M2UyMDA4ODZiYTYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJkYmIwYzhkYi1jYzE4LTRmZTItYTNjNC1hYzcxNWRhMDFjNzciLCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJjbGllbnRIb3N0IjoiNzkuMTY5LjYxLjk2IiwiY2xpZW50SWQiOiJkYmIwYzhkYi1jYzE4LTRmZTItYTNjNC1hYzcxNWRhMDFjNzciLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC1kYmIwYzhkYi1jYzE4LTRmZTItYTNjNC1hYzcxNWRhMDFjNzciLCJjbGllbnRBZGRyZXNzIjoiNzkuMTY5LjYxLjk2IiwiYWNjb3VudCI6ImMxYTkwZjQ4LWNhYjctNDJmNC1hNmQ4LWM5OTU0ZDBkNjk2ZSJ9.I-c9qWIlcBxxLsFy8cKa_y1QeIWwd4ILdkqUm-6xtl-uQMVl-_PREr-a77qBKd9CVEX4dwvnwnNUVsV1HOzZCh--JsFEV01KuhvA-3-DgeWwQhAvp02_02Kivos8hd_lV6k2mph3xuumGI-IA6MOYtnfOpN7HJezAnlarZTHSa61nStBwbyr00-SluixqUJMuNBfWiY09_ovi8oaWr73oDH54p2lii0QWGaRvpW4esoQK2X-kpDiRcuywMGcC335M8bzCyI_IvAyOf0N3sBuvRRh7Oxr7xTM1mfBcyCUbiexoGpz7WDeyLRZR4aOH8N7hjxq9CX5HWOGnXzyeSITfw"

    # Define the URL for downloading data
    download_url = "https://services.sentinel-hub.com/api/v1/process"
    bbox = [71.3965, 30.1526, 71.5794, 30.2733]

    # Define the output directory to save the files
    output_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\multan_data'

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define the payload template
    payload_template = {
        "input": {
            "bounds": {
                "bbox": bbox
            },
            "data": [{
                "type": "sentinel-2-l2a"
            }]
        },
        "evalscript": """
        //VERSION=3

        function setup() {
          return {
            input: ["B04", "B08"],
            output: {
              bands: 2
            }
          };
        }

        function evaluatePixel(
          sample,
          scenes,
          inputMetadata,
          customData,
          outputMetadata
        ) {
          var ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
          return [ndvi, ndvi, ndvi];
        }
        """
    }

    # Define the headers
    headers = {"Authorization": f"Bearer {access_token}"}

    # Loop through each year from 2015 to 2023
    for year in range(2015, 2024):
        # Update the time range for the current year
        time_range = f"{year}-11-11", f"{year}-12-31"

        # Update the payload with the new time range
        payload = payload_template.copy()
        payload["input"]["time"] = {
            "from": time_range[0],
            "to": time_range[1]
        }

        # Make the POST request to download data
        response = requests.post(download_url, headers=headers, json=payload)

        # Check if request was successful
        if response.status_code == 200:
            # Save the response content to a file
            filename = os.path.join(output_dir, f"ndvi_data_{year}.tif")
            with rasterio.io.MemoryFile(response.content) as memfile:
                with memfile.open() as src:
                    transform = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], src.width, src.height)
                    profile = src.profile
                    profile.update({
                        'driver': 'GTiff',
                        'crs': 'EPSG:4326',
                        'transform': transform
                    })
                    with rasterio.open(filename, 'w', **profile) as dst:
                        dst.write(src.read())
            print(f"NDVI data for {year} downloaded and saved as GeoTIFF successfully.")
        else:
            print(f"Failed to download NDVI data for {year}: {response.text}")

    # Step 2: Extract GeoJSON from the downloaded NDVI images
    bbox = [71.3965, 30.1526, 71.5794, 30.2733]
    ndvi_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\multan_data'
    output_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\output_geojson'

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through NDVI files in directory
    for file in os.listdir(ndvi_dir):
        if file.endswith('.tif'):
            ndvi_file = os.path.join(ndvi_dir, file)
            output_file = os.path.join(output_dir, f'{os.path.splitext(file)[0]}_green_spaces.geojson')
            extract_green_spaces(ndvi_file, output_file)

    # Step 3: Connect to the database and perform operations
    # Connect to the database
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgis_34_sample')

    # Create tables if they do not exist
    Base.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Specify the folder containing GeoJSON files
    folder_path = 'C:\\Users\\AmmarYousaf\\Fiver\\GeospatialProject\\output_geojson'

    # Iterate over GeoJSON files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.geojson'):
            year = '_'.join(filename.split('_')[:-1])  # Extract year from filename
            geojson_path = os.path.join(folder_path, filename)
            # Convert GeoJSON to Shapely geometry
            shapely_features = []
            with fiona.open(geojson_path, 'r') as src:
                for feature in src:
                    geometry = shape(feature['geometry'])
                    shapely_features.append(geometry)
            # Insert Shapely features into the database
            for shapely_feature in shapely_features:
                # Get the WKT representation of the geometry
                wkt_geometry = shapely_feature.wkt
                # Create a PolygonFeature object and add it to the session
                feature = PolygonFeature(geometry=wkt_geometry, year=year)
                session.add(feature)

    # Commit changes
    session.commit()

    # Query the database to ensure data insertion
    features = session.query(PolygonFeature).all()
    for feature in features:
        print(feature.id, feature.year)

    # Close session
    session.close()

if __name__ == "__main__":
    main()
    

