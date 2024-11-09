import requests
import json
import csv
import urllib3
import os
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

urllib3.disable_warnings()

# Configuration variables
API_URL = "https://domain/api/v2/applications"
API_TOKEN = "xxxx"  # Replace with your actual token
CSV_FILENAME = "applications_time.csv"
LOG_FILENAME = "fetch.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler()
    ]
)


def get_date_range() -> tuple[str, str]:
    """Calculate the date range for the past 7 days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return start_date.isoformat(), end_date.isoformat()

def fetch_applications() -> List[Dict[str, Any]]:
    """
    Fetch applications from the specified API endpoint.
    Returns:
        List[Dict[str, Any]]: A list of application items.
    """
    try:
        headers = {
            "Accept": "application/json",
            "Authorization": f"FortifyToken {API_TOKEN}"
        }

        # Add date range parameters
        start_date, end_date = get_date_range()
        url_with_dates = f"{API_URL}?startDate={start_date}&endDate={end_date}"
        logging.info(f"Fetching applications from {start_date} to {end_date}")

        response = requests.get(url_with_dates, headers=headers, verify=False)
        response.raise_for_status()

        response_json = response.json()
        items = response_json.get("items", [])
        logging.info(f"Fetched {len(items)} applications.")
        return items

    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
    except requests.RequestException as req_err:
        logging.error(f"Request exception occurred: {req_err}")
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from the response.")
    
    return []

def write_to_csv(items: List[Dict[str, Any]]) -> None:
    """
    Write application items to a CSV file.
    Args:
        items (List[Dict[str, Any]]): The list of application items to write.
    """
    if not items:
        logging.warning("No items to write to CSV.")
        return

    try:
        with open(CSV_FILENAME, mode="w", newline="", encoding='utf-8') as csv_file:
            fieldnames = items[0].keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(items)
        logging.info(f"Data has been written to {CSV_FILENAME}")
    except IOError as e:
        logging.error(f"IO error occurred while writing to CSV: {e}")

def process():
    """
    Main processing function to fetch applications and write them to a CSV file.
    """
    items = fetch_applications()
    write_to_csv(items)

if __name__ == "__main__":
    process()