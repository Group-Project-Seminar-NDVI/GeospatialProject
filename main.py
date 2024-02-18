import os
import requests
import rasterio
from rasterio.transform import from_bounds
from affine import Affine
import rasterio
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

# Following functions are defined in these modules correctly
from ExtractGeojson import extract_green_spaces  # Needs to process images and extract GeoJSON

def main():
    access_token = "YOUR_ACCESS_TOKEN_HERE"

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
            with rasterio.MemoryFile(response.content) as memfile:
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
    Base = declarative_base()

    class PolygonFeature(Base):
        __tablename__ = 'polygon_features'
        id = Column(Integer, primary_key=True)
        geometry = Column(Geometry(geometry_type='POLYGON', srid=4326))
        year = Column(String)

    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgis_34_sample')

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    folder_path = 'C:\\Users\\AmmarYousaf\\Fiver\\GeospatialProject\\output_geojson'
    for filename in os.listdir(folder_path):
        if filename.endswith('.geojson'):
            year = filename.split('_')[-1].split('.')[0]  # Assuming year is the first part of the filename
            geojson_path = os.path.join(folder_path, filename)
            with fiona.open(geojson_path, 'r') as src:
                for feature in src:
                    geom = shape(feature['geometry'])
                    session.add(PolygonFeature(geometry='SRID=4326;' + geom.wkt, year=year))

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
