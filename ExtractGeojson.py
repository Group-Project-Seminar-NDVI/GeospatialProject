import os
import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import shape
from rasterio.features import shapes

def determine_utm_zone(gdf):
    centroids = gdf.geometry.centroid.to_crs(epsg=4326)
    mean_x, mean_y = centroids.x.mean(), centroids.y.mean()
    utm_zone = int((mean_x + 180) / 6) + 1
    hemisphere = 'north' if mean_y >= 0 else 'south'
    utm_crs = f'EPSG:{"326" if hemisphere == "north" else "327"}{utm_zone:02d}'
    return utm_crs

def extract_green_spaces(ndvi_file, year, accumulated_geometries):
    try:
        with rasterio.open(ndvi_file) as src:
            ndvi = src.read(1)  # Read the first band
            profile = src.profile

        green_mask = np.where(ndvi > 0.4, 1, 0).astype(np.uint8)
        green_shapes = shapes(green_mask, mask=None, transform=profile['transform'])
        polygons = [shape(geom) for geom, val in green_shapes if val == 1]
        
        if year not in accumulated_geometries:
            accumulated_geometries[year] = []
        
        accumulated_geometries[year].extend(polygons)
    except Exception as e:
        print(f"Error extracting green spaces from {ndvi_file}: {e}")

def save_yearly_green_spaces(accumulated_geometries, output_dir):
    for year, geometries in accumulated_geometries.items():
        gdf = gpd.GeoDataFrame(geometry=geometries, crs="EPSG:4326")
        utm_crs = determine_utm_zone(gdf)
        gdf_utm = gdf.to_crs(utm_crs)
        gdf_utm['area_m2'] = gdf_utm.geometry.area
        total_area = gdf_utm['area_m2'].sum()

        output_file = os.path.join(output_dir, f"total_green_spaces_{year}.geojson")
        gdf_utm.to_crs("EPSG:4326").to_file(output_file, driver='GeoJSON')
        print(f"Total green space area for {year}: {total_area} m² and saved to {output_file}")

# Ensure the output directory exists
output_dir = 'output_geojson'
os.makedirs(output_dir, exist_ok=True)

# Directory containing NDVI images
ndvi_dir = 'band_data'

# Dictionary to accumulate geometries by year
accumulated_geometries = {}

# Process each NDVI TIFF file in the directory
for file in os.listdir(ndvi_dir):
    if file.endswith('.tif') and 'NDVI' in file.upper():
        ndvi_file = os.path.join(ndvi_dir, file)
        year = file.split('_')[-1].split('.')[0]  # Assuming year is at the end of the filename
        extract_green_spaces(ndvi_file, year, accumulated_geometries)

# Save aggregated green spaces by year to GeoJSON
save_yearly_green_spaces(accumulated_geometries, output_dir)
