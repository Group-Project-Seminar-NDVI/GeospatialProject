import os
import fiona
from shapely.geometry import shape, mapping
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

# Define the SQLAlchemy base
Base = declarative_base()

# Define the SQLAlchemy model for the polygon features
class PolygonFeature(Base):
    __tablename__ = 'polygon_features'
    id = Column(Integer, primary_key=True)
    geometry = Column(Geometry(geometry_type='POLYGON', srid=4326))
    year = Column(String)
    area_m2 = Column(Float)  # Add a column for the area in square meters

# Define function to convert GeoJSON to Shapely geometry and calculate area
def geojson_to_shapely_and_area(geojson_path, year):
    with fiona.open(geojson_path, 'r') as src:
        shapely_features_and_area = []
        for feature in src:
            geom = shape(feature['geometry'])
            # Calculate the area in square meters. Note: this is a placeholder
            # You might need to project this geometry to a metric CRS to accurately calculate the area
            # For simplicity, we're not transforming the geometry here
            area_m2 = geom.area  # This is not accurate for EPSG:4326
            shapely_features_and_area.append((geom, area_m2))
    return shapely_features_and_area

# Connect to the database
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgis_34_sample')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Specify the folder containing GeoJSON files
folder_path = 'C:\\Users\\AmmarYousaf\\Fiver\\GeospatialProject\\output_geojson'

# Assuming the 'geojson_to_shapely' function is adjusted to return a list of tuples (geometry, area)
for filename in os.listdir(folder_path):
    if filename.endswith('.geojson'):
        year = '_'.join(filename.split('_')[:-1])  # Extract year from filename
        geojson_path = os.path.join(folder_path, filename)
        # Convert GeoJSON to Shapely geometry and get areas
        shapely_features_with_area = geojson_to_shapely_and_area(geojson_path, year)
        # Insert Shapely features and their areas into the database
        for shapely_feature, area_m2 in shapely_features_with_area:
            wkt_geometry = shapely_feature.wkt
            feature = PolygonFeature(geometry=wkt_geometry, area_m2=area_m2, year=year)
            session.add(feature)

# Don't forget to commit and close the session as before
session.commit()
session.close()


session.commit()


session.close()
