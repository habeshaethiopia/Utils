import requests
import json
import urllib3
import csv

# -----------------------------
# Global Variables for API Tokens
# -----------------------------

# Define your API tokens here
APPLICATIONS_API_TOKEN = 'your_applications_api_token_here'
VERSIONS_API_TOKEN = 'your_versions_api_token_here'  # Replace 'xxx' with your actual token
ISSUES_API_TOKEN = 'ZWYyNjBlNmMtMDFiMS00NmI1LWExNWYtNDNhMzBlYzM0YmRk'  # Replace with your actual token

# -----------------------------
# Configuration Section
# -----------------------------

# Suppress SSL verification warnings
urllib3.disable_warnings()

# API Configurations for different endpoints
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
        "output_file": "all_project_versions.csv",
        "fields": [
            "Project Name",
            "Project ID",
            "Version ID",
            "Version Name",
            "Version Description",
            "Project Version Status",
            "Server Version Status",
            "Issue Template ID",
            "Issue Template Name",
            "Development Phase",
            "Development Strategy",
            "Business Risk Rating",
            "Business Criticality",
            "Repository URL",
            "Repository Type",
            "Issue Status",
            "Analysis Status",
            "Current Analysis Date",
            "Published Status",
            "Project Owner",
            "Project Owner First Name",
            "Project Owner Last Name",
            "Project Owner Email",
            "Application Name",
            "Application ID",
            "Application Type",
            "Application Business Unit",
            "Application Tags",
            "Project Created By",
            "Project Creation Date",
        ]
    },
    "issues": {
        "url": "https://domain/ssc/api/v1/projectVersions/{version_id}/issues",
        "headers": {
            "Accept": "application/json",
            "Authorization": f"FortifyToken {ISSUES_API_TOKEN}"
        },
        "params": {
            "limit": 5000,  # Adjust as needed
            "orderby": "friority",
            "filterset": "a243b195-0a59-3f8b-1403-d55b7a7d78e6",  # Replace with actual filter set if necessary
            "fulltextsearch": "false",
            "includeInactive": "false",
            "myAssignedIssues": "false",
            "start": 0
        },
        "output_file": "security_issues.csv",
    }
}

# -----------------------------
# Helper Functions
# -----------------------------

def fetch_api_data(endpoint_key, **kwargs):
    """
    Fetch data from a specified API endpoint.

    Args:
        endpoint_key (str): The key identifying the API configuration.
        **kwargs: Additional parameters for URL formatting or overriding params.

    Returns:
        dict or None: The JSON response from the API or None if failed.
    """
    config = API_CONFIG.get(endpoint_key)
    if not config:
        print(f"No configuration found for endpoint '{endpoint_key}'.")
        return None

    try:
        url = config["url"].format(**kwargs)
    except KeyError as e:
        print(f"URL formatting failed for endpoint '{endpoint_key}': Missing key {e.args[0]}")
        return None

    headers = config["headers"]
    params = config["params"].copy()

    # Update params if provided
    if "params_override" in kwargs and kwargs["params_override"]:
        params.update(kwargs["params_override"])

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request to '{endpoint_key}' failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response from '{endpoint_key}': {e}")
        return None

def write_to_csv(data, fieldnames, filename):
    """
    Write a list of dictionaries to a CSV file.

    Args:
        data (list): List of dictionaries containing the data.
        fieldnames (list): List of field names for the CSV header.
        filename (str): The name of the output CSV file.

    Returns:
        bool: True if writing was successful, False otherwise.
    """
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data successfully written to {filename}")
        return True
    except IOError as e:
        print(f"Failed to write to CSV file '{filename}': {e}")
        return False
    except Exception as e:
        print(f"Unexpected error while writing to CSV: {e}")
        return False

def get_applications():
    """
    Fetch and save applications data.

    Returns:
        list: List of application items or empty list if failed.
    """
    response_data = fetch_api_data("applications")
    if not response_data:
        return []

    items = response_data.get("items", [])
    if not items:
        print("No applications found.")
        return []

    # Write to CSV
    fieldnames = items[0].keys() if items else []
    success = write_to_csv(items, fieldnames, API_CONFIG["applications"]["output_file"])
    return items if success else []

def fetch_issues(version_id):
    """
    Fetch security issues for a specific project version.

    Args:
        version_id (str): The ID of the project version.

    Returns:
        list: List of issue items.
    """
    response_data = fetch_api_data("issues", version_id=version_id)
    if not response_data or "data" not in response_data:
        print(f"No issues found for version ID '{version_id}'.")
        return []

    return response_data.get("data", [])

