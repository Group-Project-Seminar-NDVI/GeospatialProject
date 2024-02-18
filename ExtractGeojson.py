import os
import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, shape
from rasterio.features import shapes
from shapely.validation import explain_validity
from pyproj import CRS

# Bounding box coordinates
bbox = [71.3965, 30.1526, 71.5794, 30.2733]

# Function to extract green spaces from NDVI image and save as GeoJSON
def extract_green_spaces(ndvi_file, output_file):
    try:
        # Open NDVI image
        with rasterio.open(ndvi_file) as src:
            ndvi = src.read(1)
            profile = src.profile

        # Threshold NDVI to identify green areas
        green_mask = np.where(ndvi > 0.4, 1, 0).astype(np.uint8)  # Adjust threshold as needed for green spaces

        # Generate polygons from thresholded image
        green_shapes = shapes(green_mask, mask=None, connectivity=4, transform=profile['transform'])

        # Convert polygons to GeoDataFrame
        polygons = []
        for geom, val in green_shapes:
            try:
                polygon = Polygon(shape(geom))
                if polygon.is_valid:
                    polygons.append({'geometry': polygon})
                else:
                    print(f"Invalid geometry detected: {explain_validity(polygon)}")
            except Exception as e:
                print(f"Error processing geometry: {e}")

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(polygons, crs=CRS.from_epsg(4326))

        # Set the geometry column
        gdf.set_geometry('geometry', inplace=True)

        # Add bounding box as CRS
        gdf.to_crs(f"EPSG:4326", inplace=True)

        # Save GeoDataFrame as GeoJSON
        gdf.to_file(output_file, driver='GeoJSON')
        print(f"Extracted green spaces from {ndvi_file} and saved as {output_file}")

    except Exception as e:
        print(f"Error extracting green spaces from {ndvi_file}: {e}")

# Directory containing NDVI images
ndvi_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\multan_data'

# Output directory for GeoJSON files
output_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\output_geojson'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Iterate through NDVI files in directory
for file in os.listdir(ndvi_dir):
    if file.endswith('.tif'):
        ndvi_file = os.path.join(ndvi_dir, file)
        output_file = os.path.join(output_dir, f'{os.path.splitext(file)[0]}_green_spaces.geojson')
        extract_green_spaces(ndvi_file, output_file)
