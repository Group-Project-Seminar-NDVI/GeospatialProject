import requests
import os
import json
import rasterio
from rasterio.transform import from_bounds
from affine import Affine

# Define the access token
access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ3dE9hV1o2aFJJeUowbGlsYXctcWd4NzlUdm1hX3ZKZlNuMW1WNm5HX0tVIn0.eyJleHAiOjE3MDg2MzU2MTcsImlhdCI6MTcwODYzMjAxNywianRpIjoiMmM4NjNkNzctMTY4Zi00MjZkLTg2MzYtODk0NzRiZDczYmFmIiwiaXNzIjoiaHR0cHM6Ly9zZXJ2aWNlcy5zZW50aW5lbC1odWIuY29tL2F1dGgvcmVhbG1zL21haW4iLCJzdWIiOiJmOWJiNDk4Yi0wMDZlLTRjNjAtOGY4Zi02M2UyMDA4ODZiYTYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJkYmIwYzhkYi1jYzE4LTRmZTItYTNjNC1hYzcxNWRhMDFjNzciLCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJjbGllbnRIb3N0IjoiNzkuMTY5LjYxLjk2IiwiY2xpZW50SWQiOiJkYmIwYzhkYi1jYzE4LTRmZTItYTNjNC1hYzcxNWRhMDFjNzciLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC1kYmIwYzhkYi1jYzE4LTRmZTItYTNjNC1hYzcxNWRhMDFjNzciLCJjbGllbnRBZGRyZXNzIjoiNzkuMTY5LjYxLjk2IiwiYWNjb3VudCI6ImMxYTkwZjQ4LWNhYjctNDJmNC1hNmQ4LWM5OTU0ZDBkNjk2ZSJ9.cTEjF7sIguvlDhYjhnlXJ2LzZwEsXB2UGuqGaWrEs_dgrEeYfHLm0frpIUnQmQHbB1XTpAZUBQCb-fjCLmZBtG2EQEseaf4NxBvQTbLMWsrDUoxO62qdTYvPPim5PR8v9fEGbkbxorfxbDDEYyzUnOUAzhTiof70kM8sUDhZRHElV49XTKN6gUaqLjcnDb5MRzW2IeDRORyPbc-dsNxWYputXarn7B4G5u2qNyjqREjbrvxZYUF4hvc-GgucWcV_0V1igYIn9Cdz4XyJM59aP2VHo2xQhjZPHmtnjy786S7qqwcXg8kHG10eMKg64zqXpDwy7twABHt_5Y6oCmeG9A"

# Define the URL for downloading data
download_url = "https://services.sentinel-hub.com/api/v1/process"
bbox = [71.3965, 30.1526, 71.5794, 30.2733]

# Define the output directory to save the files
output_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\multan_data'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define the payload template for red band (B04)
payload_red_band = {
    "input": {
        "bounds": {
            "bbox": bbox
        },
        "data": [{
            "type": "sentinel-2-l2a",
            "dataFilter": {
                "timeRange": {
                    "from": "2023-11-11T00:00:00Z",
                    "to": "2023-12-31T23:59:59Z"
                },
                "maxCloudCoverage": 5
            }
        }]
    },
    "output": {
        "width": 512,
        "height": 512
    },
    "evalscript": """
    //VERSION=3
    function setup() {
      return {
        input: ["B04"],
        output: { bands: 1 }
      };
    }

    function evaluatePixel(sample) {
      return [sample.B04];
    }
    """
}

# Define the payload template for near-infrared band (B08)
payload_nir_band = {
    "input": {
        "bounds": {
            "bbox": bbox
        },
        "data": [{
            "type": "sentinel-2-l2a",
            "dataFilter": {
                "timeRange": {
                    "from": "2023-11-11T00:00:00Z",
                    "to": "2023-12-31T23:59:59Z"
                },
                "maxCloudCoverage": 5
            }
        }]
    },
    "output": {
        "width": 512,
        "height": 512
    },
    "evalscript": """
    //VERSION=3
    function setup() {
      return {
        input: ["B08"],
        output: { bands: 1 }
      };
    }

    function evaluatePixel(sample) {
      return [sample.B08];
    }
    """
}

# Define the headers
headers = {"Authorization": f"Bearer {access_token}"}

# Make the POST request to download red band data
response_red_band = requests.post(download_url, headers=headers, json=payload_red_band)

# Check if request for red band was successful
if response_red_band.status_code == 200:
    # Save the response content to a file for red band
    red_band_filename = os.path.join(output_dir, "red_band.tif")

    with rasterio.MemoryFile(response_red_band.content) as memfile:
        with memfile.open() as src:
            transform = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], src.width, src.height)
            profile = src.profile
            profile.update({
                'driver': 'GTiff',
                'crs': 'EPSG:4326',
                'transform': transform
            })

            # Write red band data to the output file
            with rasterio.open(red_band_filename, 'w', **profile) as dst:
                dst.write(src.read())

    print("Red band imagery downloaded and saved successfully.")
else:
    print(f"Failed to download red band imagery: {response_red_band.text}")

# Make the POST request to download near-infrared band data
response_nir_band = requests.post(download_url, headers=headers, json=payload_nir_band)

# Check if request for near-infrared band was successful
if response_nir_band.status_code == 200:
    # Save the response content to a file for near-infrared band
    nir_band_filename = os.path.join(output_dir, "nir_band.tif")

    with rasterio.MemoryFile(response_nir_band.content) as memfile:
        with memfile.open() as src:
            transform = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], src.width, src.height)
            profile = src.profile
            profile.update({
                'driver': 'GTiff',
                'crs': 'EPSG:4326',
                'transform': transform
            })

            # Write near-infrared band data to the output file
            with rasterio.open(nir_band_filename, 'w', **profile) as dst:
                dst.write(src.read())

    print("Near-infrared band imagery downloaded and saved successfully.")
else:
    print(f"Failed to download near-infrared band imagery: {response_nir_band.text}")
