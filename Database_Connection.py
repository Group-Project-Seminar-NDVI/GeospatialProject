import os
import fiona
from shapely.geometry import shape
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

# Define the SQLAlchemy base
Base = declarative_base()

# Define the SQLAlchemy model for the polygon features
class PolygonFeature(Base):
    __tablename__ = 'polygon_features'
    id = Column(Integer, primary_key=True)
    geometry = Column(Geometry(geometry_type='POLYGON', srid=4326))
    year = Column(String)
    area_m2 = Column(Integer)  # Column for the area in square meters as Integer

# Define function to extract GeoJSON features and their area property
def geojson_to_shapely_and_area(geojson_path, year):
    with fiona.open(geojson_path, 'r') as src:
        shapely_features_and_area = []
        for feature in src:
            geom = shape(feature['geometry'])
            # Extract area from feature properties, assuming 'area_m2' is the key
            area_m2 = int(feature['properties'].get('area_m2', 0))  # Convert to int, default to 0 if not found
            shapely_features_and_area.append((geom, area_m2))
    return shapely_features_and_area

# Database connection and session creation
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgis_34_sample')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

folder_path = 'C:\\Users\\AmmarYousaf\\Fiver\\GeospatialProject\\output_geojson'
for filename in os.listdir(folder_path):
    if filename.endswith('.geojson'):
        year = '_'.join(filename.split('_')[:-1])  # Extract year from filename
        geojson_path = os.path.join(folder_path, filename)
        shapely_features_with_area = geojson_to_shapely_and_area(geojson_path, year)
        for shapely_feature, area_m2 in shapely_features_with_area:
            # Convert Shapely geometry to WKT for storage
            wkt_geometry = shapely_feature.wkt
            feature = PolygonFeature(geometry=wkt_geometry, area_m2=area_m2, year=year)
            session.add(feature)

session.commit()
session.close()
