import os
import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import shape
from rasterio.features import shapes

# Directory containing NDVI images
ndvi_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\band_data'

# Output directory for GeoJSON files
output_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\output_geojson'

# Function to extract green spaces from NDVI image and save as GeoJSON
def extract_green_spaces(ndvi_file, output_file):
    try:
        with rasterio.open(ndvi_file) as src:
            ndvi = src.read(1)  # Read the first band
            profile = src.profile

        # Identify green areas (NDVI > 0.3)
        green_mask = np.where(ndvi > 0.4, 1, 0).astype(np.uint8)

        # Generate shapes from the green areas mask
        green_shapes = shapes(green_mask, mask=None, transform=profile['transform'])

        # Create polygons for each shape
        polygons = [shape(geom) for geom, val in green_shapes if shape(geom).is_valid]

        # Create a GeoDataFrame from the polygons and set the CRS to the image's CRS
        gdf = gpd.GeoDataFrame(geometry=polygons, crs=profile['crs'])

        # Ensure the GeoDataFrame is in EPSG:4326 for GeoJSON compatibility
        gdf = gdf.to_crs("EPSG:4326")

        # Save the GeoDataFrame as a GeoJSON file
        gdf.to_file(output_file, driver='GeoJSON')
        print(f"Extracted green spaces from {ndvi_file} and saved as {output_file}")

    except Exception as e:
        print(f"Error extracting green spaces from {ndvi_file}: {e}")

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

# Process each NDVI TIFF file in the directory
for file in os.listdir(ndvi_dir):
    if file.endswith('.tif') and 'NDVI' in file.upper() :
        ndvi_file = os.path.join(ndvi_dir, file)
        output_file = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_green_spaces.geojson")
        extract_green_spaces(ndvi_file, output_file)
