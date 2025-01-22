import requests
import urllib.parse

# The base URL
base_url = "https://localhost:8443/User-app/api/config/reload"

# The file path
file_path = "/home/selim/projet/deploy/configurations métiers/FeatureToggle/configAge.xml"

# URL encode the file path
encoded_file_path = urllib.parse.quote(file_path)

# Construct the URL
url = f"{base_url}?path={encoded_file_path}"

# Send a GET request to the URL, bypassing SSL certificate verification
response = requests.get(url, verify=False)

# Print the response
print(response.text)