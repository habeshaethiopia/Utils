import os
import shutil
from datetime import datetime, timedelta
import requests
import json
import urllib3
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# -----------------------------
# Global Variables for API Tokens
# -----------------------------

APPLICATIONS_API_TOKEN = 'your_applications_api_token_here'
VERSIONS_API_TOKEN = 'your_versions_api_token_here'
ISSUES_API_TOKEN = 'your_issues_api_token_here'

# -----------------------------
# Configuration Section
# -----------------------------

urllib3.disable_warnings()

API_CONFIG = {
    "applications": {
        "url": "https://domain/api/v2/applications",
        "headers": {
            "Accept": "application/json",
            "Authorization": f"FortifyToken {APPLICATIONS_API_TOKEN}"
        },
        "params": {
            "startDate": None,
            "endDate": None
        },
        "output_file": "applications.csv"
    },
    "versions": {
        "url": "https://domain/ssc/api/v1/projects/{project_id}/versions",
        "headers": {
            "Accept": "application/json",
            "Authorization": f"FortifyToken {VERSIONS_API_TOKEN}"
        },
        "params": {
            "start": 0,
            "limit": 200,
            "fulltextsearch": "false",
            "includeInactive": "false",
            "myAssignedIssues": "false"
        },
        "output_file": "all_project_versions.csv"
    },
    "issues": {
        "url": "https://domain/ssc/api/v1/projectVersions/{version_id}/issues",
        "headers": {
            "Accept": "application/json",
            "Authorization": f"FortifyToken {ISSUES_API_TOKEN}"
        },
        "params": {
            "limit": 5000,
            "orderby": "friority",
            "filterset": "a243b195-0a59-3f8b-1403-d55b7a7d78e6",
            "fulltextsearch": "false",
            "includeInactive": "false",
            "myAssignedIssues": "false",
            "start": 0
        },
        "output_file": "security_issues.csv"
    }
}

# -----------------------------
# Helper Functions
# -----------------------------

def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten a nested dictionary.

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
            # Convert lists to comma-separated strings
            items.append((new_key, ', '.join(map(str, v))))
        else:
            items.append((new_key, v))
    return dict(items)

def write_to_csv(items, fieldnames, filename):
    """
    Write data to a CSV file. If the file exists, append rows without writing headers.
    If the file does not exist, create it and write headers.

    Args:
        items (list): List of dictionaries containing the data.
        fieldnames (list): List of field names for the CSV.
        filename (str): The name of the CSV file.
    
    Returns:
        bool: True if writing was successful, False otherwise.
    """
    try:
        

        file_exists = os.path.isfile(filename)
        with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header only if the file does not exist
            if not file_exists:
                writer.writeheader()
            
            for item in items:
                writer.writerow(item)
        print(f"Data successfully written to {filename}")
        return True
    except Exception as e:
        print(f"Failed to write data to {filename}: {e}")
        return False

def fetch_api_data(endpoint_key, **kwargs):
    """
    Fetch data from a specified API endpoint with optional parameter overrides.

    Args:
        endpoint_key (str): The key identifying the API configuration.
        **kwargs: Additional keyword arguments for URL formatting and parameter overrides.

    Returns:
        dict: The JSON response from the API if successful, else an empty dictionary.
    """
    config = API_CONFIG.get(endpoint_key)
    if not config:
        print(f"No API configuration found for '{endpoint_key}'.")
        return {}

    url = config["url"].format(**kwargs) if kwargs else config["url"]
    headers = config["headers"]
    params = config["params"].copy()

    # Update params if provided
    params_override = kwargs.get("params_override", {})
    if params_override:
        params.update(params_override)

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed for '{endpoint_key}': {e}")
        return {}

def fetch_applications(start_date, end_date):
    """
    Fetch applications within the specified date range.

    Args:
        start_date (str): ISO formatted start date.
        end_date (str): ISO formatted end date.

    Returns:
        list: List of application items.
    """
    params_override = {
        "startDate": start_date,
        "endDate": end_date
    }
    response_data = fetch_api_data("applications", params_override=params_override)
    if not response_data:
        return []

    applications = response_data.get("items", [])
    if applications:
        # Flatten application data
        flattened_applications = [flatten_dict(app) for app in applications]

        # Determine CSV fieldnames dynamically
        fieldnames = flattened_applications[0].keys() if flattened_applications else []
        write_to_csv(flattened_applications, fieldnames, API_CONFIG["applications"]["output_file"])
        print(f"Total applications found: {len(applications)}")
    else:
        print("No applications found.")

    return applications

