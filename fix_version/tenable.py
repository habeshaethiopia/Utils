import os
import requests
import urllib3
import csv
from datetime import datetime
import sys

urllib3.disable_warnings()

url = "domain"

header = {
    "x-apikey": "accesskey=key; secretkey=scretkey",
    "Content-Type": "application/json",
}

start_offset = 0
batch_size = 100
total_records = 200
csv_file_path = rf"tenable/application_issues.csv"  # "C:/Users/aalemay1/OneDrive - FEMA/Documents/Reports/main_application.csv"  # Path to OneDrive


def flatten_dict(d, parent_key="", sep="_"):
    """
    Flatten a nested dictionary, including handling lists and deeply nested structures.

    Args:
        d (dict): The dictionary to flatten.
        parent_key (str): The base key string.
        sep (str): Separator between parent and child keys.

    Returns:
        dict: A flattened dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to comma-separated strings if they don't contain dictionaries
            items.append((new_key, ", ".join(map(str, v))))
        else:
            items.append((new_key, v))
    return dict(items)


# Check if the CSV file exists
if not os.path.exists(csv_file_path):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    # Create the CSV file if it doesn't exist
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.writer(file)


def convert_epoch_to_human_readable(epoch_time, timezone=None):
    """
    Converts epoch time to a human-readable date and time format.

    Args:
        epoch_time (int or float): The epoch timestamp to convert.
        timezone (str, optional): A timezone name, like 'UTC' or 'Asia/Kolkata'. Defaults to None (local time).

    Returns:
        str: The human-readable date and time string.
    """
    try:
        if timezone is None:
            # Convert to local time if no timezone is provided
            dt = datetime.fromtimestamp(epoch_time)
        else:
            import pytz

            tz = pytz.timezone(timezone)

            dt = datetime.fromtimestamp(epoch_time, tz)
        # Format the datetime object to a human-readable string
        human_readable = dt.strftime("%Y-%m-%d %H:%M:%S")
        return human_readable

    except Exception as e:
        # Handle any exceptions that occur during the conversion
        return f"Error: {e}"


# Get the timestamp from command line arguments
if len(sys.argv) != 2:
    print("Usage: python tanable.py <timestamp>")
    sys.exit(1)

# Assign the timestamp from the command line argument
timestamp = sys.argv[1]

# Main loop to process data in batches
while start_offset < total_records:
    end_offset = start_offset + batch_size - 1

    payload = {
        "query": {
            "type": "vuln",
            "tool": "vulndetails",
            "sourceType": "cumulative",
            "startOffset": start_offset,
            "endOffset": end_offset,
            "filters": [
                {
                    "filterName": "lastSeen",
                    "operator": "=",
                    "value": timestamp,
                },
                {
                    "filterName": "pluginID",
                    "operator": "=",
                    "value": "0-999999",
                },
                {"filterName": "severity", "operator": "!=", "value": "0"},
            ],
        },
        "sortDir": "asc",
        "sortField": "lastSeen",
        "sourceType": "cumulative",
        "type": "vuln",
    }

    response = requests.post(url, headers=header, json=payload, verify=False)

    if response.status_code == 200:
        data = response.json()

        if data and "response" in data:
            totalRecords = data["response"].get("totalRecords", 0)
            total_records = int(totalRecords)

            if start_offset < batch_size:
                print("Total Records: ", totalRecords)

            results = data["response"].get("results", [])

            with open(csv_file_path, mode="a", newline="") as file:
                writer = csv.writer(file)

                for item in results:
                    # Flatten the dictionary for each item
                    item = flatten_dict(item)
                    # Write headers only for the first batch
                    if start_offset == 0:
                        headers = list(item.keys())
                        writer.writerow(headers)
                    # Convert epoch time to human-readable format for specific date fields
                    for date_field in [
                        "firstSeen",
                        "lastSeen",
                        "pluginModDate",
                        "pluginPubDate",
                        "patchPubDate",
                        "vulnPubDate",
                    ]:
                        if date_field in item and item[date_field]:
                            item[date_field] = convert_epoch_to_human_readable(
                                int(item[date_field])
                            )
                    # Write the data row
                    row = list(item.values())
                    writer.writerow(row)

            print(f"Batch {start_offset}-{end_offset} written to {csv_file_path}")
        else:
            print("Error: Unexpected response structure.")
            break
    else:
        print("Error:", response.status_code, response.text)
        break

    start_offset += batch_size

print("SCAN Completed")
