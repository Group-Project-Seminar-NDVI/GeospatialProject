import os
import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import shape, MultiPoint
from rasterio.features import shapes

# Function to determine UTM zone for a given CRS
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

def extract_green_spaces(ndvi_file, output_file):
    try:
        with rasterio.open(ndvi_file) as src:
            ndvi = src.read(1)  # Read the first band
            profile = src.profile
            nodata = src.nodata

        valid_data_mask = np.where(ndvi == nodata, 0, 1) if nodata is not None else np.ones_like(ndvi)
        green_mask = np.where((ndvi > 0.4) & (valid_data_mask == 1), 1, 0).astype(np.uint8)
        green_shapes = shapes(green_mask, mask=None, transform=profile['transform'])
        polygons = [shape(geom) for geom, val in green_shapes if val == 1]
        gdf = gpd.GeoDataFrame(geometry=polygons, crs=profile['crs'])

        # Determine an appropriate UTM zone CRS for area calculation
        utm_crs = determine_utm_zone(gdf)
        gdf_utm = gdf.to_crs(utm_crs)

        # Now calculate the area in square meters
        
        gdf_utm['area_m2'] = gdf_utm['geometry'].area.astype(int)

        total_area = gdf_utm['area_m2'].sum()
            # Exclude the largest polygon
        gdf_utm = gdf_utm[gdf_utm['area_m2'] != gdf_utm['area_m2'].max()]

        # Optionally, convert back to EPSG:4326 if needed for GeoJSON compatibility
        gdf_final = gdf_utm.to_crs("EPSG:4326")

        gdf_final.to_file(output_file, driver='GeoJSON')
        print(f"Extracted green spaces from {ndvi_file} and saved as {output_file}")

    except Exception as e:
        print(f"Error extracting green spaces from {ndvi_file}: {e}")

# Ensure the output directory exists
output_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\output_geojson'
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

# Directory containing NDVI images
ndvi_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\band_data'

# Process each NDVI TIFF file in the directory
for file in os.listdir(ndvi_dir):
    if file.endswith('.tif') and 'NDVI' in file.upper():
        ndvi_file = os.path.join(ndvi_dir, file)
        output_file = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_green_spaces.geojson")
        extract_green_spaces(ndvi_file, output_file)
