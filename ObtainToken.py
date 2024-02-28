import requests

# Your client ID and secret key
client_id = "dbb0c8db-cc18-4fe2-a3c4-ac715da01c77"
client_secret = "xw4ZAm0eeYjoTlmu0ftCjhIlDNU3AwlT"

# URL for the OAuth 2.0 token endpoint
token_url = "https://services.sentinel-hub.com/oauth/token"

# Request body for token endpoint
data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
}

# Make a POST request to the token endpoint
response = requests.post(token_url, data=data)

# Check if request was successful
if response.status_code == 200:
    # Parse the JSON response to get the access token
    access_token = response.json()["access_token"]
    print("Access token:", access_token)
else:
    print("Failed to obtain access token:", response.text)