def format_issue_data(issue, fields):
    """
    Format issue data for CSV output.

    Args:
        issue (dict): The issue data.
        fields (list): List of fields to include.

    Returns:
        dict: Formatted issue data.
    """
    return {key: issue.get(key, "") for key in fields}

def process_issues(versions):
    """
    Process and save security issues data for all versions.

    Args:
        versions (list): List of version dictionaries.

    Returns:
        list: List of all issues collected.
    """
    all_issues = []
    total_versions = len(versions)

    # Determine CSV fields from first issue
    sample_issue = None
    for version in versions:
        version_id = version.get("id")
        if version_id:
            sample_issue = fetch_issues(version_id)
            if sample_issue:
                sample_issue = sample_issue[0]
                break

    if not sample_issue:
        print("No issues available to determine CSV fields.")
        return []

    issue_fields = list(sample_issue.keys())

    for index, version in enumerate(versions, 1):
        version_id = version.get("id")
        if not version_id:
            continue

        print(f"Processing issues for version {index}/{total_versions} (ID: {version_id})")
        issues = fetch_issues(version_id)
        formatted_issues = [format_issue_data(issue, issue_fields) for issue in issues]
        all_issues.extend(formatted_issues)

    if all_issues:
        write_to_csv(all_issues, issue_fields, API_CONFIG["issues"]["output_file"])
        print(f"Total issues found and saved: {len(all_issues)}")
    else:
        print("No issues found.")

    return all_issues

def process_versions(applications):
    """
    Process and save versions data for all applications.

    Args:
        applications (list): List of application dictionaries.

    Returns:
        list: List of all versions collected.
    """
    all_versions = []

    for app in applications:
        project_id = app.get("id")
        if not project_id:
            continue

        print(f"Fetching versions for application '{app.get('name', 'N/A')}' (ID: {project_id})")
        versions_data = fetch_api_data("versions", project_id=project_id)
        if versions_data:
            versions = versions_data.get("data", [])
            all_versions.extend(versions)

    if all_versions:
        # Format versions data
        formatted_versions = [format_version_data(version) for version in all_versions]
        write_to_csv(formatted_versions, API_CONFIG["versions"]["fields"], API_CONFIG["versions"]["output_file"])
        print(f"Total versions found: {len(all_versions)}")
    else:
        print("No versions found.")

    return all_versions

def format_version_data(version):
    """
    Format version data for CSV output.

    Args:
        version (dict): The version data.

    Returns:
        dict: Formatted version data.
    """
    project = version.get("project", {})
    application = version.get("application", {})
    source_control = version.get("sourceControl", {})

    return {
        "Project Name": project.get("name", ""),
        "Project ID": project.get("id", ""),
        "Version ID": version.get("id", ""),
        "Version Name": version.get("name", ""),
        "Version Description": version.get("description", ""),
        "Project Version Status": version.get("status", ""),
        "Server Version Status": version.get("serverVersion", ""),
        "Issue Template ID": version.get("issueTemplateId", ""),
        "Issue Template Name": version.get("issueTemplateName", ""),
        "Development Phase": version.get("phase", ""),
        "Development Strategy": version.get("strategy", ""),
        "Business Risk Rating": version.get("businessRiskRating", ""),
        "Business Criticality": version.get("businessCriticality", ""),
        "Repository URL": source_control.get("url", ""),
        "Repository Type": source_control.get("type", ""),
        "Issue Status": version.get("issueStatus", ""),
        "Analysis Status": version.get("analysisStatus", ""),
        "Current Analysis Date": version.get("currentAnalysisDate", ""),
        "Published Status": version.get("publishedStatus", ""),
        "Project Owner": project.get("owner", ""),
        "Project Owner First Name": project.get("ownerFirstName", ""),
        "Project Owner Last Name": project.get("ownerLastName", ""),
        "Project Owner Email": project.get("ownerEmail", ""),
        "Application Name": application.get("name", ""),
        "Application ID": application.get("id", ""),
        "Application Type": application.get("type", ""),
        "Application Business Unit": application.get("businessUnit", ""),
        "Application Tags": ", ".join(application.get("tags", [])),
        "Project Created By": project.get("createdBy", ""),
        "Project Creation Date": project.get("creationDate", ""),
    }

def main():
    """
    Main execution function.
    """
    try:
        # Fetch applications
        applications = get_applications()
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