from sentinelhub import SHConfig, MimeType, CRS, BBox, SentinelHubRequest, DataCollection, bbox_to_dimensions
import os
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from datetime import datetime

# Configuration
config = SHConfig()
config.sh_client_id = 'dbb0c8db-cc18-4fe2-a3c4-ac715da01c77'  # Replace with your Sentinel Hub client ID
config.sh_client_secret = 'xw4ZAm0eeYjoTlmu0ftCjhIlDNU3AwlT'  # Replace with your actual Sentinel Hub client secret
config.save()

# Define the geographical bounds of your area of interest in WGS84
multan_coords = [71.417, 30.157, 71.529, 30.211]  # Example coordinates for Multan, Pakistan
multan_bbox = BBox(bbox=multan_coords, crs=CRS.WGS84)
resolution = 10  # Desired resolution in meters, adjust as needed

# Output directory
output_dir = "band_data"
os.makedirs(output_dir, exist_ok=True)

# Download and save a specific band for a given year
def download_and_save_band(band, year):
    time_interval = (f"{year}-01-01", f"{year}-12-31")
    
    evalscript = f"""
    //VERSION=3
    function setup() {{
        return {{
            input: ["{band}"],
            output: {{ bands: 1, sampleType: "FLOAT32" }}
        }};
    }}
    function evaluatePixel(sample) {{
        return [sample.{band}];
    }}
    """
    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[SentinelHubRequest.input_data(data_collection=DataCollection.SENTINEL2_L2A, time_interval=time_interval)],
        responses=[SentinelHubRequest.output_response('default', MimeType.TIFF)],
        bbox=multan_bbox,
        size=bbox_to_dimensions(multan_bbox, resolution=resolution),
        config=config
    )
    data = request.get_data()[0]
    file_path = os.path.join(output_dir, f'{band}_{year}.tif')
    
    # Calculate the transform for the rasterio dataset
    transform = from_bounds(*multan_bbox, data.shape[1], data.shape[0])
    
    with rasterio.open(
        file_path,
        'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype='float32',
        crs='EPSG:4326',
        transform=transform
    ) as dst:
        dst.write(data, 1)
    return file_path

# Calculate and save NDVI
def calculate_and_save_ndvi(red_band_path, nir_band_path, year):
    with rasterio.open(red_band_path) as red_src:
        red = red_src.read(1)
    with rasterio.open(nir_band_path) as nir_src:
        nir = nir_src.read(1)
    
    ndvi = (nir - red) / (nir + red + np.finfo(float).eps)
    ndvi = np.clip(ndvi, -1, 1)

    ndvi_path = os.path.join(output_dir, f'NDVI_{year}.tif')
    with rasterio.open(
        ndvi_path,
        'w',
        driver='GTiff',
        height=ndvi.shape[0],
        width=ndvi.shape[1],
        count=1,
        dtype='float32',
        crs='EPSG:4326',
        transform=from_bounds(*multan_bbox, ndvi.shape[1], ndvi.shape[0])
    ) as dst:
        dst.write(ndvi, 1)

# Process for specified years
years = [2020, 2021, 2022]

for year in years:
    red_band_path = download_and_save_band('B04', year)
    nir_band_path = download_and_save_band('B08', year)
    
    calculate_and_save_ndvi(red_band_path, nir_band_path, year)

print("NDVI calculations and savings for specified years are completed.")
