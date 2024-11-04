import requests
import urllib3
import csv
import os

urllib3.disable_warnings()

# Define the API endpoint and headers
url = "xxxx/rest/analysis"
headers = {
    "x-apikey": "accesskey=www; secretkey=yyyy",
    "Content-Type": "application/json",
}

# Define initial offsets and batch size
start_offset = 0
batch_size = 1000  # You can Adjust as needed based on API limit and performance
total_records = 15255271 
csv_file_path = "C:/Users/YourUsername/OneDrive/main_application.csv"  # Path to OneDrive edit it to your one drive folder

# Prepare CSV file with headers only if file doesn't exist 
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Define headers based on expected structure
        headers = ["pluginID", "severity_id", "severity_name", "severity_description", "hasBeenMitigated", "acceptRisk"]
        writer.writerow(headers)

# Loop over all records in batches
while start_offset < total_records:
    # Set the `endOffset` for this batch
    end_offset = start_offset + batch_size

    # Define the payload for the API request
    payload = {
        "query": {
            "type": "vuln",
            "tool": "vulndetails",
            "sourceType": "cumulative",
            "startOffset": start_offset,
            "endOffset": end_offset,
            # Add filters or other parameters as needed
        },
        "sortDir": "asc",
        "sortField": "lastSeen",
        "sourceType": "cumulative",
        "type": "vuln",
    }

    # Make the POST request to fetch data
    response = requests.post(url, headers=headers, json=payload, verify=False)

    if response.status_code == 200:
        data = response.json()
        results = data.get("response", {}).get("results", [])

        # Write each result to the CSV
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            for item in results:
                # Flatten the nested severity dictionary for CSV compatibility
                row = [
                    item.get("pluginID"),
                    item.get("severity", {}).get("id"),
                    item.get("severity", {}).get("name"),
                    item.get("severity", {}).get("description"),
                    item.get("hasBeenMitigated"),
                    item.get("acceptRisk"),
                ]
                writer.writerow(row)
        
        print(f"Batch {start_offset}-{end_offset} written to {csv_file_path}")

    else:
        print("Error:", response.status_code, response.text)
        break

    # Move to the next batch
    start_offset += batch_size
