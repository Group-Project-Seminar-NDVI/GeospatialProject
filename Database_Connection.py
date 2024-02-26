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
    total_area = Column(Integer)  # Added column for the total area as Integer

# Function to calculate total area by year from GeoJSON files
def calculate_total_area_by_year(folder_path):
    total_area_by_year = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.geojson'):
            # Correctly extract the year from the filename
            year = filename.split('_')[-1].replace('.geojson', '')
            geojson_path = os.path.join(folder_path, filename)
            with fiona.open(geojson_path, 'r') as src:
                for feature in src:
                    area_m2 = int(feature['properties'].get('area_m2', 0))  # Convert to int, default to 0 if not found
                    if year in total_area_by_year:
                        total_area_by_year[year] += area_m2
                    else:
                        total_area_by_year[year] = area_m2
    return total_area_by_year

# Database connection and session creation
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgis_34_sample')
Base.metadata.create_all(engine)  # This will now also create the total_area column
Session = sessionmaker(bind=engine)
session = Session()

folder_path = 'C:\\Users\\AmmarYousaf\\Fiver\\GeospatialProject\\output_geojson'

# Calculate total area for each year
total_area_by_year = calculate_total_area_by_year(folder_path)

for filename in os.listdir(folder_path):
    if filename.endswith('.geojson'):
        # Correctly extract the year from the filename
        year = filename.split('_')[-1].replace('.geojson', '')
        geojson_path = os.path.join(folder_path, filename)
        with fiona.open(geojson_path, 'r') as src:
            for feature in src:
                geom = shape(feature['geometry'])
                area_m2 = int(feature['properties'].get('area_m2', 0))
                wkt_geometry = geom.wkt
                total_area = total_area_by_year.get(year, 0)
                feature = PolygonFeature(geometry=wkt_geometry, area_m2=area_m2, year=year, total_area=total_area)
                session.add(feature)

session.commit()
session.close()
