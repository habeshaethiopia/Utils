import requests
import json
import csv
import urllib3
import os

urllib3.disable_warnings()

def process():
    try:
        # Define the headers
        headers = {
            "accept": "application/json",
            "Authorization": "FortifyToken xxxx"
        }
        url='https://domain/api/v2/applications'

        # Make the GET request and bypass SSL certificate validation
        response = requests.get(url, headers=headers, verify=False)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            response_json = response.json()

            # Extract items from the response
            items = response_json.get("items", [])

            # Specify the CSV file name
            csv_file_name = "applications.csv"

            with open(csv_file_name, mode="w", newline="") as csv_file:
                fieldnames = items[0].keys() if len(items) > 0 else []  # Get keys from the first item as fieldnames
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()  # Write the header
                for item in items:
                    writer.writerow(item)  # Write each item's data

            print(f"Data has been written to {csv_file_name}")
        else:
            print(f"Failed to execute request: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from the response.")

if __name__ == "__main__":
    process()
