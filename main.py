import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
import fiona
from ExtractGeojson import extract_green_spaces,determine_utm_zone
from Download_CalculateNDVI import calculate_and_save_ndvi, download_and_save_band
from Database_Connection import calculate_total_area_by_year
from sentinelhub import SHConfig, BBox, CRS

def configure_sentinelhub():
    """Configure Sentinel Hub API credentials."""
    config = SHConfig()
    config.sh_client_id = 'dbb0c8db-cc18-4fe2-a3c4-ac715da01c77'  # Replace with your Sentinel Hub client ID
    config.sh_client_secret = 'xw4ZAm0eeYjoTlmu0ftCjhIlDNU3AwlT'
    config.save()

def define_bbox():
    """Define the geographical bounds of the area of interest."""
    # Example coordinates for Multan, Pakistan
    multan_coords = [71.417, 30.157, 71.529, 30.211]
    return BBox(bbox=multan_coords, crs=CRS.WGS84)

# Define the SQLAlchemy base
Base = declarative_base()

# Define the SQLAlchemy model for the polygon features
class PolygonFeature(Base):
    __tablename__ = 'polygon_features'
    id = Column(Integer, primary_key=True)
    geometry = Column(Geometry(geometry_type='POLYGON', srid=4326))
    year = Column(String)  # Assuming year is a string like '2021'
    area_m2 = Column(Integer)  # Change to Float for decimal values
    total_area = Column(Integer)  # Added column for the total area as Integer



def main():
    # Configure Sentinel Hub
    configure_sentinelhub()

    # Define bounding box
    bbox = define_bbox()

    # Download bands and calculate NDVI
    for year in [2020, 2021, 2022]:
        red_band_path = download_and_save_band('B04', year)
        nir_band_path = download_and_save_band('B08', year)
        calculate_and_save_ndvi(red_band_path, nir_band_path, year)

    # Extract GeoJSON from NDVI images and save to database
    ndvi_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\multan_data'
    output_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\output_geojson'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Database connection setup
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgis_34_sample')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
def determine_utm_zone(gdf):
    # Calculate the centroids of the GeoDataFrame in EPSG:4326
    centroids = gdf.geometry.centroid.to_crs(epsg=4326)
    
    # If there's more than one centroid, calculate the mean position
    if len(centroids) > 1:
        mean_x = centroids.x.mean()
        mean_y = centroids.y.mean()
    else:
        # For a single centroid, just use its position
        mean_x = centroids.x
        mean_y = centroids.y
    
    # Calculate UTM zone from the mean longitude
        utm_zone = int((mean_x + 180) / 6) + 1
        hemisphere = 'north' if mean_y > 0 else 'south'
        utm_crs = f'EPSG:{"326" if hemisphere == "north" else "327"}{utm_zone:02d}'
    
        return utm_crs

    # Processing each NDVI file
    for file in os.listdir(ndvi_dir):
        if file.endswith('.tif') and 'NDVI' in file.upper():
            ndvi_file = os.path.join(ndvi_dir, file)
            output_file = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_green_spaces.geojson")
            extract_green_spaces(ndvi_file, output_file)
            
            # Load GeoJSON into database
        folder_path = 'C:\\Users\\AmmarYousaf\\Fiver\\GeospatialProject\\output_geojson'
        engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgis_34_sample')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

folder_path = 'C:\\Users\\AmmarYousaf\\Fiver\\GeospatialProject\\output_geojson'
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
                

    session.commit()
    session.close()

if __name__ == "__main__":
    main()