def fetch_versions(project_id, params_override=None):
    """
    Fetch all versions for a given project, handling pagination.

    Args:
        project_id (str): The ID of the project.
        params_override (dict, optional): Additional parameters to override defaults.

    Returns:
        list: List of version items.
    """
    all_versions = []
    start = 0
    limit = API_CONFIG["versions"]["params"]["limit"]

    while True:
        current_params = {
            "start": start,
            "limit": limit
        }
        if params_override:
            current_params.update(params_override)

        response_data = fetch_api_data("versions", project_id=project_id, params_override=current_params)
        if not response_data:
            break

        versions = response_data.get("data", [])
        if not versions:
            break

        all_versions.extend(versions)
        start += limit

        # Check if we've fetched all versions
        total_count = response_data.get("count", 0)
        if start >= total_count:
            break

    if all_versions:
        # Flatten each version's data
        flattened_versions = [flatten_dict(version) for version in all_versions]

        # Determine CSV fieldnames dynamically
        fieldnames = flattened_versions[0].keys() if flattened_versions else []
        write_to_csv(flattened_versions, fieldnames, API_CONFIG["versions"]["output_file"])
        print(f"Total versions found: {len(all_versions)}")
    else:
        print("No versions found.")

    return all_versions

def fetch_issues(version_id, params_override=None):
    """
    Fetch security issues for a specific project version, handling pagination.

    Args:
        version_id (str): The ID of the project version.
        params_override (dict, optional): Additional parameters to override defaults.

    Returns:
        list: List of issue items.
    """
    all_issues = []
    start = 0
    limit = API_CONFIG["issues"]["params"]["limit"]
    orderby = API_CONFIG["issues"]["params"]["orderby"]

    while True:
        current_params = {
            "start": start,
            "limit": limit,
            "orderby": orderby
        }
        if params_override:
            current_params.update(params_override)

        response_data = fetch_api_data("issues", version_id=version_id, params_override=current_params)
        if not response_data:
            break

        issues = response_data.get("data", [])
        if not issues:
            break

        all_issues.extend(issues)
        start += limit

        # Check if we've fetched all issues
        total_count = response_data.get("count", 0)
        if start >= total_count:
            break

    if all_issues:
        # Flatten each issue's data
        flattened_issues = [flatten_dict(issue) for issue in all_issues]

        # Determine CSV fieldnames dynamically
        fieldnames = flattened_issues[0].keys() if flattened_issues else []
        write_to_csv(flattened_issues, fieldnames, API_CONFIG["issues"]["output_file"])
        print(f"Total issues found: {len(all_issues)}")
    else:
        print("No issues found.")

    return all_issues

def fetch_issues_concurrently(version_ids, max_workers=5):
    """
    Fetch issues for multiple versions concurrently.

    Args:
        version_ids (list): List of version IDs to fetch issues for.
        max_workers (int): Number of threads to use.

    Returns:
        list: Consolidated list of all issues.
    """
    all_issues = []
    total_versions = len(version_ids)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_version = {executor.submit(fetch_issues, vid): vid for vid in version_ids}

        for future in as_completed(future_to_version):
            version_id = future_to_version[future]
            try:
                issues = future.result()
                if issues:
                    all_issues.extend(issues)
                    print(f"Issues fetched for version ID {version_id}: {len(issues)}")
            except Exception as e:
                print(f"Error fetching issues for version ID {version_id}: {e}")

    return all_issues

def process_versions(applications):
    """
    Process and save versions data for all applications.

    Args:
        applications (list): List of application dictionaries.

    Returns:
        list: List of all version items collected.
    """
    all_versions = []

    for app in applications:
        project_id = app.get("id")
        if not project_id:
            continue

        print(f"Fetching versions for application '{app.get('name', 'N/A')}' (ID: {project_id})")
        versions = fetch_versions(project_id)
        all_versions.extend(versions)

    return all_versions

def process_issues(versions):
    """
    Process and save security issues data for all versions.

    Args:
        versions (list): List of version dictionaries.

    Returns:
        list: List of all issues collected.
    """
    all_issues = []
    version_ids = [version.get("id") for version in versions if version.get("id")]
    all_issues = fetch_issues_concurrently(version_ids)
    return all_issues

def get_date_range() -> tuple[str, str]:
    """Calculate the date range for the past 7 days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return start_date.isoformat(), end_date.isoformat()



# -----------------------------
# Main Execution
# -----------------------------

def main():
    """
    Main execution function.
    """
    try:
        # Define date range for applications
        start_date, end_date = get_date_range()

        # Fetch applications with date range
        applications = fetch_applications(start_date, end_date)
        if not applications:
            print("Failed to fetch applications. Exiting.")
            return

        # Process versions
        versions = process_versions(applications)
        if not versions:
            print("Failed to fetch versions. Exiting.")
            return

        # Process issues
        process_issues(versions)

    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main() 