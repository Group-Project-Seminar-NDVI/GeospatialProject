
import os
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
