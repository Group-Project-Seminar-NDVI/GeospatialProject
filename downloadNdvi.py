import requests
import os
import rasterio
from rasterio.transform import from_bounds
from affine import Affine

# Define the access token
access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ3dE9hV1o2aFJJeUowbGlsYXctcWd4NzlUdm1hX3ZKZlNuMW1WNm5HX0tVIn0.eyJleHAiOjE3MDgyODM0OTUsImlhdCI6MTcwODI3OTg5NSwianRpIjoiNTI0ZTlmZDctMzdlNy00M2FmLTlmZTQtNzNmZmI2MjQxN2IyIiwiaXNzIjoiaHR0cHM6Ly9zZXJ2aWNlcy5zZW50aW5lbC1odWIuY29tL2F1dGgvcmVhbG1zL21haW4iLCJzdWIiOiJmOWJiNDk4Yi0wMDZlLTRjNjAtOGY4Zi02M2UyMDA4ODZiYTYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJkYmIwYzhkYi1jYzE4LTRmZTItYTNjNC1hYzcxNWRhMDFjNzciLCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJjbGllbnRIb3N0IjoiNzkuMTY5LjYxLjk2IiwiY2xpZW50SWQiOiJkYmIwYzhkYi1jYzE4LTRmZTItYTNjNC1hYzcxNWRhMDFjNzciLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC1kYmIwYzhkYi1jYzE4LTRmZTItYTNjNC1hYzcxNWRhMDFjNzciLCJjbGllbnRBZGRyZXNzIjoiNzkuMTY5LjYxLjk2IiwiYWNjb3VudCI6ImMxYTkwZjQ4LWNhYjctNDJmNC1hNmQ4LWM5OTU0ZDBkNjk2ZSJ9.PmeIQa1c4KbTDYLAqSLnULp5GPBjBUc1qe8TQmtj_GzJTa_AXOZSbDipyEQb3zF4IOvombpTHyDhZ13qydXdP7XzHACht0fhqNqR1HpW5HCTE0XwTPO12wsNaWr9uV5fqJyTKbbPdpYVgj6wN3_PUxavvpObjZUEYfAjlOun4BKbFsStA56o5DlJtPSAN6JlBCzButWm7JtMBjGVvXwq6PTspMfeKo2fSlQK7XEWgztAluGvPKzoPBIx40RV0bhCXV64dOzsFn2fIW1zmI2zeJ9gX_N-HinWVcX29SIC1OqlECpJdRXmkkazg-SLBBcmhI_wkvzBhHLh-KlKwu324Q"

# Define the URL for downloading data
download_url = "https://services.sentinel-hub.com/api/v1/process"
bbox = [71.3965, 30.1526, 71.5794, 30.2733]

# Define the output directory to save the files
output_dir = r'C:\Users\AmmarYousaf\Fiver\GeospatialProject\multan_data'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define the payload template
payload_template = {
    "input": {
        "bounds": {
            "bbox": bbox
        },
        "data": [{
            "type": "sentinel-2-l2a"
        }]
    },
    "evalscript": """
    //VERSION=3

    function setup() {
      return {
        input: ["B04", "B08"],
        output: {
          bands: 2
        }
      };
    }

    function evaluatePixel(
      sample,
      scenes,
      inputMetadata,
      customData,
      outputMetadata
    ) {
      var ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
      return [ndvi, ndvi, ndvi];
    }
    """
}

# Define the headers
headers = {"Authorization": f"Bearer {access_token}"}

# Loop through each year from 2015 to 2023
for year in range(2015, 2024):
    # Update the time range for the current year
    time_range = f"{year}-11-11", f"{year}-12-31"

    # Update the payload with the new time range
    payload = payload_template.copy()
    payload["input"]["time"] = {
        "from": time_range[0],
        "to": time_range[1]
    }

    # Make the POST request to download data
    response = requests.post(download_url, headers=headers, json=payload)

    # Check if request was successful
    if response.status_code == 200:
        # Save the response content to a file
        filename = os.path.join(output_dir, f"ndvi_data_{year}.tif")
        with rasterio.MemoryFile(response.content) as memfile:
            with memfile.open() as src:
                transform = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], src.width, src.height)
                profile = src.profile
                profile.update({
                    'driver': 'GTiff',
                    'crs': 'EPSG:4326',
                    'transform': transform
                })
                with rasterio.open(filename, 'w', **profile) as dst:
                    dst.write(src.read())
        print(f"NDVI data for {year} downloaded and saved as GeoTIFF successfully.")
    else:
        print(f"Failed to download NDVI data for {year}: {response.text}")
