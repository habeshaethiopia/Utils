import requests
import json
import urllib3

# API Configuration
base_url = "domain/ssc/api/v1/projects/20/versions"
headers = {
    "accept": "application/json",
    "Authorization": "FortifyToken token"
}

# Request parameters
params = {
    "start": 0,
    "limit": 200,
    "fulltextsearch": "false",
    "includeInactive": "false",
    "myAssignedIssues": "false"
}

# Suppress SSL verification warnings (optional, but recommended if bypassing SSL)
urllib3.disable_warnings()
# Make the API request
response = requests.get(base_url, headers=headers, params=params, verify=False)

# Check if the request was successfull
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    output_file = 'res2.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Scan data has been saved to {output_file}")
else:
    print(f"Error: Request failed with status code {response.status_code}")

    
