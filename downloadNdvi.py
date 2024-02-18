import ee
import geemap

# Authenticate Earth Engine
ee.Authenticate()
ee.Initialize()

# Define the region of interest for Multan city
multan_bbox = ee.Geometry.Rectangle([71.3965, 30.1526, 71.5794, 30.2733])

# Filter Sentinel-2 imagery for Multan city using the bounding box and date range
sentinel2 = ee.ImageCollection('COPERNICUS/S2') \
    .filterBounds(multan_bbox) \
    .filterDate('2010-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

# Define bands for NDVI calculation
red_band = 'B4'  # Red band
nir_band = 'B8'  # Near-infrared band

# Define a function to calculate NDVI
def calculate_ndvi(image):
    return image.normalizedDifference([nir_band, red_band])

# Define a function to download NDVI images
def download_ndvi_images(collection, years):
    # Initialize a list to store NDVI images
    ndvi_images = []

    # Loop over the specified years
    for year in years:
        # Filter the collection for the current year
        filtered_collection = collection.filterDate(f'{year}-01-01', f'{year+1}-01-01')

        # Get the median image from the filtered collection
        median_image = filtered_collection.median()

        # Calculate NDVI for the median image
        ndvi_image = calculate_ndvi(median_image)

        # Clip the NDVI image to the region of interest
        ndvi_image = ndvi_image.clip(multan_bbox)

        # Append the NDVI image to the list
        ndvi_images.append(ndvi_image)

        # Define the file path for the NDVI image
        file_path = f'C:\\Users\\AmmarYousaf\\Fiver\\GeospatialProject\\multan_data\\ndvi_{year}.tif'

        # Export the NDVI image
        print(f"Downloading NDVI image for {year}")
        geemap.ee_export_image(ndvi_image, filename=file_path, scale=30)

    return ndvi_images

# Download NDVI images for the years 2010, 2015, 2020, and 2023
download_ndvi_images(sentinel2, [2015, 2017, 2019,2021, 2023])
