import os
import fiona
from shapely.geometry import shape
from sqlalchemy import create_engine, Column, Integer, String
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
    year = Column(String)  # Add a new column for year

# Define function to convert GeoJSON to Shapely geometry
def geojson_to_shapely(geojson_path, year):
    with fiona.open(geojson_path, 'r') as src:
        shapely_features = []
        for feature in src:
            geometry = shape(feature['geometry'])
            shapely_features.append(geometry)
    return shapely_features

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
        shapely_features = geojson_to_shapely(geojson_path, year)
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
