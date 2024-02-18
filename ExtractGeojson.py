import os
import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
from rasterio.features import shapes

# Function to extract green spaces from NDVI image and save as GeoJSON
def extract_green_spaces(ndvi_file, output_file):
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
        polygon = Polygon(geom['coordinates'][0])
        polygons.append({'geometry': polygon})
    gdf = gpd.GeoDataFrame(polygons)

    # Set the geometry column
    gdf.set_geometry('geometry', inplace=True)

    # Save GeoDataFrame as GeoJSON
    gdf.to_file(output_file, driver='GeoJSON')

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
        print(f"Extracted green spaces from {file} and saved as {output_file}")
